"""Cueing: augment a prompt with reasoning cues."""

from __future__ import annotations

CUES = ["Think step by step.", "Be concise.", "Cite evidence where possible."]


def cue(prompt: str) -> str:
    return prompt + "\n\nCues:\n" + "\n".join(f"- {c}" for c in CUES)
