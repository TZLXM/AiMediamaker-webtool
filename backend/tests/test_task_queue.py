"""
任务队列测试 - Milestone M2.3
测试任务创建、并发控制、状态轮询、取消、历史记录
"""
import pytest
import pytest_asyncio
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.task import Task, TaskMode, TaskStatus
from app.models.file import FileRecord, FileType, FileSource
from app.models.model_config import ApiConfig, ModelConfig, PlatformType, GenerationMode
from app.services.task_queue import TaskQueue, task_queue
from app.utils.security import get_password_hash


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        username=f"task_test_{uuid.uuid4().hex[:8]}",
        password_hash=get_password_hash("testpass"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_model_config(db_session: AsyncSession):
    """Create a test API config and model config."""
    api = ApiConfig(
        name="Test API",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="test_key",
        base_url="https://test.volces.com/api/v3",
        total_concurrency=2,
        is_active=True,
    )
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    model_id = f"test-video-model-{uuid.uuid4().hex[:8]}"
    model = ModelConfig(
        name="Test Video Model",
        model_id=model_id,
        api_config_id=api.id,
        mode=GenerationMode.VIDEO,
        concurrency_limit=1,
        parameters_schema=[],
        supported_input_types=["image", "video", "audio"],
        is_active=True,
        sort_order=1,
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    return model


@pytest_asyncio.fixture
async def test_input_file(db_session: AsyncSession, test_user):
    """Create a test input file record."""
    file_rec = FileRecord(
        file_id=f"file_{uuid.uuid4().hex[:12]}",
        original_name="test.png",
        storage_name="test.png",
        storage_path="/tmp/test.png",
        file_type=FileType.IMAGE,
        mime_type="image/png",
        size_bytes=1024,
        source=FileSource.UPLOAD,
        user_id=test_user.id,
    )
    db_session.add(file_rec)
    await db_session.commit()
    await db_session.refresh(file_rec)
    return file_rec


@pytest.mark.asyncio
async def test_enqueue_creates_queued_task(db_session: AsyncSession, test_user, test_model_config, test_input_file):
    """任务入队后状态应为 QUEUED"""
    queue = TaskQueue()
    
    task = await queue.enqueue(
        db=db_session,
        user_id=test_user.id,
        mode=TaskMode.VIDEO,
        model_id=test_model_config.model_id,
        prompt="A test prompt",
        parameters={"ratio": "16:9"},
        file_ids=[test_input_file.file_id],
    )
    
    assert task.status == TaskStatus.QUEUED
    assert task.platform_task_id.startswith("task_")
    assert task.user_id == test_user.id
    assert len(task.input_files) == 1
    assert task.input_files[0].file_id == test_input_file.file_id


@pytest.mark.asyncio
async def test_concurrency_slot_acquire_and_release(db_session: AsyncSession, test_user, test_model_config):
    """测试并发槽位的占用与释放"""
    queue = TaskQueue()
    model_id = test_model_config.model_id
    
    # Mock model_manager concurrency
    from app.services.model_manager import model_manager
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[model_id] = test_model_config
    
    try:
        # 占用槽位
        acquired = await queue._acquire_slot(model_id)
        assert acquired is True
        
        active = await queue.get_active_count(model_id)
        assert active == 1
        
        # 再次占用应失败（concurrency_limit=1）
        acquired2 = await queue._acquire_slot(model_id)
        assert acquired2 is False
        
        # 释放槽位
        await queue._release_slot(model_id)
        active2 = await queue.get_active_count(model_id)
        assert active2 == 0
    finally:
        model_manager._model_cache = original_cache
        await queue._release_slot(model_id)


@pytest.mark.asyncio
async def test_cancel_queued_task(db_session: AsyncSession, test_user, test_model_config):
    """取消排队中的任务"""
    queue = TaskQueue()
    
    task = await queue.enqueue(
        db=db_session,
        user_id=test_user.id,
        mode=TaskMode.VIDEO,
        model_id=test_model_config.model_id,
        prompt="Cancel me",
        parameters={},
        file_ids=[],
    )
    
    success = await queue.cancel_task(db_session, task.platform_task_id, test_user.id)
    assert success is True
    
    result = await db_session.execute(select(Task).where(Task.id == task.id))
    updated = result.scalar_one()
    assert updated.status == TaskStatus.CANCELLED
    assert updated.cancelled_at is not None


@pytest.mark.asyncio
async def test_cancel_already_finished_task(db_session: AsyncSession, test_user, test_model_config):
    """取消已结束的任务应返回 False"""
    queue = TaskQueue()
    
    task = await queue.enqueue(
        db=db_session,
        user_id=test_user.id,
        mode=TaskMode.VIDEO,
        model_id=test_model_config.model_id,
        prompt="Done",
        parameters={},
        file_ids=[],
    )
    task.status = TaskStatus.SUCCEEDED
    task.completed_at = datetime.now()
    await db_session.commit()
    
    success = await queue.cancel_task(db_session, task.platform_task_id, test_user.id)
    assert success is False


@pytest.mark.asyncio
async def test_poll_task_succeeded(db_session: AsyncSession, test_user, test_model_config):
    """轮询到任务成功完成"""
    queue = TaskQueue()
    
    task = await queue.enqueue(
        db=db_session,
        user_id=test_user.id,
        mode=TaskMode.VIDEO,
        model_id=test_model_config.model_id,
        prompt="Success",
        parameters={},
        file_ids=[],
    )
    task.status = TaskStatus.RUNNING
    task.remote_task_id = "remote_123"
    task.started_at = datetime.now()
    await db_session.commit()
    
    queue._poll_interval = 0.01  # 加速测试
    
    mock_client = MagicMock()
    mock_client.get_task_status = AsyncMock(return_value={
        "status": "succeeded",
        "content": [{"video_url": {"url": "http://example.com/video.mp4"}}],
    })
    
    with patch("app.services.file_manager.FileManager.save_model_output", new_callable=AsyncMock) as mock_save:
        await queue._poll_task(db_session, task, mock_client, "remote_123")
    
    result = await db_session.execute(select(Task).where(Task.id == task.id))
    updated = result.scalar_one()
    assert updated.status == TaskStatus.SUCCEEDED
    assert updated.completed_at is not None


@pytest.mark.asyncio
async def test_poll_task_failed(db_session: AsyncSession, test_user, test_model_config):
    """轮询到任务失败"""
    queue = TaskQueue()
    
    task = await queue.enqueue(
        db=db_session,
        user_id=test_user.id,
        mode=TaskMode.VIDEO,
        model_id=test_model_config.model_id,
        prompt="Fail",
        parameters={},
        file_ids=[],
    )
    task.status = TaskStatus.RUNNING
    task.remote_task_id = "remote_456"
    task.started_at = datetime.now()
    await db_session.commit()
    
    queue._poll_interval = 0.01  # 加速测试
    
    mock_client = MagicMock()
    mock_client.get_task_status = AsyncMock(return_value={
        "status": "failed",
        "error": {"code": "E001", "message": "Generation failed"},
    })
    
    await queue._poll_task(db_session, task, mock_client, "remote_456")
    
    result = await db_session.execute(select(Task).where(Task.id == task.id))
    updated = result.scalar_one()
    assert updated.status == TaskStatus.FAILED
    assert updated.error_code == "E001"
    assert updated.error_message == "Generation failed"


@pytest.mark.asyncio
async def test_poll_task_cancelled(db_session: AsyncSession, test_user, test_model_config):
    """轮询到任务被取消"""
    queue = TaskQueue()
    
    task = await queue.enqueue(
        db=db_session,
        user_id=test_user.id,
        mode=TaskMode.VIDEO,
        model_id=test_model_config.model_id,
        prompt="Cancelled",
        parameters={},
        file_ids=[],
    )
    task.status = TaskStatus.RUNNING
    task.remote_task_id = "remote_789"
    task.started_at = datetime.now()
    await db_session.commit()
    
    queue._poll_interval = 0.01  # 加速测试
    
    mock_client = MagicMock()
    mock_client.get_task_status = AsyncMock(return_value={"status": "cancelled"})
    
    await queue._poll_task(db_session, task, mock_client, "remote_789")
    
    result = await db_session.execute(select(Task).where(Task.id == task.id))
    updated = result.scalar_one()
    assert updated.status == TaskStatus.CANCELLED
    assert updated.cancelled_at is not None


@pytest.mark.asyncio
async def test_history_list_ascending_order(db_session: AsyncSession, test_user, test_model_config):
    """历史记录应按 created_at 升序排列（最晚生成的在最下方）"""
    from app.api.v1.tasks import list_history
    
    # 创建多个已结束任务
    for i in range(3):
        task = Task(
            platform_task_id=f"hist_task_{i}",
            user_id=test_user.id,
            mode=TaskMode.VIDEO,
            model_id=test_model_config.model_id,
            prompt=f"History {i}",
            status=TaskStatus.SUCCEEDED if i % 2 == 0 else TaskStatus.FAILED,
            completed_at=datetime.now(),
        )
        db_session.add(task)
    await db_session.commit()
    
    class MockUser:
        id = test_user.id
        role = UserRole.USER
    
    results = await list_history(db=db_session, user=MockUser())
    
    # 升序排列：最早的在前，最晚的在后
    assert len(results) == 3
    created_ats = [r.created_at for r in results]
    assert created_ats == sorted(created_ats)


@pytest.mark.asyncio
async def test_recover_queued_tasks(db_session: AsyncSession, test_user, test_model_config):
    """测试恢复 QUEUED 状态的任务"""
    queue = TaskQueue()
    
    task = await queue.enqueue(
        db=db_session,
        user_id=test_user.id,
        mode=TaskMode.VIDEO,
        model_id=test_model_config.model_id,
        prompt="Recover me",
        parameters={},
        file_ids=[],
    )
    # 确保状态是 QUEUED
    assert task.status == TaskStatus.QUEUED
    
    started = []
    
    async def mock_db_factory():
        class Ctx:
            async def __aenter__(self):
                return db_session
            async def __aexit__(self, *args):
                pass
        return Ctx()
    
    original_start = queue.start_task_processing
    
    async def capture_start(db_factory, ptid):
        started.append(ptid)
    
    queue.start_task_processing = capture_start
    try:
        await queue.recover_tasks(db_session, mock_db_factory)
        assert task.platform_task_id in started
    finally:
        queue.start_task_processing = original_start
