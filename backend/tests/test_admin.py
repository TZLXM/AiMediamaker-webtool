"""
管理后台路由测试 - Milestone M2.1
测试 API配置和模型配置的 CRUD (Admin only)
"""
import pytest
import pytest_asyncio
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_config import ApiConfig, ModelConfig, PlatformType, GenerationMode
from app.models.user import User, UserRole
from app.api.v1.admin import (
    create_api_config,
    list_api_configs,
    get_api_config,
    update_api_config,
    delete_api_config,
    create_model_config,
    list_model_configs,
    get_model_config,
    update_model_config,
    delete_model_config,
)
from app.schemas.model_config import ApiConfigCreate, ApiConfigUpdate, ModelConfigCreate, ModelConfigUpdate
from app.utils.security import get_password_hash


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Create an admin user for testing."""
    user = User(
        username=f"admin_test_{uuid.uuid4().hex[:8]}",
        password_hash=get_password_hash("adminpass"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def normal_user(db_session: AsyncSession):
    """Create a normal user for testing."""
    user = User(
        username=f"normal_test_{uuid.uuid4().hex[:8]}",
        password_hash=get_password_hash("userpass"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_api_config(db_session: AsyncSession, admin_user):
    """Test admin can create API config."""
    data = ApiConfigCreate(
        name="New API",
        platform="volcengine_ark",
        api_key="new_key_123",
        base_url="https://api.test.com/v3",
        total_concurrency=10,
    )
    
    result = await create_api_config(data=data, db=db_session, admin=admin_user)
    
    assert result.name == "New API"
    assert result.platform == "volcengine_ark"
    assert result.total_concurrency == 10


@pytest.mark.asyncio
async def test_list_api_configs(db_session: AsyncSession, admin_user):
    """Test admin can list API configs."""
    api1 = ApiConfig(name="API 1", api_key="key1", is_active=True)
    api2 = ApiConfig(name="API 2", api_key="key2", is_active=True)
    db_session.add_all([api1, api2])
    await db_session.commit()
    
    results = await list_api_configs(db=db_session, admin=admin_user)
    
    assert len(results) >= 2


@pytest.mark.asyncio
async def test_get_api_config(db_session: AsyncSession, admin_user):
    """Test admin can get single API config."""
    api = ApiConfig(name="Get API", api_key="key_get", is_active=True)
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    result = await get_api_config(config_id=api.id, db=db_session, admin=admin_user)
    
    assert result.name == "Get API"


@pytest.mark.asyncio
async def test_get_api_config_not_found(db_session: AsyncSession, admin_user):
    """Test get non-existent API config returns 404."""
    with pytest.raises(HTTPException) as exc_info:
        await get_api_config(config_id=99999, db=db_session, admin=admin_user)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_api_config(db_session: AsyncSession, admin_user):
    """Test admin can update API config."""
    api = ApiConfig(name="Old Name", api_key="key_old", is_active=True)
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    data = ApiConfigUpdate(name="Updated Name", total_concurrency=20)
    result = await update_api_config(
        config_id=api.id, data=data, db=db_session, admin=admin_user
    )
    
    assert result.name == "Updated Name"
    assert result.total_concurrency == 20


@pytest.mark.asyncio
async def test_delete_api_config(db_session: AsyncSession, admin_user):
    """Test admin can delete API config."""
    api = ApiConfig(name="Delete API", api_key="key_del", is_active=True)
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    result = await delete_api_config(config_id=api.id, db=db_session, admin=admin_user)
    
    assert result is None
    # Verify deleted
    from sqlalchemy import select
    check = await db_session.execute(select(ApiConfig).where(ApiConfig.id == api.id))
    assert check.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_create_model_config(db_session: AsyncSession, admin_user):
    """Test admin can create model config."""
    api = ApiConfig(name="API for Model", api_key="key_model", is_active=True)
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    data = ModelConfigCreate(
        name="New Model",
        model_id=f"new-model-{uuid.uuid4().hex[:8]}",
        api_config_id=api.id,
        mode="video",
        concurrency_limit=3,
        supported_input_types=["image", "video"],
    )
    
    result = await create_model_config(data=data, db=db_session, admin=admin_user)
    
    assert result.name == "New Model"
    assert result.model_id == data.model_id
    assert result.mode == "video"


@pytest.mark.asyncio
async def test_create_model_config_duplicate_model_id(db_session: AsyncSession, admin_user):
    """Test creating model with duplicate model_id fails."""
    api = ApiConfig(name="API", api_key="key", is_active=True)
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    dup_id = f"dup-model-{uuid.uuid4().hex[:8]}"
    model = ModelConfig(
        name="Existing",
        model_id=dup_id,
        api_config_id=api.id,
        mode=GenerationMode.IMAGE,
        is_active=True,
    )
    db_session.add(model)
    await db_session.commit()
    
    data = ModelConfigCreate(
        name="Duplicate",
        model_id=dup_id,
        api_config_id=api.id,
        mode="image",
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await create_model_config(data=data, db=db_session, admin=admin_user)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_model_config_invalid_api_config(db_session: AsyncSession, admin_user):
    """Test creating model with non-existent api_config_id fails."""
    data = ModelConfigCreate(
        name="Orphan Model",
        model_id=f"orphan-{uuid.uuid4().hex[:8]}",
        api_config_id=99999,
        mode="image",
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await create_model_config(data=data, db=db_session, admin=admin_user)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_list_model_configs(db_session: AsyncSession, admin_user):
    """Test admin can list model configs."""
    api = ApiConfig(name="API", api_key="key", is_active=True)
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    model = ModelConfig(
        name="List Model",
        model_id=f"list-model-{uuid.uuid4().hex[:8]}",
        api_config_id=api.id,
        mode=GenerationMode.VIDEO,
        is_active=True,
    )
    db_session.add(model)
    await db_session.commit()
    
    results = await list_model_configs(db=db_session, admin=admin_user)
    
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_update_model_config(db_session: AsyncSession, admin_user):
    """Test admin can update model config."""
    api = ApiConfig(name="API", api_key="key", is_active=True)
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    model = ModelConfig(
        name="Old Model",
        model_id=f"update-model-{uuid.uuid4().hex[:8]}",
        api_config_id=api.id,
        mode=GenerationMode.IMAGE,
        concurrency_limit=2,
        is_active=True,
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    
    data = ModelConfigUpdate(name="Updated Model", concurrency_limit=10)
    result = await update_model_config(
        model_config_id=model.id, data=data, db=db_session, admin=admin_user
    )
    
    assert result.name == "Updated Model"
    assert result.concurrency_limit == 10


@pytest.mark.asyncio
async def test_delete_model_config(db_session: AsyncSession, admin_user):
    """Test admin can delete model config."""
    api = ApiConfig(name="API", api_key="key", is_active=True)
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    model = ModelConfig(
        name="Delete Model",
        model_id=f"delete-model-{uuid.uuid4().hex[:8]}",
        api_config_id=api.id,
        mode=GenerationMode.VIDEO,
        is_active=True,
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    
    result = await delete_model_config(
        model_config_id=model.id, db=db_session, admin=admin_user
    )
    
    assert result is None
    from sqlalchemy import select
    check = await db_session.execute(select(ModelConfig).where(ModelConfig.id == model.id))
    assert check.scalar_one_or_none() is None
