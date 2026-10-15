from __future__ import annotations

import json
import os
from urllib import parse, request

from app.security.control import Capability, controller


def search_web(query: str, limit: int = 5) -> list[dict]:
    controller.require(Capability.NETWORK)
    endpoint = os.getenv("NVC_SEARCH_ENDPOINT", "").strip()
    if not endpoint:
        raise RuntimeError("Web search endpoint is not configured. Set NVC_SEARCH_ENDPOINT to a trusted SearXNG-compatible JSON endpoint.")
    url = endpoint.rstrip("/") + "/search?" + parse.urlencode({"q": query, "format": "json"})
    req = request.Request(url, headers={"User-Agent": "NilaVirtualComputer/0.3"})
    with request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    results = []
    for item in data.get("results", [])[:max(1, min(limit, 10))]:
        results.append({"title": str(item.get("title", ""))[:300], "url": str(item.get("url", ""))[:2000], "snippet": str(item.get("content", ""))[:1000]})
    return results
