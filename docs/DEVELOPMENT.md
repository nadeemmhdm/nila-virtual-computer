# Development Guide

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment overrides

```text
NVC_DATA_ROOT
NVC_WORKSPACE_ROOT
NVC_SHARED_ROOT
NVC_DATABASE_PATH
NVC_MAX_HEAVY_TASKS
NVC_BROWSER_IDLE_TIMEOUT
NVC_COMMAND_TIMEOUT
```

For development, point the roots at a writable temporary directory instead of system paths.

## Engineering rules

- Do not add arbitrary shell execution paths for the AI.
- Keep security decisions outside model prompts.
- Add tests for every permission/path/state-machine change.
- Prefer direct subprocess argv execution over shell parsing.
- Keep frontend polling intervals conservative.
- Avoid adding always-on processes without a measured resource budget.
- Never fake terminal/browser/tool output in UI demos.

## Pull request checklist

1. Does the change preserve managed filesystem boundaries?
2. Does it add or increase privilege?
3. Can it leave a heavy process running after a task ends?
4. Does it need explicit user permission?
5. Is success verifiable?
6. Are secrets redacted from logs?
7. Is there a test for failure/cancellation?
8. Is the 4 GB target still credible?
