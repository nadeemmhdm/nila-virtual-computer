from __future__ import annotations

from enum import Enum


class TaskState(str, Enum):
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    WAITING_PERMISSION = "WAITING_PERMISSION"
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    INTERRUPTED = "INTERRUPTED"


_ALLOWED: dict[TaskState, set[TaskState]] = {
    TaskState.QUEUED: {TaskState.PLANNING, TaskState.CANCELLED},
    TaskState.PLANNING: {TaskState.WAITING_PERMISSION, TaskState.PREPARING, TaskState.FAILED, TaskState.CANCELLED},
    TaskState.WAITING_PERMISSION: {TaskState.PREPARING, TaskState.CANCELLED, TaskState.FAILED},
    TaskState.PREPARING: {TaskState.RUNNING, TaskState.FAILED, TaskState.CANCELLED},
    TaskState.RUNNING: {TaskState.PAUSED, TaskState.VERIFYING, TaskState.FAILED, TaskState.CANCELLED, TaskState.INTERRUPTED},
    TaskState.PAUSED: {TaskState.RUNNING, TaskState.CANCELLED, TaskState.FAILED},
    TaskState.VERIFYING: {TaskState.COMPLETED, TaskState.FAILED, TaskState.PAUSED},
    TaskState.INTERRUPTED: {TaskState.RUNNING, TaskState.CANCELLED, TaskState.FAILED},
    TaskState.COMPLETED: set(),
    TaskState.FAILED: set(),
    TaskState.CANCELLED: set(),
}


def can_transition(current: TaskState, target: TaskState) -> bool:
    return target in _ALLOWED[current]


def transition(current: TaskState, target: TaskState) -> TaskState:
    if not can_transition(current, target):
        raise ValueError(f"invalid task transition: {current} -> {target}")
    return target
