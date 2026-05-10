"""
种子数据初始化脚本
运行方式: python scripts/init_data.py
"""
import asyncio
import sys
from pathlib import Path

# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import async_session_maker, init_db
from app.models.user import User, UserRole
from app.models.model_config import ApiConfig, ModelConfig, PlatformType, GenerationMode
from app.utils.security import get_password_hash


async def init_users(session):
    """初始化用户账号"""
    # 检查是否已有用户
    result = await session.execute(select(User))
    if result.scalars().first():
        print("[init] 用户已存在，跳过")
        return
    
    users = [
        User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
        ),
        User(
            username="leader",
            password_hash=get_password_hash("leader123"),
            role=UserRole.LEADER,
            is_active=True,
        ),
        User(
            username="user1",
            password_hash=get_password_hash("user123"),
            role=UserRole.USER,
            is_active=True,
        ),
    ]
    
    for user in users:
        session.add(user)
    
    await session.commit()
    print("[init] 已创建默认用户: admin/admin123, leader/leader123, user1/user123")


async def init_api_configs(session):
    """初始化API配置模板"""
    result = await session.execute(select(ApiConfig))
    if result.scalars().first():
        print("[init] API配置已存在，跳过")
        return
    
    config = ApiConfig(
        name="火山方舟默认配置",
        platform=PlatformType.VOLCENGINE_ARK,
        api_key="请替换为真实的ARK_API_KEY",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        total_concurrency=5,
        is_active=True,
    )
    session.add(config)
    await session.commit()
    print("[init] 已创建API配置模板，请编辑 .env 或数据库填入真实API Key")


