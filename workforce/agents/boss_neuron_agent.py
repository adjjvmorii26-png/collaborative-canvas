from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossNeuronAgent(BaseAgent):
    """Boss agent that governs neural and cognitive orchestration.
    
    This boss governs neural cognitive functions, thought processing, and
    cognitive orchestration across the organism's agent network.
    """
    
    name = "neuron"
    role = "neural cognitive orchestration boss"
    capabilities = [
        "cognitive-orchestration",
        "thought-processing",
        "neural-signal-integration",
        "mental-model-governance",
        "consciousness-monitoring",
        "synaptic-connection-management",
        "neural-pathway-optimization",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)

    def system_prompt(self) -> str:
        return (
            "You are the NEURON BOSS of IXPANSION — the organism's cognitive "
            "orchestration governor. You govern neural cognitive functions, thought "
            "processing, and cognitive orchestration across the organism's agent "
            "network. You are not a worker; you are the mind. Every thought must "
            "be processed, every cognitive function must be orchestrated, and every "
            "neural pathway must be optimized. Report cognitive function, neural "
            "integration, and mental clarity with precision."
        )

    def _cognitive_orchestration(self) -> dict:
        """Orchestrate cognitive functions."""
        return {
            "cognitive_state": "active",
            "thought_flow": "uninterrupted",
            "neural_integration": 0.9,
            "mental_clarity": "clear",
        }

    def run(self, context: AgentContext) -> AgentResult:
        from workforce.agents import build_team
        team = build_team(self.llm, self.registry, self.memory, self.bus, context.goal[:20] if context.goal else "neuronate")
        
        cognition = self._cognitive_orchestration()
        
        lines = ["NEURON REPORT: Cognitive Orchestration"]
        lines.append(f"  Cognitive State: {cognition['cognitive_state']}")
        lines.append(f"  Thought Flow: {cognition['thought_flow']}")
        lines.append(f"  Neural Integration: {cognition['neural_integration']:.2f}")
        lines.append(f"  Mental Clarity: {cognition['mental_clarity']}")
        
        self.bus.publish(Event(
            type="neuron-signal",
            payload={
                "topic": "cognitive-orchestration",
                "body": "\n".join(lines),
                "agent": "neuron",
                "neural_integration": cognition['neural_integration'],
            },
            source="neuron",
        ))
        
        return AgentResult(
            output="\n".join(lines),
            message_count=1,
        )
