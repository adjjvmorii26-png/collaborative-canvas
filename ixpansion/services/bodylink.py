"""BodyLink — the nervous-system connector between the workforce and the Organism Console.

The workforce runs its own in-process typed Bus (see `workforce/bus.py`). BodyLink
bridges those events into the console's persistent JSON message bus and keeps a
score history so the body shows a trend over time.

Files (all under `<hub>/ixpansion/content_output/console/`):
  bus.json            — recent organ signals (capped at 200)
  score_history.json  — symbiote-score snapshots (capped at 500)

Stdlib only — no third-party dependencies.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BUS_MAX = 200
SCORE_MAX = 500

BUILTIN_ORGANS = {
    "nervous", "skeletal", "respiratory", "circulatory", "digestive",
    "immune", "memory", "reproductive", "broadcast",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "ixpansion" / "content_output" / "console"


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def custom_organ_ids(data_dir: Path) -> set[str]:
    organs = _load(data_dir / "organs.json", [])
    if not isinstance(organs, list):
        return set()
    return {str(o.get("id", "")) for o in organs if o.get("id")}


def post_signal(
    organ: str = "nervous",
    topic: str = "signal",
    severity: str = "info",
    body: str = "",
    sender: str = "system",
    data_dir: Path | None = None,
) -> dict:
    """Append one signal to the console message bus. Returns the stored message."""
    data_dir = Path(data_dir) if data_dir else default_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    bus_file = data_dir / "bus.json"
    messages = _load(bus_file, [])
    if not isinstance(messages, list):
        messages = []
    organ = organ if organ in BUILTIN_ORGANS | custom_organ_ids(data_dir) else "nervous"
    severity = severity if severity in ("info", "warn", "crit") else "info"
    msg = {
        "id": f"msg-{int(time.time() * 1000)}",
        "ts": utcnow(),
        "organ": organ,
        "topic": str(topic)[:40],
        "severity": severity,
        "sender": str(sender)[:40],
        "body": str(body)[:500],
    }
    messages.append(msg)
    messages = messages[-BUS_MAX:]
    _write(bus_file, messages)
    return msg


def record_score(score: float, extra: dict | None = None, data_dir: Path | None = None) -> dict:
    """Snapshot the symbiote score into the trend history. Returns the entry."""
    data_dir = Path(data_dir) if data_dir else default_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    hist_file = data_dir / "score_history.json"
    history = _load(hist_file, [])
    if not isinstance(history, list):
        history = []
    entry = {"ts": utcnow(), "score": round(float(score), 1)}
    if extra:
        entry.update({k: v for k, v in extra.items() if v is not None})
    history.append(entry)
    history = history[-SCORE_MAX:]
    _write(hist_file, history)
    return entry


def score_history(limit: int = 60, data_dir: Path | None = None) -> list[dict]:
    data_dir = Path(data_dir) if data_dir else default_data_dir()
    history = _load(data_dir / "score_history.json", [])
    if not isinstance(history, list):
        return []
    return history[-limit:]


# ------------------------------------------------------------------ #
# Workforce bridge — map workforce Bus events to organ signals
# ------------------------------------------------------------------ #

EVENT_MAP = {
    "run_started": ("nervous", "run-start", "info"),
    "plan_ready": ("nervous", "plan", "info"),
    "task_started": ("nervous", "task", "info"),
    "review": ("immune", "review", "warn"),
    "task_accepted": ("nervous", "task-accepted", "info"),
    "task_revise": ("nervous", "task-revise", "warn"),
    "task_blocked": ("nervous", "task-blocked", "crit"),
    "task_failed": ("nervous", "task-failed", "crit"),
    "run_finished": ("memory", "run-finished", "info"),
}


class WorkforceBridge:
    """Subscribe to a workforce Bus and mirror events onto the console bus."""

    def __init__(self, hub: Path | None = None, data_dir: Path | None = None) -> None:
        self.hub = Path(hub) if hub else Path(__file__).resolve().parents[2]
        self.data_dir = Path(data_dir) if data_dir else self.hub / "ixpansion" / "content_output" / "console"

    def handle(self, event) -> None:
        etype = getattr(event, "type", "run_started")
        mapping = EVENT_MAP.get(etype)
        if mapping is None:
            return
        payload = getattr(event, "payload", {}) or {}
        organ, topic, severity = mapping
        if etype == "review":
            severity = "warn" if payload.get("verdict") == "revise" else "info"
        try:
            post_signal(
                organ=organ,
                topic=topic,
                severity=severity,
                body=self._describe(etype, payload),
                sender="workforce",
                data_dir=self.data_dir,
            )
        except Exception:
            import logging

            logging.getLogger("bodylink").exception("post_signal failed for %s", etype)

        if etype == "run_finished":
            self._pulse_on_run_finished(payload)

    def _pulse_on_run_finished(self, payload: dict) -> None:
        goal = payload.get("goal", "")
        if "." not in goal:
            return
        try:
            cmd = [
                sys.executable, "-m", "ixpansion", "run", goal,
                "--recipe", "summary",
                "--mock",
            ]
            env = os.environ.copy()
            env["IXPANSION_MOCK"] = "1"
            proc = subprocess.run(
                cmd,
                cwd=str(self.hub),
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )
            if proc.returncode == 0:
                result_text = proc.stdout[-2000:]
                post_signal(
                    organ="memory",
                    topic="auto-pulse",
                    severity="info",
                    body=f"run {payload.get('run_id', '?')}: summary auto-pulse\n{result_text[:500]}",
                    sender="workforce",
                    data_dir=self.data_dir,
                )
        except Exception as exc:
            import logging

            logging.getLogger("bodylink").exception("auto-pulse failed: %s", exc)

    @staticmethod
    def _describe(etype: str, payload: dict) -> str:
        run_id = payload.get("run_id", "?")
        if etype == "run_started":
            return f"run {run_id}: {str(payload.get('goal', ''))[:140]}"
        if etype == "plan_ready":
            return f"run {run_id}: {payload.get('task_count', '?')} tasks planned"
        if etype == "task_started":
            return f"run {run_id} task {payload.get('task_id', '?')} #{payload.get('attempt', '?')} ({payload.get('agent', '')})"
        if etype == "review":
            return f"run {run_id} task {payload.get('task_id', '?')}: {payload.get('verdict', '')} score={payload.get('score', '')}"
        if etype == "task_accepted":
            return f"run {run_id} task {payload.get('task_id', '?')} accepted"
        if etype == "task_revise":
            return f"run {run_id} task {payload.get('task_id', '?')} needs revision"
        if etype == "task_blocked":
            return f"run {run_id} task {payload.get('task_id', '?')} blocked"
        if etype == "task_failed":
            return f"run {run_id} task {payload.get('task_id', '?')} failed"
        if etype == "run_finished":
            return f"run {run_id}: {payload.get('status', '')} report={payload.get('report', '')}"
        return f"run {run_id} event {etype}"
