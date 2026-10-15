from __future__ import annotations
from dataclasses import dataclass
from app.ai.provider import chat_cloud, cloud_status
from app.ai.websearch import search_web

@dataclass
class RuntimeSettings:
    cloud_enabled: bool = False
    web_search_enabled: bool = False

runtime_settings = RuntimeSettings()
SYSTEM = "You are Nila, the assistant inside Nila Virtual Computer. Be concise. Never claim a computer action completed unless task verification confirms it. Markdown formatting is allowed."

def status() -> dict:
    return {"cloud_enabled": runtime_settings.cloud_enabled, "web_search_enabled": runtime_settings.web_search_enabled, "cloud": cloud_status()}

def respond(message: str) -> dict:
    sources = search_web(message) if runtime_settings.web_search_enabled else []
    context = "\n".join(f"{x['title']}: {x['snippet']} ({x['url']})" for x in sources)
    if runtime_settings.cloud_enabled:
        reply = chat_cloud([{"role":"system","content":SYSTEM},{"role":"user","content":message + ("\nWeb context:\n" + context if context else "")}])
        return {"reply":reply,"provider":"ollama-cloud","sources":sources}
    return {"reply":"Cloud AI is off. The request can still be assigned as a controlled task.","provider":"task-only","sources":sources}
