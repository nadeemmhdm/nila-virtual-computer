from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import platform
import re
import threading
import time


class Capability(str, Enum):
    FILES = "files"
    TERMINAL = "terminal"
    NETWORK = "network"
    BROWSER = "browser"
    PACKAGE_INSTALL = "package_install"
    SYSTEM_SETTINGS = "system_settings"


class Risk(str, Enum):
    SAFE = "SAFE"
    SENSITIVE = "SENSITIVE"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"


@dataclass
class SecurityState:
    emergency_stop: bool = False
    safe_mode: bool = False
    local_only: bool = False
    capabilities: dict[str, bool] = field(default_factory=lambda: {
        Capability.FILES.value: True,
        Capability.TERMINAL.value: False,
        Capability.NETWORK.value: False,
        Capability.BROWSER.value: False,
        Capability.PACKAGE_INSTALL.value: False,
        Capability.SYSTEM_SETTINGS.value: False,
    })
    updated_at: float = field(default_factory=time.time)


class SecurityController:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.state = SecurityState()

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "emergency_stop": self.state.emergency_stop,
                "safe_mode": self.state.safe_mode,
                "local_only": self.state.local_only,
                "capabilities": dict(self.state.capabilities),
                "updated_at": self.state.updated_at,
                "platform": platform.system().lower(),
            }

    def set_emergency_stop(self, enabled: bool) -> dict:
        with self._lock:
            self.state.emergency_stop = enabled
            self.state.updated_at = time.time()
            return self.snapshot()

    def set_mode(self, *, safe_mode: bool | None = None, local_only: bool | None = None) -> dict:
        with self._lock:
            if safe_mode is not None:
                self.state.safe_mode = safe_mode
            if local_only is not None:
                self.state.local_only = local_only
            self.state.updated_at = time.time()
            return self.snapshot()

    def set_capability(self, capability: Capability, allowed: bool) -> dict:
        with self._lock:
            self.state.capabilities[capability.value] = allowed
            self.state.updated_at = time.time()
            return self.snapshot()

    def require(self, capability: Capability) -> None:
        state = self.snapshot()
        if state["emergency_stop"]:
            raise PermissionError("AI emergency stop is active")
        if state["safe_mode"] and capability not in {Capability.FILES}:
            raise PermissionError("safe mode blocks active system capabilities")
        if state["local_only"] and capability in {Capability.NETWORK, Capability.BROWSER, Capability.PACKAGE_INSTALL}:
            raise PermissionError("local-only mode blocks network-dependent capabilities")
        if not state["capabilities"].get(capability.value, False):
            raise PermissionError(f"capability not granted: {capability.value}")


_DANGEROUS = [
    (Risk.CRITICAL, re.compile(r"\b(rm\s+-rf\s+/|mkfs\b|format\s+[a-z]:|diskpart\b|bcdedit\b|shutdown\b)", re.I)),
    (Risk.HIGH_RISK, re.compile(r"\b(sudo\b|runas\b|reg\s+(add|delete)\b|Set-MpPreference\b|ufw\s+disable\b|chmod\s+777\b)", re.I)),
    (Risk.SENSITIVE, re.compile(r"\b(apt|apt-get|dnf|yum|pacman|winget|choco|pip|npm)\s+(install|remove|uninstall|upgrade)\b", re.I)),
]


def classify_command(command: str) -> Risk:
    for risk, pattern in _DANGEROUS:
        if pattern.search(command):
            return risk
    return Risk.SAFE


def protected_roots() -> list[Path]:
    if platform.system() == "Windows":
        return [Path(r"C:\Windows"), Path(r"C:\Program Files"), Path(r"C:\Program Files (x86)")]
    return [Path("/boot"), Path("/etc"), Path("/usr"), Path("/bin"), Path("/sbin")]


controller = SecurityController()
