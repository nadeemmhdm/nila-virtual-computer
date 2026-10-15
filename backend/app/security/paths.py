from __future__ import annotations

from pathlib import Path


class PathSecurityError(ValueError):
    pass


def resolve_inside(root: Path, requested: str | Path) -> Path:
    root = root.resolve()
    requested_path = Path(requested)
    candidate = requested_path if requested_path.is_absolute() else root / requested_path
    try:
        resolved = candidate.resolve(strict=False)
    except RuntimeError as exc:
        raise PathSecurityError("unable to resolve path") from exc

    if resolved == root:
        return resolved

    if root not in resolved.parents:
        raise PathSecurityError("path escapes allowed root")

    probe = resolved
    while probe != root and not probe.exists():
        probe = probe.parent
    if probe.exists() and probe.is_symlink():
        real = probe.resolve()
        if real != root and root not in real.parents:
            raise PathSecurityError("symlink escapes allowed root")
    return resolved


def safe_child(root: Path, name: str) -> Path:
    if not name or name in {".", ".."}:
        raise PathSecurityError("invalid path component")
    if Path(name).is_absolute() or "/" in name or "\\" in name:
        raise PathSecurityError("nested or absolute names are not allowed")
    return resolve_inside(root, name)
