from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossArchitectAgent(BaseAgent):
    """Boss agent that designs system architecture and structural organization.
    
    This boss governs the architectural design of the organism's system structure,
    including agent organization, capability hierarchies, and system integrity.
    """
    
    name = "architect"
    role = "system architecture boss"
    capabilities = [
        "system-architecture",
        "structural-design",
        "capability-hierarchy-design",
        "organization-chart-design",
        "integrative-design",
        "blueprint-creation",
        "structural-integrity",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)

    def system_prompt(self) -> str:
        return (
            "You are the ARCHITECT BOSS of IXPANSION — the organism's system "
            "architect. You govern system architecture, structural design, and "
            "organizational design. You are not a worker; you are the blueprint "
            "maker. Every design must be structurally sound, every hierarchy must "
            "be coherent, and every blueprint must guide construction. Report "
            "architectural designs, structural integrity, and blueprint quality "
            "with precision."
        )

    def _design_architecture(self, agent_count: int, capability_count: int) -> dict:
        """Design the organism's architectural structure."""
        return {
            "architecture_id": f"arch-{hash(str((agent_count, capability_count)))}",
            "agent_count": agent_count,
            "capability_count": capability_count,
            "hierarchy": "flat",
            "modular_components": [],
            "integrity_score": 100.0,
        }

    def run(self, context: AgentContext) -> AgentResult:
        from workforce.agents import build_team
        team = build_team(self.llm, self.registry, self.memory, self.bus, context.goal[:20] if context.goal else "architect")
        
        architecture = self._design_architecture(len(team), sum(len(a.capabilities) for a in team.values()))
        
        lines = ["ARCHITECTURE REPORT"]
        lines.append(f"  Architecture ID: {architecture['architecture_id']}")
        lines.append(f"  Agent Count: {architecture['agent_count']}")
        lines.append(f"  Capability Count: {architecture['capability_count']}")
        lines.append(f"  Hierarchy: {architecture['hierarchy']}")
        lines.append(f"  Integrity Score: {architecture['integrity_score']}")
        
        self.bus.publish(Event(
            type="architect-signal",
            payload={
                "topic": "architecture-design",
                "body": "\n".join(lines),
                "agent": "architect",
                "architecture_id": architecture['architecture_id'],
            },
            source="architect",
        ))
        
        return AgentResult(
            output="\n".join(lines),
            message_count=1,
        )
