"""
文件路由 - 上传、下载、预览
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.config import settings
from ...models.user import User
from ...models.file import FileRecord, FileType
from ...schemas.file import FileUploadResponse, FileResponse as FileSchema
from ...services.file_manager import file_manager
from ...api.deps import get_db, get_current_user

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """上传文件"""
    # 验证文件类型
    if file.content_type not in (
        settings.ALLOWED_IMAGE_TYPES + 
        settings.ALLOWED_VIDEO_TYPES + 
        settings.ALLOWED_AUDIO_TYPES
    ):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # 读取文件内容
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # 保存文件
    record = await file_manager.save_upload(
        db=db,
        file_data=content,
        original_name=file.filename,
        mime_type=file.content_type,
        user_id=user.id,
    )
    
    return FileUploadResponse(
        file_id=record.file_id,
        original_name=record.original_name,
        file_type=record.file_type.value,
        mime_type=record.mime_type,
        size_bytes=record.size_bytes,
        url=file_manager.get_file_url(record),
        created_at=record.created_at,
    )


@router.get("/{file_id}")
async def serve_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """提供文件访问 (仅限自己的文件)"""
    result = await db.execute(
        select(FileRecord).where(
            and_(FileRecord.file_id == file_id, FileRecord.user_id == user.id)
        )
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    
    path = file_manager.get_file_path(record)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(path),
        media_type=record.mime_type,
        filename=record.original_name,
    )


@router.get("/assets/list", response_model=List[FileSchema])
async def list_assets(
    file_type: str = None,
    search: str = None,
    page: int = 1,
    page_size: int = 40,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取用户资产列表 (模型生成的文件)"""
    from ...models.file import FileSource
    
    query = select(FileRecord).where(
        and_(
            FileRecord.user_id == user.id,
            FileRecord.source == FileSource.MODEL_OUTPUT,
        )
    )
    
    if file_type:
        query = query.where(FileRecord.file_type == file_type)
    if search:
        query = query.where(FileRecord.original_name.contains(search))
    
    query = query.order_by(desc(FileRecord.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    return [
        FileSchema(
            file_id=f.file_id,
            original_name=f.original_name,
            file_type=f.file_type.value,
            mime_type=f.mime_type,
            size_bytes=f.size_bytes,
            source=f.source.value,
            url=file_manager.get_file_url(f),
            created_at=f.created_at,
        )
        for f in files
    ]
