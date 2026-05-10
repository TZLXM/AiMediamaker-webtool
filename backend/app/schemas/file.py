"""
文件相关 Pydantic Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_id: str
    original_name: str
    file_type: str
    mime_type: str
    size_bytes: int
    url: str  # 前端访问URL
    thumbnail_url: Optional[str] = None
    created_at: datetime


class FileResponse(BaseModel):
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
    
    class Config:
        from_attributes = True


class FileListFilter(BaseModel):
    file_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 40
