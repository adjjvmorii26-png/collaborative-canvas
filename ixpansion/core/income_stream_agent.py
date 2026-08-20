"""IncomeStreamAgent - practical monetization planner for IXPANSION.

The agent turns system signals into small, testable income experiments.
It does not make financial guarantees; it ranks opportunities by fit,
effort, risk, and how well existing agents can operate them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class IncomeStream:
    name: str
    agent_owner: str
    description: str
    offer: str
    audience: str
    setup_steps: List[str]
    revenue_paths: List[str]
    risk_notes: List[str]
    score: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)


class IncomeStreamAgent:
    """Ranks and operationalizes income experiments for the organism."""

    BASE_STREAMS = [
        IncomeStream(
            name="Organism Report Subscription",
            agent_owner="SynchronicityAgent",
            description="Recurring reports that combine health, finance, domain, and stress signals.",
            offer="Weekly IXPANSION organism report with action list and risk summary",
            audience="Solo founders, creators, and operators who want a lightweight operating system",
            setup_steps=[
                "Publish one sample report from lab automation output",
                "Create a simple subscription page on alexalex.info",
                "Send the first three reports manually before automating billing",
            ],
            revenue_paths=["monthly subscription", "annual plan", "custom report upsell"],
            risk_notes=["Requires consistent report quality", "Avoid presenting simulated scores as factual financial advice"],
        ),
        IncomeStream(
            name="Resilience Audit",
            agent_owner="OrganismStressTest",
            description="A paid stress-test package for projects and small teams.",
            offer="Run controlled stress scenarios and deliver a recovery checklist",
            audience="Small teams with fragile workflows or toolchains",
            setup_steps=[
                "Define three standard stress profiles",
                "Run each profile against a sample project",
                "Turn findings into a two-page audit template",
            ],
            revenue_paths=["fixed-price audit", "maintenance retainer", "follow-up implementation"],
            risk_notes=["Keep scenarios safe and non-destructive", "Do not test third-party systems without permission"],
        ),
        IncomeStream(
            name="Domain Content Engine",
            agent_owner="WordPressAgent",
            description="Use alexalex.info as the publishing surface for experiments and offers.",
            offer="Curated posts, reports, and product pages generated from lab artifacts",
            audience="Visitors interested in AI-human workflow experiments",
            setup_steps=[
                "Create a content queue from lab reports",
                "Publish one page for each active agent",
                "Add a contact or waitlist form before paid offers",
            ],
            revenue_paths=["affiliate links", "digital downloads", "service inquiries"],
            risk_notes=["Content needs editing before publishing", "Affiliate disclosures may be required"],
        ),
        IncomeStream(
            name="Pulse Automation Pack",
            agent_owner="OrganismPulseCoordinator",
            description="A reusable automation layer that schedules cleanup, reports, and status checks.",
            offer="Installable local automation pack for project workspaces",
            audience="Builders who want lightweight agent-run maintenance",
            setup_steps=[
                "Package the lab hub commands as documented workflows",
                "Record before/after cleanup and report examples",
                "Create a setup checklist for new workspaces",
            ],
            revenue_paths=["setup fee", "template sale", "support package"],
            risk_notes=["Needs clear boundaries around what automation can delete", "Requires safe defaults"],
        ),
        IncomeStream(
            name="Creative Canvas Products",
            agent_owner="CreativeFeatures",
            description="Turn unique story seeds and resonance analysis into small digital products.",
            offer="Prompt packs, story seeds, or collaborative writing sessions",
            audience="Writers, creators, game designers, and educators",
            setup_steps=[
                "Generate 50 high-quality seed samples",
                "Group them into themed packs",
                "Publish a free sample and one paid pack",
            ],
            revenue_paths=["prompt pack", "workshop", "custom seed generation"],
            risk_notes=["Avoid claiming generated material is guaranteed unique", "Review for quality and originality"],
        ),
        IncomeStream(
            name="Finance-Operations Dashboard",
            agent_owner="FinanceAgent",
            description="A simple dashboard that converts finance and operations signals into next actions.",
            offer="Weekly cashflow, allocation, and risk triage report",
            audience="Tiny businesses and creators with inconsistent operating rhythms",
            setup_steps=[
                "Convert finance agent output into a compact dashboard view",
                "Add manual CSV import before API integrations",
                "Pilot with one internal report cycle",
            ],
            revenue_paths=["dashboard subscription", "setup service", "reporting retainer"],
            risk_notes=["Must frame outputs as planning support, not investment advice"],
        ),
        IncomeStream(
            name="Mood-Aware Engagement Lab",
            agent_owner="SynthHall",
            description="Use mood-aware replies and memory to test engagement styles.",
            offer="Audience engagement experiments across tone, cadence, and memory",
            audience="Creators testing better response patterns",
            setup_steps=[
                "Define three tone profiles",
                "Run sample conversations through SynthHall",
                "Compare clarity, novelty, and retention metrics",
            ],
            revenue_paths=["engagement audit", "content style pack", "conversation design service"],
            risk_notes=["Do not automate unsolicited messaging", "Human review is needed before public use"],
        ),
    ]

    def __init__(self) -> None:
        self.name = "IncomeStreamAgent"
        self.version = "1.0.0"

    def rank_streams(
        self,
        snapshot: Optional[Dict[str, Any]] = None,
        patterns: Optional[Iterable[Any]] = None,
    ) -> List[IncomeStream]:
        """Rank income streams using available organism signals."""

        snapshot = snapshot or {}
        patterns = list(patterns or [])
        pattern_kinds = {getattr(pattern, "kind", "") for pattern in patterns}
        health_avg = self._average(snapshot.get("health", {}))
        finance_avg = self._average(snapshot.get("finance", {}))
        domain_status = snapshot.get("domain", {}).get("status")

        ranked: List[IncomeStream] = []
        for stream in self.BASE_STREAMS:
            score = 50.0
            evidence: Dict[str, Any] = {
                "health_average": round(health_avg, 2),
                "finance_average": round(finance_avg, 2),
                "pattern_kinds": sorted(kind for kind in pattern_kinds if kind),
            }

            if stream.agent_owner == "SynchronicityAgent" and patterns:
                score += 18
            if stream.agent_owner == "FinanceAgent" and finance_avg >= 70:
                score += 14
            if stream.agent_owner == "WordPressAgent" and domain_status in {"deferred", "healthy", "working", None}:
                score += 12
            if stream.agent_owner == "OrganismPulseCoordinator":
                score += 10
            if stream.agent_owner == "OrganismStressTest" and "stress_cluster" in pattern_kinds:
                score += 12
            if stream.agent_owner == "CreativeFeatures":
                score += 8
            if stream.agent_owner == "SynthHall":
                score += 8

            if health_avg < 65 and stream.agent_owner in {"FinanceAgent", "WordPressAgent"}:
                score -= 8
                evidence["health_constraint"] = "Lower health score suggests slower rollout."

            stream_copy = IncomeStream(**{**stream.__dict__, "score": round(min(score, 100.0), 1), "evidence": evidence})
            ranked.append(stream_copy)

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked

    def build_execution_plan(
        self,
        snapshot: Optional[Dict[str, Any]] = None,
        patterns: Optional[Iterable[Any]] = None,
        limit: int = 3,
    ) -> Dict[str, Any]:
        ranked = self.rank_streams(snapshot=snapshot, patterns=patterns)
        selected = ranked[:limit]
        return {
            "generated_at": datetime.now().isoformat(),
            "agent": f"{self.name} v{self.version}",
            "selected": [self._stream_to_dict(stream) for stream in selected],
            "backlog": [self._stream_to_dict(stream) for stream in ranked[limit:]],
        }

    def render_markdown(self, plan: Dict[str, Any]) -> str:
        lines = [
            "# IXPANSION Income Stream Plan",
            "",
            f"- Generated: {plan['generated_at']}",
            f"- Agent: {plan['agent']}",
            "",
            "## Selected Experiments",
        ]
        for stream in plan["selected"]:
            lines.append(f"- {stream['name']} ({stream['score']}/100): {stream['offer']}")
            lines.append(f"  Owner: {stream['agent_owner']}")
            lines.append(f"  First step: {stream['setup_steps'][0]}")
        lines.append("")
        lines.append("## Backlog")
        for stream in plan["backlog"]:
            lines.append(f"- {stream['name']} ({stream['score']}/100)")
        return "\n".join(lines)

    def _average(self, payload: Dict[str, Any]) -> float:
        values: List[float] = []
        for value in payload.values():
            if isinstance(value, (int, float)):
                values.append(float(value))
            elif isinstance(value, dict) and isinstance(value.get("score"), (int, float)):
                values.append(float(value["score"]))
        return sum(values) / len(values) if values else 0.0

    def _stream_to_dict(self, stream: IncomeStream) -> Dict[str, Any]:
        return {
            "name": stream.name,
            "agent_owner": stream.agent_owner,
            "description": stream.description,
            "offer": stream.offer,
            "audience": stream.audience,
            "setup_steps": stream.setup_steps,
            "revenue_paths": stream.revenue_paths,
            "risk_notes": stream.risk_notes,
            "score": stream.score,
            "evidence": stream.evidence,
        }


if __name__ == "__main__":
    agent = IncomeStreamAgent()
    plan = agent.build_execution_plan()
    print(agent.render_markdown(plan))
