"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from .core.config import settings
from .core.database import init_db, close_db
from .api.v1 import router as api_v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    await init_db()
    
    # 加载模型配置缓存
    from .core.database import async_session_maker
    from .services.model_manager import model_manager
    async with async_session_maker() as db:
        try:
            await model_manager.reload(db)
            logger.info(f"Model manager loaded: {len(model_manager._api_cache)} APIs, {len(model_manager._model_cache)} models")
        except Exception as e:
            logger.warning(f"Failed to load model configs on startup: {e}")
    
    # TOS配置校验 (必选项)
    from .services.tos_uploader import tos_uploader
    if not tos_uploader._is_configured():
        logger.warning(
            "TOS configuration incomplete. "
            "Please set TOS_ENDPOINT, TOS_ACCESS_KEY, TOS_SECRET_KEY, TOS_BUCKET. "
            "TOS upload is required for model reference files."
        )
    else:
        logger.info("TOS configuration verified.")
    
    yield
    # 关闭
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS
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
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
