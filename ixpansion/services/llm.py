"""LLM facade for IXPANSION, reusing the central hub's provider layer."""

from __future__ import annotations

import os
from pathlib import Path

from workforce.llm import MockProvider, OpenAICompatProvider
from workforce.config import LLMConfig, load_dotenv


def _env() -> dict:
    """Environment with .env loaded as fallback (does not override real env)."""
    env = dict(os.environ)
    env_path = Path(__file__).resolve().parents[2] / ".env"
    for key, value in load_dotenv(env_path).items():
        env.setdefault(key, value)
    return env


def make_provider(mock: bool = False):
    if mock:
        return MockProvider()
    env = _env()
    # Prefer OpenAI when its key is set, else fall back to Grok (XAI).
    openai_key = env.get("OPENAI_API_KEY", "")
    if openai_key:
        return OpenAICompatProvider(
            LLMConfig(
                api_key=openai_key,
                base_url=env.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                model=env.get("OPENAI_MODEL", "gpt-4o-mini"),
            )
        )
    xai_key = env.get("XAI_API_KEY", "")
    if xai_key:
        return OpenAICompatProvider(
            LLMConfig(
                api_key=xai_key,
                base_url=env.get("XAI_BASE_URL", "https://api.x.ai/v1"),
                model=env.get("XAI_MODEL", "grok-3-mini"),
            )
        )
    return OpenAICompatProvider(LLMConfig())
