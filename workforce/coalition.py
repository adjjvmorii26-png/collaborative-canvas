"""Coalition: groups of agents vote on a decision."""

from __future__ import annotations

from collections import Counter

from .agents import AGENT_LOOKUP, AgentContext
from .models import Task


class Coalition:
    def __init__(self, members, llm, registry, memory, bus, run_id):
        self.members = members
        self.llm = llm
        self.registry = registry
        self.memory = memory
        self.bus = bus
        self.run_id = run_id

    def vote(self, question: str) -> dict:
        results = {}
        for name in self.members:
            cls = AGENT_LOOKUP.get(name)
            if not cls:
                continue
            agent = cls(self.llm, self.registry, self.memory, self.bus, f"{self.run_id}-{name}")
            out = agent.run(
                AgentContext(
                    goal=question,
                    task=Task(id="v", title="Vote", capability="vote", description=question),
                )
            ).output
            choice = out.strip().splitlines()[0][:60] if out.strip() else "abstain"
            results[name] = choice
        tally = Counter(results.values())
        winner = tally.most_common(1)[0][0] if tally else "none"
        return {"question": question, "votes": results, "winner": winner}
