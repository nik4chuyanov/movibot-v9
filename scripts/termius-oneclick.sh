#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/example/movibot-v9.git}"
BRANCH="${BRANCH:-main}"
DEPLOY_DIR="${DEPLOY_DIR:-$HOME/movibot-v9}"

if [[ ! -d "${DEPLOY_DIR}/.git" ]]; then
  echo "[oneclick] Cloning ${REPO_URL} (${BRANCH}) to ${DEPLOY_DIR}"
  git clone --branch "${BRANCH}" --single-branch "${REPO_URL}" "${DEPLOY_DIR}"
else
  echo "[oneclick] Updating existing repository at ${DEPLOY_DIR}"
  git -C "${DEPLOY_DIR}" fetch --all --prune
  git -C "${DEPLOY_DIR}" checkout "${BRANCH}"
  git -C "${DEPLOY_DIR}" pull --ff-only origin "${BRANCH}"
fi

cd "${DEPLOY_DIR}"

./scripts/ubuntu/bootstrap.sh

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[oneclick] Created .env from template."
fi

./scripts/deploy.sh

echo "[oneclick] MovieBot v9 deployment complete."
