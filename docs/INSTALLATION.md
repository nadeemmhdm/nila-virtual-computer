# Installation

## Target system

Recommended production base:

- Debian Stable Minimal, 64-bit
- 4 GB RAM minimum target
- CPU-only is supported
- At least 12 GB free disk is recommended before model/browser installation
- No GNOME/KDE/Cinnamon desktop environment required

## 1. Prepare Debian

Install Debian Minimal with SSH enabled if remote administration is required. Keep the machine on a private LAN initially.

Optional swap example for a 4 GB host:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Add the swap entry to `/etc/fstab` only after confirming it works. Swap is an emergency pressure buffer; it is not treated as normal RAM.

## 2. Clone and install

```bash
git clone https://github.com/nadeemmhdm/nila-virtual-computer.git
cd nila-virtual-computer
chmod +x scripts/*.sh
sudo ./scripts/install.sh
```

The installer:

1. verifies it is running with root privileges;
2. reports detected RAM, disk and architecture;
3. installs only foundation dependencies;
4. creates the `nila-computer` system user;
5. creates managed data/workspace/shared roots;
6. copies the application to `/opt/nila-virtual-computer`;
7. builds the Python virtual environment;
8. builds the Vite frontend;
9. installs a hardened systemd backend unit;
10. enables auto-start;
11. performs an HTTP health check.

The installer can be run again. It is intended to refresh application files without deleting user workspaces.

## 3. Validate

```bash
sudo ./scripts/diagnostics.sh
systemctl status nila-virtual-computer
curl http://127.0.0.1:8765/api/health
```

Expected health payload includes `status: ok`.

## 4. Frontend serving

The Vite production build is created at:

```text
/opt/nila-virtual-computer/frontend/dist
```

The foundation installer deliberately does not expose this to the public internet. For production, serve it through a local/private reverse proxy with authentication and forward `/api` and authenticated WebSocket routes to the backend.

## 5. Storage layout

```text
/opt/nila-virtual-computer                 application code
/var/lib/nila-virtual-computer             persistent service data
/var/lib/nila-virtual-computer/workspaces  autonomous task workspaces
/home/nila-computer/shared                 user-visible shared files
```

## 6. Local model installation

The runtime architecture targets llama.cpp and compatible GGUF models. Full automatic model bootstrap belongs to the Local AI phase. Until that phase lands, do not assume the foundation installer downloads a model.

When adding a model later, keep model files outside Git and validate:

- file is a readable GGUF;
- architecture is supported by the installed llama.cpp build;
- estimated resident memory remains below the configured safe ceiling;
- model license permits the intended use.

## 7. Updating

From the installed source clone:

```bash
sudo /opt/nila-virtual-computer/scripts/update.sh
```

The updater backs up known service data, fetches `origin/main`, rebuilds dependencies, restarts the backend, and performs a health check. On a failed health check it rolls code back to the prior commit when that rollback path is available.

## 8. Uninstalling

```bash
sudo /opt/nila-virtual-computer/scripts/uninstall.sh
```

The uninstaller removes the service and application files but preserves user data by default.

## Security note

Do not bind the raw backend or terminal endpoint to the public internet. The intended default is local/private access with authentication, secure cookies, origin checks, WebSocket authentication and rate limiting before remote exposure.
