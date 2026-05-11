"""
模型管理模块测试 - Milestone M2.1
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_config import ApiConfig, ModelConfig, PlatformType, GenerationMode
from app.services.model_manager import ModelManager


def _unique_model_id(base: str) -> str:
    """Generate unique model id using test counter."""
    import uuid
    return f"{base}-{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_model_manager_reload(db_session: AsyncSession):
    """Test ModelManager.reload loads configs into cache."""
    # 创建API配置
    api = ApiConfig(
        name="Test API",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="test_key",
        base_url="https://test.volces.com/api/v3",
        total_concurrency=5,
        is_active=True,
    )
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    # 创建模型配置
    model = ModelConfig(
        name="Test Model",
        model_id=_unique_model_id("test-model-001"),
        api_config_id=api.id,
        mode=GenerationMode.VIDEO,
        description="A test model",
        concurrency_limit=3,
        parameters_schema=[{"key": "ratio", "type": "select"}],
        supported_input_types=["image", "video"],
        is_active=True,
        sort_order=1,
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    
    # 加载缓存 (使用新实例避免全局状态污染)
    manager = ModelManager()
    await manager.reload(db_session)
    
    assert len(manager._api_cache) >= 1
    assert len(manager._model_cache) >= 1
    assert manager.get_api_config(api.id) is not None
    assert manager.get_model_config(model.model_id) is not None


@pytest.mark.asyncio
async def test_model_manager_list_models_by_mode(db_session: AsyncSession):
    """Test list_models_by_mode filters correctly."""
    api = ApiConfig(
        name="Test API",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="test_key",
        is_active=True,
    )
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    video_model = ModelConfig(
        name="Video Model",
        model_id=_unique_model_id("video-001"),
        api_config_id=api.id,
        mode=GenerationMode.VIDEO,
        is_active=True,
        sort_order=1,
    )
    image_model = ModelConfig(
        name="Image Model",
        model_id=_unique_model_id("image-001"),
        api_config_id=api.id,
        mode=GenerationMode.IMAGE,
        is_active=True,
        sort_order=2,
    )
    db_session.add_all([video_model, image_model])
    await db_session.commit()
    
    manager = ModelManager()
    await manager.reload(db_session)
    
    video_models = manager.list_models_by_mode("video")
    image_models = manager.list_models_by_mode("image")
    
    # 确保包含我们创建的模型
    assert any(m.model_id == video_model.model_id for m in video_models)
    assert any(m.model_id == image_model.model_id for m in image_models)


@pytest.mark.asyncio
async def test_model_manager_concurrency_and_api_key(db_session: AsyncSession):
    """Test get_model_concurrency and get_api_key."""
    api = ApiConfig(
        name="Test API",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="secret_key_123",
        is_active=True,
    )
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    model = ModelConfig(
        name="Test Model",
        model_id=_unique_model_id("test-model-002"),
        api_config_id=api.id,
        mode=GenerationMode.IMAGE,
        concurrency_limit=5,
        is_active=True,
    )
    db_session.add(model)
    await db_session.commit()
    
    manager = ModelManager()
    await manager.reload(db_session)
    
    assert manager.get_model_concurrency(model.model_id) == 5
    assert manager.get_api_key(model.model_id) == "secret_key_123"
    assert manager.get_base_url(model.model_id) == "https://ark.cn-beijing.volces.com/api/v3"


@pytest.mark.asyncio
async def test_model_manager_supported_input_types(db_session: AsyncSession):
    """Test get_supported_input_types."""
    api = ApiConfig(
        name="Test API",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="test_key",
        is_active=True,
    )
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    model = ModelConfig(
        name="Multi Model",
        model_id=_unique_model_id("multi-001"),
        api_config_id=api.id,
        mode=GenerationMode.VIDEO,
        supported_input_types=["image", "video", "audio"],
        is_active=True,
    )
    db_session.add(model)
    await db_session.commit()
    
    manager = ModelManager()
    await manager.reload(db_session)
    
    types = manager.get_supported_input_types(model.model_id)
    assert types == ["image", "video", "audio"]


@pytest.mark.asyncio
async def test_model_manager_inactive_excluded(db_session: AsyncSession):
    """Test inactive configs are not loaded."""
    api = ApiConfig(
        name="Inactive API",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="test_key",
        is_active=False,
    )
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    
    model = ModelConfig(
        name="Inactive Model",
        model_id=_unique_model_id("inactive-001"),
        api_config_id=api.id,
        mode=GenerationMode.IMAGE,
        is_active=False,
    )
    db_session.add(model)
    await db_session.commit()
    
    manager = ModelManager()
    await manager.reload(db_session)
    
    assert manager.get_model_config(model.model_id) is None
    assert manager.get_api_config(api.id) is None
