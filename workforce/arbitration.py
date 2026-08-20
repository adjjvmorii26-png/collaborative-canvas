"""Tool arbitration: pick the right tool for a request."""

from __future__ import annotations


def arbitrate_tool(request: str) -> dict:
    req = request.lower()
    if "read" in req and "file" in req:
        return {"chosen": "read_file", "reason": "user asked to read a file", "rejected": []}
    if "write" in req and "file" in req:
        return {"chosen": "write_file", "reason": "user asked to write a file", "rejected": []}
    if "search" in req or "web" in req:
        return {"chosen": "search_web", "reason": "request involves finding info", "rejected": []}
    if "fetch" in req or "url" in req:
        return {"chosen": "fetch_url", "reason": "request asks for a specific URL", "rejected": []}
    return {"chosen": "NONE", "reason": "no tool matches the request", "rejected": []}
