"""
Database model tests - Milestone M1.2
"""
import pytest
from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base
from app.models.user import User, UserRole
from app.models.task import Task, TaskMode, TaskStatus
from app.models.file import FileRecord, FileType, FileSource, StorageStatus
from app.models.model_config import ApiConfig, ModelConfig, PlatformType, GenerationMode
from app.utils.security import get_password_hash


@pytest.mark.asyncio
async def test_all_tables_created(engine):
    """Verify all 5 tables are created by init_db."""
    async with engine.connect() as conn:
        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(get_tables)
        assert "users" in tables
        assert "tasks" in tables
        assert "files" in tables
        assert "api_configs" in tables
        assert "model_configs" in tables


@pytest.mark.asyncio
async def test_user_crud(db_session: AsyncSession):
    """Test User model create and read."""
    user = User(
        username="testuser",
        password_hash=get_password_hash("testpass"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.role == UserRole.USER
    assert user.is_active is True

    result = await db_session.execute(select(User).where(User.username == "testuser"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.id == user.id


@pytest.mark.asyncio
async def test_task_crud(db_session: AsyncSession):
    """Test Task model create and read."""
    user = User(
        username="taskuser",
        password_hash=get_password_hash("taskpass"),
        role=UserRole.USER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    task = Task(
        platform_task_id="task_123456",
        user_id=user.id,
        mode=TaskMode.VIDEO,
        model_id="doubao-seedance-2-0-260128",
        prompt="A cute cat playing",
        parameters={"ratio": "16:9", "duration": 5},
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    assert task.id is not None
    assert task.platform_task_id == "task_123456"
    assert task.mode == TaskMode.VIDEO
    assert task.status == TaskStatus.PENDING

    result = await db_session.execute(select(Task).where(Task.platform_task_id == "task_123456"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.user_id == user.id


@pytest.mark.asyncio
async def test_file_record_crud(db_session: AsyncSession):
    """Test FileRecord model create and read."""
    file_rec = FileRecord(
        file_id="file_abc123",
        original_name="test.jpg",
        storage_name="uuid_test.jpg",
        storage_path="/storage/uploads/image/uuid_test.jpg",
        file_type=FileType.IMAGE,
        mime_type="image/jpeg",
        size_bytes=1024,
        source=FileSource.UPLOAD,
        user_id=1,
        public_url=None,
        storage_status=StorageStatus.LOCAL,
    )
    db_session.add(file_rec)
    await db_session.commit()
    await db_session.refresh(file_rec)

    assert file_rec.id is not None
    assert file_rec.file_id == "file_abc123"
    assert file_rec.storage_status == StorageStatus.LOCAL


@pytest.mark.asyncio
async def test_api_config_crud(db_session: AsyncSession):
    """Test ApiConfig model create and read."""
    config = ApiConfig(
        name="Test API",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="test_key_123",
        base_url="https://test.volces.com/api/v3",
        total_concurrency=5,
        is_active=True,
    )
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)

    assert config.id is not None
    assert config.platform == PlatformType.VOLCENGINE_ARK
    assert config.total_concurrency == 5


@pytest.mark.asyncio
async def test_model_config_crud(db_session: AsyncSession):
    """Test ModelConfig model create and read."""
    model = ModelConfig(
        name="Test Model",
        model_id="test-model-001",
        api_config_id=1,
        mode=GenerationMode.IMAGE,
        description="A test model",
        concurrency_limit=2,
        parameters_schema=[{"key": "size", "type": "select"}],
        supported_input_types=["image"],
        is_active=True,
        sort_order=1,
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)

    assert model.id is not None
    assert model.model_id == "test-model-001"
    assert model.mode == GenerationMode.IMAGE
    assert model.parameters_schema == [{"key": "size", "type": "select"}]


@pytest.mark.asyncio
async def test_user_roles():
    """Test UserRole enum values."""
    assert UserRole.ADMIN == "admin"
    assert UserRole.LEADER == "leader"
    assert UserRole.USER == "user"


@pytest.mark.asyncio
async def test_task_status_transitions():
    """Test TaskStatus enum values."""
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.RUNNING == "running"
    assert TaskStatus.SUCCEEDED == "succeeded"
    assert TaskStatus.FAILED == "failed"
    assert TaskStatus.CANCELLED == "cancelled"
