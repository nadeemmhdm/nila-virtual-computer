from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil

from app.core.config import settings
from app.security.paths import resolve_inside


class SnapshotManager:
    def __init__(self) -> None:
        self.root = settings.data_root / "snapshots"
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, task_id: str, workspace: Path) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = self.root / task_id / stamp
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(workspace, target, dirs_exist_ok=False)
        return target

    def rollback(self, task_id: str, snapshot_name: str, workspace: Path) -> None:
        source = resolve_inside(self.root / task_id, snapshot_name)
        if not source.exists() or not source.is_dir():
            raise FileNotFoundError("snapshot not found")
        if workspace.exists():
            shutil.rmtree(workspace)
        shutil.copytree(source, workspace)

    def list(self, task_id: str) -> list[str]:
        root = self.root / task_id
        if not root.exists():
            return []
        return sorted((p.name for p in root.iterdir() if p.is_dir()), reverse=True)


snapshots = SnapshotManager()
