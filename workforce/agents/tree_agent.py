from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class TreeAgent(BaseAgent):
    name = "tree"
    role = "growth and stability anchor"
    capabilities = [
        "root-growth",
        "canopy-expansion",
        "seasonal-adaptation",
        "nutrient-cycling",
        "structure-maintenance",
        "shadow-provision",
        "legacy-recording",
    ]


