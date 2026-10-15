from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import shutil
import subprocess


class ToolCategory(str, Enum):
    DEVELOPMENT = "development"
    MEDIA = "media"
    ARCHIVE = "archive"
    NETWORK = "network"
    BROWSER = "browser"
    DOCUMENT = "document"


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    package: str
    executable: str
    category: ToolCategory
    min_version: str
    install_source: str = "debian"
    privileged: bool = True
    ram_mb: int = 64


REGISTRY: dict[str, ToolSpec] = {
    "git": ToolSpec("git", "git", "git", ToolCategory.DEVELOPMENT, "2.39"),
    "python": ToolSpec("python", "python3", "python3", ToolCategory.DEVELOPMENT, "3.11", privileged=False),
    "node": ToolSpec("node", "nodejs", "node", ToolCategory.DEVELOPMENT, "20"),
    "npm": ToolSpec("npm", "npm", "npm", ToolCategory.DEVELOPMENT, "9"),
    "ffmpeg": ToolSpec("ffmpeg", "ffmpeg", "ffmpeg", ToolCategory.MEDIA, "5"),
    "imagemagick": ToolSpec("imagemagick", "imagemagick", "convert", ToolCategory.MEDIA, "6"),
    "zip": ToolSpec("zip", "zip", "zip", ToolCategory.ARCHIVE, "3"),
    "unzip": ToolSpec("unzip", "unzip", "unzip", ToolCategory.ARCHIVE, "6"),
    "curl": ToolSpec("curl", "curl", "curl", ToolCategory.NETWORK, "7"),
    "wget": ToolSpec("wget", "wget", "wget", ToolCategory.NETWORK, "1"),
}


def inspect_tool(tool_id: str) -> dict:
    spec = REGISTRY[tool_id]
    path = shutil.which(spec.executable)
    if not path:
        return {"tool": tool_id, "installed": False, "package": spec.package}
    try:
        result = subprocess.run([path, "--version"], text=True, capture_output=True, timeout=3)
        first_line = (result.stdout or result.stderr).splitlines()[0][:200]
    except Exception as exc:
        first_line = f"version probe failed: {exc}"
    return {"tool": tool_id, "installed": True, "path": path, "version_output": first_line}
