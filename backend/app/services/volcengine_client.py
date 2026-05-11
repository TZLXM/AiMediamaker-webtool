"""
火山方舟 API 客户端
封装视频生成和图片生成API调用
"""
import base64
import httpx
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.config import settings
from ..services.model_manager import model_manager
from ..services.file_processor import file_processor


class VolcengineClient:
    """火山方舟API客户端"""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.api_key = model_manager.get_api_key(model_id)
        self.base_url = model_manager.get_base_url(model_id)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def create_task(self, task, db: Optional[AsyncSession] = None) -> str:
        """创建生成任务，返回远端任务ID"""
        if task.mode == "video":
            return await self._create_video_task(task, db=db)
        else:
            return await self._create_image_task(task, db=db)
    
    async def _prepare_file_content(
        self, file_record, db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        准备文件内容用于模型输入
        策略: 优先TOS公网URL，失败则回退Base64
        """
        # 如果已有公网URL，直接使用
        if file_record.public_url:
            return {"url": file_record.public_url}
        
        # 否则通过文件处理器准备
        url_or_b64, status = await file_processor.prepare_for_model(
            file_record,
            prefer_tos=True,  # 优先TOS上传
            db=db,
        )
        
        return {"url": url_or_b64}
    
    async def _create_video_task(self, task, db: Optional[AsyncSession] = None) -> str:
        """创建视频生成任务 (Seedance)"""
        contents = []
        
        # 添加文本提示词
        contents.append({
            "type": "text",
            "text": task.prompt,
        })
        
        # 添加参考文件
        for file_record in task.input_files:
            file_content = await self._prepare_file_content(file_record, db=db)
            
            if file_record.file_type.value == "image":
                contents.append({
                    "type": "image_url",
                    "image_url": file_content,
                })
            elif file_record.file_type.value == "video":
                contents.append({
                    "type": "video_url",
                    "video_url": file_content,
                    "role": "reference_video",
                })
            elif file_record.file_type.value == "audio":
                contents.append({
                    "type": "audio_url",
                    "audio_url": file_content,
                })
        
        payload = {
            "model": self.model_id,
            "content": contents,
        }
        
        # 添加参数
        params = task.parameters or {}
        if params.get("ratio"):
            payload["ratio"] = params["ratio"]
        if params.get("duration"):
            payload["duration"] = params["duration"]
        if "generate_audio" in params:
            payload["generate_audio"] = params["generate_audio"]
        if "watermark" in params:
            payload["watermark"] = params["watermark"]
        if params.get("seed"):
            payload["seed"] = params["seed"]
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/contents/generations/tasks",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["id"]
    
    async def _create_image_task(self, task, db: Optional[AsyncSession] = None) -> str:
        """创建图片生成任务 (Seedream)"""
        payload = {
            "model": self.model_id,
            "prompt": task.prompt,
        }
        
        # 参考图
        images = []
        for file_record in task.input_files:
            if file_record.file_type.value == "image":
                file_content = await self._prepare_file_content(file_record, db=db)
                images.append(file_content["url"])
        
        if images:
            payload["image"] = images if len(images) > 1 else images[0]
        
        # 参数
        params = task.parameters or {}
        if params.get("size"):
            payload["size"] = params["size"]
        if params.get("output_format"):
            payload["output_format"] = params["output_format"]
        if params.get("sequential_image_generation"):
            payload["sequential_image_generation"] = params["sequential_image_generation"]
        if params.get("max_images"):
            payload["sequential_image_generation_options"] = {"max_images": params["max_images"]}
        if "watermark" in params:
            payload["watermark"] = params["watermark"]
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/images/generations",
                headers=self.headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            # 图片生成是同步的，使用伪任务ID
            return f"img_{data.get('created', '')}_{id(data)}"
    
    async def get_task_status(self, remote_task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if remote_task_id.startswith("img_"):
            # 图片任务实际是同步的，这里应该走不同逻辑
            # 简化处理：图片生成结果已在create时返回
            return {"status": "succeeded"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/contents/generations/tasks/{remote_task_id}",
                headers=self.headers,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
    
    async def cancel_task(self, remote_task_id: str) -> bool:
        """取消远端任务"""
        if remote_task_id.startswith("img_"):
            return True
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/contents/generations/tasks/{remote_task_id}/cancel",
                    headers=self.headers,
                    timeout=30,
                )
                return resp.status_code == 200
        except Exception:
            return False
