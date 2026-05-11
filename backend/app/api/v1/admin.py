"""
管理后台路由 - API配置和模型配置CRUD
仅限 admin 角色访问
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.model_config import ApiConfig, ModelConfig
from ...schemas.model_config import (
    ApiConfigResponse,
    ApiConfigCreate,
    ApiConfigUpdate,
    ModelConfigResponse,
    ModelConfigCreate,
    ModelConfigUpdate,
)
from ...services.model_manager import model_manager
from ...api.deps import get_db, get_current_admin

router = APIRouter()


# ============== API Config CRUD ==============

@router.post("/api-configs", response_model=ApiConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_api_config(
    data: ApiConfigCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """创建API配置 (Admin only)"""
    config = ApiConfig(
        name=data.name,
        platform=data.platform,
        api_key=data.api_key,
        base_url=data.base_url,
        total_concurrency=data.total_concurrency,
        is_active=data.is_active,
        extra_config=data.extra_config or {},
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    # 刷新缓存
    await model_manager.reload(db)
    
    return ApiConfigResponse.model_validate(config)


@router.get("/api-configs", response_model=List[ApiConfigResponse])
async def list_api_configs(
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """获取所有API配置 (Admin only)"""
    result = await db.execute(select(ApiConfig).order_by(ApiConfig.id))
    configs = result.scalars().all()
    return [ApiConfigResponse.model_validate(c) for c in configs]


@router.get("/api-configs/{config_id}", response_model=ApiConfigResponse)
async def get_api_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """获取单个API配置 (Admin only)"""
    result = await db.execute(select(ApiConfig).where(ApiConfig.id == config_id))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="API config not found")
    return ApiConfigResponse.model_validate(config)


@router.put("/api-configs/{config_id}", response_model=ApiConfigResponse)
async def update_api_config(
    config_id: int,
    data: ApiConfigUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """更新API配置 (Admin only)"""
    result = await db.execute(select(ApiConfig).where(ApiConfig.id == config_id))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="API config not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    await db.commit()
    await db.refresh(config)
    
    # 刷新缓存
    await model_manager.reload(db)
    
    return ApiConfigResponse.model_validate(config)


@router.delete("/api-configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """删除API配置 (Admin only)"""
    result = await db.execute(select(ApiConfig).where(ApiConfig.id == config_id))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="API config not found")
    
    await db.delete(config)
    await db.commit()
    
    # 刷新缓存
    await model_manager.reload(db)
    
    return None


# ============== Model Config CRUD ==============

@router.post("/model-configs", response_model=ModelConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_model_config(
    data: ModelConfigCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """创建模型配置 (Admin only)"""
    # 检查 api_config_id 是否存在
    api_result = await db.execute(select(ApiConfig).where(ApiConfig.id == data.api_config_id))
    if api_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=400, detail="API config not found")
    
    # 检查 model_id 是否已存在
    existing = await db.execute(select(ModelConfig).where(ModelConfig.model_id == data.model_id))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="Model ID already exists")
    
    model = ModelConfig(
        name=data.name,
        model_id=data.model_id,
        api_config_id=data.api_config_id,
        mode=data.mode,
        description=data.description,
        concurrency_limit=data.concurrency_limit,
        parameters_schema=[s.model_dump() for s in data.parameters_schema],
        supported_input_types=data.supported_input_types,
        is_active=data.is_active,
        sort_order=data.sort_order,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    
    # 刷新缓存
    await model_manager.reload(db)
    
    return ModelConfigResponse.model_validate(model)


@router.get("/model-configs", response_model=List[ModelConfigResponse])
async def list_model_configs(
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """获取所有模型配置 (Admin only)"""
    result = await db.execute(select(ModelConfig).order_by(ModelConfig.sort_order))
    models = result.scalars().all()
    return [ModelConfigResponse.model_validate(m) for m in models]


@router.get("/model-configs/{model_config_id}", response_model=ModelConfigResponse)
async def get_model_config(
    model_config_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """获取单个模型配置 (Admin only)"""
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == model_config_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model config not found")
    return ModelConfigResponse.model_validate(model)


@router.put("/model-configs/{model_config_id}", response_model=ModelConfigResponse)
async def update_model_config(
    model_config_id: int,
    data: ModelConfigUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """更新模型配置 (Admin only)"""
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == model_config_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model config not found")
    
    update_data = data.model_dump(exclude_unset=True)
    
    # 特殊处理 parameters_schema
    if "parameters_schema" in update_data and update_data["parameters_schema"] is not None:
        update_data["parameters_schema"] = [s.model_dump() for s in update_data["parameters_schema"]]
    
    # 如果更新 model_id，检查唯一性
    if "model_id" in update_data and update_data["model_id"] != model.model_id:
        existing = await db.execute(
            select(ModelConfig).where(ModelConfig.model_id == update_data["model_id"])
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(status_code=400, detail="Model ID already exists")
    
    for field, value in update_data.items():
        setattr(model, field, value)
    
    await db.commit()
    await db.refresh(model)
    
    # 刷新缓存
    await model_manager.reload(db)
    
    return ModelConfigResponse.model_validate(model)


@router.delete("/model-configs/{model_config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_config(
    model_config_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """删除模型配置 (Admin only)"""
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == model_config_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model config not found")
    
    await db.delete(model)
    await db.commit()
    
    # 刷新缓存
    await model_manager.reload(db)
    
    return None
