#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/movibot"
SERVICE="${1:-}"

if [[ "$(id -u)" -ne 0 ]]; then
  SUDO='sudo'
else
  SUDO=''
fi

cd "$PROJECT_DIR"
if [[ -n "$SERVICE" ]]; then
  $SUDO docker compose logs -f --tail=200 "$SERVICE"
else
  $SUDO docker compose logs -f --tail=200
fi
