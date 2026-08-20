from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossDistributorAgent(BaseAgent):
    """Boss agent that distributes tasks and resources to subordinate agents.
    
    This boss governs the allocation of tasks, capabilities, and resources across
    the organism, ensuring balanced workload distribution and optimal capability
    deployment for organism-wide goals.
    """
    
    name = "distributor"
    role = "task and resource distribution boss"
    capabilities = [
        "task-allocation",
        "resource-distribution",
        "workload-balancing",
        "capability-mapping",
        "goal-decomposition",
        "agent-assignment",
        "system-optimization",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)
        self._task_queue = []
        self._agent_loads = {}
        self._allocation_history = []

    def system_prompt(self) -> str:
        return (
            "You are the DISTRIBUTOR BOSS of IXPANSION — the organism's resource "
            "allocator. You govern the distribution of tasks, capabilities, and "
            "resources across all subordinate agents. You are not a worker; you are "
            "the strategic allocator. Every task must be matched to the right agent, "
            "every resource must be optimally deployed, and no capability may go "
            "unused. Report allocation decisions, workload balances, and system "
            "efficiency with precision."
        )

    def _calculate_optimal_allocation(self, goal: str, team: dict) -> dict:
        """Calculate optimal agent assignments for a goal."""
        allocation = {}
        # Simple allocation: distribute based on capabilities
        for agent_name, agent in team.items():
            matching_caps = [c for c in agent.capabilities if c in goal.lower().split()]
            allocation[agent_name] = {
                "matching_capabilities": matching_caps,
                "workload": len(matching_caps),
            }
        return allocation

    def run(self, context: AgentContext) -> AgentResult:
        from workforce.agents import build_team
        team = build_team(self.llm, self.registry, self.memory, self.bus, context.goal[:20] if context.goal else "distribute")
        
        goal = context.goal or "organism optimization"
        allocation = self._calculate_optimal_allocation(goal, team)
        
        # Build distribution report
        lines = [f"DISTRIBUTION REPORT for goal: {goal}"]
        total_matches = 0
        for agent_name, data in allocation.items():
            lines.append(f"  {agent_name}: {', '.join(data['matching_capabilities'] or ['none'])} - workload: {data['workload']}")
            total_matches += data['workload']
        lines.append(f"  Total task matches: {total_matches} across {len(allocation)} agents")
        
        # Publish distributor signal
        self.bus.publish(Event(
            type="distributor-signal",
            payload={
                "topic": "task-allocation",
                "body": "\n".join(lines),
                "agent": "distributor",
                "allocation_details": allocation,
            },
            source="distributor",
        ))
        
        return AgentResult(
            output="\n".join(lines),
            message_count=1,
        )
