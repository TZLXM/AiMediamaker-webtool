"""
火山方舟 API 客户端
封装视频生成(Seedance)和图片生成(Seedream) API调用

API 文档:
- Seedance: https://www.volcengine.com/docs/82379/2291680
- Seedream: https://www.volcengine.com/docs/82379/1824121
- 多模态输入: https://www.volcengine.com/docs/82379/2298881
"""
import base64
import httpx
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.config import settings
from ..services.model_manager import model_manager
from ..services.file_processor import file_processor

logger = logging.getLogger(__name__)

# Seedream 官方文档推荐像素值映射表
# 模型ID -> 分辨率档位 -> 比例 -> 像素值
SEEDREAM_SIZE_MAP = {
    "doubao-seedream-5-0-lite-260128": {
        "2K": {"1:1": "2048x2048", "3:4": "1728x2304", "4:3": "2304x1728", "16:9": "2848x1600", "9:16": "1600x2848", "3:2": "2496x1664", "2:3": "1664x2496", "21:9": "3136x1344"},
        "3K": {"1:1": "3072x3072", "3:4": "2592x3456", "4:3": "3456x2592", "16:9": "4096x2304", "9:16": "2304x4096", "2:3": "2496x3744", "3:2": "3744x2496", "21:9": "4704x2016"},
        "4K": {"1:1": "4096x4096", "3:4": "3520x4704", "4:3": "4704x3520", "16:9": "5504x3040", "9:16": "3040x5504", "2:3": "3328x4992", "3:2": "4992x3328", "21:9": "6240x2656"},
    },
    "doubao-seedream-4-5-260128": {
        "2K": {"1:1": "2048x2048", "3:4": "1728x2304", "4:3": "2304x1728", "16:9": "2848x1600", "9:16": "1600x2848", "3:2": "2496x1664", "2:3": "1664x2496", "21:9": "3136x1344"},
        "4K": {"1:1": "4096x4096", "3:4": "3520x4704", "4:3": "4704x3520", "16:9": "5504x3040", "9:16": "3040x5504", "2:3": "3328x4992", "3:2": "4992x3328", "21:9": "6240x2656"},
    },
    "doubao-seedream-4-5-251128": {
        "2K": {"1:1": "2048x2048", "3:4": "1728x2304", "4:3": "2304x1728", "16:9": "2848x1600", "9:16": "1600x2848", "3:2": "2496x1664", "2:3": "1664x2496", "21:9": "3136x1344"},
        "4K": {"1:1": "4096x4096", "3:4": "3520x4704", "4:3": "4704x3520", "16:9": "5504x3040", "9:16": "3040x5504", "2:3": "3328x4992", "3:2": "4992x3328", "21:9": "6240x2656"},
    },
}


class VolcengineAPIError(Exception):
    """火山方舟API业务错误"""
    def __init__(self, code: str, message: str, status_code: int = 0):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{code}] {message}")