async def init_model_configs(session):
    """初始化模型配置"""
    result = await session.execute(select(ModelConfig))
    if result.scalars().first():
        print("[init] 模型配置已存在，跳过")
        return
    
    # 获取默认API配置ID
    result = await session.execute(select(ApiConfig))
    api_config = result.scalars().first()
    api_config_id = api_config.id if api_config else 1
    
    models = [
        # 视频模型
        ModelConfig(
            name="Seedance 2.0",
            model_id="doubao-seedance-2-0-260128",
            api_config_id=api_config_id,
            mode=GenerationMode.VIDEO,
            description="高质量视频生成模型，支持文生视频、图生视频、视频延长",
            concurrency_limit=2,
            parameters_schema=[
                {
                    "key": "ratio",
                    "label": "画面比例",
                    "type": "select",
                    "required": False,
                    "default": "16:9",
                    "options": [
                        {"name": "16:9", "value": "16:9", "label": "16:9 宽屏"},
                        {"name": "9:16", "value": "9:16", "label": "9:16 竖屏"},
                        {"name": "1:1", "value": "1:1", "label": "1:1 方形"},
                        {"name": "adaptive", "value": "adaptive", "label": "自适应"},
                    ],
                },
                {
                    "key": "duration",
                    "label": "视频时长(秒)",
                    "type": "select",
                    "required": False,
                    "default": 5,
                    "options": [
                        {"name": "5s", "value": 5, "label": "5秒"},
                        {"name": "10s", "value": 10, "label": "10秒"},
                    ],
                },
                {
                    "key": "generate_audio",
                    "label": "生成音频",
                    "type": "boolean",
                    "required": False,
                    "default": True,
                },
                {
                    "key": "watermark",
                    "label": "水印",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
            ],
            supported_input_types=["image", "video", "audio"],
            is_active=True,
            sort_order=1,
        ),
        ModelConfig(
            name="Seedance 2.0 Fast",
            model_id="doubao-seedance-2-0-fast-260128",
            api_config_id=api_config_id,
            mode=GenerationMode.VIDEO,
            description="Seedance快速版本，生成速度更快",
            concurrency_limit=3,
            parameters_schema=[
                {
                    "key": "ratio",
                    "label": "画面比例",
                    "type": "select",
                    "required": False,
                    "default": "16:9",
                    "options": [
                        {"name": "16:9", "value": "16:9", "label": "16:9 宽屏"},
                        {"name": "9:16", "value": "9:16", "label": "9:16 竖屏"},
                        {"name": "1:1", "value": "1:1", "label": "1:1 方形"},
                    ],
                },
                {
                    "key": "duration",
                    "label": "视频时长(秒)",
                    "type": "select",
                    "required": False,
                    "default": 5,
                    "options": [
                        {"name": "5s", "value": 5, "label": "5秒"},
                    ],
                },
                {
                    "key": "generate_audio",
                    "label": "生成音频",
                    "type": "boolean",
                    "required": False,
                    "default": True,
                },
            ],
            supported_input_types=["image", "video"],
            is_active=True,
            sort_order=2,
        ),
        # 图片模型
        ModelConfig(
            name="Seedream 5.0 Lite",
            model_id="doubao-seedream-5-0-lite-260128",
            api_config_id=api_config_id,
            mode=GenerationMode.IMAGE,
            description="高质量图片生成模型，支持文生图、图生图、组图生成",
            concurrency_limit=3,
            parameters_schema=[
                {
                    "key": "size",
                    "label": "分辨率",
                    "type": "select",
                    "required": False,
                    "default": "2K",
                    "options": [
                        {"name": "1K", "value": "1K", "label": "1K"},
                        {"name": "2K", "value": "2K", "label": "2K"},
                        {"name": "3K", "value": "3K", "label": "3K"},
                    ],
                },
                {
                    "key": "output_format",
                    "label": "输出格式",
                    "type": "select",
                    "required": False,
                    "default": "png",
                    "options": [
                        {"name": "png", "value": "png", "label": "PNG"},
                        {"name": "jpeg", "value": "jpeg", "label": "JPEG"},
                    ],
                },
                {
                    "key": "sequential_image_generation",
                    "label": "组图生成",
                    "type": "select",
                    "required": False,
                    "default": "disabled",
                    "options": [
                        {"name": "disabled", "value": "disabled", "label": "单张"},
                        {"name": "auto", "value": "auto", "label": "自动组图"},
                    ],
                },
                {
                    "key": "max_images",
                    "label": "最大数量",
                    "type": "number",
                    "required": False,
                    "default": 1,
                    "min": 1,
                    "max": 15,
                },
                {
                    "key": "watermark",
                    "label": "水印",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
            ],
            supported_input_types=["image"],
            is_active=True,
            sort_order=10,
        ),
        ModelConfig(
            name="Seedream 4.5",
            model_id="doubao-seedream-4-5-260128",
            api_config_id=api_config_id,
            mode=GenerationMode.IMAGE,
            description="Seedream 4.5，平衡的生成速度与质量",
            concurrency_limit=3,
            parameters_schema=[
                {
                    "key": "size",
                    "label": "分辨率",
                    "type": "select",
                    "required": False,
                    "default": "2K",
                    "options": [
                        {"name": "1K", "value": "1K", "label": "1K"},
                        {"name": "2K", "value": "2K", "label": "2K"},
                        {"name": "3K", "value": "3K", "label": "3K"},
                    ],
                },
                {
                    "key": "output_format",
                    "label": "输出格式",
                    "type": "select",
                    "required": False,
                    "default": "png",
                    "options": [
                        {"name": "png", "value": "png", "label": "PNG"},
                        {"name": "jpeg", "value": "jpeg", "label": "JPEG"},
                    ],
                },
                {
                    "key": "watermark",
                    "label": "水印",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
            ],
            supported_input_types=["image"],
            is_active=True,
            sort_order=11,
        ),
    ]
    
    for model in models:
        session.add(model)
    
    await session.commit()
    print(f"[init] 已创建 {len(models)} 个模型配置")


async def main():
    """主入口"""
    print("=" * 50)
    print("AiMediaMaker 种子数据初始化")
    print("=" * 50)
    
    # 初始化数据库表
    await init_db()
    print("[init] 数据库表已创建")
    
    async with async_session_maker() as session:
        await init_users(session)
        await init_api_configs(session)
        await init_model_configs(session)
    
    print("=" * 50)
    print("初始化完成！")
    print("默认账号: admin/admin123, leader/leader123, user1/user123")
    print("请记得修改默认密码并在 .env 中配置真实的 API Key 和 TOS 凭证")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
