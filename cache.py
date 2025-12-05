"""
Redis cache manager
"""
import json
import redis.asyncio as redis
from typing import Optional, Any
from datetime import datetime, timedelta
import logging

from config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages Redis caching operations"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Redis connection"""
        if self._initialized:
            return
        
        try:
            self.redis_client = await redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.redis_max_connections,
            )
            
            # Test connection
            await self.redis_client.ping()
            self._initialized = True
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self._initialized = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                await self.redis_client.setex(key, ttl, serialized)
            else:
                await self.redis_client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple keys at once"""
        if not self.redis_client:
            return {}
        
        try:
            values = await self.redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
            return result
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return {}
    
    async def set_many(
        self,
        items: dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set multiple key-value pairs"""
        if not self.redis_client:
            return False
        
        try:
            pipe = self.redis_client.pipeline()
            for key, value in items.items():
                serialized = json.dumps(value, default=str)
                if ttl:
                    pipe.setex(key, ttl, serialized)
                else:
                    pipe.set(key, serialized)
            await pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    deleted += await self.redis_client.delete(*keys)
                if cursor == 0:
                    break
            return deleted
        except Exception as e:
            logger.error(f"Cache clear_pattern error: {e}")
            return 0
    
    async def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {}
        
        try:
            info = await self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human"),
                "total_keys": await self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"connected": False}


# Global cache instance
cache_manager = CacheManager()


# Cache key generators
def course_cache_key(term: str, subject: str) -> str:
    """Generate cache key for course data"""
    return f"courses:{term}:{subject}"


def professor_cache_key(professor_name: str) -> str:
    """Generate cache key for professor rating"""
    return f"professor:{professor_name.lower().replace(' ', '_')}"


def crn_cache_key(term: str, crn: str) -> str:
    """Generate cache key for specific CRN"""
    return f"crn:{term}:{crn}"
