from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    data_root: Path = Path(os.getenv("NVC_DATA_ROOT", "/var/lib/nila-virtual-computer"))
    workspace_root: Path = Path(os.getenv("NVC_WORKSPACE_ROOT", "/var/lib/nila-virtual-computer/workspaces"))
    shared_root: Path = Path(os.getenv("NVC_SHARED_ROOT", "/home/nila-computer/shared"))
    database_path: Path = Path(os.getenv("NVC_DATABASE_PATH", "/var/lib/nila-virtual-computer/nila.db"))
    max_heavy_tasks: int = int(os.getenv("NVC_MAX_HEAVY_TASKS", "1"))
    browser_idle_timeout_seconds: int = int(os.getenv("NVC_BROWSER_IDLE_TIMEOUT", "180"))
    command_timeout_seconds: int = int(os.getenv("NVC_COMMAND_TIMEOUT", "120"))


settings = Settings()
