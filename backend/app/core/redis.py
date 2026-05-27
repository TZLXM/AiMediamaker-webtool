"""
Redis 客户端模块
用于分布式并发控制、任务状态缓存
"""
import redis.asyncio as redis
from .config import settings


class RedisClient:
    """异步 Redis 客户端"""
    
    def __init__(self):
        self._client: redis.Redis | None = None
    
    async def connect(self):
        """建立连接"""
        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
            await self._client.ping()
        except Exception:
            self._client = None
    
    async def close(self):
        """关闭连接"""
        if self._client:
            await self._client.close()
            self._client = None
    
    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return self._client
    
    def is_connected(self) -> bool:
        return self._client is not None
    
    async def ping(self) -> bool:
        """测试 Redis 连接是否可用"""
        if not self.is_connected():
            return False
        try:
            await self._client.ping()
            return True
        except Exception:
            return False
    
    # --- 并发控制 ---
    
    async def incr_model_active(self, model_id: str) -> int:
        """增加模型活跃任务计数，返回当前值。自动设置 5 分钟 TTL 防止泄漏。"""
        if not self.is_connected():
            return 0
        key = f"task:active:{model_id}"
        val = await self.client.incr(key)
        # 设置 TTL：5 分钟。即使进程崩溃未释放，计数器也会自动过期
        await self.client.expire(key, 300)
        return val
    
    async def decr_model_active(self, model_id: str) -> int:
        """减少模型活跃任务计数，返回当前值"""
        if not self.is_connected():
            return 0
        key = f"task:active:{model_id}"
        val = await self.client.decr(key)
        if val < 0:
            await self.client.set(key, 0)
            return 0
        return val
    
    async def get_model_active(self, model_id: str) -> int:
        """获取模型当前活跃任务数"""
        if not self.is_connected():
            return 0
        key = f"task:active:{model_id}"
        val = await self.client.get(key)
        return int(val) if val is not None else 0
    
    async def reset_model_active(self, model_id: str):
        """重置模型活跃任务计数"""
        if self.is_connected():
            key = f"task:active:{model_id}"
            await self.client.delete(key)
    
    async def reset_all_model_active(self):
        """重置所有模型的活跃任务计数"""
        if not self.is_connected():
            return
        keys = await self.client.keys("task:active:*")
        if keys:
            await self.client.delete(*keys)


# 全局实例
redis_client = RedisClient()
