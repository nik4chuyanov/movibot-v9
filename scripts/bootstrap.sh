#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/movibot"
REPO_URL_DEFAULT="https://github.com/your-org/movibot-v9.git"
REPO_URL="${MOVIBOT_REPO_URL:-$REPO_URL_DEFAULT}"
BRANCH="${MOVIBOT_BRANCH:-main}"

if [[ "$(id -u)" -ne 0 ]]; then
  SUDO='sudo'
else
  SUDO=''
fi

log() {
  echo "[bootstrap] $*"
}

require_ubuntu_24_04() {
  if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    if [[ "${ID:-}" != "ubuntu" ]]; then
      log "This script targets Ubuntu. Detected: ${ID:-unknown}."
    fi
    if [[ "${VERSION_ID:-}" != "24.04" ]]; then
      log "Warning: expected Ubuntu 24.04, found ${VERSION_ID:-unknown}. Continuing."
    fi
  fi
}

install_base_packages() {
  log "Installing base packages (git, curl, ca-certificates, gnupg)..."
  $SUDO apt-get update -y
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y \
    git curl ca-certificates gnupg
}

install_docker() {
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    log "Docker Engine and Compose plugin already installed."
    return
  fi

  log "Installing Docker Engine + Docker Compose plugin..."
  $SUDO install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  $SUDO chmod a+r /etc/apt/keyrings/docker.gpg

  ARCH="$(dpkg --print-architecture)"
  UBUNTU_CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
  echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME} stable" \
    | $SUDO tee /etc/apt/sources.list.d/docker.list >/dev/null

  $SUDO apt-get update -y
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y \
    docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  $SUDO systemctl enable docker
  $SUDO systemctl start docker
}

ensure_project_layout() {
  log "Preparing project directories..."
  $SUDO mkdir -p "$PROJECT_DIR" "$PROJECT_DIR/content" "$PROJECT_DIR/data" "$PROJECT_DIR/logs"

  if [[ ! -d "$PROJECT_DIR/.git" ]]; then
    log "Cloning repository into $PROJECT_DIR..."
    $SUDO git clone --branch "$BRANCH" "$REPO_URL" "$PROJECT_DIR"
  else
    log "Repository already present at $PROJECT_DIR."
  fi

  $SUDO mkdir -p "$PROJECT_DIR/content" "$PROJECT_DIR/data" "$PROJECT_DIR/logs"

  if [[ ! -f "$PROJECT_DIR/.env" && -f "$PROJECT_DIR/.env.example" ]]; then
    log "Creating .env from .env.example..."
    $SUDO cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
  fi
}

start_stack() {
  log "Building and starting services via Docker Compose..."
  $SUDO docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d --build
}

main() {
  require_ubuntu_24_04
  install_base_packages
  install_docker
  ensure_project_layout
  start_stack
  log "Bootstrap complete."
}

main "$@"
