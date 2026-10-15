#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="nila-virtual-computer"
APP_USER="nila-computer"
APP_DIR="/opt/${APP_NAME}"
DATA_DIR="/var/lib/${APP_NAME}"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

require_root(){ [[ "${EUID}" -eq 0 ]] || { echo "Run with sudo: sudo ./scripts/install.sh"; exit 1; }; }

check_system() {
  [[ -f /etc/debian_version ]] || echo "Warning: Debian-compatible Linux is recommended."
  local mem_kb disk_kb
  mem_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
  disk_kb=$(df -Pk / | awk 'NR==2 {print $4}')
  echo "Detected RAM: $((mem_kb / 1024)) MB"
  echo "Free root disk: $((disk_kb / 1024)) MB"
  if (( mem_kb < 3400000 )); then echo "Warning: less than ~3.4 GB RAM; configure swap before local AI."; fi
  if (( disk_kb < 2097152 )); then echo "Warning: less than 2 GB free disk space."; fi
  uname -m
}

install_core() {
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip nodejs npm git curl ca-certificates build-essential rsync
}

create_user_and_dirs() {
  id "${APP_USER}" >/dev/null 2>&1 || useradd --system --create-home --home-dir "/home/${APP_USER}" --shell /usr/sbin/nologin "${APP_USER}"
  install -d -m 0750 -o "${APP_USER}" -g "${APP_USER}" "${DATA_DIR}" "${DATA_DIR}/workspaces" "/home/${APP_USER}/shared"
  install -d -m 0755 "${APP_DIR}"
}

copy_source() {
  local root
  root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
  if [[ "${root}" != "${APP_DIR}" ]]; then
    rsync -a --delete --exclude '.git' --exclude 'node_modules' --exclude '.venv' "${root}/" "${APP_DIR}/"
  fi
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
  for _ in {1..15}; do
    if curl --fail --silent http://127.0.0.1:8765/api/health >/dev/null; then echo "Backend health check passed."; return 0; fi
    sleep 1
  done
  systemctl status "${APP_NAME}.service" --no-pager || true
  return 1
}

run_tests() {
  "${APP_DIR}/backend/.venv/bin/python" -m pytest "${APP_DIR}/tests" -q
  (cd "${APP_DIR}/frontend" && npm run build)
}

require_root
check_system
install_core
create_user_and_dirs
copy_source
build_backend
build_frontend
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}" "${DATA_DIR}" "/home/${APP_USER}/shared"
install_service
health_check
run_tests

echo
echo "Nila Virtual Computer installed and verified."
echo "Backend: http://127.0.0.1:8765"
echo "Frontend build: ${APP_DIR}/frontend/dist"
echo "Run diagnostics: sudo ${APP_DIR}/scripts/diagnostics.sh"
