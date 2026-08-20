"""Knowledge: build a graph from run/task facts in memory."""

from __future__ import annotations

from .memory import Memory


class KnowledgeGraph:
    def __init__(self, memory: Memory):
        self.memory = memory

    def build(self) -> dict:
        nodes, edges = [], []
        for r in self.memory.list_runs(limit=50):
            for t in self.memory.get_tasks(r["run_id"]):
                nodes.append({"id": t["task_id"], "cap": t["capability"], "status": t["status"]})
                for dep in t.get("depends_on") or []:
                    edges.append({"from": dep, "to": t["task_id"]})
        return {"nodes": nodes, "edges": edges}
