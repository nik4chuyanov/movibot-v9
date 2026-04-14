from __future__ import annotations

import asyncpg
from redis.asyncio import Redis

from app.config import Settings


class ServiceContainer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pg_pool: asyncpg.Pool | None = None
        self.redis: Redis | None = None

    async def connect(self) -> None:
        self.pg_pool = await asyncpg.create_pool(self.settings.postgres_dsn, min_size=1, max_size=5)
        self.redis = Redis.from_url(self.settings.redis_url, decode_responses=True)
        await self.redis.ping()

    async def close(self) -> None:
        if self.redis is not None:
            await self.redis.aclose()
        if self.pg_pool is not None:
            await self.pg_pool.close()

    async def ping(self) -> dict[str, str]:
        if self.pg_pool is None or self.redis is None:
            return {"postgres": "disconnected", "redis": "disconnected"}

        async with self.pg_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        await self.redis.ping()
        return {"postgres": "ok", "redis": "ok"}
