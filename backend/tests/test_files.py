"""
文件路由测试 - Milestone M2.2
测试文件上传、下载、预览、删除
"""
import pytest
import pytest_asyncio
import io
import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import FileRecord, FileType, FileSource, StorageStatus
from app.models.user import User, UserRole
from app.api.v1.files import upload_file, serve_file, preview_file, delete_file, list_assets
from app.utils.security import get_password_hash
from app.services.file_manager import file_manager


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        username=f"file_test_{uuid.uuid4().hex[:8]}",
        password_hash=get_password_hash("testpass"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def _make_upload_file(filename: str, content: bytes, content_type: str) -> UploadFile:
    """Helper to create UploadFile with content_type set via headers."""
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content),
        headers={"content-type": content_type},
    )


@pytest.mark.asyncio
async def test_upload_file_success(db_session: AsyncSession, test_user):
    """Test successful file upload."""
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    file = _make_upload_file("test.png", content, "image/png")
    
    result = await upload_file(file=file, db=db_session, user=test_user)
    
    assert result.file_id is not None
    assert result.original_name == "test.png"
    assert result.file_type == "image"
    assert result.mime_type == "image/png"
    assert result.size_bytes == len(content)
    assert result.url is not None
    
    # Cleanup
    rec = await file_manager.get_file_by_id(db_session, result.file_id)
    if rec:
        await file_manager.delete_file(db_session, rec)


@pytest.mark.asyncio
async def test_upload_file_unsupported_type(db_session: AsyncSession, test_user):
    """Test upload with unsupported file type returns 400."""
    content = b"some text content"
    file = _make_upload_file("test.txt", content, "text/plain")
    
    with pytest.raises(HTTPException) as exc_info:
        await upload_file(file=file, db=db_session, user=test_user)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_upload_file_too_large(db_session: AsyncSession, test_user):
    """Test upload with file exceeding max size returns 413."""
    from app.core.config import settings
    
    # Temporarily reduce max size for testing
    original_max = settings.MAX_UPLOAD_SIZE
    settings.MAX_UPLOAD_SIZE = 100
    
    try:
        content = b"\x00" * 200
        file = _make_upload_file("large.png", content, "image/png")
        
        with pytest.raises(HTTPException) as exc_info:
            await upload_file(file=file, db=db_session, user=test_user)
        assert exc_info.value.status_code == 413
    finally:
        settings.MAX_UPLOAD_SIZE = original_max


@pytest.mark.asyncio
async def test_serve_file_success(db_session: AsyncSession, test_user):
    """Test serving own file."""
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    record = await file_manager.save_upload(
        db=db_session,
        file_data=content,
        original_name="serve_test.png",
        mime_type="image/png",
        user_id=test_user.id,
    )
    
    response = await serve_file(file_id=record.file_id, db=db_session, user=test_user)
    
    assert response.media_type == "image/png"
    
    # Cleanup
    await file_manager.delete_file(db_session, record)


@pytest.mark.asyncio
async def test_serve_file_not_found(db_session: AsyncSession, test_user):
    """Test serving non-existent file returns 404."""
    with pytest.raises(HTTPException) as exc_info:
        await serve_file(file_id="nonexistent", db=db_session, user=test_user)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_serve_file_other_users_file(db_session: AsyncSession, test_user):
    """Test serving another user's file returns 404."""
    other_user = User(
        username=f"other_{uuid.uuid4().hex[:8]}",
        password_hash=get_password_hash("pass"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    record = await file_manager.save_upload(
        db=db_session,
        file_data=content,
        original_name="private.png",
        mime_type="image/png",
        user_id=other_user.id,
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await serve_file(file_id=record.file_id, db=db_session, user=test_user)
    assert exc_info.value.status_code == 404
    
    # Cleanup
    await file_manager.delete_file(db_session, record)


@pytest.mark.asyncio
async def test_preview_file_image(db_session: AsyncSession, test_user):
    """Test preview endpoint for image returns thumbnail."""
    content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 100
    record = await file_manager.save_upload(
        db=db_session,
        file_data=content,
        original_name="preview_test.png",
        mime_type="image/png",
        user_id=test_user.id,
    )
    
    response = await preview_file(file_id=record.file_id, width=128, db=db_session, user=test_user)
    
    assert response.media_type == "image/png"
    
    # Cleanup
    await file_manager.delete_file(db_session, record)


@pytest.mark.asyncio
async def test_preview_file_not_found(db_session: AsyncSession, test_user):
    """Test preview non-existent file returns 404."""
    with pytest.raises(HTTPException) as exc_info:
        await preview_file(file_id="nonexistent", db=db_session, user=test_user)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_file_success(db_session: AsyncSession, test_user):
    """Test deleting own file."""
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    record = await file_manager.save_upload(
        db=db_session,
        file_data=content,
        original_name="delete_test.png",
        mime_type="image/png",
        user_id=test_user.id,
    )
    
    result = await delete_file(file_id=record.file_id, db=db_session, user=test_user)
    
    assert result is None
    
    # Verify deleted
    rec = await file_manager.get_file_by_id(db_session, record.file_id)
    assert rec is None


@pytest.mark.asyncio
async def test_delete_file_not_found(db_session: AsyncSession, test_user):
    """Test deleting non-existent file returns 404."""
    with pytest.raises(HTTPException) as exc_info:
        await delete_file(file_id="nonexistent", db=db_session, user=test_user)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_list_assets(db_session: AsyncSession, test_user):
    """Test listing model output assets."""
    # Create a model output file
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    record = await file_manager.save_model_output(
        db=db_session,
        file_data=content,
        original_name="output.png",
        mime_type="image/png",
        source_task_id=1,
        user_id=test_user.id,
    )
    
    results = await list_assets(db=db_session, user=test_user)
    
    assert len(results) >= 1
    assert any(r.file_id == record.file_id for r in results)
    
    # Cleanup
    await file_manager.delete_file(db_session, record)


@pytest.mark.asyncio
async def test_list_assets_pagination(db_session: AsyncSession, test_user):
    """Test asset list pagination."""
    results = await list_assets(page=1, page_size=5, db=db_session, user=test_user)
    
    assert len(results) <= 5
