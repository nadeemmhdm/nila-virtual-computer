from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from threading import RLock

from app.core.config import settings

_lock = RLock()


def audit_path() -> Path:
    path = settings.data_root / "logs" / "audit.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def record(event: str, *, actor: str = "system", task_id: str | None = None, details: dict | None = None) -> dict:
    item = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "actor": actor,
        "task_id": task_id,
        "details": details or {},
    }
    with _lock:
        with audit_path().open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    return item


def recent(limit: int = 100) -> list[dict]:
    path = audit_path()
    if not path.exists():
        return []
    with _lock:
        lines = path.read_text(encoding="utf-8").splitlines()[-max(1, min(limit, 500)):]
    result = []
    for line in lines:
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return result
