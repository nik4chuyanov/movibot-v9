#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/movibot"
BACKUP_DIR="${PROJECT_DIR}/backups"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
ARCHIVE_PATH="${BACKUP_DIR}/movibot-backup-${TIMESTAMP}.tar.gz"

if [[ "$(id -u)" -ne 0 ]]; then
  SUDO='sudo'
else
  SUDO=''
fi

$SUDO mkdir -p "$BACKUP_DIR"
$SUDO tar -czf "$ARCHIVE_PATH" -C "$PROJECT_DIR" data content logs .env

echo "Backup created: $ARCHIVE_PATH"
