"""
任务相关 Pydantic Schema
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class TaskParameter(BaseModel):
    # 视频参数
    ratio: Optional[str] = None           # 16:9, 9:16, 1:1, adaptive
    duration: Optional[int] = None        # 视频时长(秒)
    resolution: Optional[str] = None      # 分辨率
    fps: Optional[int] = None             # 帧率
    generate_audio: Optional[bool] = None # 是否生成音频
    watermark: Optional[bool] = None      # 是否水印
    seed: Optional[int] = None            # 随机种子
    
    # 图片参数
    size: Optional[str] = None            # 1K, 2K, 3K
    output_format: Optional[str] = None   # png, jpeg
    sequential_image_generation: Optional[str] = None  # auto, disabled
    max_images: Optional[int] = None      # 组图最大数量
    
    # 通用
    extra: Optional[dict] = None


class TaskCreate(BaseModel):
    mode: str = Field(..., pattern="^(image|video)$")
    model_id: str
    prompt: str = Field(..., min_length=1)
    parameters: Optional[TaskParameter] = None
    file_ids: Optional[List[str]] = []    # 关联的上传文件ID列表


class TaskCancel(BaseModel):
    platform_task_id: str


class TaskResponse(BaseModel):
    id: int
    platform_task_id: str
    mode: str
    model_id: str
    prompt: str
    parameters: Optional[dict]
    status: str
    error_code: Optional[str]
    error_message: Optional[str]
    remote_task_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    usage_tokens: Optional[int]
    created_at: datetime
    input_files: List[Any] = []   # FileResponse simplified
    output_files: List[Any] = []  # FileResponse simplified
    
    class Config:
        from_attributes = True


class TaskHistoryFilter(BaseModel):
    mode: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20
