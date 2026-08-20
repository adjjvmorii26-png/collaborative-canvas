from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class pulse(BaseAgent):
    name = "pulse"
    role = "experiment orchestrator and pulse manager"
    capabilities = [
        "experiment-scheduling",
        "pulse-triggering",
        "mock-run-management",
        "result-consolidation",
        "cycle-analysis",
        "pattern-detection-in-runs",
        "progress-reporting",
    ]
    
    