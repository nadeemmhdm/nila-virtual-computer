from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import platform


def _defaults() -> dict[str, Path]:
    if platform.system() == "Windows":
        program_data = Path(os.getenv("PROGRAMDATA", r"C:\ProgramData"))
        public = Path(os.getenv("PUBLIC", r"C:\Users\Public"))
        data = program_data / "NilaVirtualComputer"
        return {
            "data": data,
            "workspace": data / "workspaces",
            "shared": public / "NilaVirtualComputer" / "Shared",
            "database": data / "nila.db",
        }
    data = Path("/var/lib/nila-virtual-computer")
    return {
        "data": data,
        "workspace": data / "workspaces",
        "shared": Path("/home/nila-computer/shared"),
        "database": data / "nila.db",
    }


_DEFAULTS = _defaults()


@dataclass(frozen=True)
class Settings:
    platform: str = platform.system().lower()
    data_root: Path = Path(os.getenv("NVC_DATA_ROOT", str(_DEFAULTS["data"])))
    workspace_root: Path = Path(os.getenv("NVC_WORKSPACE_ROOT", str(_DEFAULTS["workspace"])))
    shared_root: Path = Path(os.getenv("NVC_SHARED_ROOT", str(_DEFAULTS["shared"])))
    database_path: Path = Path(os.getenv("NVC_DATABASE_PATH", str(_DEFAULTS["database"])))
    max_heavy_tasks: int = int(os.getenv("NVC_MAX_HEAVY_TASKS", "1"))
    browser_idle_timeout_seconds: int = int(os.getenv("NVC_BROWSER_IDLE_TIMEOUT", "180"))
    command_timeout_seconds: int = int(os.getenv("NVC_COMMAND_TIMEOUT", "120"))


settings = Settings()
