"""
任务相关 Pydantic Schema
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


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
    model_config = ConfigDict(protected_namespaces=())
    mode: str = Field(..., pattern="^(image|video)$")
    model_id: str
    prompt: str = Field(..., min_length=1)
    parameters: Optional[TaskParameter] = None
    file_ids: Optional[List[str]] = []    # 关联的上传文件ID列表


class TaskCancel(BaseModel):
    platform_task_id: str


class TaskFileResponse(BaseModel):
    """任务中的文件响应（用于从 ORM 对象自动序列化）"""
    file_id: str
    original_name: str
    file_type: str
    mime_type: str
    size_bytes: int
    source: str
    url: str
    thumbnail_url: Optional[str] = None
    public_url: Optional[str] = None
    created_at: datetime

    @model_validator(mode='before')
    @classmethod
    def build_from_orm(cls, data: Any) -> Any:
        """从 FileRecord ORM 对象中提取字段并生成 url"""
        if hasattr(data, '__dict__') and hasattr(data, 'file_id'):
            # 是 ORM 对象
            from app.services.file_manager import file_manager
            
            def get_enum_value(v):
                return v.value if hasattr(v, 'value') else v
            
            return {
                'file_id': data.file_id,
                'original_name': data.original_name,
                'file_type': get_enum_value(data.file_type),
                'mime_type': data.mime_type,
                'size_bytes': data.size_bytes,
                'source': get_enum_value(data.source),
                'url': file_manager.get_file_url(data),
                'thumbnail_url': None,
                'public_url': data.public_url,
                'created_at': data.created_at,
            }
        return data

    model_config = ConfigDict(protected_namespaces=())


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
    input_files: List[TaskFileResponse] = []
    output_files: List[TaskFileResponse] = []
    
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)


class TaskHistoryFilter(BaseModel):
    mode: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20
