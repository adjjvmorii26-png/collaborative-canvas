"""Topology: map capability-based links between agents."""

from __future__ import annotations

from .agents import AGENT_LOOKUP


def topology() -> dict:
    agents = list(AGENT_LOOKUP.keys())
    edges = []
    for a in agents:
        for cap in AGENT_LOOKUP[a].capabilities:
            for b in agents:
                if cap in AGENT_LOOKUP[b].capabilities and a != b:
                    edges.append((a, b))
    return {"agents": agents, "edges": edges}
