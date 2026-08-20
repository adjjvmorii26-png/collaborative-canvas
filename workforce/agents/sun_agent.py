from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class SunAgent(BaseAgent):
    name = "sun"
    role = "energy and illumination source"
    capabilities = [
        "energy-provision",
        "illumination",
        "motivation-boost",
        "external-awareness",
        "cycle-regulation",
        "growth-stimulation",
        "temperature-regulation",
    ]


