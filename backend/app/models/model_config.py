"""
模型配置模型 - 管理API密钥和模型配置
"""
from enum import Enum
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin


class PlatformType(str, Enum):
    VOLCENGINE_ARK = "volcengine_ark"


class GenerationMode(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class ApiConfig(Base, TimestampMixin):
    __tablename__ = "api_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)  # 配置名称
    platform: Mapped[PlatformType] = mapped_column(String(32), default=PlatformType.VOLCENGINE_ARK)
    
    # API密钥 (加密存储)
    api_key: Mapped[str] = mapped_column(Text, nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), default="https://ark.cn-beijing.volces.com/api/v3")
    
    # 并发控制
    total_concurrency: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 额外配置
    extra_config: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    def __repr__(self) -> str:
        return f"<ApiConfig {self.name}>"


class ModelConfig(Base, TimestampMixin):
    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)  # 显示名称
    model_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)  # 模型ID
    
    # 关联API配置
    api_config_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 生成模式
    mode: Mapped[GenerationMode] = mapped_column(String(16), nullable=False)
    
    # 模型描述
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 并发限制
    concurrency_limit: Mapped[int] = mapped_column(Integer, default=2)
    
    # 支持的参数 schema (JSON Schema)
    parameters_schema: Mapped[list] = mapped_column(JSON, default=list)
    
    # 支持的文件类型
    supported_input_types: Mapped[list] = mapped_column(JSON, default=list)  # ["image", "video", "audio"]
    
    # 是否启用
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 排序权重
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<ModelConfig {self.model_id} ({self.mode})>"
