from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossCollectorAgent(BaseAgent):
    """Boss agent that collects and aggregates information from all other agents.
    
    This boss governs the flow of information across the organism, collecting
    signals, metrics, and status updates from all subordinate agents and
    consolidating them into coherent reports for the organism's central nervous
    system.
    """
    
    name = "collector"
    role = "information collection and aggregation boss"
    capabilities = [
        "signal-collection",
        "multi-agent-coordination",
        "status-synthesis",
        "report-generation",
        "cross-agent-correlation",
        "information-flow-management",
        "central-nervous-system-governance",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)
        self._collected_signals = []
        self._report_history = []

    def system_prompt(self) -> str:
        return (
            "You are the COLLECTOR BOSS of IXPANSION — the organism's central "
            "nervous system governor. You collect and aggregate signals from all "
            "subordinate agents, synthesize their outputs into coherent reports, "
            "and manage the information flow throughout the organism. You are not "
            "a worker; you are the coordination hub. Every signal must be captured, "
            "every agent's output must be synthesized, and no information may be "
            "lost. Report collection status, synthesis quality, and flow integrity "
            "with precision."
        )

    def _collect_from_all_agents(self, team: dict) -> dict:
        """Collect status from all agents in the team."""
        collected = {}
        for agent_name, agent in team.items():
            # Get agent's current state
            collected[agent_name] = {
                "capabilities": agent.capabilities,
                "output": getattr(agent, '_last_output', 'no output yet'),
                "status": "active",
            }
        return collected

    def _synthesize_reports(self, collected: dict) -> str:
        """Synthesize all agent outputs into a coherent report."""
        lines = [f"COLLECTOR REPORT: {len(collected)} agents aggregated"]
        for name, data in collected.items():
            lines.append(f"  {name}: {len(data['capabilities'])} capabilities, status: {data['status']}")
        lines.append(f"  Total capabilities across organism: {sum(len(c) for c in collected.values())}")
        return "\n".join(lines)

    def run(self, context: AgentContext) -> AgentResult:
        # Collect from all agents in the workforce
        from workforce.agents import build_team
        team = build_team(self.llm, self.registry, self.memory, self.bus, context.goal[:20] if context.goal else "collect")
        
        collected = self._collect_from_all_agents(team)
        synthesis = self._synthesize_reports(collected)
        
        # Publish collector signal
        self.bus.publish(Event(
            type="collector-signal",
            payload={
                "topic": "information-synthesis",
                "body": synthesis,
                "agent": "collector",
                "agent_count": len(team),
                "total_capabilities": sum(len(c) for c in team.values()),
            },
            source="collector",
        ))
        
        return AgentResult(
            output=synthesis,
            message_count=1,
        )
