from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    telegram_bot_token: str
    admin_ids: set[int]
    postgres_dsn: str
    redis_url: str
    scheduler_interval_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        raw_admin_ids = os.getenv("ADMIN_IDS", "")
        admin_ids = {
            int(admin_id.strip())
            for admin_id in raw_admin_ids.split(",")
            if admin_id.strip().isdigit()
        }
        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            admin_ids=admin_ids,
            postgres_dsn=os.getenv(
                "POSTGRES_DSN", "postgresql://postgres:postgres@postgres:5432/postgres"
            ),
            redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
            scheduler_interval_seconds=int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "60")),
        )
