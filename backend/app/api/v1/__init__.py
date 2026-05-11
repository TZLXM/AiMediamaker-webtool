"""
API V1 路由聚合
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .tasks import router as tasks_router
from .files import router as files_router
from .models import router as models_router
from .admin import router as admin_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router, prefix="/auth", tags=["认证"])
router.include_router(tasks_router, prefix="/tasks", tags=["任务"])
router.include_router(files_router, prefix="/files", tags=["文件"])
router.include_router(models_router, prefix="/models", tags=["模型"])
router.include_router(admin_router, prefix="/admin", tags=["管理"])
