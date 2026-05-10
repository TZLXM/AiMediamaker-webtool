"""
用户模型
"""
from enum import Enum
from typing import TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .task import Task


class UserRole(str, Enum):
    ADMIN = "admin"
    LEADER = "leader"
    USER = "user"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(16), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Relations
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"
