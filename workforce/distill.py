"""Distill: compress run history into a short summary."""

from __future__ import annotations

from .memory import Memory


def distill(memory: Memory, limit: int = 20) -> str:
    runs = memory.list_runs(limit=limit)
    lines = [f"# Distilled memory - {len(runs)} runs"]
    for r in runs:
        tasks = memory.get_tasks(r["run_id"])
        lines.append(f"- run {r['run_id']} ({r['status']}): {len(tasks)} tasks")
    return "\n".join(lines)
