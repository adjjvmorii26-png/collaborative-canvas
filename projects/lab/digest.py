"""Digest — formats and outputs organism state as a readable digest."""

import json
import urllib.request
from datetime import datetime


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return json.loads(resp.read().decode())
    except:
        return None


def digest():
    body = fetch("http://127.0.0.1:8890/api/body")
    lines = []
    lines.append("=" * 50)
    lines.append("IXPANSION DIGEST")
    lines.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)
    
    if body:
        score = body.get("symbiote_score", "?")
        meta = body.get("metabolism", {})
        lines.append(f"  Score: {score}")
        lines.append(f"  Heart Rate: {meta.get('heart_rate', '?')}")
        lines.append(f"  Stress: {meta.get('stress', '?')}")
    else:
        lines.append("  Console offline")
    
    lines.append("=" * 50)
    return "\n".join(lines)


if __name__ == "__main__":
    print(digest())
