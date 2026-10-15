from __future__ import annotations

from pathlib import Path
import psutil


def snapshot(path: Path | str = "/") -> dict:
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage(str(path))
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.05),
        "memory": {
            "total": vm.total,
            "available": vm.available,
            "percent": vm.percent,
        },
        "swap": {"total": swap.total, "used": swap.used, "percent": swap.percent},
        "disk": {"total": disk.total, "free": disk.free, "percent": disk.percent},
    }


def pressure_level(data: dict) -> str:
    mem = float(data["memory"]["percent"])
    if mem >= 92:
        return "CRITICAL"
    if mem >= 85:
        return "HIGH"
    if mem >= 75:
        return "PRESSURE"
    return "NORMAL"
