from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.security.paths import resolve_inside


class WorkspaceManager:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, task_id: str | None = None) -> Path:
        task_id = task_id or f"task-{uuid4().hex[:12]}"
        workspace = resolve_inside(self.root, task_id)
        for name in ("files", "output", "logs", "metadata", "tmp"):
            (workspace / name).mkdir(parents=True, exist_ok=True)
        return workspace

    def get(self, task_id: str) -> Path:
        return resolve_inside(self.root, task_id)
