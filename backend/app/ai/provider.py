from __future__ import annotations

import json
import os
from urllib import request

from app.security.control import Capability, controller

CLOUD_BASE = os.getenv("NVC_OLLAMA_CLOUD_BASE", "https://ollama.com")
DEFAULT_MODEL = os.getenv("NVC_OLLAMA_CLOUD_MODEL", "gpt-oss:20b-cloud")


def cloud_status() -> dict:
    return {"configured": bool(os.getenv("OLLAMA_API_KEY", "").strip()), "model": DEFAULT_MODEL}


def chat_cloud(messages: list[dict], model: str | None = None) -> str:
    controller.require(Capability.NETWORK)
    key = os.getenv("OLLAMA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OLLAMA_API_KEY is not configured")
    body = json.dumps({"model": model or DEFAULT_MODEL, "messages": messages, "stream": False}).encode("utf-8")
    req = request.Request(CLOUD_BASE.rstrip("/") + "/api/chat", data=body, headers={"Content-Type": "application/json", "Authorization": "Bearer " + key}, method="POST")
    with request.urlopen(req, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    content = (data.get("message") or {}).get("content")
    if not isinstance(content, str):
        raise RuntimeError("Cloud provider returned an invalid response")
    return content
