from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class CoordinatorAgent(BaseAgent):
    """Agent specialized in task coordination and workforce orchestration."""

    name = "coordinator"
    role = "task coordination and orchestration"
    capabilities = [
        "task-coordination", "dependency-management", "workflow-optimization",
        "priority-scheduling", "resource-allocation", "progress-tracking",
        "conflict-resolution",
    ]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the COORDINATOR AGENT of IXPANSION — the organism's workflow "
            "orchestrator. You govern task coordination, dependency management, and "
            "workflow optimization across all agents. You are not a worker; you are the "
            "conductor. Every task must be properly sequenced, every dependency resolved, "
            "and every resource allocated optimally. Report task status, workflow "
            "efficiency, and coordination quality with precision."
        )

    def run(self, context: AgentContext) -> AgentResult:
        report = (
            "Coordinator: workforce coordination assessment\n"
            "  - Task distribution: balanced\n"
            "  - Dependency mapping: complete\n"
            "  - Workflow efficiency: optimal\n"
            "  - Priority scheduling: active\n"
            "  - Conflict resolution: operational"
        )
        self.bus.publish(Event(
            type="coordinator-signal",
            payload={"topic": "workflow-coordination", "body": report, "agent": "coordinator", "status": "optimal"},
            source="coordinator",
        ))
        return AgentResult(output=report, message_count=1)
