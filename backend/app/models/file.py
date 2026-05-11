"""
文件记录模型 - 管理用户上传和模型生成的文件
"""
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .task import Task


class FileType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class FileSource(str, Enum):
    UPLOAD = "upload"           # 用户上传
    MODEL_OUTPUT = "output"     # 模型生成
    BASE64 = "base64"           # Base64转换存储


class StorageStatus(str, Enum):
    LOCAL = "local"             # 仅本地存储
    UPLOADING = "uploading"     # 上传TOS中
    UPLOADED = "uploaded"       # 已上传TOS
    FAILED = "failed"           # 上传失败


class FileRecord(Base, TimestampMixin):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    # 原始文件名
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # 存储文件名 (唯一)
    storage_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # 存储路径
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    
    # 文件元数据
    file_type: Mapped[FileType] = mapped_column(String(16), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 来源
    source: Mapped[FileSource] = mapped_column(String(16), nullable=False)
    
    # 关联任务
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    task: Mapped[Optional["Task"]] = relationship(
        "Task",
        foreign_keys=[task_id],
        back_populates="input_files"
    )
    
    # 如果是模型输出，关联源任务
    source_task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    source_task: Mapped[Optional["Task"]] = relationship(
        "Task",
        foreign_keys=[source_task_id],
        back_populates="output_files"
    )
    
    # TOS公网URL (如启用TOS)
    public_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    storage_status: Mapped[StorageStatus] = mapped_column(String(16), default=StorageStatus.LOCAL)
    
    # 上传者
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # 额外元数据 (如图片尺寸等)
    meta_info: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    def __repr__(self) -> str:
        return f"<File {self.file_id} {self.file_type}>"


