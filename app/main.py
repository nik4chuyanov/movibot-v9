import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.base import Base
from app.db.models import MediaItem
from app.db.session import engine, get_db
from app.jobs.scheduler_jobs import run_publish_job, run_scanner_job

logging.basicConfig(level=logging.INFO)
settings = get_settings()
scheduler = BackgroundScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)

    scheduler.add_job(
        run_scanner_job,
        "interval",
        seconds=settings.scanner_interval_seconds,
        id="scanner_job",
        replace_existing=True,
    )
    scheduler.add_job(
        run_publish_job,
        "interval",
        seconds=settings.publish_interval_seconds,
        id="publish_job",
        replace_existing=True,
    )
    scheduler.start()

    yield

    scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/items")
def list_items(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(MediaItem).order_by(MediaItem.id.desc()).limit(100)).all()
    return [
        {
            "id": row.id,
            "source": row.source,
            "title": row.title,
            "status": row.status,
            "created_at": row.created_at.isoformat(),
            "published_at": row.published_at.isoformat() if row.published_at else None,
        }
        for row in rows
    ]
