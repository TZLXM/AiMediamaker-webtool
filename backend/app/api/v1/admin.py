"""
管理后台路由 - API配置和模型配置CRUD
仅限 admin 角色访问
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.model_config import ApiConfig, ModelConfig
from ...models.system_config import SystemConfig
from ...models.user import User, UserRole
from ...models.task import Task, TaskStatus
from ...schemas.model_config import (
    ApiConfigResponse,
    ApiConfigCreate,
    ApiConfigUpdate,
    ModelConfigResponse,
    ModelConfigCreate,
    ModelConfigUpdate,
    SystemConfigResponse,
    SystemConfigUpdate,
)
from ...schemas.user import UserResponse, UserCreate
from ...schemas.task import TaskResponse
from ...services.model_manager import model_manager
from ...api.deps import get_db, get_current_admin
from ...core.config import settings
from ...core.redis import redis_client

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


# ============== System Config ==============

@router.get("/system-config/{config_key}", response_model=SystemConfigResponse)
async def get_system_config(
    config_key: str,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """获取系统配置 (Admin only)"""
    result = await db.execute(select(SystemConfig).where(SystemConfig.config_key == config_key))
    config = result.scalar_one_or_none()
    if not config:
        # TOS 配置不存在时返回 .env 默认值
        if config_key == "tos":
            return SystemConfigResponse(
                config_key="tos",
                config_value={
                    "endpoint": settings.TOS_ENDPOINT,
                    "region": settings.TOS_REGION,
                    "bucket": settings.TOS_BUCKET,
                    "access_key": settings.TOS_ACCESS_KEY,
                    "secret_key": settings.TOS_SECRET_KEY,
                },
                description="TOS对象存储配置",
            )
        raise HTTPException(status_code=404, detail="Config not found")
    return SystemConfigResponse.model_validate(config)


@router.put("/system-config/{config_key}", response_model=SystemConfigResponse)
async def update_system_config(
    config_key: str,
    data: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """更新系统配置 (Admin only)"""
    result = await db.execute(select(SystemConfig).where(SystemConfig.config_key == config_key))
    config = result.scalar_one_or_none()
    if not config:
        config = SystemConfig(
            config_key=config_key,
            config_value=data.config_value,
            description=data.description,
        )
        db.add(config)
    else:
        config.config_value = data.config_value
        if data.description is not None:
            config.description = data.description
    
    await db.commit()
    await db.refresh(config)
    
    # 更新 TOS uploader 运行时配置
    if config_key == "tos":
        from ...services.tos_uploader import tos_uploader
        tos_uploader.update_config_from_db(config.config_value or {})
    
    return SystemConfigResponse.model_validate(config)


# ============== Admin User Management ==============

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """获取所有用户 (Admin only)"""
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """创建用户 (Admin only)"""
    from ...api.v1.auth import get_password_hash
    
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """更新用户状态/角色 (Admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if is_active is not None:
        user.is_active = is_active
    if role is not None:
        user.role = role
    
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


# ============== Admin Task Management ==============

@router.get("/tasks", response_model=List[dict])
async def list_tasks(
    mode: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """获取所有任务 (Admin only)"""
    query = select(Task, User.username).join(User, Task.user_id == User.id)
    
    if mode:
        query = query.where(Task.mode == mode)
    if status:
        query = query.where(Task.status == status)
    
    query = query.order_by(desc(Task.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    rows = result.all()
    
    tasks = []
    for task, username in rows:
        t = TaskResponse.model_validate(task)
        d = t.model_dump()
        d["username"] = username
        tasks.append(d)
    
    return tasks


@router.post("/tasks/{platform_task_id}/cancel")
async def admin_cancel_task(
    platform_task_id: str,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """管理员取消任意任务 (Admin only)"""
    from ...services.task_queue import task_queue
    task = await db.execute(select(Task).where(Task.platform_task_id == platform_task_id))
    task_obj = task.scalar_one_or_none()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    
    success = await task_queue.cancel_task(db, platform_task_id, task_obj.user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel task")
    return {"success": True, "message": "Task cancelled"}


# ============== Dashboard Status ==============

@router.get("/status")
async def get_system_status(
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin),
):
    """获取系统状态 Dashboard (Admin only)"""
    from ...services.tos_uploader import tos_uploader
    
    active_tasks = await db.execute(select(func.count()).select_from(Task).where(Task.status == TaskStatus.RUNNING))
    queued_tasks = await db.execute(select(func.count()).select_from(Task).where(Task.status == TaskStatus.QUEUED))
    total_users = await db.execute(select(func.count()).select_from(User))
    total_tasks = await db.execute(select(func.count()).select_from(Task))
    
    # 磁盘使用率 (%)
    import shutil
    disk = shutil.disk_usage(settings.STORAGE_PATH)
    disk_usage = round((disk.used / disk.total) * 100, 1)
    
    # Redis 连接状态
    redis_connected = False
    try:
        redis_connected = await redis_client.ping()
    except Exception:
        pass
    
    return {
        "active_tasks": active_tasks.scalar(),
        "queued_tasks": queued_tasks.scalar(),
        "total_users": total_users.scalar(),
        "total_tasks": total_tasks.scalar(),
        "disk_usage": disk_usage,
        "redis_connected": redis_connected,
        "tos_connected": tos_uploader._is_configured(),
    }


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
