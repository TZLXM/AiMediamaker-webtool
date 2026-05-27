"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from sqlalchemy import select

from .core.config import settings
from .core.database import init_db, close_db, async_session_maker
from .core.redis import redis_client
from .api.v1 import router as api_v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    await init_db()
    
    # 连接 Redis
    try:
        await redis_client.connect()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Concurrency control will fall back to memory-only.")
    
    # 加载模型配置缓存
    from .services.model_manager import model_manager
    async with async_session_maker() as db:
        try:
            await model_manager.reload(db)
            logger.info(f"Model manager loaded: {len(model_manager._api_cache)} APIs, {len(model_manager._model_cache)} models")
        except Exception as e:
            logger.warning(f"Failed to load model configs on startup: {e}")
    
    # 加载数据库中的系统配置（覆盖环境变量）
    from .models.system_config import SystemConfig
    async with async_session_maker() as db:
        try:
            result = await db.execute(select(SystemConfig).where(SystemConfig.config_key == "tos"))
            tos_db_config = result.scalar_one_or_none()
            if tos_db_config and tos_db_config.config_value:
                from .services.tos_uploader import tos_uploader
                tos_uploader.update_config_from_db(tos_db_config.config_value)
                logger.info("TOS configuration loaded from database.")
        except Exception as e:
            logger.warning(f"Failed to load TOS config from database: {e}")
    
    # TOS配置校验 (必选项)
    from .services.tos_uploader import tos_uploader
    if not tos_uploader._is_configured():
        logger.error(
            "TOS configuration incomplete. "
            "Please set TOS_ENDPOINT, TOS_ACCESS_KEY, TOS_SECRET_KEY, TOS_BUCKET "
            "or configure via admin panel. "
            "TOS upload is required for model reference files."
        )
    else:
        logger.info("TOS configuration verified.")
    
    # 恢复未完成的任务
    from .services.task_queue import task_queue
    async with async_session_maker() as db:
        try:
            await task_queue.recover_tasks(db, async_session_maker)
            logger.info("Task queue recovery completed")
        except Exception as e:
            logger.warning(f"Failed to recover tasks on startup: {e}")
    
    yield
    
    # 关闭
    logger.info("Shutting down...")
    await task_queue.shutdown()
    await redis_client.close()
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS
if settings.DEBUG:
    # DEBUG 模式：动态反射 Origin，兼容内网穿透/局域网/任意测试域名
    from starlette.responses import Response

    @app.middleware("http")
    async def dynamic_cors_middleware(request, call_next):
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            origin = request.headers.get("origin", "*")
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response

        response = await call_next(request)
        origin = request.headers.get("origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


# API路由
app.include_router(api_v1_router, prefix="/api")

# 静态文件 (前端构建产物) - 必须放在最后，避免覆盖API路由
import os
backend_dir = os.path.dirname(os.path.dirname(__file__))
project_root = os.path.dirname(backend_dir)

# 后台管理 (挂载到 /admin)
admin_dist = os.path.join(project_root, "frontend-admin", "dist")
if os.path.exists(admin_dist):
    app.mount("/admin", StaticFiles(directory=admin_dist, html=True), name="admin")
    logger.info(f"Admin frontend mounted at /admin from {admin_dist}")

# 用户前台 (挂载到根路径 /)
frontend_dist = os.path.join(project_root, "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    logger.info(f"User frontend mounted at / from {frontend_dist}")
