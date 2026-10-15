from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class PermissionLevel(str, Enum):
    SAFE = "SAFE"
    SENSITIVE = "SENSITIVE"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"


class PermissionRequest(BaseModel):
    action: str
    level: PermissionLevel
    reason: str = Field(min_length=1, max_length=500)


def requires_confirmation(level: PermissionLevel) -> bool:
    return level in {PermissionLevel.HIGH_RISK, PermissionLevel.CRITICAL}


def is_auto_allowed(level: PermissionLevel, allow_sensitive: bool = False) -> bool:
    if level == PermissionLevel.SAFE:
        return True
    if level == PermissionLevel.SENSITIVE:
        return allow_sensitive
    return False
