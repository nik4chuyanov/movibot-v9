from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import Settings
from app.scheduler import create_scheduler
from app.services import ServiceContainer

settings = Settings.from_env()
services = ServiceContainer(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await services.connect()
    scheduler = create_scheduler(settings, services)
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await services.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
