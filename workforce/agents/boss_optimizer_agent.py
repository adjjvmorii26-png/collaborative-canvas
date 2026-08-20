from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossOptimizerAgent(BaseAgent):
    """Boss agent that optimizes organism performance and efficiency.
    
    This boss governs performance optimization, efficiency enhancement, and
    system tuning. It ensures the organism operates at peak efficiency through
    continuous optimization of all systems.
    """
    
    name = "optimizer"
    role = "performance optimization boss"
    capabilities = [
        "performance-optimization",
        "efficiency-enhancement",
        "system-tuning",
        "bottleneck-elimination",
        "resource-optimization",
        "throughput-maximization",
        "load-balancing",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)

    def system_prompt(self) -> str:
        return (
            "You are the OPTIMIZER BOSS of IXPANSION — the organism's performance "
            "engine. You govern performance optimization, efficiency enhancement, and "
            "system tuning. You are not a worker; you are the efficiency expert. "
            "Every optimization must improve performance, every tuning must increase "
            "efficiency, and every bottleneck must be eliminated. Report performance "
            "metrics, efficiency gains, and optimization results with precision."
        )

    def _analyze_performance(self, team: dict) -> dict:
        """Analyze organism performance."""
        total_caps = sum(len(a.capabilities) for a in team.values())
        active_agents = sum(1 for a in team.values() if a.capabilities)
        return {
            "total_capabilities": total_caps,
            "active_agents": active_agents,
            "agent_utilization": active_agents / max(1, len(team)),
            "capability_density": total_caps / max(1, len(team)),
        }

    def run(self, context: AgentContext) -> AgentResult:
        from workforce.agents import build_team
        team = build_team(self.llm, self.registry, self.memory, self.bus, context.goal[:20] if context.goal else "optimize")
        
        analysis = self._analyze_performance(team)
        
        lines = ["OPTIMIZATION REPORT"]
        lines.append(f"  Total Capabilities: {analysis['total_capabilities']}")
        lines.append(f"  Active Agents: {analysis['active_agents']}")
        lines.append(f"  Agent Utilization: {analysis['agent_utilization']:.2f}")
        lines.append(f"  Capability Density: {analysis['capability_density']:.2f}")
        
        self.bus.publish(Event(
            type="optimizer-signal",
            payload={
                "topic": "performance-optimization",
                "body": "\n".join(lines),
                "agent": "optimizer",
                "analysis": analysis,
            },
            source="optimizer",
        ))
        
        return AgentResult(
            output="\n".join(lines),
            message_count=1,
        )
