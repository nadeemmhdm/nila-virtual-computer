# Windows 10/11 support

Nila Virtual Computer now has a native Windows installation path in addition to Linux. The shared FastAPI, React, task, security and AI architecture remains cross-platform; OS-specific service/package/filesystem operations are isolated by platform policy.

## Install

Open **PowerShell as Administrator** and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force; irm https://raw.githubusercontent.com/nadeemmhdm/nila-virtual-computer/main/install.ps1 | iex
```

The installer uses `winget` only when Git, Python or Node are missing, clones the repository, creates the Python virtual environment, builds the frontend, configures Windows storage, creates an AtStartup Scheduled Task for the backend, starts it, runs backend tests, runs the frontend production build and checks backend health.

## Paths

- Data: `%ProgramData%\NilaVirtualComputer`
- Workspaces: `%ProgramData%\NilaVirtualComputer\workspaces`
- Shared: `%PUBLIC%\NilaVirtualComputer\Shared`
- Source: `%ProgramData%\NilaVirtualComputer\source`

## Verify again

```powershell
& "$env:ProgramData\NilaVirtualComputer\source\scripts\test-all.ps1"
```

## Linux

Linux keeps its systemd-based service model and controlled `/var/lib/nila-virtual-computer` + `/home/nila-computer/shared` roots. See `docs/INSTALLATION.md`.

## Security

Windows support does not translate Linux root/sudo commands into unrestricted Administrator PowerShell. Future privileged operations must use a narrow OS-specific helper and approved package registry. `winget` is used by the bootstrap only for explicit core prerequisites.
