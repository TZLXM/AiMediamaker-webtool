"""
任务模型 - 存储用户提交的任务和历史记录
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import String, Text, Integer, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .file import FileRecord


class TaskMode(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class TaskStatus(str, Enum):
    PENDING = "pending"           # 等待中
    QUEUED = "queued"             # 已入队
    RUNNING = "running"           # 运行中
    SUCCEEDED = "succeeded"       # 成功
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消
    CANCELLING = "cancelling"     # 取消中
    DOWNLOADING = "downloading"   # 下载结果中


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    platform_task_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    # 用户关联
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    
    # 任务内容
    mode: Mapped[TaskMode] = mapped_column(String(16), nullable=False)
    model_id: Mapped[str] = mapped_column(String(64), nullable=False)  # 如 doubao-seedance-2-0-260128
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 生成参数 (JSON)
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # 上游任务ID (远端API分配)
    remote_task_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # 状态
    status: Mapped[TaskStatus] = mapped_column(String(16), default=TaskStatus.PENDING, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间记录
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # 资源用量
    usage_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 关联文件
    input_files: Mapped[List["FileRecord"]] = relationship(
        "FileRecord",
        foreign_keys="FileRecord.task_id",
        back_populates="task",
        lazy="selectin"
    )
    output_files: Mapped[List["FileRecord"]] = relationship(
        "FileRecord",
        foreign_keys="FileRecord.source_task_id",
        back_populates="source_task",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Task {self.platform_task_id} {self.status}>"


