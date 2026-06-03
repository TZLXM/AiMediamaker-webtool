"""
文件路由 - 上传、下载、预览、删除
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.config import settings
from ...models.user import User
from ...models.file import FileRecord, FileType, FileSource
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
        file_type=record.file_type,
        mime_type=record.mime_type,
        size_bytes=record.size_bytes,
        url=file_manager.get_file_url(record),
        created_at=record.created_at,
    )


@router.get("/{file_id}")
async def serve_file(
    file_id: str,
    download: bool = False,
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
        filename=record.original_name if download else None,
    )


@router.get("/{file_id}/preview")
async def preview_file(
    file_id: str,
    width: int = Query(default=512, ge=64, le=1920),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    文件预览/缩略图 (仅限自己的文件)
    - 图片: 返回缩放后的缩略图
    - 视频: 返回原视频 (前端可自行截取首帧)
    - 音频: 返回原音频文件
    """
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
    
    # 图片文件生成缩略图
    if record.file_type == FileType.IMAGE:
        try:
            from PIL import Image
            import io
            
            img = Image.open(path)
            img.thumbnail((width, width), Image.LANCZOS)
            
            # 保持原格式
            fmt = record.mime_type.split("/")[-1].upper()
            if fmt == "JPEG":
                fmt = "JPEG"
            elif fmt == "PNG":
                fmt = "PNG"
            elif fmt == "WEBP":
                fmt = "WEBP"
            else:
                fmt = "JPEG"
            
            buf = io.BytesIO()
            img.save(buf, format=fmt)
            buf.seek(0)
            
            return StreamingResponse(
                buf,
                media_type=record.mime_type,
            )
        except Exception:
            # 缩略图生成失败则返回原文件
            pass
    
    # 视频/音频或缩略图生成失败时返回原文件
    return FileResponse(
        path=str(path),
        media_type=record.mime_type,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除文件 (仅限自己的文件)"""
    result = await db.execute(
        select(FileRecord).where(
            and_(FileRecord.file_id == file_id, FileRecord.user_id == user.id)
        )
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    
    await file_manager.delete_file(db, record)
    return None


@router.get("/assets/list", response_model=List[FileSchema])
async def list_assets(
    file_type: str = None,
    search: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    page_size: int = 40,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取用户资产列表 (模型生成的文件)"""
    from datetime import datetime, timedelta
    
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
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00').replace('+00:00', ''))
            query = query.where(FileRecord.created_at >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00').replace('+00:00', ''))
            end_dt = end_dt + timedelta(days=1)
            query = query.where(FileRecord.created_at < end_dt)
        except ValueError:
            pass
    
    query = query.order_by(desc(FileRecord.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    return [
        FileSchema(
            file_id=f.file_id,
            original_name=f.original_name,
            file_type=f.file_type,
            mime_type=f.mime_type,
            size_bytes=f.size_bytes,
            source=f.source,
            url=file_manager.get_file_url(f),
            created_at=f.created_at,
        )
        for f in files
    ]
