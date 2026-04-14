import logging

from redis import Redis

from app.config import get_settings
from app.db.session import SessionLocal
from app.services.publish_service import PublishService
from app.services.queue_service import QueueService
from app.services.scanner_service import ScannerService

logger = logging.getLogger(__name__)
settings = get_settings()


def run_scanner_job() -> None:
    db = SessionLocal()
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    queue_service = QueueService(redis_client)
    scanner_service = ScannerService(db, queue_service)

    try:
        sources = [s.strip() for s in settings.scanner_seed_sources.split(",") if s.strip()]
        created = scanner_service.scan_sources(sources)
        logger.info("scanner_job created=%s", created)
    finally:
        db.close()


def run_publish_job() -> None:
    db = SessionLocal()
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    queue_service = QueueService(redis_client)
    publisher = PublishService(db, queue_service)

    try:
        published = publisher.publish_next()
        logger.info("publish_job published=%s", published)
    finally:
        db.close()
