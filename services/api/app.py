import os
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="MovieBot v9 API", version="9.0.0")


@app.get("/healthz")
def healthz() -> dict:
    return {
        "status": "ok",
        "service": "api",
        "environment": os.getenv("MOVIEBOT_ENV", "unknown"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
def root() -> dict:
    return {
        "name": "MovieBot v9",
        "message": "API gateway is online.",
        "docs": "/docs",
    }
