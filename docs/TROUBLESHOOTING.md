# Troubleshooting

## Backend does not start

Check the service:

```bash
systemctl status nila-virtual-computer
journalctl -u nila-virtual-computer -n 100 --no-pager
```

Then run:

```bash
sudo /opt/nila-virtual-computer/scripts/diagnostics.sh
```

Common causes are missing Python dependencies, incorrect file ownership, a port conflict on 8765, or a damaged virtual environment.

## Health endpoint fails

```bash
curl -v http://127.0.0.1:8765/api/health
```

If connection is refused, confirm the service is active. If another process owns the port:

```bash
ss -ltnp | grep 8765
```

## Frontend build fails

```bash
cd /opt/nila-virtual-computer/frontend
npm install
npm run build
```

Check the installed Node.js version. The development target is Node.js 20+.

## Permission denied in workspace

Verify ownership:

```bash
sudo chown -R nila-computer:nila-computer /var/lib/nila-virtual-computer
sudo chown -R nila-computer:nila-computer /home/nila-computer/shared
```

Do not broaden permissions to world-writable as a shortcut.

## Low memory

Check:

```bash
free -h
ps aux --sort=-%mem | head
```

On a 4 GB host, close unnecessary browser automation workers and development servers. Use a small local GGUF model. Avoid running multiple heavy autonomous tasks.

## Update fails

The updater backs up known state before changing code. Review service logs and the backup directory under:

```text
/var/lib/nila-virtual-computer/backups/
```

Do not delete workspaces to fix an application update.

## Files API rejects a path

This is expected when a path attempts to leave the managed root. Do not disable path validation. Move the required file into the shared root or use an explicit future administrator-controlled mount/import flow.

## Browser automation unavailable

The foundation release does not yet install Playwright/Chromium automatically. Browser automation is scheduled for the Browser phase because keeping Chromium permanently installed/running without lifecycle control conflicts with the 4 GB RAM target.

## Local AI unavailable

The foundation release includes the structured runtime boundary but not the final llama.cpp/model bootstrap. Follow `docs/ROADMAP.md`; do not treat this as a completed Local AI release yet.
