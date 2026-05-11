"""
核心配置文件 - 环境变量与全局配置
"""
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AiMediaMaker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database (SQLite)
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/app.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Storage
    STORAGE_PATH: str = str(STORAGE_DIR)
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff", "image/gif"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/quicktime", "video/x-msvideo"]
    ALLOWED_AUDIO_TYPES: List[str] = ["audio/mpeg", "audio/wav", "audio/ogg", "audio/aac"]
    
    # Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    JWT_ALGORITHM: str = "HS256"
    
    # Task Queue
    TASK_POLL_INTERVAL: int = 30  # seconds
    TASK_MAX_RETRIES: int = 3
    
    # Volcengine Ark
    ARK_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    ARK_API_KEY: Optional[str] = None
    
    # TOS (Volcengine Object Storage) - 必选项
    TOS_ENDPOINT: str = "tos-cn-beijing.volces.com"
    TOS_ACCESS_KEY: str = ""
    TOS_SECRET_KEY: str = ""
    TOS_BUCKET: str = ""
    TOS_REGION: str = "cn-beijing"
    TOS_EXPIRES: int = 86400 * 7  # 预签名URL有效期7天
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
