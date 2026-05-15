import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, delete
from app.core.database import async_session_maker
from app.models.model_config import ModelConfig, ApiConfig
from app.services.model_manager import model_manager

async def main():
    async with async_session_maker() as db:
        result = await db.execute(select(ApiConfig))
        apis = result.scalars().all()
        if not apis:
            print('No API config found! Please create one first.')
            return
        api_id = apis[0].id
        print(f'Using api_config_id={api_id}')
        
        await db.execute(delete(ModelConfig))
        await db.commit()
        print('Cleared existing model configs')
        
        models = [
            ModelConfig(
                name='Seedance 2.0',
                model_id='doubao-seedance-2-0-260128',
                api_config_id=api_id,
                mode='video',
                description='Seedance 2.0 视频生成模型',
                concurrency_limit=2,
                parameters_schema=[
                    {'key': 'ratio', 'label': '画面比例', 'type': 'select', 'required': True, 'default': '16:9',
                     'options': [{'name': '16:9 横屏', 'value': '16:9', 'label': '16:9'},
                                 {'name': '9:16 竖屏', 'value': '9:16', 'label': '9:16'},
                                 {'name': '1:1 方形', 'value': '1:1', 'label': '1:1'},
                                 {'name': '自适应', 'value': 'adaptive', 'label': '自适应'}]},
                    {'key': 'duration', 'label': '视频时长(秒)', 'type': 'number', 'required': True, 'default': 5,
                     'min': 4, 'max': 15},
                    {'key': 'resolution', 'label': '分辨率', 'type': 'select', 'required': False, 'default': '1080p',
                     'options': [{'name': '720p', 'value': '720p', 'label': '720p'},
                                 {'name': '1080p', 'value': '1080p', 'label': '1080p'},
                                 {'name': '2K', 'value': '2K', 'label': '2K'}]},
                    {'key': 'generate_audio', 'label': '生成音频', 'type': 'boolean', 'required': False, 'default': True},
                    {'key': 'watermark', 'label': '添加水印', 'type': 'boolean', 'required': False, 'default': False},
                    {'key': 'seed', 'label': '随机种子', 'type': 'number', 'required': False, 'default': None},
                ],
                supported_input_types=['image', 'video', 'audio'],
                is_active=True,
                sort_order=1,
            ),
            ModelConfig(
                name='Seedance 2.0 Fast',
                model_id='doubao-seedance-2-0-fast-260128',
                api_config_id=api_id,
                mode='video',
                description='Seedance 2.0 Fast 快速视频生成',
                concurrency_limit=3,
                parameters_schema=[
                    {'key': 'ratio', 'label': '画面比例', 'type': 'select', 'required': True, 'default': '16:9',
                     'options': [{'name': '16:9 横屏', 'value': '16:9', 'label': '16:9'},
                                 {'name': '9:16 竖屏', 'value': '9:16', 'label': '9:16'},
                                 {'name': '1:1 方形', 'value': '1:1', 'label': '1:1'},
                                 {'name': '自适应', 'value': 'adaptive', 'label': '自适应'}]},
                    {'key': 'duration', 'label': '视频时长(秒)', 'type': 'number', 'required': True, 'default': 5,
                     'min': 4, 'max': 15},
                    {'key': 'resolution', 'label': '分辨率', 'type': 'select', 'required': False, 'default': '720p',
                     'options': [{'name': '480p', 'value': '480p', 'label': '480p'},
                                 {'name': '720p', 'value': '720p', 'label': '720p'}]},
                    {'key': 'generate_audio', 'label': '生成音频', 'type': 'boolean', 'required': False, 'default': True},
                    {'key': 'watermark', 'label': '添加水印', 'type': 'boolean', 'required': False, 'default': False},
                    {'key': 'seed', 'label': '随机种子', 'type': 'number', 'required': False, 'default': None},
                ],
                supported_input_types=['image', 'video', 'audio'],
                is_active=True,
                sort_order=2,
            ),
            ModelConfig(
                name='Seedream 5.0 Lite',
                model_id='doubao-seedream-5-0-lite-260128',
                api_config_id=api_id,
                mode='image',
                description='Seedream 5.0 Lite 图片生成模型',
                concurrency_limit=2,
                parameters_schema=[
                    {'key': 'size', 'label': '图片尺寸', 'type': 'select', 'required': True, 'default': '2K',
                     'options': [{'name': '1K', 'value': '1K', 'label': '1K'},
                                 {'name': '2K', 'value': '2K', 'label': '2K'},
                                 {'name': '3K', 'value': '3K', 'label': '3K'}]},
                    {'key': 'output_format', 'label': '输出格式', 'type': 'select', 'required': False, 'default': 'png',
                     'options': [{'name': 'PNG', 'value': 'png', 'label': 'PNG'},
                                 {'name': 'JPEG', 'value': 'jpeg', 'label': 'JPEG'}]},
                    {'key': 'sequential_image_generation', 'label': '连续组图', 'type': 'select', 'required': False, 'default': 'disabled',
                     'options': [{'name': '自动', 'value': 'auto', 'label': '自动'},
                                 {'name': '禁用', 'value': 'disabled', 'label': '禁用'}]},
                    {'key': 'max_images', 'label': '最大图片数', 'type': 'number', 'required': False, 'default': 1,
                     'min': 1, 'max': 10},
                    {'key': 'watermark', 'label': '添加水印', 'type': 'boolean', 'required': False, 'default': False},
                    {'key': 'response_format', 'label': '响应格式', 'type': 'select', 'required': False, 'default': 'url',
                     'options': [{'name': 'URL', 'value': 'url', 'label': 'URL'},
                                 {'name': 'Base64', 'value': 'b64_json', 'label': 'Base64'}]},
                ],
                supported_input_types=['image'],
                is_active=True,
                sort_order=3,
            ),
            ModelConfig(
                name='Seedream 4.5',
                model_id='doubao-seedream-4-5-260128',
                api_config_id=api_id,
                mode='image',
                description='Seedream 4.5 图片生成模型',
                concurrency_limit=2,
                parameters_schema=[
                    {'key': 'size', 'label': '图片尺寸', 'type': 'select', 'required': True, 'default': '2K',
                     'options': [{'name': '1K', 'value': '1K', 'label': '1K'},
                                 {'name': '2K', 'value': '2K', 'label': '2K'},
                                 {'name': '3K', 'value': '3K', 'label': '3K'}]},
                    {'key': 'output_format', 'label': '输出格式', 'type': 'select', 'required': False, 'default': 'png',
                     'options': [{'name': 'PNG', 'value': 'png', 'label': 'PNG'},
                                 {'name': 'JPEG', 'value': 'jpeg', 'label': 'JPEG'}]},
                    {'key': 'sequential_image_generation', 'label': '连续组图', 'type': 'select', 'required': False, 'default': 'disabled',
                     'options': [{'name': '自动', 'value': 'auto', 'label': '自动'},
                                 {'name': '禁用', 'value': 'disabled', 'label': '禁用'}]},
                    {'key': 'max_images', 'label': '最大图片数', 'type': 'number', 'required': False, 'default': 1,
                     'min': 1, 'max': 10},
                    {'key': 'watermark', 'label': '添加水印', 'type': 'boolean', 'required': False, 'default': False},
                    {'key': 'response_format', 'label': '响应格式', 'type': 'select', 'required': False, 'default': 'url',
                     'options': [{'name': 'URL', 'value': 'url', 'label': 'URL'},
                                 {'name': 'Base64', 'value': 'b64_json', 'label': 'Base64'}]},
                ],
                supported_input_types=['image'],
                is_active=True,
                sort_order=4,
            ),
        ]
        
        for m in models:
            db.add(m)
        await db.commit()
        print(f'Inserted {len(models)} model configs')
        
        await model_manager.reload(db)
        print('Model manager cache reloaded')

if __name__ == '__main__':
    asyncio.run(main())
