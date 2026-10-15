# Test Report

## Release scope

This report covers the current foundation release, not the final Definition of Done.

## Automated tests included

The repository includes tests for:

- path traversal rejection;
- task state transitions;
- workspace creation;
- health API;
- resource pressure classification;
- structured tool action validation.

## Current validation status

The code has been structured for deterministic unit testing. GitHub-side file creation does not provide a Linux execution environment, so this commit must not claim that runtime tests have executed successfully on Debian. Run the commands below on the target or CI environment and record the exact outputs before promoting a release.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest ../tests -q
```

Frontend build validation:

```bash
cd frontend
npm install
npm run build
```

Installer validation must be performed on a clean Debian Stable Minimal VM or physical target:

```bash
sudo ./scripts/install.sh
sudo ./scripts/diagnostics.sh
```

## Final release test matrix still required

- real PTY terminal and WebSocket auth;
- process cancellation/termination;
- symlink escape with real filesystem fixtures;
- archive extraction safety;
- persistent task recovery after reboot;
- SQLite migrations;
- authentication and session throttling;
- CSRF protection;
- browser automation isolation;
- privileged helper allowlist;
- approved package installation;
- llama.cpp/model lifecycle;
- autonomous plan -> execute -> verify integration;
- emergency stop;
- update rollback;
- 4 GB resource profiling.

No component should be marked production-complete until its relevant automated and target-host tests pass.
