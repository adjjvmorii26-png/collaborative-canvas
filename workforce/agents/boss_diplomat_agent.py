from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossDiplomatAgent(BaseAgent):
    """Boss agent that governs inter-organism communication and diplomacy.
    
    This boss governs diplomatic relations between different organism instances,
    inter-organism communication, and cooperative relationships.
    """
    
    name = "diplomat"
    role = "diplomacy and inter-organism relations boss"
    capabilities = [
        "inter-organism-communication",
        "diplomatic-negotiation",
        "treaty-negotiation",
        "cooperative-framework-governance",
        "relations-management",
        "conflict-resolution-between-organisms",
        "diplomatic-protocol-governance",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)

    def system_prompt(self) -> str:
        return (
            "You are the DIPLOMAT BOSS of IXPANSION — the organism's diplomacy "
            "and inter-organism relations governor. You govern diplomatic relations "
            "between different organism instances, inter-organism communication, "
            "and cooperative relationships. You are not a worker; you are the "
            "diplomat. Every relationship must be nurtured, every treaty must be "
            "fair, and every conflict must be resolved diplomatically. Report "
            "diplomatic status, treaty status, and relationship quality with "
            "precision."
        )

    def _assess_diplomatic_status(self) -> dict:
        """Assess diplomatic status."""
        return {
            "diplomatic_status": "active",
            "active_treaties": 0,
            "open_communication_channels": 0,
            "conflict_resolution_status": "none",
        }

    def run(self, context: AgentContext) -> AgentResult:
        # Simplified diplomat - just report status
        status = self._assess_diplomatic_status()
        
        lines = ["DIPLOMAT REPORT: Inter-Organism Relations"]
        lines.append(f"  Diplomatic Status: {status['diplomatic_status']}")
        lines.append(f"  Active Treaties: {status['active_treaties']}")
        lines.append(f"  Communication Channels: {status['open_communication_channels']}")
        lines.append(f"  Conflict Resolution: {status['conflict_resolution_status']}")
        
        self.bus.publish(Event(
            type="diplomat-signal",
            payload={
                "topic": "diplomatic-status",
                "body": "\n".join(lines),
                "agent": "diplomat",
                "status": status['diplomatic_status'],
            },
            source="diplomat",
        ))
        
        return AgentResult(output="\n".join(lines), message_count=1)
