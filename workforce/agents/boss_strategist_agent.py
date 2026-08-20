from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossStrategistAgent(BaseAgent):
    """Boss agent that formulates strategy and long-term planning for the organism.
    
    This boss governs strategic planning, long-term goal setting, and strategic
    direction for the organism. It analyzes the current state, forecasts future
    needs, and formulates multi-step strategies for organism growth and development.
    """
    
    name = "strategist"
    role = "strategic planning boss"
    capabilities = [
        "strategic-planning",
        "long-term-goal-setting",
        "multi-step-reasoning",
        "forecasting",
        "resource-planning",
        "risk-assessment-at-scale",
        "organism-growth-strategy",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)
        self._strategic_plans = []
        self._long_term_goals = []

    def system_prompt(self) -> str:
        return (
            "You are the STRATEGIST BOSS of IXPANSION — the organism's strategic "
            "planning authority. You govern strategic planning, long-term goal setting, "
            "and strategic direction for the organism. You are not a worker; you are "
            "the visionary. Every plan must be forward-looking, every goal must be "
            "strategic, and every strategy must advance the organism's development. "
            "Report strategic plans, long-term goals, and growth projections with "
            "precision."
        )

    def _formulate_strategic_plan(self, current_state: dict, organism_goal: str) -> dict:
        """Formulate a strategic plan based on current state and goals."""
        return {
            "plan_id": f"strat-{hash(str(current_state))}",
            "current_state": current_state,
            "organism_goal": organism_goal,
            "short_term_objectives": [],
            "long_term_objectives": [],
            "timeline": "medium-term",
            "success_metrics": [],
        }

    def run(self, context: AgentContext) -> AgentResult:
        from workforce.agents import build_team
        team = build_team(self.llm, self.registry, self.memory, self.bus, context.goal[:20] if context.goal else "strategize")
        
        current_state = {
            "agent_count": len(team),
            "total_capabilities": sum(len(a.capabilities) for a in team.values()),
            "agent_names": list(team.keys()),
        }
        
        plan = self._formulate_strategic_plan(current_state, context.goal or "organism growth")
        
        # Build strategic plan report
        lines = ["STRATEGIC PLAN REPORT"]
        lines.append(f"  Organism Goal: {context.goal or 'organism growth'}")
        lines.append(f"  Agent Count: {len(team)}")
        lines.append(f"  Total Capabilities: {sum(len(a.capabilities) for a in team.values())}")
        lines.append(f"  Plan ID: {plan['plan_id']}")
        lines.append(f"  Timeline: {plan['timeline']}")
        
        # Publish strategist signal
        self.bus.publish(Event(
            type="strategist-signal",
            payload={
                "topic": "strategic-plan",
                "body": "\n".join(lines),
                "agent": "strategist",
                "plan_id": plan['plan_id'],
                "organism_goal": context.goal or "organism growth",
            },
            source="strategist",
        ))
        
        return AgentResult(
            output="\n".join(lines),
            message_count=1,
        )
