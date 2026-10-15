#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
INSTALLED=0
[[ "${1:-}" == "--installed" ]] && INSTALLED=1

pass(){ printf '[PASS] %s\n' "$1"; }
run(){ local name="$1"; shift; printf '\n== %s ==\n' "$name"; "$@"; pass "$name"; }

run "Python syntax" python3 -m compileall -q "${ROOT}/backend/app"

if [[ ! -d "${ROOT}/backend/.venv" ]]; then
  python3 -m venv "${ROOT}/backend/.venv"
  "${ROOT}/backend/.venv/bin/pip" install -q --upgrade pip
  "${ROOT}/backend/.venv/bin/pip" install -q -r "${ROOT}/backend/requirements.txt"
fi
run "Backend automated tests" "${ROOT}/backend/.venv/bin/python" -m pytest "${ROOT}/tests" -q

if [[ ! -d "${ROOT}/frontend/node_modules" ]]; then
  (cd "${ROOT}/frontend" && npm install)
fi
run "Frontend production build" bash -c "cd '${ROOT}/frontend' && npm run build"

if (( INSTALLED )); then
  run "Installed-system diagnostics" "${ROOT}/scripts/diagnostics.sh"
  run "Backend HTTP health" curl --fail --silent --show-error http://127.0.0.1:8765/api/health
  run "Systemd active" systemctl is-active --quiet nila-virtual-computer.service
fi

printf '\nAll requested verification checks passed.\n'
