"""Redis cache service using Upstash."""
import json
import redis.asyncio as redis
from typing import Optional, Any, Dict
from datetime import datetime
from app.config import settings


class CacheService:
    """Redis cache service for stock data."""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        try:
            self.client = await redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await self.client.ping()
            print("✅ Redis connected")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.client = None

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            print("👋 Redis disconnected")

    def _get_stock_key(self, code: str) -> str:
        return f"stock:{code}"

    def _get_analysis_key(self, code: str) -> str:
        return f"analysis:{code}"

    async def get_stock(self, code: str) -> Optional[Dict[str, Any]]:
        """Get cached stock data."""
        if not self.client:
            return None
        try:
            key = self._get_stock_key(code)
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"⚠️ Cache get error: {e}")
            return None

    async def set_stock(self, code: str, data: Dict[str, Any], ttl: int = 300):
        """Cache stock data with TTL (default 5 minutes)."""
        if not self.client:
            return
        try:
            key = self._get_stock_key(code)
            data['cached_at'] = datetime.utcnow().isoformat()
            await self.client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            print(f"⚠️ Cache set error: {e}")

    async def get_analysis(self, code: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result."""
        if not self.client:
            return None
        try:
            key = self._get_analysis_key(code)
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"⚠️ Cache get error: {e}")
            return None

    async def set_analysis(self, code: str, data: Dict[str, Any], ttl: int = 3600):
        """Cache analysis result with TTL (default 1 hour)."""
        if not self.client:
            return
        try:
            key = self._get_analysis_key(code)
            await self.client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            print(f"⚠️ Cache set error: {e}")

    async def delete_analysis(self, code: str):
        """Delete cached analysis (for forced refresh)."""
        if not self.client:
            return
        try:
            key = self._get_analysis_key(code)
            await self.client.delete(key)
        except Exception as e:
            print(f"⚠️ Cache delete error: {e}")

    async def ping(self) -> bool:
        """Check if Redis is connected."""
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except:
            return False


cache_service = CacheService()
