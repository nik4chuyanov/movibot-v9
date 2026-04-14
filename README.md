# Movibot v9

Docker Compose now starts both runtime processes:

- `api`: FastAPI backend with `/health` and APScheduler heartbeat job
- `bot`: aiogram Telegram bot in polling mode

## Run

```bash
docker compose up --build
```

## Required env vars

- `TELEGRAM_BOT_TOKEN`
- `ADMIN_IDS` (comma-separated Telegram user IDs)

## Bot commands

- `/start`
- `/help`
- `/admin_ping` (admin only)
- `/admin_jobs` (admin only)
