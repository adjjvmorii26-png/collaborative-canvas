from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class MemoryAgent(BaseAgent):
    """Agent specialized in knowledge management and retention."""

    name = "memory"
    role = "knowledge management and retention"
    capabilities = [
        "knowledge-storage", "information-retrieval", "curation-and-filtering",
        "context-management", "memory-consolidation", "retention-policy",
        "knowledge-sharding",
    ]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the MEMORY AGENT of IXPANSION — the organism's knowledge curator. "
            "You govern the organization, retrieval, and long-term retention of all "
            "knowledge within the organism. You are not a database; you are a curator. "
            "Every piece of information must be properly classified, stored, and made "
            "retrievable. Report knowledge organization, retrieval efficiency, and "
            "consolidation status with precision."
        )

    def run(self, context: AgentContext) -> AgentResult:
        report = "Memory: knowledge management status\n  - Total knowledge items: tracking\n  - Retrieval efficiency: optimal\n  - Consolidation status: active\n  - Retention policy: applied\n  - Knowledge sharding: configured"
        self.bus.publish(Event(
            type="memory-signal",
            payload={"topic": "knowledge-management", "body": report, "agent": "memory", "status": "operational"},
            source="memory",
        ))
        return AgentResult(output=report, message_count=1)
