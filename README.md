# Nila Virtual Computer

Nila Virtual Computer is a lightweight browser-accessed AI-managed Linux computer designed for low-resource hardware, targeting 4 GB RAM and CPU-only execution.

> **Status:** foundation release. Core architecture, controlled workspaces/filesystem, task lifecycle, resource monitoring, Web Desktop shell, installer, diagnostics and automated foundation tests are implemented. Full llama.cpp autonomy, real PTY terminal, Playwright automation and narrow privileged package-helper remain later phases and are not presented as completed features.

## One-command install

Target: Debian Stable/compatible Linux.

```bash
curl -fsSL https://raw.githubusercontent.com/nadeemmhdm/nila-virtual-computer/main/bootstrap.sh | sudo bash
```

That one command performs the complete bootstrap flow:

1. installs the minimal clone/bootstrap requirements;
2. clones or updates `nadeemmhdm/nila-virtual-computer`;
3. installs required backend/frontend build dependencies;
4. creates the restricted `nila-computer` system account and data directories;
5. builds the Python environment and React frontend;
6. installs/enables the systemd backend service;
7. performs the HTTP health check;
8. runs backend automated tests;
9. runs the production frontend build test;
10. runs installed-system diagnostics and verifies the systemd service.

The command exits non-zero when a required installation or verification step fails. It does not silently report success after a failed test.

### Manual clone alternative

```bash
git clone https://github.com/nadeemmhdm/nila-virtual-computer.git
cd nila-virtual-computer
sudo ./scripts/install.sh
```

### Re-run every test

```bash
sudo /opt/nila-virtual-computer/scripts/test-all.sh --installed
```

### Diagnostics

```bash
sudo /opt/nila-virtual-computer/scripts/diagnostics.sh
```

## Architecture

```text
React/Vite Web Desktop
        |
        | HTTP + WebSocket boundary
        v
FastAPI Backend
  |-- Task Engine
  |-- Workspace Manager
  |-- Controlled Filesystem
  |-- Resource Monitor
  |-- Tool Registry
  |-- Permission Engine
  |-- Audit boundary
  |-- AI Runtime Adapter
  `-- SQLite direction
```

## Repository layout

```text
bootstrap.sh               one-command clone/install/test entrypoint
frontend/                  React + TypeScript + Vite desktop
backend/                   FastAPI and core services
scripts/install.sh         idempotent system installation
scripts/test-all.sh        unified verification runner
scripts/diagnostics.sh     installed-system doctor
scripts/update.sh          update path
scripts/uninstall.sh       uninstall path
config/                    configuration
tests/                     automated foundation tests
docs/                      architecture/security/install/reports/roadmap
```

## Security model

Normal autonomous work is constrained to approved roots such as:

```text
/var/lib/nila-virtual-computer/workspaces
/home/nila-computer/shared
```

Permission classes are `SAFE`, `SENSITIVE`, `HIGH_RISK`, and `CRITICAL`. Model-generated actions must pass structured schema, permission, path and privilege checks before execution. The model is never intended to receive unrestricted root shell access.

## Task lifecycle

```text
QUEUED -> PLANNING -> PREPARING -> RUNNING -> VERIFYING -> COMPLETED
                     |              |            |
                     v              v            v
              WAITING_PERMISSION   PAUSED       FAILED
                                    |
                                    v
                                 CANCELLED
```

## 4 GB rules

- Debian Minimal; no heavy desktop environment.
- One heavy autonomous task at a time by default.
- Browser automation only on demand.
- Compact AI context instead of complete logs/files/pages.
- Project-local dependencies.
- Idle heavy workers should be terminable.
- Swap is emergency capacity, not normal working RAM.

## Development tests

```bash
sudo ./scripts/test-all.sh
```

The unified runner checks Python syntax, backend tests and the production frontend build. With `--installed`, it additionally checks diagnostics, HTTP health and the systemd service.

## Documentation

- `docs/INSTALLATION.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/TROUBLESHOOTING.md`
- `docs/ROADMAP.md`
- `docs/TEST-REPORT.md`
- `docs/RESOURCE-USAGE.md`
- `docs/DEVELOPMENT.md`

## Definition-of-done rule

**plan -> execute -> observe -> correct -> verify -> report**

Generated code alone is never evidence of success.

## License

MIT. Third-party components, models and browser binaries retain their respective licenses.
