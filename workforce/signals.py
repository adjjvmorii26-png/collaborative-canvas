"""Signals: detect phase transitions / criticality in run history."""

from __future__ import annotations

from dataclasses import dataclass
from .memory import Memory


@dataclass
class Signal:
    name: str
    kind: str
    score: float
    explanation: str = ""


class SignalsEngine:
    def __init__(self, memory: Memory):
        self.memory = memory

    def scan(self) -> list[Signal]:
        tasks = [
            t
            for r in self.memory.list_runs(limit=200)
            for t in self.memory.get_tasks(r["run_id"])
            if t.get("status") == "accepted"
        ]
        if len(tasks) < 5:
            return []
        scores = [t.get("score") or 0 for t in tasks]
        mean = sum(scores) / len(scores)
        var = sum((s - mean) ** 2 for s in scores) / len(scores)
        crit = min(100.0, var ** 0.5 * 5.0)
        return [
            Signal(
                "criticality",
                "criticality",
                round(crit, 1),
                f"score variance across {len(tasks)} tasks suggests a phase transition",
            )
        ]
