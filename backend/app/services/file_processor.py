"""
任务文件处理模块

负责处理上传给模型的文件，提供两种处理方法：
1. Base64 转换: 将用户上传文件转为 Base64 格式（仅小文件 ≤5MB）
2. TOS 上传: 将文件上传至火山引擎对象存储 TOS，返回公网 URL

【TOS 功能定位】：TOS 仅用于将参考文件转换为公网 URL，
供火山方舟 API（Seedance/Seedream）读取。平台主存储始终在本地文件系统。
"""
import base64
import logging
from pathlib import Path
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.file import FileRecord, StorageStatus
from ..services.tos_uploader import tos_uploader

logger = logging.getLogger(__name__)


class FileProcessor:
    """文件处理器 - 提供两种文件处理方式"""
    
    # Base64 大小限制 (5MB，超过则强制使用TOS)
    BASE64_MAX_SIZE = 5 * 1024 * 1024
    
    @staticmethod
    def to_base64(file_record: FileRecord) -> Tuple[str, bool]:
        """
        将本地文件转为Base64格式
        
        Returns:
            (base64_string, success)
        """
        path = Path(file_record.storage_path)
        if not path.exists():
            return ("", False)
        
        # 超过限制不推荐用Base64
        if path.stat().st_size > FileProcessor.BASE64_MAX_SIZE:
            return ("", False)
        
        try:
            with open(path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode("utf-8")
            ext = file_record.mime_type.split("/")[-1]
            return (f"data:{file_record.mime_type};base64,{b64}", True)
        except Exception:
            return ("", False)
    
    @staticmethod
    async def upload_to_tos(
        file_record: FileRecord,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[str, StorageStatus]:
        """
        将文件上传至TOS，返回公网URL和状态
        
        Args:
            file_record: 文件记录
            db: 可选的数据库会话，如果提供则会更新并持久化 file_record 状态
        
        Returns:
            (public_url, storage_status)
        
        状态流转:
            local -> uploading -> uploaded / failed
        """
        # 如果已经上传过，直接返回
        if file_record.storage_status == StorageStatus.UPLOADED and file_record.public_url:
            return (file_record.public_url, StorageStatus.UPLOADED)
        
        # 更新状态为上传中
        file_record.storage_status = StorageStatus.UPLOADING
        if db:
            await db.commit()
        
        try:
            url, status = await tos_uploader.upload_file(file_record)
            file_record.public_url = url
            file_record.storage_status = status
            if db:
                await db.commit()
            return (url, status)
        except Exception as e:
            # 上传失败但保留本地副本
            logger.error(f"[FileProcessor] TOS upload failed for {file_record.file_id}: {e}")
            file_record.storage_status = StorageStatus.FAILED
            if db:
                await db.commit()
            return ("", StorageStatus.FAILED)
    
    @classmethod
    async def prepare_for_model(
        cls,
        file_record: FileRecord,
        prefer_tos: bool = True,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[str, StorageStatus]:
        """
        为模型调用准备文件URL
        
        策略:
        - 优先TOS上传 (返回公网URL，模型可直接访问)
        - TOS失败且文件小 -> 回退Base64
        - 文件大且TOS失败 -> 报错
        
        Args:
            file_record: 文件记录
            prefer_tos: 是否优先使用TOS
            db: 可选的数据库会话，用于持久化状态
        
        Returns:
            (url_or_base64, status)
        """
        path = Path(file_record.storage_path)
        size = path.stat().st_size if path.exists() else 0
        
        # 优先TOS
        if prefer_tos or size > cls.BASE64_MAX_SIZE:
            url, status = await cls.upload_to_tos(file_record, db=db)
            if status == StorageStatus.UPLOADED:
                return (url, status)
            
            # TOS失败但文件小，回退Base64
            if size <= cls.BASE64_MAX_SIZE:
                b64, ok = cls.to_base64(file_record)
                if ok:
                    return (b64, StorageStatus.LOCAL)
            
            # 大文件TOS失败无法回退
            raise RuntimeError(
                f"文件 {file_record.original_name} 大小超过Base64限制 ({cls.BASE64_MAX_SIZE}字节) "
                f"且TOS上传失败: {str(e)}"
            )
        
        # 小文件，先尝试Base64
        b64, ok = cls.to_base64(file_record)
        if ok:
            return (b64, StorageStatus.LOCAL)
        
        # Base64失败，回退TOS
        return await cls.upload_to_tos(file_record, db=db)


# 全局实例
file_processor = FileProcessor()
