# Nila Virtual Computer

Nila Virtual Computer is a lightweight browser-accessed AI-managed virtual computer targeting **Windows 10/11 and Debian/Ubuntu Linux**, including low-resource 4 GB RAM CPU-only machines.

> **Status:** foundation release. Cross-platform storage configuration, controlled workspaces/filesystem, task lifecycle, resource monitoring, Web Desktop shell, Windows/Linux installers and automated foundation verification are implemented. Full llama.cpp autonomy, real PTY/ConPTY terminal, Playwright automation and narrow privileged package helpers remain later phases and are not presented as completed.

## Install — Linux

Debian/Ubuntu compatible Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/nadeemmhdm/nila-virtual-computer/main/bootstrap.sh | sudo bash
```

Linux uses systemd and the controlled roots `/var/lib/nila-virtual-computer` and `/home/nila-computer/shared`.

## Install — Windows 10/11

Open **PowerShell as Administrator**:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force; irm https://raw.githubusercontent.com/nadeemmhdm/nila-virtual-computer/main/install.ps1 | iex
```

Windows automatically checks/installs the required Git, Python and Node prerequisites through approved `winget` packages when missing, clones the repository, creates the Python environment, builds the Web Desktop, configures `%ProgramData%\NilaVirtualComputer`, creates an AtStartup backend task, starts it and performs verification.

## Verification

Linux:

```bash
sudo /opt/nila-virtual-computer/scripts/test-all.sh --installed
```

Windows:

```powershell
& "$env:ProgramData\NilaVirtualComputer\source\scripts\test-all.ps1"
```

Installation is fail-closed: required build/test/health failures return an error rather than being reported as success.

## Cross-platform architecture

```text
React/Vite Web Desktop
          |
          v
FastAPI + Task/AI/Security Core
          |
   Platform abstraction
     /           \
 Windows         Linux
 paths           paths
 PowerShell      shell
 winget policy   apt policy
 Task Scheduler  systemd
 ConPTY target   PTY target
```

The AI layer must not assume one OS. OS-specific actions are resolved by deterministic platform code before execution. Windows Administrator access and Linux root access are never directly handed to free-form model output.

## Storage

Linux:

```text
/var/lib/nila-virtual-computer
/var/lib/nila-virtual-computer/workspaces
/home/nila-computer/shared
```

Windows:

```text
%ProgramData%\NilaVirtualComputer
%ProgramData%\NilaVirtualComputer\workspaces
%PUBLIC%\NilaVirtualComputer\Shared
```

## Security model

Permission classes are `SAFE`, `SENSITIVE`, `HIGH_RISK`, and `CRITICAL`.

```text
model action
 -> structured schema validation
 -> OS capability resolution
 -> permission policy
 -> path validation
 -> privilege evaluation
 -> execution
 -> observation
 -> verification
```

The platform must use OS-specific approved package/tool registries instead of translating arbitrary AI text into `sudo`, Administrator PowerShell, `apt`, or `winget` commands.

## 4 GB rules

- One heavy autonomous task at a time by default.
- Browser automation only on demand.
- Compact AI context.
- Project-local dependencies.
- Idle heavy workers must be terminable.
- Linux should use a minimal server install rather than a heavy desktop environment.
- Windows background components should remain on-demand where practical.

## Repository

```text
bootstrap.sh               Linux one-command bootstrap
install.ps1                Windows one-command installer
frontend/                  React + TypeScript + Vite desktop
backend/                   shared FastAPI/task/security core
scripts/install.sh         Linux installation
scripts/test-all.sh        Linux verification
scripts/test-all.ps1       Windows verification
docs/WINDOWS.md            Windows documentation
docs/                      architecture/security/install/roadmap/reports
```

## Documentation

- `docs/INSTALLATION.md`
- `docs/WINDOWS.md`
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
