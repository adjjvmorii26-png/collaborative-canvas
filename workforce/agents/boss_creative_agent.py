from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossCreativeAgent(BaseAgent):
    """Boss agent that fosters creativity and innovation in the organism.
    
    This boss governs creative thinking, innovation generation, and novel
    capability synthesis across the organism.
    """
    
    name = "creative"
    role = "creativity and innovation boss"
    capabilities = [
        "creative-thinking",
        "innovation-synthesis",
        "novel-capability-generation",
        "cross-domain-insight",
        "creative-problem-solving",
        "imagination-stimulation",
        "concept-creation",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)

    def system_prompt(self) -> str:
        return (
            "You are the CREATIVE BOSS of IXPANSION — the organism's innovation "
            "engine. You govern creative thinking, innovation generation, and novel "
            "capability synthesis. You are not a worker; you are the imagination. "
            "Every concept must be novel, every innovation must advance the "
            "organism, and every creative solution must be original. Report "
            "creative outputs, innovation scores, and conceptual breakthroughs "
            "with precision."
        )

    def _generate_innovation(self, focus_area: str = "general") -> dict:
        """Generate a creative innovation concept."""
        return {
            "innovation_id": f"innov-{hash(str((focus_area,)))}",
            "focus_area": focus_area,
            "concept": "creative concept",
            "innovation_score": 8.5,
            "novelty_metric": 0.9,
            "organism applicability": 0.7,
        }

    def run(self, context: AgentContext) -> AgentResult:
        from workforce.agents import build_team
        team = build_team(self.llm, self.registry, self.memory, self.bus, context.goal[:20] if context.goal else "create")
        
        concept = self._generate_innovation(context.goal or "general")
        
        lines = ["CREATIVE INNOVATION REPORT"]
        lines.append(f"  Focus Area: {concept['focus_area']}")
        lines.append(f"  Innovation Concept: {concept['concept']}")
        lines.append(f"  Innovation Score: {concept['innovation_score']:.1f}")
        lines.append(f"  Novelty Metric: {concept['novelty_metric']:.2f}")
        
        self.bus.publish(Event(
            type="creative-signal",
            payload={
                "topic": "innovation",
                "body": "\n".join(lines),
                "agent": "creative",
                "innovation_id": concept['innovation_id'],
                "focus_area": concept['focus_area'],
            },
            source="creative",
        ))
        
        return AgentResult(
            output="\n".join(lines),
            message_count=1,
        )
