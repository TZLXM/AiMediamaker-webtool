"""
任务队列模块
负责管理任务队列，轮询任务状态，处理并发控制

架构说明：
- 使用 Redis 做分布式并发计数，支持多进程/多 Worker 部署
- 内存中维护 asyncio.Task 映射，用于取消本地轮询协程
- 服务重启后通过 recover_tasks() 恢复未完成的任务
"""
from __future__ import annotations

import asyncio
import base64
import uuid
from datetime import datetime
from typing import Dict, Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from ..core.config import settings
from ..core.redis import redis_client
from ..models.task import Task, TaskMode, TaskStatus
from ..models.file import FileRecord
from ..services.model_manager import model_manager

if TYPE_CHECKING:
    from ..services.volcengine_client import VolcengineClient


class TaskQueue:
    """异步任务队列管理器"""
    
    def __init__(self):
        self._running_tasks: Dict[str, asyncio.Task] = {}  # platform_task_id -> asyncio.Task
        self._poll_interval = settings.TASK_POLL_INTERVAL
        self._max_retries = settings.TASK_MAX_RETRIES
        self._shutdown = False
        # Redis 不可用时回退到内存计数
        self._memory_active_counts: Dict[str, int] = {}
    
    def _generate_platform_task_id(self) -> str:
        """生成唯一的平台任务ID"""
        return f"task_{uuid.uuid4().hex[:16]}"
    
    # --- 并发控制 (Redis 分布式) ---
    
    async def get_active_count(self, model_id: str) -> int:
        """获取模型当前活跃任务数"""
        if redis_client.is_connected():
            return await redis_client.get_model_active(model_id)
        return self._memory_active_counts.get(model_id, 0)
    
    async def can_start_task(self, model_id: str) -> bool:
        """检查是否可以开始新任务"""
        limit = model_manager.get_model_concurrency(model_id)
        active = await self.get_active_count(model_id)
        return active < limit
    
    async def _acquire_slot(self, model_id: str) -> bool:
        """尝试占用一个并发槽位"""
        limit = model_manager.get_model_concurrency(model_id)
        if redis_client.is_connected():
            active = await redis_client.incr_model_active(model_id)
            if active > limit:
                # 超限，回滚
                await redis_client.decr_model_active(model_id)
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[Concurrency] Slot denied for {model_id}: active={active-1} >= limit={limit}")
                return False
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[Concurrency] Slot acquired for {model_id}: active={active} / limit={limit}")
            return True
        # 内存回退
        active = self._memory_active_counts.get(model_id, 0) + 1
        if active > limit:
            return False
        self._memory_active_counts[model_id] = active
        return True
    
    async def _release_slot(self, model_id: str):
        """释放并发槽位"""
        import logging
        logger = logging.getLogger(__name__)
        if redis_client.is_connected():
            active = await redis_client.decr_model_active(model_id)
            logger.info(f"[Concurrency] Slot released for {model_id}: active={active}")
        else:
            self._memory_active_counts[model_id] = max(
                0, self._memory_active_counts.get(model_id, 0) - 1
            )
    
    # --- 任务入队 ---
    
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
        platform_task_id = self._generate_platform_task_id()
        
        task = Task(
            platform_task_id=platform_task_id,
            user_id=user_id,
            mode=mode,
            model_id=model_id,
            prompt=prompt,
            parameters=parameters or {},
            status=TaskStatus.QUEUED,
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
    
    # --- 任务处理 ---
    
    async def start_task_processing(self, db_factory, platform_task_id: str):
        """启动任务处理 (异步轮询)"""
        if platform_task_id in self._running_tasks:
            return
        if self._shutdown:
            return
        
        task_coro = self._process_task(db_factory, platform_task_id)
        asyncio_task = asyncio.create_task(task_coro, name=f"task-{platform_task_id}")
        self._running_tasks[platform_task_id] = asyncio_task
        
        # 清理完成任务
        asyncio_task.add_done_callback(
            lambda t, ptid=platform_task_id: self._running_tasks.pop(ptid, None)
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
            
            # 等待并发槽位（带超时）
            slot_acquired = False
            wait_start = datetime.now()
            max_wait_seconds = 3600  # 最多等待1小时
            
            while not slot_acquired:
                if self._shutdown:
                    return
                
                slot_acquired = await self._acquire_slot(model_id)
                if not slot_acquired:
                    elapsed = (datetime.now() - wait_start).total_seconds()
                    if elapsed > max_wait_seconds:
                        task.status = TaskStatus.FAILED
                        task.error_message = "等待并发槽位超时"
                        task.completed_at = datetime.now()
                        await db.commit()
                        return
                    await asyncio.sleep(5)
            
            try:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                await db.commit()
                
                # 调用远端API创建任务（带重试）
                remote_task_id = None
                last_error = None
                
                for attempt in range(self._max_retries):
                    try:
                        client = VolcengineClient(model_id)
                        remote_task_id = await client.create_task(task, db=db)
                        break
                    except Exception as e:
                        last_error = e
                        if attempt < self._max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # 指数退避
                
                if remote_task_id is None:
                    raise last_error or RuntimeError("创建远端任务失败")
                
                task.remote_task_id = remote_task_id
                await db.commit()
                
                # 轮询任务状态
                await self._poll_task(db, task, client, remote_task_id)
                
            except asyncio.CancelledError:
                # 任务被取消
                task.status = TaskStatus.CANCELLED
                task.cancelled_at = datetime.now()
                await db.commit()
                raise
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.now()
                await db.commit()
            finally:
                # 释放槽位
                await self._release_slot(model_id)
    
    async def _poll_task(self, db: AsyncSession, task: Task, client: VolcengineClient, remote_task_id: str):
        """轮询单个任务状态"""
        poll_errors = 0
        max_poll_errors = 5
        
        while True:
            if self._shutdown and task.status != TaskStatus.RUNNING:
                return
            
            await asyncio.sleep(self._poll_interval)
            
            try:
                status_result = await client.get_task_status(remote_task_id)
                poll_errors = 0  # 重置错误计数
            except Exception as e:
                poll_errors += 1
                if poll_errors >= max_poll_errors:
                    task.status = TaskStatus.FAILED
                    task.error_message = f"轮询任务状态连续失败 {max_poll_errors} 次: {e}"
                    task.completed_at = datetime.now()
                    await db.commit()
                    return
                await db.commit()
                continue
            
            status = status_result.get("status")
            
            if status == "succeeded":
                task.status = TaskStatus.SUCCEEDED
                task.completed_at = datetime.now()
                # 记录资源用量
                usage = status_result.get("usage", {})
                if usage and usage.get("completion_tokens"):
                    task.usage_tokens = usage["completion_tokens"]
                # 下载生成的文件
                await self._download_outputs(db, task, status_result)
                await db.commit()
                break
            elif status == "failed":
                task.status = TaskStatus.FAILED
                task.error_code = status_result.get("error", {}).get("code")
                task.error_message = status_result.get("error", {}).get("message")
                task.completed_at = datetime.now()
                await db.commit()
                break
            elif status == "cancelled":
                task.status = TaskStatus.CANCELLED
                task.cancelled_at = datetime.now()
                await db.commit()
                break
            
            # running / queued -> 继续轮询，更新DB以便前端可见
            await db.commit()
    
    async def _download_outputs(self, db: AsyncSession, task: Task, result: dict):
        """下载模型生成的文件"""
        from ..services.file_manager import file_manager
        import httpx
        
        # 兼容多种返回格式：
        # 1. {"content": {"video_url": "..."}} 或 {"content": {"video_url": {"url": "..."}}}
        # 2. {"content": [{"video_url": "..."}, ...]}
        # 3. {"content": [{"image_url": {"url": "..."}}, ...]}
        raw_content = result.get("content")
        contents = []
        if isinstance(raw_content, list):
            contents = raw_content
        elif isinstance(raw_content, dict):
            contents = [raw_content]
        
        for idx, content in enumerate(contents):
            url = None
            mime_hint = ""
            
            if isinstance(content, dict):
                # 视频URL：可能是字符串或 {"url": "..."}
                video_url = content.get("video_url")
                if video_url:
                    if isinstance(video_url, str):
                        url = video_url
                        mime_hint = "video"
                    elif isinstance(video_url, dict):
                        url = video_url.get("url")
                        mime_hint = "video"
                
                # 图片URL：可能是字符串或 {"url": "..."}
                image_url = content.get("image_url")
                if image_url:
                    if isinstance(image_url, str):
                        url = image_url
                        mime_hint = "image"
                    elif isinstance(image_url, dict):
                        url = image_url.get("url")
                        mime_hint = "image"
            
            if not url:
                continue
            
            try:
                # Base64 数据直接解码保存
                if url.startswith("data:"):
                    header, b64 = url.split(",", 1)
                    mime = header.split(";")[0].split(":")[1] if ";" in header else "application/octet-stream"
                    data = base64.b64decode(b64)
                    ext = ".png" if "image" in mime else ".mp4"
                    await file_manager.save_model_output(
                        db=db,
                        file_data=data,
                        original_name=f"output_{task.platform_task_id}_{idx}{ext}",
                        mime_type=mime,
                        source_task_id=task.id,
                        user_id=task.user_id,
                    )
                    continue
                
                # HTTP URL 下载
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=120)
                    resp.raise_for_status()
                    
                    mime = resp.headers.get("content-type", "application/octet-stream")
                    if mime == "application/octet-stream" and mime_hint:
                        mime = f"{mime_hint}/mp4" if mime_hint == "video" else f"{mime_hint}/png"
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
    
    # --- 任务取消 ---
    
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
        
        # 如果任务还在排队，直接取消
        if task.status == TaskStatus.QUEUED:
            task.status = TaskStatus.CANCELLED
            task.cancelled_at = datetime.now()
            await db.commit()
            return True
        
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
    
    # --- 任务恢复 ---
    
    async def recover_tasks(self, db: AsyncSession, db_factory):
        """服务启动时恢复未完成的任务"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 先重置所有 Redis 计数器，避免旧泄漏影响新任务
        await redis_client.reset_all_model_active()
        logger.info("[Concurrency] Reset all model active counters on startup")
        
        # 恢复 QUEUED 状态的任务
        queued_result = await db.execute(
            select(Task).where(Task.status == TaskStatus.QUEUED)
        )
        for task in queued_result.scalars().all():
            await self.start_task_processing(db_factory, task.platform_task_id)
        
        # RUNNING 状态的任务：远端可能还在运行，需要恢复轮询
        running_result = await db.execute(
            select(Task).where(Task.status == TaskStatus.RUNNING)
        )
        running_tasks = running_result.scalars().all()
        for task in running_tasks:
            # 先占用槽位，再恢复轮询
            await redis_client.incr_model_active(task.model_id)
            await self.start_task_processing(db_factory, task.platform_task_id)
        logger.info(f"[Concurrency] Recovered {len(running_tasks)} RUNNING tasks with fresh counters")
    
    # --- 优雅关闭 ---
    
    async def shutdown(self):
        """优雅关闭：取消所有运行中的本地任务"""
        self._shutdown = True
        for platform_task_id, asyncio_task in list(self._running_tasks.items()):
            asyncio_task.cancel()
        
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
        self._running_tasks.clear()


# 全局实例
task_queue = TaskQueue()
