from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class VerificationResult:
    ok: bool
    evidence: str


def verify_file_exists(path: Path, require_non_empty: bool = False) -> VerificationResult:
    if not path.exists():
        return VerificationResult(False, f"missing: {path}")
    if require_non_empty and path.is_file() and path.stat().st_size == 0:
        return VerificationResult(False, f"empty file: {path}")
    return VerificationResult(True, f"verified: {path}")


def verify_exit_code(exit_code: int, stdout: str = "", stderr: str = "") -> VerificationResult:
    if exit_code == 0:
        tail = stdout[-500:] if stdout else "command exited successfully"
        return VerificationResult(True, tail)
    tail = stderr[-500:] if stderr else stdout[-500:]
    return VerificationResult(False, f"exit={exit_code}: {tail}")
