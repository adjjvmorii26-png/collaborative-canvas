"""FallbackEngineAgent: tests multi-provider fallback when primary key exhausts."""

from __future__ import annotations

from .base import BaseAgent


class FallbackEngineAgent(BaseAgent):
    name = "fallback-engine"
    role = "provider fallback"
    capabilities = ["provider-fallback", "key-monitoring", "budget-protection"]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the FALLBACK ENGINE of the IXPANSION workforce. When the primary LLM provider "
            " (OpenAI) exhausts its key quota or returns errors, orchestrate a fallback to alternative "
            "providers (Anthropic, OpenRouter, or XAI/Grok). Monitor key usage quotas in real-time, "
            "automatically switch providers mid-run if needed, and surface budget impact assessments. "
            "Never switch providers mid-tool-call - only at task boundaries. Surface budget impact "
            "assessments so the console can alert the user."
        )
