from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.resources.monitor import pressure_level, snapshot
from app.security.paths import PathSecurityError, resolve_inside
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


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "nila-virtual-computer", "version": "0.1.0"}


@router.get("/resources")
def resources() -> dict:
    data = snapshot(settings.data_root if settings.data_root.exists() else "/")
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
        items.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
            "size": item.stat().st_size if item.is_file() else None,
        })
    return {"path": str(target.relative_to(settings.shared_root)), "items": items}


@router.post("/files")
def write_file(payload: FileWrite) -> dict:
    try:
        target = resolve_inside(settings.shared_root, payload.path)
    except PathSecurityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload.content, encoding="utf-8")
    return {"ok": True, "path": str(target.relative_to(settings.shared_root)), "size": target.stat().st_size}


@router.post("/tasks")
def create_task(payload: TaskCreate) -> dict:
    task_id = f"task-{uuid4().hex[:12]}"
    workspace = workspace_manager.create(task_id)
    task = {
        "id": task_id,
        "name": payload.name,
        "objective": payload.objective,
        "state": TaskState.QUEUED.value,
        "workspace": str(workspace),
    }
    TASKS[task_id] = task
    return task


@router.get("/tasks")
def list_tasks() -> list[dict]:
    return list(TASKS.values())


@router.post("/tasks/{task_id}/transition/{target}")
def transition_task(task_id: str, target: TaskState) -> dict:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    try:
        task["state"] = transition(TaskState(task["state"]), target).value
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return task


@router.get("/tools")
def tools() -> list[dict]:
    return [{**spec.__dict__, **inspect_tool(tool_id)} for tool_id, spec in REGISTRY.items()]
