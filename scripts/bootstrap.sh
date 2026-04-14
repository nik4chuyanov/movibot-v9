#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "Building and starting Movibot stack..."
docker compose up -d --build

echo "Movibot is bootstrapped."
echo "Health: curl http://localhost:${PORT:-8000}/health"
