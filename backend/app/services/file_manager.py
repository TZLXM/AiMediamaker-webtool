"""
文件管理模块
负责管理用户上传的文件和模型输出文件
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.config import settings
from ..models.file import FileRecord, FileType, FileSource, StorageStatus


class FileManager:
    """文件管理器"""
    
    UPLOAD_DIR = Path(settings.STORAGE_PATH) / "uploads"
    OUTPUT_DIR = Path(settings.STORAGE_PATH) / "outputs"
    TEMP_DIR = Path(settings.STORAGE_PATH) / "temp"
    
    def __init__(self):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_subdir(self, file_type: FileType) -> str:
        """根据文件类型获取子目录"""
        return file_type.value
    
    def _generate_storage_name(self, original_name: str, file_type: FileType) -> str:
        """生成唯一存储文件名"""
        ext = Path(original_name).suffix.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{file_type.value}_{timestamp}_{unique_id}{ext}"
    
    def _detect_file_type(self, mime_type: str) -> FileType:
        """根据MIME类型检测文件类型"""
        if mime_type.startswith("image/"):
            return FileType.IMAGE
        elif mime_type.startswith("video/"):
            return FileType.VIDEO
        elif mime_type.startswith("audio/"):
            return FileType.AUDIO
        raise ValueError(f"Unsupported mime type: {mime_type}")
    
    async def save_upload(
        self,
        db: AsyncSession,
        file_data: bytes,
        original_name: str,
        mime_type: str,
        user_id: int
    ) -> FileRecord:
        """保存用户上传文件"""
        file_type = self._detect_file_type(mime_type)
        storage_name = self._generate_storage_name(original_name, file_type)
        
        # 按类型分子目录
        subdir = self._get_subdir(file_type)
        storage_dir = self.UPLOAD_DIR / subdir
        storage_dir.mkdir(exist_ok=True)
        
        storage_path = storage_dir / storage_name
        
        # 写入文件
        with open(storage_path, "wb") as f:
            f.write(file_data)
        
        # 创建数据库记录
        file_record = FileRecord(
            file_id=f"file_{uuid.uuid4().hex[:12]}",
            original_name=original_name,
            storage_name=storage_name,
            storage_path=str(storage_path),
            file_type=file_type,
            mime_type=mime_type,
            size_bytes=len(file_data),
            source=FileSource.UPLOAD,
            user_id=user_id,
        )
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
        
        return file_record
    
    async def save_model_output(
        self,
        db: AsyncSession,
        file_data: bytes,
        original_name: str,
        mime_type: str,
        source_task_id: int,
        user_id: int
    ) -> FileRecord:
        """保存模型输出文件"""
        file_type = self._detect_file_type(mime_type)
        storage_name = self._generate_storage_name(original_name, file_type)
        
        subdir = self._get_subdir(file_type)
        storage_dir = self.OUTPUT_DIR / subdir
        storage_dir.mkdir(exist_ok=True)
        
        storage_path = storage_dir / storage_name
        
        with open(storage_path, "wb") as f:
            f.write(file_data)
        
        file_record = FileRecord(
            file_id=f"out_{uuid.uuid4().hex[:12]}",
            original_name=original_name,
            storage_name=storage_name,
            storage_path=str(storage_path),
            file_type=file_type,
            mime_type=mime_type,
            size_bytes=len(file_data),
            source=FileSource.MODEL_OUTPUT,
            source_task_id=source_task_id,
            user_id=user_id,
        )
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
        
        return file_record
    
    async def get_file_by_id(self, db: AsyncSession, file_id: str) -> Optional[FileRecord]:
        """通过file_id获取文件记录"""
        result = await db.execute(select(FileRecord).where(FileRecord.file_id == file_id))
        return result.scalar_one_or_none()
    
    async def list_user_files(
        self,
        db: AsyncSession,
        user_id: int,
        file_type: Optional[FileType] = None
    ) -> List[FileRecord]:
        """列出用户的文件"""
        query = select(FileRecord).where(FileRecord.user_id == user_id)
        if file_type:
            query = query.where(FileRecord.file_type == file_type)
        result = await db.execute(query.order_by(FileRecord.created_at.desc()))
        return list(result.scalars().all())
    
    def get_file_path(self, file_record: FileRecord) -> Path:
        """获取文件的本地路径"""
        return Path(file_record.storage_path)
    
    def get_file_url(self, file_record: FileRecord) -> str:
        """获取文件的访问URL"""
        return f"/api/files/{file_record.file_id}"
    
    async def delete_file(self, db: AsyncSession, file_record: FileRecord):
        """删除文件"""
        path = Path(file_record.storage_path)
        if path.exists():
            path.unlink()
        await db.delete(file_record)
        await db.commit()


# 全局实例
file_manager = FileManager()
