"""
模型管理模块
负责配置API以及模型功能，兼容火山方舟API
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.model_config import ApiConfig, ModelConfig, PlatformType, GenerationMode
from ..schemas.model_config import ModelConfigResponse, ModelSelectorInfo
from ..core.config import settings


class ModelManager:
    """模型管理器 - 单例模式"""
    
    def __init__(self):
        self._api_cache: Dict[int, ApiConfig] = {}
        self._model_cache: Dict[str, ModelConfig] = {}
    
    async def reload(self, db: AsyncSession):
        """重新加载所有配置到缓存"""
        self._api_cache.clear()
        self._model_cache.clear()
        
        # 加载API配置
        result = await db.execute(select(ApiConfig).where(ApiConfig.is_active == True))
        for api in result.scalars().all():
            self._api_cache[api.id] = api
        
        # 加载模型配置
        result = await db.execute(
            select(ModelConfig)
            .where(ModelConfig.is_active == True)
            .order_by(ModelConfig.sort_order)
        )
        for model in result.scalars().all():
            self._model_cache[model.model_id] = model
    
    def get_api_config(self, api_config_id: int) -> Optional[ApiConfig]:
        """获取API配置"""
        return self._api_cache.get(api_config_id)
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        return self._model_cache.get(model_id)
    
    def list_models_by_mode(self, mode: str) -> List[ModelConfig]:
        """按生成模式列出模型"""
        return [m for m in self._model_cache.values() if m.mode == mode and m.is_active]
    
    def list_all_models(self) -> List[ModelConfig]:
        """列出所有激活模型"""
        return list(self._model_cache.values())
    
    def get_model_concurrency(self, model_id: str) -> int:
        """获取模型并发限制"""
        model = self._model_cache.get(model_id)
        if model:
            return model.concurrency_limit
        return 1
    
    def get_api_key(self, model_id: str) -> Optional[str]:
        """获取模型对应的API Key
        
        优先从数据库缓存读取，若无效则回退到 .env 的 ARK_API_KEY
        """
        model = self._model_cache.get(model_id)
        if model and model.api_config_id in self._api_cache:
            db_key = self._api_cache[model.api_config_id].api_key
            # 排除占位符和空值
            if db_key and not db_key.startswith("请替换"):
                return db_key
        # 回退到环境变量
        return settings.ARK_API_KEY or None
    
    def get_base_url(self, model_id: str) -> str:
        """获取模型对应的Base URL"""
        model = self._model_cache.get(model_id)
        if model and model.api_config_id in self._api_cache:
            return self._api_cache[model.api_config_id].base_url
        return "https://ark.cn-beijing.volces.com/api/v3"
    
    def get_supported_input_types(self, model_id: str) -> List[str]:
        """获取模型支持的输入文件类型"""
        model = self._model_cache.get(model_id)
        if model:
            return model.supported_input_types or []
        return []


# 全局实例
model_manager = ModelManager()
