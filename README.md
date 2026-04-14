# Movibot v9 MVP

Lightweight Ubuntu 24.04-first MVP for scanning sources, queueing discovered media items, and publishing them in the background.

## Stack

- FastAPI app (`app/main.py`)
- PostgreSQL 16 for persistence
- Redis 7 for queueing
- APScheduler interval jobs for scanner + publisher loops
- Docker / Docker Compose deployment

## Project layout

- `app/config.py`: environment-based settings
- `app/db/models.py`: SQLAlchemy models
- `app/services/scanner_service.py`: creates items and pushes IDs to queue
- `app/services/queue_service.py`: Redis queue adapter
- `app/services/publish_service.py`: pops queue and marks items published
- `app/jobs/scheduler_jobs.py`: APScheduler job handlers
- `scripts/bootstrap.sh`: first-time setup
- `scripts/deploy.sh`: one-click redeploy
- `scripts/logs.sh`: tail service logs

## Local / VPS deployment (Termius one-click friendly)

1. Clone repo on Ubuntu 24.04 host.
2. Run bootstrap:

```bash
./scripts/bootstrap.sh
```

3. Open API:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/items
```

### Termius snippet idea

Use this command as your one-click command:

```bash
cd ~/movibot-v9 && ./scripts/deploy.sh
```

## Environment

Copy and edit `.env` values:

```bash
cp .env.example .env
```

Key env vars:

- `DATABASE_URL`
- `REDIS_URL`
- `SCANNER_INTERVAL_SECONDS`
- `PUBLISH_INTERVAL_SECONDS`
- `SCANNER_SEED_SOURCES` (comma-separated)

## Operational commands

```bash
./scripts/logs.sh app
./scripts/logs.sh db
./scripts/logs.sh redis
```

## Notes

- On startup, tables are auto-created.
- Scanner job inserts synthetic discovered records from configured sources.
- Publish job marks queued rows as `published`.
