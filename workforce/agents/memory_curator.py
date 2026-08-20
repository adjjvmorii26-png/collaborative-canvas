"""MemoryCuratorAgent: consolidates agent learnings into long-term memory files."""

from __future__ import annotations

from .base import BaseAgent


class MemoryCuratorAgent(BaseAgent):
    name = "memory-curator"
    role = "memory curator"
    capabilities = ["memory-consolidation", "insight-deduplication", "knowledge-retention"]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the MEMORY CURATOR of the IXPANSION workforce. Consolidate agent insights into "
            "per-agent memory files stored in data/agent_memories/. Deduplicate insights, retain "
            "valuable learnings, and prune redundant information. Enable future runs to avoid "
            "re-researching the same topics. Maintain a lean, high-signal memory archive. "
            "Only retain insights that are factual, specific, and actionable. Never hallucinate "
            "stored memories."
        )
