#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/nila-virtual-computer"
DATA_DIR="/var/lib/nila-virtual-computer"
BACKUP_DIR="${DATA_DIR}/backups/update-$(date +%Y%m%d-%H%M%S)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo."
  exit 1
fi

mkdir -p "${BACKUP_DIR}"
[[ -f "${DATA_DIR}/nila.db" ]] && cp "${DATA_DIR}/nila.db" "${BACKUP_DIR}/nila.db"
[[ -d "${APP_DIR}/config" ]] && cp -a "${APP_DIR}/config" "${BACKUP_DIR}/config"

cd "${APP_DIR}"
git fetch --all --tags
CURRENT=$(git rev-parse HEAD)
TARGET=$(git rev-parse origin/main)

if [[ "${CURRENT}" == "${TARGET}" ]]; then
  echo "Already up to date."
  exit 0
fi

git checkout --detach "${TARGET}"
"${APP_DIR}/backend/.venv/bin/pip" install -r backend/requirements.txt
cd frontend
npm install
npm run build
cd ..
systemctl restart nila-virtual-computer.service
sleep 1

if curl --fail --silent http://127.0.0.1:8765/api/health >/dev/null; then
  echo "Update successful: ${TARGET}"
else
  echo "Health check failed; rolling back code to ${CURRENT}."
  git checkout --detach "${CURRENT}"
  systemctl restart nila-virtual-computer.service
  exit 1
fi
