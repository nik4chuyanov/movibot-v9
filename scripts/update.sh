#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/movibot"

if [[ "$(id -u)" -ne 0 ]]; then
  SUDO='sudo'
else
  SUDO=''
fi

cd "$PROJECT_DIR"
$SUDO git fetch --all --prune
$SUDO git pull --ff-only
$SUDO docker compose pull
$SUDO docker compose up -d
