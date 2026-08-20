"""Governance: charter-based voting with thresholds."""

from __future__ import annotations

from .coalition import Coalition


class Governance:
    def __init__(self, members, threshold, llm, registry, memory, bus, run_id):
        self.coalition = Coalition(members, llm, registry, memory, bus, run_id)
        self.threshold = threshold

    def decide(self, question):
        v = self.coalition.vote(question)
        votes = list(v["votes"].values())
        if not votes:
            return {"passed": False, "reason": "no votes"}
        support = sum(1 for x in votes if x == v["winner"]) / len(votes)
        return {"passed": support >= self.threshold, "support": support, "winner": v["winner"]}
