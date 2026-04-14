#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo ".env missing; run scripts/bootstrap.sh first"
  exit 1
fi

# Pull latest code if repo has remotes configured.
if git remote -v >/dev/null 2>&1; then
  git pull --ff-only || true
fi

docker compose down
docker compose up -d --build

echo "Deploy complete"
