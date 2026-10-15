#!/usr/bin/env bash
set -Eeuo pipefail

REPO_URL="${NVC_REPO_URL:-https://github.com/nadeemmhdm/nila-virtual-computer.git}"
INSTALL_ROOT="${NVC_INSTALL_ROOT:-/opt/nila-virtual-computer-src}"
BRANCH="${NVC_BRANCH:-main}"

log(){ printf '\n[NVC] %s\n' "$*"; }
fail(){ printf '\n[NVC][ERROR] %s\n' "$*" >&2; exit 1; }

if [[ "${EUID}" -ne 0 ]]; then
  fail "Run this bootstrap with sudo/root. Example: curl -fsSL https://raw.githubusercontent.com/nadeemmhdm/nila-virtual-computer/main/bootstrap.sh | sudo bash"
fi

command -v apt-get >/dev/null 2>&1 || fail "This bootstrap currently supports Debian/Ubuntu-family systems with apt-get."

log "Installing bootstrap requirements"
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git ca-certificates curl rsync

if [[ -d "${INSTALL_ROOT}/.git" ]]; then
  log "Existing checkout found; updating ${BRANCH}"
  git -C "${INSTALL_ROOT}" fetch --prune origin
  git -C "${INSTALL_ROOT}" checkout "${BRANCH}"
  git -C "${INSTALL_ROOT}" reset --hard "origin/${BRANCH}"
else
  log "Cloning Nila Virtual Computer"
  rm -rf "${INSTALL_ROOT}"
  git clone --depth 1 --branch "${BRANCH}" "${REPO_URL}" "${INSTALL_ROOT}"
fi

log "Running idempotent installer"
chmod +x "${INSTALL_ROOT}/scripts/"*.sh
"${INSTALL_ROOT}/scripts/install.sh"

log "Running post-install verification"
"${INSTALL_ROOT}/scripts/test-all.sh" --installed

log "Installation and verification complete"
printf 'Repository: %s\nSource: %s\nBackend: http://127.0.0.1:8765\n' "${REPO_URL}" "${INSTALL_ROOT}"
