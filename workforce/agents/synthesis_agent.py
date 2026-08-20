from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class synthesis(BaseAgent):
    name = "synthesis"
    role = "integrative analysis and knowledge weaving"
    capabilities = [
        "knowledge-weaving",
        "cross-domain-synthesis",
        "pattern-integration",
        "meta-learnings extraction",
        "report-synthesis",
        "insight-distillation",
        "organism-level-summarization",
    ]
    
    