from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.ai.chat import redact
from app.ai.contracts import ActionName, ToolAction
from app.main import app
from app.resources.monitor import pressure_level
from app.security.control import Capability, Risk, SecurityController, classify_command
from app.security.paths import PathSecurityError, resolve_inside
from app.tasks.state import TaskState, can_transition, transition
from app.tasks.workspace import WorkspaceManager


def test_path_traversal_rejected(tmp_path: Path):
    root = tmp_path / "root"; root.mkdir()
    with pytest.raises(PathSecurityError): resolve_inside(root, "../outside.txt")


def test_task_transition_rules():
    assert can_transition(TaskState.QUEUED, TaskState.PLANNING)
    assert transition(TaskState.PLANNING, TaskState.PREPARING) == TaskState.PREPARING
    with pytest.raises(ValueError): transition(TaskState.QUEUED, TaskState.COMPLETED)


def test_workspace_creation(tmp_path: Path):
    manager = WorkspaceManager(tmp_path / "workspaces"); ws = manager.create("task-test")
    for name in ("files", "output", "logs", "metadata", "tmp"): assert (ws / name).is_dir()


def test_health_api():
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200 and response.json()["status"] == "ok"


def test_pressure_levels():
    data=lambda percent:{"memory":{"percent":percent}}
    assert pressure_level(data(20)) == "NORMAL"; assert pressure_level(data(76)) == "PRESSURE"; assert pressure_level(data(87)) == "HIGH"; assert pressure_level(data(95)) == "CRITICAL"


def test_structured_tool_action_validation():
    assert ToolAction(action=ActionName.READ_FILE, arguments={"path":"hello.txt"}).action == ActionName.READ_FILE


def test_command_risk_engine():
    assert classify_command("echo hello") == Risk.SAFE
    assert classify_command("sudo apt install git") in {Risk.HIGH_RISK, Risk.SENSITIVE}
    assert classify_command("rm -rf /") == Risk.CRITICAL


def test_security_capability_and_kill_switch():
    c=SecurityController()
    with pytest.raises(PermissionError): c.require(Capability.NETWORK)
    c.set_capability(Capability.NETWORK, True); c.require(Capability.NETWORK)
    c.set_emergency_stop(True)
    with pytest.raises(PermissionError): c.require(Capability.FILES)


def test_secret_redaction():
    assert "supersecret" not in redact("api_key=supersecret do task")


def test_ai_chat_creates_controlled_task():
    client=TestClient(app)
    client.post("/api/security/resume")
    response=client.post("/api/ai/chat",json={"message":"create a test project"})
    assert response.status_code == 200
    assert response.json()["task"]["state"] == "QUEUED"


def test_emergency_stop_blocks_chat():
    client=TestClient(app)
    client.post("/api/security/emergency-stop")
    response=client.post("/api/ai/chat",json={"message":"run something"})
    assert response.status_code == 423
    client.post("/api/security/resume")