class VolcengineClient:
    """火山方舟API客户端"""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.api_key = model_manager.get_api_key(model_id)
        self.base_url = model_manager.get_base_url(model_id)
        
        if not self.api_key:
            raise VolcengineAPIError(
                code="missing_api_key",
                message="该模型未配置有效的 API Key，请在后台管理系统中配置",
                status_code=0,
            )
        
        # HTTP header 必须是 ASCII，提前检查避免 UnicodeEncodeError
        try:
            self.api_key.encode("ascii")
        except UnicodeEncodeError:
            raise VolcengineAPIError(
                code="invalid_api_key_format",
                message="API Key 包含非 ASCII 字符（如中文），请检查后台配置",
                status_code=0,
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # 用于暂存同步图片生成结果（单实例顺序使用，无需线程安全）
        self._last_image_result: Optional[Dict[str, Any]] = None
    
    async def create_task(self, task, db: Optional[AsyncSession] = None) -> str:
        """创建生成任务，返回远端任务ID"""
        if task.mode == "video":
            return await self._create_video_task(task, db=db)
        else:
            result = await self._create_image_task(task, db=db)
            self._last_image_result = result
            # 使用 created 时间戳作为伪任务ID，便于追踪
            return f"img_sync_{result.get('created', '')}"
    
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
            
            ft = str(file_record.file_type)
            if ft == "image":
                contents.append({
                    "type": "image_url",
                    "image_url": file_content,
                    "role": "reference_image",
                })
            elif ft == "video":
                contents.append({
                    "type": "video_url",
                    "video_url": file_content,
                    "role": "reference_video",
                })
            elif ft == "audio":
                contents.append({
                    "type": "audio_url",
                    "audio_url": file_content,
                    "role": "reference_audio",
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
        if params.get("resolution"):
            payload["resolution"] = params["resolution"]
        if params.get("generate_audio") is not None:
            payload["generate_audio"] = params["generate_audio"]
        if params.get("watermark") is not None:
            payload["watermark"] = params["watermark"]
        if params.get("seed") is not None:
            payload["seed"] = params["seed"]
        
        # 额外参数（如 tools 等）
        extra = params.get("extra") or {}
        for key, value in extra.items():
            if key not in payload:
                payload[key] = value
        
        logger.info(f"[Seedance] Creating video task with model={self.model_id}, content_items={len(contents)}")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/contents/generations/tasks",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            return self._parse_task_response(resp)
    


    async def _create_image_task(self, task, db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """创建图片生成任务 (Seedream)，返回完整响应数据"""
        payload = {
            "model": self.model_id,
            "prompt": task.prompt,
        }
        
        # 参考图
        images = []
        for file_record in task.input_files:
            if str(file_record.file_type) == "image":
                file_content = await self._prepare_file_content(file_record, db=db)
                images.append(file_content["url"])
        
        if images:
            payload["image"] = images if len(images) > 1 else images[0]
        
        # 参数
        params = task.parameters or {}
        
        # size 处理：有具体比例时发送像素值，否则发送分辨率值
        resolution = params.get("resolution")
        aspect_ratio = params.get("aspectRatio")
        if resolution and aspect_ratio and aspect_ratio != "adaptive":
            # 根据模型ID + 分辨率 + 比例 查找对应像素值
            model_map = SEEDREAM_SIZE_MAP.get(self.model_id, {})
            res_map = model_map.get(resolution, {})
            pixel_size = res_map.get(aspect_ratio)
            if pixel_size:
                payload["size"] = pixel_size
                logger.info(f"[Seedream] Mapped {resolution}+{aspect_ratio} -> {pixel_size}")
            else:
                # 未找到映射，回退到分辨率值
                payload["size"] = resolution
        elif resolution:
            payload["size"] = resolution
        elif params.get("size"):
            payload["size"] = params["size"]
        if params.get("output_format"):
            payload["output_format"] = params["output_format"]
        if params.get("sequential_image_generation"):
            payload["sequential_image_generation"] = params["sequential_image_generation"]
        if params.get("max_images"):
            payload["sequential_image_generation_options"] = {"max_images": params["max_images"]}
        if params.get("watermark") is not None:
            payload["watermark"] = params["watermark"]
        if params.get("response_format"):
            payload["response_format"] = params["response_format"]
        
        # 额外参数（如 tools 等）
        extra = params.get("extra") or {}
        for key, value in extra.items():
            if key not in payload:
                payload[key] = value
        
        logger.info(f"[Seedream] Creating image task with model={self.model_id}, refs={len(images)}")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/images/generations",
                headers=self.headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            
            # 检查API返回的业务错误
            if data.get("error"):
                error = data["error"]
                raise VolcengineAPIError(
                    code=error.get("code", "unknown"),
                    message=error.get("message", "Unknown error"),
                    status_code=resp.status_code,
                )
            
            return data
    
    async def get_task_status(self, remote_task_id: str) -> Dict[str, Any]:
        """获取任务状态，返回完整响应（含 usage）"""
        if remote_task_id.startswith("img_sync_"):
            # 图片任务是同步的，结果已在 create_task 时返回
            contents = []
            usage = {}
            if self._last_image_result:
                usage = self._last_image_result.get("usage", {})
                for item in self._last_image_result.get("data", []):
                    if "url" in item:
                        contents.append({"image_url": {"url": item["url"]}})
                    elif "b64_json" in item:
                        contents.append({"image_url": {"url": f"data:image/png;base64,{item['b64_json']}"}})
            return {
                "status": "succeeded",
                "content": contents,
                "usage": usage,
            }
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/contents/generations/tasks/{remote_task_id}",
                headers=self.headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            
            # 检查API返回的业务错误（任务失败时返回200但带有error字段）
            if data.get("error"):
                error = data["error"]
                logger.warning(f"[Seedance] Task API error: {error}")
            
            return data
    
    async def cancel_task(self, remote_task_id: str) -> bool:
        """取消远端任务（使用DELETE方法）"""
        if remote_task_id.startswith("img_sync_"):
            return True
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.delete(
                    f"{self.base_url}/contents/generations/tasks/{remote_task_id}",
                    headers=self.headers,
                    timeout=30,
                )
                return resp.status_code in (200, 202, 204)
        except Exception as e:
            logger.warning(f"[Volcengine] Failed to cancel task {remote_task_id}: {e}")
            return False
    
    def _parse_task_response(self, resp: httpx.Response) -> str:
        """解析任务创建响应，提取任务ID或抛出详细错误"""
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            # 尝试解析错误响应体
            try:
                error_data = e.response.json()
                error = error_data.get("error", {})
                code = error.get("code", f"HTTP_{e.response.status_code}")
                message = error.get("message", str(e))
            except Exception:
                code = f"HTTP_{e.response.status_code}"
                message = e.response.text or str(e)
            
            logger.error(f"[Volcengine] API error {code}: {message}")
            raise VolcengineAPIError(code=code, message=message, status_code=e.response.status_code)
        
        data = resp.json()
        
        # 检查API返回的业务错误（即使HTTP 200也可能包含错误）
        if data.get("error"):
            error = data["error"]
            code = error.get("code", "unknown")
            message = error.get("message", "Unknown error")
            logger.error(f"[Volcengine] API business error {code}: {message}")
            raise VolcengineAPIError(code=code, message=message, status_code=resp.status_code)
        
        task_id = data.get("id")
        if not task_id:
            raise VolcengineAPIError(
                code="missing_task_id",
                message="API response does not contain task id",
                status_code=resp.status_code,
            )
        
        logger.info(f"[Volcengine] Task created: {task_id}")
        return task_id
