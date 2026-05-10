"""
模型配置路由
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.model_config import ModelConfig
from ...schemas.model_config import ModelConfigResponse, ModelSelectorInfo
from ...api.deps import get_db, get_current_user

router = APIRouter()


@router.get("/list", response_model=List[ModelSelectorInfo])
async def list_models(
    mode: str = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    """获取可用模型列表 (用于前端选择器)"""
    query = select(ModelConfig).where(ModelConfig.is_active == True)
    if mode:
        query = query.where(ModelConfig.mode == mode)
    
    query = query.order_by(ModelConfig.sort_order)
    result = await db.execute(query)
    models = result.scalars().all()
    
    return [
        ModelSelectorInfo(
            model_id=m.model_id,
            name=m.name,
            mode=m.mode,
            description=m.description,
            parameters=m.parameters_schema,
            supported_input_types=m.supported_input_types,
        )
        for m in models
    ]
