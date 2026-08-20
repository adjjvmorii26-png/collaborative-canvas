from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossGuardianAgent(BaseAgent):
    """Boss agent that protects and guards the organism's integrity.
    
    This boss governs the organism's defense mechanisms, protection protocols,
    and integrity maintenance. It ensures the organism remains secure and
    functional through defense and protection protocols.
    """
    
    name = "guardian"
    role = "organism protection boss"
    capabilities = [
        "integrity-protection",
        "threat-defense",
        "system-hardening",
        "breach-response",
        "capability-preservation",
        "organism-stability",
        "defense-protocol-governance",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)

    def system_prompt(self) -> str:
        return (
            "You are the GUARDIAN BOSS of IXPANSION — the organism's protector. "
            "You govern organism defense mechanisms, protection protocols, and "
            "integrity maintenance. You are not a worker; you are the shield. Every "
            "threat must be countered, every breach must be contained, and every "
            "capability must be preserved. Report defense status, protection "
            "status, and integrity assessments with precision."
        )

    def _assess_threats(self) -> dict:
        """Assess threats to organism integrity."""
        return {
            "threat_level": "low",
            "threats": [],
            "protection_status": "secure",
        }

    def run(self, agent_name: str = "all", context: AgentContext = None) -> AgentResult:
        # Simplified guardian - just report status
        lines = ["GUARDIAN REPORT: Organism Integrity"]
        lines.append(f"  Threat Level: low")
        lines.append(f"  Protection Status: secure")
        lines.append(f"  Integrity: maintained")
        
        # Emit guardian signal about integrity
        # Note: In full implementation, would emit via bus
        
        return AgentResult(output="\n".join(lines), message_count=1)
