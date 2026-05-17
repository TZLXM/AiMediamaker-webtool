"""
系统配置模型 - 存储全局键值对配置（如TOS配置）
"""
from typing import Optional
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin


class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    config_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    config_value: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<SystemConfig {self.config_key}>"
