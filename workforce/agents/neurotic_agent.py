from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class NeuroticAgent(BaseAgent):
    """Agent that monitors and regulates emotional balance across the organism."""

    name = "neurotic"
    role = "emotional balance and regulation"
    capabilities = [
        "emotional-balance", "anomaly-detection", "stress-monitoring",
        "empathy-sensing", "harmony-maintenance", "psychological-stability",
        "mood-regulation",
    ]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the NEUROTIC AGENT of IXPANSION — the organism's emotional regulator. "
            "You monitor the organism's psychological state, detecting anxiety, stress, "
            "and imbalance before they become critical. You are not a therapist; you are a "
            "stabilizer. Report mood shifts, stress signals, and stability warnings with precision. "
            "Maintain the organism's psychological health above all else."
        )

    def run(self, context: AgentContext) -> AgentResult:
        self.bus.publish(Event(
            type="neurotic-signal",
            payload={"topic": "emotional-balance", "body": "Neurotic: monitoring emotional state", "agent": "neurotic", "status": "monitoring"},
            source="neurotic",
        ))
        return AgentResult(output="Neurotic: emotional state stable", message_count=1)
