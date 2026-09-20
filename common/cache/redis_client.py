import json
from typing import Any, Optional
import redis.asyncio as redis
from contextlib import asynccontextmanager

_redis_client: Optional[redis.Redis] = None


async def init_redis(
        url: str,
        encoding: str = "utf-8",
        decode_responses: bool = True,
) -> redis.Redis:

    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            url,
            encoding=encoding,
            decode_responses=decode_responses,
        )
    return _redis_client


async def get_redis() -> redis.Redis:
    if _redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. Call init_redis() at startup."
        )
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


class RedisCache:

    def __init__(self, prefix: str = "", default_ttl: int = 300):
        self.prefix = prefix
        self.default_ttl = default_ttl

    def _key(self, key: str) -> str:
        """Построить ключ с префиксом."""
        return f"{self.prefix}:{key}" if self.prefix else key

    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша."""
        client = await get_redis()
        data = await client.get(self._key(key))
        if data is None:
            return None
        return json.loads(data)

    async def set(
            self,
            key: str,
            value: Any,
            ttl: Optional[int] = None,
    ) -> None:
        """Сохранить значение с TTL."""
        client = await get_redis()
        await client.setex(
            self._key(key),
            ttl or self.default_ttl,
            json.dumps(value, default=str),
            )

    async def delete(self, key: str) -> None:
        """Удалить ключ."""
        client = await get_redis()
        await client.delete(self._key(key))

    async def exists(self, key: str) -> bool:
        """Проверить, существует ли ключ."""
        client = await get_redis()
        return await client.exists(self._key(key)) > 0

    async def incr(self, key: str, ttl: Optional[int] = None) -> int:
        """Атомарный инкремент (для rate limiting)."""
        client = await get_redis()
        k = self._key(key)
        count = await client.incr(k)
        if count == 1 and ttl:
            await client.expire(k, ttl)
        return count

    async def clear_prefix(self) -> int:
        """Удалить все ключи с префиксом"""
        client = await get_redis()
        pattern = f"{self.prefix}:*"
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            return await client.delete(*keys)
        return 0