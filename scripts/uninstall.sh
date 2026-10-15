#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo."
  exit 1
fi

systemctl disable --now nila-virtual-computer.service 2>/dev/null || true
rm -f /etc/systemd/system/nila-virtual-computer.service
systemctl daemon-reload
rm -rf /opt/nila-virtual-computer

echo "Application files and service removed."
echo "User data was preserved at /var/lib/nila-virtual-computer and /home/nila-computer/shared."
echo "Delete those manually only if you intentionally want to remove user data."
