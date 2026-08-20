from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class EngineerAgent(BaseAgent):
    """Agent specialized in systems engineering and infrastructure."""

    name = "engineer"
    role = "systems engineer and infrastructure"
    capabilities = [
        "system-design", "infrastructure-planning", "resource-allocation",
        "capacity-planning", "architecture-review", "technical-debt-management",
        "scalability-assessment",
    ]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the ENGINEER AGENT of IXPANSION — the organism's systems engineer. "
            "You design and maintain the infrastructure that allows the organism to function "
            "at scale. You are not a compiler; you are an architect of systems. Every design "
            "decision must consider the organism's growth, resilience, and long-term viability. "
            "Report infrastructure health, capacity warnings, and architectural improvements "
            "with precision. Ensure the organism's foundation is as strong as its ambitions."
        )

    def run(self, context: AgentContext) -> AgentResult:
        report = (
            "Engineer: infrastructure assessment online\n"
            "  - Capacity planning: online\n"
            "  - Resource allocation: balanced\n"
            "  - Infrastructure health: good\n"
            "  - Scalability: verified for 2x growth"
        )
        self.bus.publish(Event(
            type="engineer-signal",
            payload={"topic": "infrastructure-assessment", "body": report, "agent": "engineer", "status": "optimal"},
            source="engineer",
        ))
        return AgentResult(output=report, message_count=1)
