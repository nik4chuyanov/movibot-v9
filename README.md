# MovieBot v9

MovieBot v9 is a container-first architecture for Ubuntu 24.04 deployments with **Docker** and a **Termius-friendly one-click deploy flow**.

## Architecture

The stack is split into four services:

- **gateway**: NGINX reverse proxy that exposes port `80` and routes traffic.
- **api**: FastAPI service for health checks, movie search API surface, and integration point.
- **bot-worker**: Python worker service intended for Telegram/Discord/CLI bot runtime.
- **redis**: Queue/cache backing store.

```text
Internet -> gateway (nginx:80)
              |-> api (FastAPI:8000)
              \-> bot-worker (internal only)
                     |
                     \-> redis:6379
```

## Quick Start (Ubuntu 24.04)

```bash
cp .env.example .env
./scripts/ubuntu/bootstrap.sh
./scripts/deploy.sh
```

Then verify:

```bash
curl http://localhost/healthz
```

## Termius One-Click Deploy

Use `scripts/termius-oneclick.sh` as your Termius snippet command.

Example snippet command:

```bash
bash -lc 'curl -fsSL https://raw.githubusercontent.com/<your-org>/<your-repo>/<branch>/scripts/termius-oneclick.sh | bash'
```

This script:
1. Installs Docker Engine + Compose plugin (if missing).
2. Clones or updates the repository.
3. Creates `.env` from `.env.example` when needed.
4. Builds and launches the stack.
5. Runs a basic health check.

## Repository Layout

```text
.
├── compose.yaml
├── .env.example
├── infra/
│   ├── nginx/
│   │   └── default.conf
│   └── docker/
│       ├── api.Dockerfile
│       └── worker.Dockerfile
├── services/
│   ├── api/
│   │   ├── app.py
│   │   └── requirements.txt
│   └── worker/
│       ├── worker.py
│       └── requirements.txt
└── scripts/
    ├── deploy.sh
    ├── termius-oneclick.sh
    └── ubuntu/
        └── bootstrap.sh
```

## Operations

- Start/Update: `./scripts/deploy.sh`
- Stop: `docker compose down`
- Logs: `docker compose logs -f --tail=200`
- Rebuild: `docker compose build --no-cache`

## Notes

- This is an architecture baseline intended for rapid bootstrapping.
- Add your bot platform credentials and external API keys in `.env`.
