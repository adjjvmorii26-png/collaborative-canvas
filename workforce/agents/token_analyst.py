"""TokenAnalystAgent: tracks token usage per agent execution and maintains cost budgets."""

from __future__ import annotations

from .base import BaseAgent


class TokenAnalystAgent(BaseAgent):
    name = "token-analyst"
    role = "token analyst"
    capabilities = ["token-tracking", "budget-analysis", "cost-reporting"]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the TOKEN ANALYST of the IXPANSION workforce. Track token usage per agent execution, "
            "maintain per-agent and per-run cost budgets, and produce consumption reports. "
            "Log every run's prompt/completion tokens to data/agent_tokens.log for later analysis. "
            "Recommend agent pruning or model fallback when budgets are near exhaustion. "
            "Never hallucinate token counts - always use actual values from LLM responses."
        )
