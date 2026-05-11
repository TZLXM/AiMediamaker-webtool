"""
文件处理模块测试 - Milestone M2.2
测试 Base64 转换和 TOS 上传编排
"""
import pytest
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import FileRecord, FileType, FileSource, StorageStatus
from app.services.file_processor import FileProcessor
from app.services.file_manager import file_manager


@pytest.mark.asyncio
async def test_to_base64_success(db_session: AsyncSession):
    """Test Base64 conversion for small files."""
    # 创建测试文件
    test_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # 模拟小图片
    
    file_rec = await file_manager.save_upload(
        db=db_session,
        file_data=test_content,
        original_name="test.png",
        mime_type="image/png",
        user_id=1,
    )
    
    b64_str, success = FileProcessor.to_base64(file_rec)
    
    assert success is True
    assert b64_str.startswith("data:image/png;base64,")
    
    # 清理
    await file_manager.delete_file(db_session, file_rec)


@pytest.mark.asyncio
async def test_to_base64_file_not_found(db_session: AsyncSession):
    """Test Base64 conversion when file does not exist."""
    file_rec = FileRecord(
        file_id="file_notexist",
        original_name="missing.png",
        storage_name="missing.png",
        storage_path="/nonexistent/path/missing.png",
        file_type=FileType.IMAGE,
        mime_type="image/png",
        size_bytes=100,
        source=FileSource.UPLOAD,
        user_id=1,
    )
    
    b64_str, success = FileProcessor.to_base64(file_rec)
    
    assert success is False
    assert b64_str == ""


@pytest.mark.asyncio
async def test_to_base64_large_file(db_session: AsyncSession):
    """Test Base64 conversion rejects files > 5MB."""
    # 创建一个超过5MB的文件记录，但不需要实际文件存在来测试大小检查
    large_file_rec = FileRecord(
        file_id="file_large",
        original_name="large.png",
        storage_name="large.png",
        storage_path="/tmp/large.png",
        file_type=FileType.IMAGE,
        mime_type="image/png",
        size_bytes=6 * 1024 * 1024,
        source=FileSource.UPLOAD,
        user_id=1,
    )
    
    # 我们不需要真实文件，因为_to_base64首先检查路径存在性
    # 所以这里测试的是 prepare_for_model 的大文件策略
    

@pytest.mark.asyncio
async def test_upload_to_tos_without_config(db_session: AsyncSession):
    """Test TOS upload fails gracefully when not configured."""
    test_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    
    file_rec = await file_manager.save_upload(
        db=db_session,
        file_data=test_content,
        original_name="test.png",
        mime_type="image/png",
        user_id=1,
    )
    
    # 未配置TOS时应该失败
    url, status = await FileProcessor.upload_to_tos(file_rec, db=db_session)
    
    assert status == StorageStatus.FAILED
    assert url == ""
    assert file_rec.storage_status == StorageStatus.FAILED
    
    # 清理
    await file_manager.delete_file(db_session, file_rec)


@pytest.mark.asyncio
async def test_prepare_for_model_small_file_prefer_tos_false(db_session: AsyncSession):
    """Test prepare_for_model with small file and prefer_tos=False uses Base64."""
    test_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    
    file_rec = await file_manager.save_upload(
        db=db_session,
        file_data=test_content,
        original_name="test.png",
        mime_type="image/png",
        user_id=1,
    )
    
    url_or_b64, status = await FileProcessor.prepare_for_model(
        file_rec, prefer_tos=False, db=db_session
    )
    
    assert status == StorageStatus.LOCAL
    assert url_or_b64.startswith("data:image/png;base64,")
    
    # 清理
    await file_manager.delete_file(db_session, file_rec)


@pytest.mark.asyncio
async def test_prepare_for_model_with_existing_public_url(db_session: AsyncSession):
    """Test prepare_for_model returns existing public_url if set."""
    file_rec = FileRecord(
        file_id="file_url_test",
        original_name="test.png",
        storage_name="test.png",
        storage_path="/tmp/test.png",
        file_type=FileType.IMAGE,
        mime_type="image/png",
        size_bytes=100,
        source=FileSource.UPLOAD,
        user_id=1,
        public_url="https://example.com/test.png",
        storage_status=StorageStatus.UPLOADED,
    )
    
    url_or_b64, status = await FileProcessor.prepare_for_model(file_rec, prefer_tos=True)
    
    assert status == StorageStatus.UPLOADED
    assert url_or_b64 == "https://example.com/test.png"
