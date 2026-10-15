#!/usr/bin/env bash
set -euo pipefail

APP_NAME="nila-virtual-computer"
APP_USER="nila-computer"
APP_DIR="/opt/${APP_NAME}"
DATA_DIR="/var/lib/${APP_NAME}"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    echo "Run with sudo: sudo ./scripts/install.sh"
    exit 1
  fi
}

check_system() {
  if [[ ! -f /etc/debian_version ]]; then
    echo "Warning: Debian-compatible Linux is recommended."
  fi
  local mem_kb
  mem_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
  echo "Detected RAM: $((mem_kb / 1024)) MB"
  if (( mem_kb < 3400000 )); then
    echo "Warning: less than ~3.4 GB RAM detected; configure swap before running local AI."
  fi
  df -h /
  uname -m
}

install_core() {
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip nodejs npm git curl ca-certificates build-essential
}

create_user_and_dirs() {
  if ! id "${APP_USER}" >/dev/null 2>&1; then
    useradd --system --create-home --home-dir "/home/${APP_USER}" --shell /usr/sbin/nologin "${APP_USER}"
  fi
  install -d -m 0750 -o "${APP_USER}" -g "${APP_USER}" "${DATA_DIR}" "${DATA_DIR}/workspaces" "/home/${APP_USER}/shared"
  install -d -m 0755 "${APP_DIR}"
}

copy_source() {
  local root
  root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
  rsync -a --delete --exclude '.git' --exclude 'node_modules' --exclude '.venv' "${root}/" "${APP_DIR}/"
}

build_backend() {
  python3 -m venv "${APP_DIR}/backend/.venv"
  "${APP_DIR}/backend/.venv/bin/pip" install --upgrade pip
  "${APP_DIR}/backend/.venv/bin/pip" install -r "${APP_DIR}/backend/requirements.txt"
}

build_frontend() {
  cd "${APP_DIR}/frontend"
  npm install
  npm run build
}

install_service() {
  cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Nila Virtual Computer backend
After=network.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}/backend
Environment=NVC_DATA_ROOT=${DATA_DIR}
Environment=NVC_WORKSPACE_ROOT=${DATA_DIR}/workspaces
Environment=NVC_SHARED_ROOT=/home/${APP_USER}/shared
Environment=NVC_DATABASE_PATH=${DATA_DIR}/nila.db
ExecStart=${APP_DIR}/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8765
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=${DATA_DIR} /home/${APP_USER}/shared

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable --now "${APP_NAME}.service"
}

health_check() {
  sleep 1
  curl --fail --silent http://127.0.0.1:8765/api/health >/dev/null
  echo "Backend health check passed."
}

require_root
check_system
install_core
create_user_and_dirs
apt-get install -y --no-install-recommends rsync
copy_source
build_backend
build_frontend
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}" "${DATA_DIR}" "/home/${APP_USER}/shared"
install_service
health_check

echo
echo "Nila Virtual Computer foundation installed."
echo "Backend: http://127.0.0.1:8765"
echo "Frontend build: ${APP_DIR}/frontend/dist"
echo "Next production step: serve frontend through an authenticated local reverse proxy."
