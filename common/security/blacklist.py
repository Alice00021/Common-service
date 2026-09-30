from datetime import datetime, timezone
from typing import Optional

from common.cache import get_redis


def seconds_until(exp_timestamp: Optional[int]) -> int:
    """Сколько секунд осталось до exp (unix-время); минимум 1, чтобы ключ Redis жил."""
    if not exp_timestamp:
        return 1
    return max(1, int(exp_timestamp - datetime.now(timezone.utc).timestamp()))


class TokenBlacklist:
    """
    Чёрный список отозванных JWT в Redis (по jti).

    Запись живёт ровно до истечения самого токена, после этого токен всё равно
    невалиден, поэтому список не растёт бесконечно.
    """

    def __init__(self, prefix: str = "revoked"):
        self.prefix = prefix

    def _key(self, jti: str) -> str:
        return f"{self.prefix}:{jti}"

    async def revoke(self, jti: str, ttl_seconds: int) -> bool:
        """
        Отозвать токен. True — отозван сейчас, False — уже был отозван раньше.

        SET NX атомарен: из двух одновременных вызовов True получит только один
        (на этом держится одноразовость refresh-токенов).
        """
        client = await get_redis()
        return bool(await client.set(self._key(jti), "1", ex=max(1, ttl_seconds), nx=True))

    async def is_revoked(self, jti: str) -> bool:
        client = await get_redis()
        return await client.exists(self._key(jti)) > 0
