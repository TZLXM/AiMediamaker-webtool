"""
数据库配置 - 异步SQLite
"""
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import settings
from ..models.base import Base


def _set_sqlite_pragma(dbapi_conn, connection_record):
    """启用SQLite WAL模式以提升并发性能"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    # SQLite specific: connect_args for aiosqlite
    connect_args={"check_same_thread": False},
)

# 为同步回调注册事件监听（SQLAlchemy在底层使用sqlite3时触发）
# aiosqlite 底层也基于 sqlite3，所以此事件有效
@event.listens_for(engine.sync_engine, "connect")
def _on_connect(dbapi_conn, connection_record):
    _set_sqlite_pragma(dbapi_conn, connection_record)


# 会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

AsyncSessionLocal = async_session_maker


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
