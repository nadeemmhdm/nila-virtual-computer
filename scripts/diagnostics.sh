#!/usr/bin/env bash
set -u

PASS=0
FAIL=0

check() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf '[PASS] %s\n' "$name"
    PASS=$((PASS+1))
  else
    printf '[FAIL] %s\n' "$name"
    FAIL=$((FAIL+1))
  fi
}

echo "Nila Virtual Computer doctor"
echo "============================"
check "Python" python3 --version
check "Node" node --version
check "npm" npm --version
check "Git" git --version
check "Backend health" curl --fail --silent http://127.0.0.1:8765/api/health
check "Data directory" test -d /var/lib/nila-virtual-computer
check "Workspace directory" test -d /var/lib/nila-virtual-computer/workspaces
check "Shared directory" test -d /home/nila-computer/shared
check "Systemd unit" systemctl cat nila-virtual-computer.service

echo
echo "RAM:"
free -h || true
echo
echo "Disk:"
df -h / || true
echo
echo "Results: ${PASS} passed, ${FAIL} failed"

if (( FAIL > 0 )); then
  exit 1
fi
