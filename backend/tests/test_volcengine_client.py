"""
火山方舟客户端测试 - Milestone M2.4
测试 Seedance 视频生成、Seedream 图片生成、多模态输入、错误处理、资源用量
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
from app.services.volcengine_client import VolcengineClient, VolcengineAPIError
from app.utils.security import get_password_hash


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        username=f"volc_test_{uuid.uuid4().hex[:8]}",
        password_hash=get_password_hash("testpass"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_api_config(db_session: AsyncSession):
    """Create a test API config."""
    api = ApiConfig(
        name="Test Volcengine API",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="test_api_key_123",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        total_concurrency=5,
        is_active=True,
    )
    db_session.add(api)
    await db_session.commit()
    await db_session.refresh(api)
    return api


@pytest_asyncio.fixture
async def test_video_model(db_session: AsyncSession, test_api_config):
    """Create a test video model config."""
    from app.services.model_manager import model_manager
    original_api_cache = model_manager._api_cache.copy()
    
    model_id = f"doubao-seedance-2-0-{uuid.uuid4().hex[:8]}"
    model = ModelConfig(
        name="Seedance 2.0",
        model_id=model_id,
        api_config_id=test_api_config.id,
        mode=GenerationMode.VIDEO,
        concurrency_limit=2,
        parameters_schema=[],
        supported_input_types=["image", "video", "audio"],
        is_active=True,
        sort_order=1,
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    
    model_manager._api_cache[test_api_config.id] = test_api_config
    yield model
    
    model_manager._api_cache = original_api_cache


@pytest_asyncio.fixture
async def test_image_model(db_session: AsyncSession, test_api_config):
    """Create a test image model config."""
    from app.services.model_manager import model_manager
    original_api_cache = model_manager._api_cache.copy()
    
    model_id = f"doubao-seedream-5-0-{uuid.uuid4().hex[:8]}"
    model = ModelConfig(
        name="Seedream 5.0 Lite",
        model_id=model_id,
        api_config_id=test_api_config.id,
        mode=GenerationMode.IMAGE,
        concurrency_limit=2,
        parameters_schema=[],
        supported_input_types=["image"],
        is_active=True,
        sort_order=2,
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    
    model_manager._api_cache[test_api_config.id] = test_api_config
    yield model
    
    model_manager._api_cache = original_api_cache


@pytest_asyncio.fixture
async def test_input_files(db_session: AsyncSession, test_user):
    """Create test input file records."""
    image_file = FileRecord(
        file_id=f"file_{uuid.uuid4().hex[:12]}",
        original_name="ref.png",
        storage_name="ref.png",
        storage_path="/tmp/ref.png",
        file_type=FileType.IMAGE,
        mime_type="image/png",
        size_bytes=1024,
        source=FileSource.UPLOAD,
        user_id=test_user.id,
        public_url="https://example.com/ref.png",
    )
    video_file = FileRecord(
        file_id=f"file_{uuid.uuid4().hex[:12]}",
        original_name="ref.mp4",
        storage_name="ref.mp4",
        storage_path="/tmp/ref.mp4",
        file_type=FileType.VIDEO,
        mime_type="video/mp4",
        size_bytes=2048,
        source=FileSource.UPLOAD,
        user_id=test_user.id,
        public_url="https://example.com/ref.mp4",
    )
    audio_file = FileRecord(
        file_id=f"file_{uuid.uuid4().hex[:12]}",
        original_name="ref.mp3",
        storage_name="ref.mp3",
        storage_path="/tmp/ref.mp3",
        file_type=FileType.AUDIO,
        mime_type="audio/mpeg",
        size_bytes=512,
        source=FileSource.UPLOAD,
        user_id=test_user.id,
        public_url="https://example.com/ref.mp3",
    )
    db_session.add_all([image_file, video_file, audio_file])
    await db_session.commit()
    await db_session.refresh(image_file)
    await db_session.refresh(video_file)
    await db_session.refresh(audio_file)
    return {"image": image_file, "video": video_file, "audio": audio_file}


@pytest.mark.asyncio
async def test_video_task_request_format(db_session: AsyncSession, test_user, test_video_model, test_input_files):
    """测试视频生成请求的格式是否符合 Seedance API 规范"""
    from app.services.model_manager import model_manager
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[test_video_model.model_id] = test_video_model
    
    try:
        client = VolcengineClient(test_video_model.model_id)
        
        task = Task(
            platform_task_id="task_test_001",
            user_id=test_user.id,
            mode=TaskMode.VIDEO,
            model_id=test_video_model.model_id,
            prompt="A cute cat playing",
            parameters={"ratio": "16:9", "duration": 5, "generate_audio": True, "watermark": False},
        )
        task.input_files = [
            test_input_files["image"],
            test_input_files["video"],
            test_input_files["audio"],
        ]
        
        captured_payload = {}
        
        async def mock_post(*args, **kwargs):
            nonlocal captured_payload
            captured_payload = kwargs.get("json", {})
            class MockResp:
                status_code = 200
                def json(self): return {"id": "cgt-test-123"}
                def raise_for_status(self): pass
            return MockResp()
        
        with patch("httpx.AsyncClient.post", new=mock_post):
            task_id = await client._create_video_task(task, db=db_session)
        
        assert task_id == "cgt-test-123"
        
        # 验证 payload 结构
        # content 顺序：参考图片 -> 参考视频 -> 参考音频 -> 文本提示词
        content = captured_payload["content"]

        # 图片（单张，统一加 role="reference_image"）
        assert content[0]["type"] == "image_url"
        assert content[0]["image_url"]["url"] == "https://example.com/ref.png"
        assert content[0]["role"] == "reference_image"

        # 视频
        assert content[1]["type"] == "video_url"
        assert content[1]["video_url"]["url"] == "https://example.com/ref.mp4"
        assert content[1]["role"] == "reference_video"

        # 音频
        assert content[2]["type"] == "audio_url"
        assert content[2]["audio_url"]["url"] == "https://example.com/ref.mp3"
        assert content[2]["role"] == "reference_audio"

        # 文本提示词
        assert content[3]["type"] == "text"
        assert content[3]["text"] == "A cute cat playing"
        
        # 参数
        assert captured_payload["ratio"] == "16:9"
        assert captured_payload["duration"] == 5
        assert captured_payload["generate_audio"] is True
        assert captured_payload["watermark"] is False
    finally:
        model_manager._model_cache = original_cache


@pytest.mark.asyncio
async def test_video_task_multi_images_role(db_session: AsyncSession, test_user, test_video_model, test_input_files):
    """测试多图片参考视频生成时 role=reference_image"""
    from app.services.model_manager import model_manager
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[test_video_model.model_id] = test_video_model

    try:
        client = VolcengineClient(test_video_model.model_id)

        # 构造第二张图片
        from app.models.file import FileRecord, FileType, FileSource
        import uuid
        image_file2 = FileRecord(
            file_id=f"file_{uuid.uuid4().hex[:12]}",
            original_name="ref2.png",
            storage_name="ref2.png",
            storage_path="/tmp/ref2.png",
            file_type=FileType.IMAGE,
            mime_type="image/png",
            size_bytes=1024,
            source=FileSource.UPLOAD,
            user_id=test_user.id,
            public_url="https://example.com/ref2.png",
        )
        db_session.add(image_file2)
        await db_session.commit()
        await db_session.refresh(image_file2)

        task = Task(
            platform_task_id="task_test_multi_img",
            user_id=test_user.id,
            mode=TaskMode.VIDEO,
            model_id=test_video_model.model_id,
            prompt="Multi reference images test",
            parameters={"ratio": "16:9", "duration": 5},
        )
        task.input_files = [
            test_input_files["image"],
            image_file2,
        ]

        captured_payload = {}

        async def mock_post(*args, **kwargs):
            nonlocal captured_payload
            captured_payload = kwargs.get("json", {})
            class MockResp:
                status_code = 200
                def json(self): return {"id": "cgt-test-multi"}
                def raise_for_status(self): pass
            return MockResp()

        with patch("httpx.AsyncClient.post", new=mock_post):
            task_id = await client._create_video_task(task, db=db_session)

        assert task_id == "cgt-test-multi"
        content = captured_payload["content"]

        # 两张图片都应带 role=reference_image
        assert content[0]["type"] == "image_url"
        assert content[0]["role"] == "reference_image"
        assert content[1]["type"] == "image_url"
        assert content[1]["role"] == "reference_image"
        # 文本在最后
        assert content[2]["type"] == "text"
    finally:
        model_manager._model_cache = original_cache


@pytest.mark.asyncio
async def test_image_task_request_format(db_session: AsyncSession, test_user, test_image_model, test_input_files):
    """测试图片生成请求的格式是否符合 Seedream API 规范"""
    from app.services.model_manager import model_manager
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[test_image_model.model_id] = test_image_model
    
    try:
        client = VolcengineClient(test_image_model.model_id)
        
        task = Task(
            platform_task_id="task_test_002",
            user_id=test_user.id,
            mode=TaskMode.IMAGE,
            model_id=test_image_model.model_id,
            prompt="A beautiful landscape",
            parameters={"size": "2K", "output_format": "png", "watermark": False},
        )
        task.input_files = [test_input_files["image"]]
        
        captured_payload = {}
        
        async def mock_post(*args, **kwargs):
            nonlocal captured_payload
            captured_payload = kwargs.get("json", {})
            class MockResp:
                status_code = 200
                def json(self): return {"created": 1234567890, "data": [{"url": "https://example.com/img.png"}]}
                def raise_for_status(self): pass
            return MockResp()
        
        with patch("httpx.AsyncClient.post", new=mock_post):
            result = await client._create_image_task(task, db=db_session)
        
        assert result["data"][0]["url"] == "https://example.com/img.png"
        
        # 验证 payload
        assert captured_payload["model"] == test_image_model.model_id
        assert captured_payload["prompt"] == "A beautiful landscape"
        assert captured_payload["image"] == "https://example.com/ref.png"
        assert captured_payload["size"] == "2K"
        assert captured_payload["output_format"] == "png"
        assert captured_payload["watermark"] is False
    finally:
        model_manager._model_cache = original_cache


@pytest.mark.asyncio
async def test_api_error_handling(db_session: AsyncSession, test_video_model):
    """测试 API 错误被正确解析为 VolcengineAPIError"""
    from app.services.model_manager import model_manager
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[test_video_model.model_id] = test_video_model
    
    try:
        client = VolcengineClient(test_video_model.model_id)
        
        async def mock_post(*args, **kwargs):
            class MockResp:
                status_code = 400
                def json(self): return {"error": {"code": "E1001", "message": "Invalid parameter"}}
                def raise_for_status(self):
                    import httpx
                    raise httpx.HTTPStatusError(
                        "Bad Request",
                        request=MagicMock(),
                        response=self,
                    )
            return MockResp()
        
        task = Task(
            platform_task_id="task_err_001",
            user_id=1,
            mode=TaskMode.VIDEO,
            model_id=test_video_model.model_id,
            prompt="test",
        )
        
        with pytest.raises(VolcengineAPIError) as exc_info:
            with patch("httpx.AsyncClient.post", new=mock_post):
                await client._create_video_task(task, db=db_session)
        
        assert exc_info.value.code == "E1001"
        assert "Invalid parameter" in exc_info.value.message
        assert exc_info.value.status_code == 400
    finally:
        model_manager._model_cache = original_cache


@pytest.mark.asyncio
async def test_cancel_task_uses_delete(db_session: AsyncSession, test_video_model):
    """测试取消任务使用 DELETE 方法"""
    from app.services.model_manager import model_manager
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[test_video_model.model_id] = test_video_model
    
    try:
        client = VolcengineClient(test_video_model.model_id)
        
        method_used = None
        
        async def mock_delete(*args, **kwargs):
            nonlocal method_used
            method_used = "DELETE"
            class MockResp:
                status_code = 204
            return MockResp()
        
        with patch("httpx.AsyncClient.delete", new=mock_delete):
            success = await client.cancel_task("cgt-test-123")
        
        assert success is True
        assert method_used == "DELETE"
    finally:
        model_manager._model_cache = original_cache


@pytest.mark.asyncio
async def test_get_task_status_with_usage(db_session: AsyncSession, test_video_model):
    """测试获取任务状态时返回 usage 信息"""
    from app.services.model_manager import model_manager
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[test_video_model.model_id] = test_video_model
    
    try:
        client = VolcengineClient(test_video_model.model_id)
        
        async def mock_get(*args, **kwargs):
            class MockResp:
                status_code = 200
                def json(self):
                    return {
                        "id": "cgt-test-123",
                        "status": "succeeded",
                        "model": "doubao-seedance-2-0-260128",
                        "content": {"video_url": "https://example.com/video.mp4"},
                        "usage": {"completion_tokens": 123456},
                        "created_at": 1234567890,
                        "updated_at": 1234567999,
                    }
                def raise_for_status(self): pass
            return MockResp()
        
        with patch("httpx.AsyncClient.get", new=mock_get):
            result = await client.get_task_status("cgt-test-123")
        
        assert result["status"] == "succeeded"
        assert result["usage"]["completion_tokens"] == 123456
        assert result["content"]["video_url"] == "https://example.com/video.mp4"
    finally:
        model_manager._model_cache = original_cache


@pytest.mark.asyncio
async def test_image_sync_result_with_usage(db_session: AsyncSession, test_image_model):
    """测试图片同步任务返回 usage"""
    from app.services.model_manager import model_manager
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[test_image_model.model_id] = test_image_model
    
    try:
        client = VolcengineClient(test_image_model.model_id)
        client._last_image_result = {
            "created": 1234567890,
            "data": [{"url": "https://example.com/img.png"}],
            "usage": {"completion_tokens": 9999},
        }
        
        result = await client.get_task_status("img_sync_1234567890")
        
        assert result["status"] == "succeeded"
        assert result["usage"]["completion_tokens"] == 9999
        assert len(result["content"]) == 1
        assert result["content"][0]["image_url"]["url"] == "https://example.com/img.png"
    finally:
        model_manager._model_cache = original_cache


@pytest.mark.asyncio
async def test_task_queue_records_usage_tokens(db_session: AsyncSession, test_user, test_video_model):
    """测试任务队列在任务成功时记录 usage_tokens"""
    from app.services.task_queue import TaskQueue
    from app.services.model_manager import model_manager
    
    original_cache = model_manager._model_cache.copy()
    model_manager._model_cache[test_video_model.model_id] = test_video_model
    
    try:
        queue = TaskQueue()
        queue._poll_interval = 0.01
        
        task = await queue.enqueue(
            db=db_session,
            user_id=test_user.id,
            mode=TaskMode.VIDEO,
            model_id=test_video_model.model_id,
            prompt="Test usage",
            parameters={},
            file_ids=[],
        )
        task.status = TaskStatus.RUNNING
        task.remote_task_id = "cgt-usage-123"
        task.started_at = datetime.now()
        await db_session.commit()
        
        mock_client = MagicMock()
        mock_client.get_task_status = AsyncMock(return_value={
            "status": "succeeded",
            "content": [{"video_url": "https://example.com/video.mp4"}],
            "usage": {"completion_tokens": 55555},
        })
        
        with patch("app.services.file_manager.FileManager.save_model_output", new_callable=AsyncMock):
            await queue._poll_task(db_session, task, mock_client, "cgt-usage-123")
        
        result = await db_session.execute(select(Task).where(Task.id == task.id))
        updated = result.scalar_one()
        assert updated.status == TaskStatus.SUCCEEDED
        assert updated.usage_tokens == 55555
    finally:
        model_manager._model_cache = original_cache
