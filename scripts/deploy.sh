#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[deploy] Created .env from .env.example"
fi

echo "[deploy] Pulling base images..."
docker compose pull --ignore-pull-failures

echo "[deploy] Building services..."
docker compose build

echo "[deploy] Starting stack..."
docker compose up -d

echo "[deploy] Service status:"
docker compose ps

echo "[deploy] Health check:"
curl -fsS http://localhost/healthz && echo

echo "[deploy] Done."
