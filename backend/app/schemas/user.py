"""
用户相关 Pydantic Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    role: str = "user"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
