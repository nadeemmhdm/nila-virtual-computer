from __future__ import annotations

from dataclasses import dataclass
import re
from uuid import uuid4

from app.security.control import controller

_SECRET = re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)")


def redact(text: str) -> str:
    return _SECRET.sub(lambda m: f"{m.group(1)}=[REDACTED]", text)


@dataclass
class ChatAssignment:
    id: str
    message: str
    task_name: str
    objective: str


def assign(message: str) -> ChatAssignment:
    if controller.snapshot()["emergency_stop"]:
        raise PermissionError("AI emergency stop is active")
    clean = redact(message.strip())
    if not clean:
        raise ValueError("message is empty")
    short = clean.replace("\n", " ")[:70]
    return ChatAssignment(
        id=f"chat-{uuid4().hex[:12]}",
        message=clean,
        task_name=f"Nila: {short}",
        objective=clean,
    )
