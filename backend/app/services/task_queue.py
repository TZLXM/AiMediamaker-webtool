"""
任务队列模块
负责管理任务队列，轮询任务状态，处理并发控制
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from ..core.config import settings
from ..models.task import Task, TaskMode, TaskStatus
from ..models.file import FileRecord
from ..services.model_manager import model_manager


class TaskQueue:
    """异步任务队列管理器"""
    
    def __init__(self):
        self._running_tasks: Dict[str, asyncio.Task] = {}  # platform_task_id -> asyncio.Task
        self._active_counts: Dict[str, int] = {}  # model_id -> 当前活跃任务数
        self._poll_interval = settings.TASK_POLL_INTERVAL
    
    def _generate_platform_task_id(self) -> str:
        """生成唯一的平台任务ID"""
        return f"task_{uuid.uuid4().hex[:16]}"
    
    def get_active_count(self, model_id: str) -> int:
        """获取模型当前活跃任务数"""
        return self._active_counts.get(model_id, 0)
    
    def can_start_task(self, model_id: str) -> bool:
        """检查是否可以开始新任务"""
        limit = model_manager.get_model_concurrency(model_id)
        return self.get_active_count(model_id) < limit
    
    async def enqueue(
        self,
        db: AsyncSession,
        user_id: int,
        mode: TaskMode,
        model_id: str,
        prompt: str,
        parameters: Optional[dict],
        file_ids: Optional[list]
    ) -> Task:
        """将任务加入队列"""
        # 创建任务记录
        platform_task_id = self._generate_platform_task_id()
        
        task = Task(
            platform_task_id=platform_task_id,
            user_id=user_id,
            mode=mode,
            model_id=model_id,
            prompt=prompt,
            parameters=parameters or {},
            status=TaskStatus.PENDING,
        )
        
        # 关联文件
        if file_ids:
            files_result = await db.execute(
                select(FileRecord).where(FileRecord.file_id.in_(file_ids))
            )
            files = files_result.scalars().all()
            task.input_files = list(files)
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        return task
    
    async def start_task_processing(self, db_factory, platform_task_id: str):
        """启动任务处理 (异步轮询)"""
        if platform_task_id in self._running_tasks:
            return
        
        task_coro = self._process_task(db_factory, platform_task_id)
        asyncio_task = asyncio.create_task(task_coro)
        self._running_tasks[platform_task_id] = asyncio_task
        
        # 清理完成任务
        asyncio_task.add_done_callback(
            lambda t: self._running_tasks.pop(platform_task_id, None)
        )
    
    async def _process_task(self, db_factory, platform_task_id: str):
        """任务处理主循环"""
        from ..services.volcengine_client import VolcengineClient
        
        async with db_factory() as db:
            result = await db.execute(
                select(Task).where(Task.platform_task_id == platform_task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                return
            
            model_id = task.model_id
            
            # 等待并发槽位
            while not self.can_start_task(model_id):
                await asyncio.sleep(5)
            
            # 占用槽位
            self._active_counts[model_id] = self._active_counts.get(model_id, 0) + 1
            
            try:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                await db.commit()
                
                # 调用远端API创建任务
                client = VolcengineClient(model_id)
                remote_task_id = await client.create_task(task, db=db)
                
                task.remote_task_id = remote_task_id
                await db.commit()
                
                # 轮询任务状态
                while True:
                    await asyncio.sleep(self._poll_interval)
                    
                    status_result = await client.get_task_status(remote_task_id)
                    status = status_result.get("status")
                    
                    if status == "succeeded":
                        task.status = TaskStatus.SUCCEEDED
                        task.completed_at = datetime.now()
                        # 下载生成的文件
                        await self._download_outputs(db, task, status_result)
                        break
                    elif status == "failed":
                        task.status = TaskStatus.FAILED
                        task.error_code = status_result.get("error", {}).get("code")
                        task.error_message = status_result.get("error", {}).get("message")
                        task.completed_at = datetime.now()
                        break
                    elif status == "cancelled":
                        task.status = TaskStatus.CANCELLED
                        task.cancelled_at = datetime.now()
                        break
                    
                    # running / queued -> 继续轮询
                    await db.commit()
                
                await db.commit()
                
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.now()
                await db.commit()
            finally:
                # 释放槽位
                self._active_counts[model_id] = max(0, self._active_counts.get(model_id, 0) - 1)
    
    async def _download_outputs(self, db: AsyncSession, task: Task, result: dict):
        """下载模型生成的文件"""
        from ..services.file_manager import file_manager
        import httpx
        
        contents = result.get("content", [])
        if not isinstance(contents, list):
            contents = [contents]
        
        for idx, content in enumerate(contents):
            if isinstance(content, dict) and content.get("video_url"):
                url = content["video_url"]
            elif isinstance(content, dict) and content.get("image_url"):
                url = content["image_url"]
            else:
                continue
            
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=120)
                    resp.raise_for_status()
                    
                    mime = resp.headers.get("content-type", "application/octet-stream")
                    ext = ".mp4" if "video" in mime else ".png"
                    
                    await file_manager.save_model_output(
                        db=db,
                        file_data=resp.content,
                        original_name=f"output_{task.platform_task_id}_{idx}{ext}",
                        mime_type=mime,
                        source_task_id=task.id,
                        user_id=task.user_id,
                    )
            except Exception:
                pass  # 下载失败但不中断流程
    
    async def cancel_task(self, db: AsyncSession, platform_task_id: str, user_id: int) -> bool:
        """取消任务"""
        result = await db.execute(
            select(Task).where(
                and_(
                    Task.platform_task_id == platform_task_id,
                    Task.user_id == user_id
                )
            )
        )
        task = result.scalar_one_or_none()
        
        if not task:
            return False
        
        if task.status in (TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            return False
        
        # 如果已提交到远端，调用远端取消
        if task.remote_task_id:
            from ..services.volcengine_client import VolcengineClient
            client = VolcengineClient(task.model_id)
            await client.cancel_task(task.remote_task_id)
        
        task.status = TaskStatus.CANCELLED
        task.cancelled_at = datetime.now()
        await db.commit()
        
        # 取消本地轮询任务
        if platform_task_id in self._running_tasks:
            self._running_tasks[platform_task_id].cancel()
        
        return True


# 全局实例
task_queue = TaskQueue()
