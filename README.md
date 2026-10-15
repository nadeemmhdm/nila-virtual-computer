# Nila Virtual Computer

Nila Virtual Computer is a lightweight, browser-accessed AI-managed Linux computer designed for low-resource hardware (target: 4 GB RAM, CPU-only). It combines a desktop-like web UI with a controlled backend, task engine, local AI runtime integration, terminal, file manager, task manager, resource monitor, and security policy layer.

> Status: Foundation release. The repository is intentionally phased so every milestone remains runnable and testable. The current build establishes the core architecture, controlled task/workspace model, filesystem safety boundary, desktop shell, installer/update/doctor scripts, and automated tests. Local llama.cpp integration, full browser automation, privileged package helper, and richer desktop apps are documented as follow-on phases in `docs/ROADMAP.md`.

## Core principles

- Browser desktop, not a generic SaaS dashboard.
- Debian Stable Minimal target; no GNOME/KDE/Cinnamon requirement.
- Structured tool execution; no arbitrary root shell from model output.
- Per-task isolated workspaces.
- Verification before marking autonomous work complete.
- On-demand heavy services for 4 GB RAM viability.
- Local-first AI runtime through llama.cpp.

## Architecture

```text
React/Vite Web Desktop
        |
        | HTTP + WebSocket
        v
FastAPI Backend
  |-- Task Engine
  |-- Workspace Manager
  |-- Controlled Filesystem
  |-- Resource Monitor
  |-- Tool Registry
  |-- Permission Engine
  |-- Audit Log
  |-- AI Runtime Adapter
  `-- SQLite
```

## Repository layout

```text
frontend/                 React/TypeScript/Vite browser desktop
backend/                  FastAPI service and core logic
  app/
    api/                   REST endpoints
    core/                  config/database/models
    security/              path and permission controls
    tasks/                 task state/workspace/verifier
    tools/                 trusted tool registry
    resources/             CPU/RAM/disk monitor
    ai/                    structured AI contracts/runtime boundary
scripts/                   install/update/uninstall/doctor
config/                    default configuration
tests/                     automated backend tests
docs/                      install/architecture/security/reports/roadmap
```

## Development quick start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Health check:

```bash
curl http://127.0.0.1:8765/api/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. By default the frontend expects the API at `http://127.0.0.1:8765`.

## Debian installation

```bash
git clone https://github.com/nadeemmhdm/nila-virtual-computer.git
cd nila-virtual-computer
sudo ./scripts/install.sh
```

See `docs/INSTALLATION.md` for the production path, systemd service behavior, storage layout, and low-memory guidance.

## Current foundation scope

Implemented in this initial build:

- FastAPI application with health, filesystem, task and resource endpoints.
- Managed filesystem roots with traversal/symlink escape protection.
- Dedicated per-task workspaces.
- Explicit task lifecycle and transition validation.
- File/command verification helpers.
- Trusted tool registry model.
- Lightweight resource monitor.
- React desktop shell with taskbar, launchable windows, movable/resizable app panels, terminal/file/task/system-monitor surfaces.
- Installer, updater, uninstaller and diagnostics scripts.
- Architecture, installation, security, troubleshooting, test and resource documentation.
- Core unit tests.

## Safety model

Ordinary autonomous work is restricted to approved roots such as:

```text
/var/lib/nila-virtual-computer/workspaces
/home/nila-computer/shared
```

Permission classes:

- `SAFE` — workspace-local reads/writes and approved non-privileged execution.
- `SENSITIVE` — network access, browser automation, approved package install.
- `HIGH_RISK` — OS/network/security configuration changes; explicit confirmation.
- `CRITICAL` — reboot/shutdown/destructive disk operations; strong confirmation.

All executable actions follow:

```text
model action -> schema validation -> permission policy -> path validation -> privilege evaluation -> execution -> observation -> verification
```

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

Interrupted tasks must be restored as interrupted/recoverable after restart rather than silently marked completed.

## Local AI direction

The design target is llama.cpp with a small Qwen-family instruct GGUF model around 0.5B–0.6B parameters using Q4-class quantization. The runtime adapter is model-file agnostic; the platform should not depend on one exact model filename.

Structured tool names include:

```text
read_file
write_file
list_directory
create_directory
move_file
delete_file
execute_command
install_tool
inspect_tool
browser_open
browser_click
browser_extract
browser_download
process_status
stop_process
inspect_resources
```

No unrestricted root execution of free-form LLM text is permitted.

## Testing

Backend:

```bash
cd backend
source .venv/bin/activate
pytest ../tests -q
```

Frontend:

```bash
cd frontend
npm run build
```

## 4 GB RAM design rules

- Debian Minimal only.
- One heavy autonomous task at a time by default.
- Chromium/Playwright only when required.
- Compact AI context; never ship full logs/pages/files into the model.
- Project-local Python and Node dependencies.
- Idle browser/AI workers should be stoppable.
- Swap is emergency capacity, not normal RAM.

See `docs/RESOURCE-USAGE.md`.

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

The project follows:

**plan -> execute -> observe -> correct -> verify -> report**

Generated code alone is never evidence of success.

## License

MIT. Third-party components, models and browser binaries retain their own licenses.
