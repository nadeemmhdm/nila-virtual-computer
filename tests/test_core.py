from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.ai.contracts import ActionName, ToolAction
from app.main import app
from app.resources.monitor import pressure_level
from app.security.paths import PathSecurityError, resolve_inside
from app.tasks.state import TaskState, can_transition, transition
from app.tasks.workspace import WorkspaceManager


def test_path_traversal_rejected(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    with pytest.raises(PathSecurityError):
        resolve_inside(root, "../outside.txt")


def test_task_transition_rules():
    assert can_transition(TaskState.QUEUED, TaskState.PLANNING)
    assert transition(TaskState.PLANNING, TaskState.PREPARING) == TaskState.PREPARING
    with pytest.raises(ValueError):
        transition(TaskState.QUEUED, TaskState.COMPLETED)


def test_workspace_creation(tmp_path: Path):
    manager = WorkspaceManager(tmp_path / "workspaces")
    ws = manager.create("task-test")
    for name in ("files", "output", "logs", "metadata", "tmp"):
        assert (ws / name).is_dir()


def test_health_api():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_pressure_levels():
    def data(percent: float):
        return {"memory": {"percent": percent}}
    assert pressure_level(data(20)) == "NORMAL"
    assert pressure_level(data(76)) == "PRESSURE"
    assert pressure_level(data(87)) == "HIGH"
    assert pressure_level(data(95)) == "CRITICAL"


def test_structured_tool_action_validation():
    action = ToolAction(action=ActionName.READ_FILE, arguments={"path": "hello.txt"})
    assert action.action == ActionName.READ_FILE
