from __future__ import annotations

import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Settings
from app.services import ServiceContainer

LOGGER = logging.getLogger(__name__)


def create_scheduler(settings: Settings, services: ServiceContainer) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=UTC)

    async def heartbeat_job() -> None:
        status = await services.ping()
        LOGGER.info("scheduler heartbeat at %s (%s)", datetime.now(UTC).isoformat(), status)

    scheduler.add_job(
        heartbeat_job,
        "interval",
        seconds=settings.scheduler_interval_seconds,
        id="heartbeat",
        replace_existing=True,
    )
    return scheduler
