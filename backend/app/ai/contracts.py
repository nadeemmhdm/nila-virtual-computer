from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ActionName(str, Enum):
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    LIST_DIRECTORY = "list_directory"
    CREATE_DIRECTORY = "create_directory"
    MOVE_FILE = "move_file"
    DELETE_FILE = "delete_file"
    EXECUTE_COMMAND = "execute_command"
    INSTALL_TOOL = "install_tool"
    INSPECT_TOOL = "inspect_tool"
    BROWSER_OPEN = "browser_open"
    BROWSER_CLICK = "browser_click"
    BROWSER_EXTRACT = "browser_extract"
    BROWSER_DOWNLOAD = "browser_download"
    PROCESS_STATUS = "process_status"
    STOP_PROCESS = "stop_process"
    INSPECT_RESOURCES = "inspect_resources"


class ToolAction(BaseModel):
    action: ActionName
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(default="", max_length=500)


class TaskPlan(BaseModel):
    objective: str = Field(min_length=1, max_length=1000)
    steps: list[str] = Field(min_length=1, max_length=30)
    required_tools: list[str] = Field(default_factory=list, max_length=20)
