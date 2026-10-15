from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.chat import assign
from app.core.config import settings
from app.resources.monitor import pressure_level, snapshot
from app.security.audit import recent, record
from app.security.control import Capability, controller
from app.security.paths import PathSecurityError, resolve_inside
from app.tasks.snapshots import snapshots
from app.tasks.state import TaskState, transition
from app.tasks.workspace import WorkspaceManager
from app.tools.registry import REGISTRY, inspect_tool

router = APIRouter()
workspace_manager = WorkspaceManager(settings.workspace_root)
TASKS: dict[str, dict] = {}


class FileWrite(BaseModel):
    path: str
    content: str = Field(max_length=2_000_000)


class TaskCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    objective: str = Field(min_length=1, max_length=2000)


class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class SecurityModes(BaseModel):
    safe_mode: bool | None = None
    local_only: bool | None = None


class CapabilityUpdate(BaseModel):
    allowed: bool


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "nila-virtual-computer", "version": "0.2.0", "platform": settings.platform}


@router.get("/resources")
def resources() -> dict:
    data = snapshot(settings.data_root if settings.data_root.exists() else settings.shared_root.anchor or "/")
    data["pressure"] = pressure_level(data)
    return data


@router.get("/files")
def list_files(path: str = ".") -> dict:
    try:
        target = resolve_inside(settings.shared_root, path)
    except PathSecurityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    target.mkdir(parents=True, exist_ok=True) if target == settings.shared_root else None
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail="directory not found")
    items = []
    for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        items.append({"name": item.name, "type": "directory" if item.is_dir() else "file", "size": item.stat().st_size if item.is_file() else None})
    return {"path": str(target.relative_to(settings.shared_root)), "items": items}


@router.post("/files")
def write_file(payload: FileWrite) -> dict:
    try:
        controller.require(Capability.FILES)
        target = resolve_inside(settings.shared_root, payload.path)
    except (PathSecurityError, PermissionError) as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload.content, encoding="utf-8")
    record("file.write", actor="user", details={"path": str(target.relative_to(settings.shared_root)), "size": target.stat().st_size})
    return {"ok": True, "path": str(target.relative_to(settings.shared_root)), "size": target.stat().st_size}


@router.post("/tasks")
def create_task(payload: TaskCreate) -> dict:
    if controller.snapshot()["emergency_stop"]:
        raise HTTPException(status_code=423, detail="AI emergency stop is active")
    task_id = f"task-{uuid4().hex[:12]}"
    workspace = workspace_manager.create(task_id)
    task = {"id": task_id, "name": payload.name, "objective": payload.objective, "state": TaskState.QUEUED.value, "workspace": str(workspace), "verification": "pending"}
    TASKS[task_id] = task
    record("task.created", actor="user", task_id=task_id, details={"name": payload.name})
    return task


@router.post("/ai/chat")
def ai_chat(payload: ChatMessage) -> dict:
    try:
        assignment = assign(payload.message)
    except (PermissionError, ValueError) as exc:
        raise HTTPException(status_code=423, detail=str(exc)) from exc
    task = create_task(TaskCreate(name=assignment.task_name, objective=assignment.objective))
    record("ai.chat.assignment", actor="user", task_id=task["id"], details={"chat_id": assignment.id})
    return {"reply": "Task assigned. Nila created a controlled workspace and queued it for planning. Execution still requires capability and risk-policy approval.", "task": task, "security": controller.snapshot()}


@router.get("/tasks")
def list_tasks() -> list[dict]:
    return list(TASKS.values())


@router.post("/tasks/{task_id}/transition/{target}")
def transition_task(task_id: str, target: TaskState) -> dict:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    if controller.snapshot()["emergency_stop"] and target in {TaskState.PREPARING, TaskState.RUNNING}:
        raise HTTPException(status_code=423, detail="AI emergency stop is active")
    try:
        task["state"] = transition(TaskState(task["state"]), target).value
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    record("task.transition", task_id=task_id, details={"state": task["state"]})
    return task


@router.post("/tasks/{task_id}/snapshot")
def create_snapshot(task_id: str) -> dict:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    path = snapshots.create(task_id, workspace_manager.get(task_id))
    record("task.snapshot", task_id=task_id, details={"snapshot": path.name})
    return {"ok": True, "snapshot": path.name}


@router.get("/security")
def security_state() -> dict:
    return controller.snapshot()


@router.post("/security/emergency-stop")
def emergency_stop() -> dict:
    state = controller.set_emergency_stop(True)
    for task in TASKS.values():
        if task["state"] not in {TaskState.COMPLETED.value, TaskState.FAILED.value, TaskState.CANCELLED.value}:
            task["state"] = TaskState.PAUSED.value
    record("security.emergency_stop", actor="user")
    return state


@router.post("/security/resume")
def resume_ai() -> dict:
    state = controller.set_emergency_stop(False)
    record("security.resume", actor="user")
    return state


@router.post("/security/modes")
def security_modes(payload: SecurityModes) -> dict:
    state = controller.set_mode(safe_mode=payload.safe_mode, local_only=payload.local_only)
    record("security.modes", actor="user", details=state)
    return state


@router.post("/security/capabilities/{capability}")
def capability_update(capability: Capability, payload: CapabilityUpdate) -> dict:
    state = controller.set_capability(capability, payload.allowed)
    record("security.capability", actor="user", details={"capability": capability.value, "allowed": payload.allowed})
    return state


@router.get("/audit")
def audit(limit: int = 100) -> list[dict]:
    return recent(limit)


@router.get("/tools")
def tools() -> list[dict]:
    return [{**spec.__dict__, **inspect_tool(tool_id)} for tool_id, spec in REGISTRY.items()]
