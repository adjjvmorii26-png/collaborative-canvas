"""SynchronicityAgent - IXPANSION cross-system pattern detector.

This agent correlates health, finance, stress, and pulse signals into
actionable patterns and income opportunities.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


try:
    from ixpansion.core.finance_agent import FinanceAgent
    from ixpansion.core.health_monitor_agent import OrganHealthMonitor
    from ixpansion.core.organism_pulse_coordinator import OrganismPulseCoordinator
    from ixpansion.core.stress_test_agent import OrganismStressTest
except Exception:  # pragma: no cover - fallback for partial environments
    FinanceAgent = None
    OrganHealthMonitor = None
    OrganismPulseCoordinator = None
    OrganismStressTest = None


@dataclass
class SynchronicityPattern:
    kind: str
    strength: float
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)


class SynchronicityAgent:
    """Detects meaningful synchronicities across the IXPANSION organism."""

    HEALTH_FINANCE_MAP = {
        "cardiovascular": "cashflow",
        "neurological": "revenue",
        "digestive": "allocation",
        "respiratory": "compliance",
        "immune": "risk",
        "metabolic": "wealth",
        "detoxification": "investment",
    }
    TIME_WINDOW_HOURS = 24

    INCOME_OPPORTUNITIES = [
        "Advisory service: explain health-finance resonance to users",
        "Subscription: automated organism wellness and resilience reports",
        "Content product: publish the highest-signal insights from the canvas",
        "Domain service: package alexalex.info content and analysis as a product",
        "Automation service: sell the pulse-based scheduling and cleanup layer",
        "Consulting: offer stress-to-recovery workflows as continuity planning",
    ]

    def __init__(self, console_url: str = "http://127.0.0.1:8890") -> None:
        self.console_url = console_url
        self.name = "SynchronicityAgent"
        self.version = "1.0.0"
        self.history: List[Dict[str, Any]] = []

    def collect_snapshot(
        self,
        health: Optional[Dict[str, Any]] = None,
        finance: Optional[Dict[str, Any]] = None,
        stress: Optional[List[Dict[str, Any]]] = None,
        pulse: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Collect a system snapshot from local agents or supplied state."""

        if health is None and OrganHealthMonitor is not None:
            health = OrganHealthMonitor(self.console_url).fetch_organ_scores()
        if finance is None and FinanceAgent is not None:
            finance = FinanceAgent(self.console_url)._fetch_finance_health()
        if stress is None and OrganismStressTest is not None:
            stress = list(OrganismStressTest(self.console_url).stress_history)
        if pulse is None and OrganismPulseCoordinator is not None:
            coordinator = OrganismPulseCoordinator(self.console_url)
            pulse = coordinator.current_pulse or {
                "id": "idle",
                "type": "idle",
                "intensity": 0.0,
                "timestamp": datetime.now().isoformat(),
                "status": "inactive",
            }

        return {
            "health": health or {},
            "finance": finance or {},
            "stress": stress or [],
            "pulse": pulse or {},
            "captured_at": datetime.now().isoformat(),
        }

    def detect_synchronicity(self, snapshot: Optional[Dict[str, Any]] = None) -> List[SynchronicityPattern]:
        """Detect useful cross-system patterns."""

        if snapshot is None:
            snapshot = self.collect_snapshot()

        health = snapshot["health"]
        finance = snapshot["finance"]
        stress = snapshot["stress"]
        pulse = snapshot["pulse"]

        patterns: List[SynchronicityPattern] = []

        # Health / finance alignment.
        matches = []
        for organ, finance_key in self.HEALTH_FINANCE_MAP.items():
            if organ in health and finance_key in finance:
                health_score = health[organ] if isinstance(health[organ], (int, float)) else health[organ].get("score", 0)
                finance_score = finance[finance_key] if isinstance(finance[finance_key], (int, float)) else finance[finance_key].get("score", 0)
                alignment = max(0.0, 1.0 - abs(float(health_score) - float(finance_score)) / 30.0)
                matches.append((organ, finance_key, alignment, health_score, finance_score))

        if matches:
            avg_alignment = sum(m[2] for m in matches) / len(matches)
            patterns.append(
                SynchronicityPattern(
                    kind="health_finance_alignment",
                    strength=avg_alignment,
                    description=f"{len(matches)} organ-finance pairings are aligned",
                    evidence={
                        "pairs": [
                            {
                                "organ": organ,
                                "finance": finance_key,
                                "alignment": round(alignment, 3),
                                "health_score": health_score,
                                "finance_score": finance_score,
                            }
                            for organ, finance_key, alignment, health_score, finance_score in matches
                        ]
                    },
                )
            )

        # Stress / pulse resonance.
        if stress and pulse:
            pulse_intensity = float(pulse.get("intensity", 0.0) or 0.0)
            stressed_organs = {item.get("affected_organ", "") for item in stress if item.get("status") in {"active", "recovered"}}
            if stressed_organs:
                resonance = min(1.0, (pulse_intensity + len(stressed_organs) / 10.0) / 2.0)
                patterns.append(
                    SynchronicityPattern(
                        kind="stress_pulse_resonance",
                        strength=resonance,
                        description="Stress history and pulse activity are interacting",
                        evidence={
                            "pulse_id": pulse.get("id", "unknown"),
                            "pulse_intensity": pulse_intensity,
                            "stressed_organs": sorted(stressed_organs),
                        },
                    )
                )

            pulse_timestamp = pulse.get("timestamp")
            if pulse_timestamp:
                active_stresses = []
                pulse_events = pulse.get("events") or [pulse]
                for stress_item in stress:
                    stress_ts = stress_item.get("timestamp")
                    if not stress_ts:
                        continue
                    for pulse_event in pulse_events:
                        pulse_event_ts = pulse_event.get("timestamp")
                        if not pulse_event_ts:
                            continue
                        try:
                            stress_dt = datetime.fromisoformat(stress_ts)
                            pulse_dt = datetime.fromisoformat(pulse_event_ts)
                        except ValueError:
                            continue
                        if abs((stress_dt - pulse_dt).total_seconds()) <= self.TIME_WINDOW_HOURS * 3600:
                            active_stresses.append(stress_item.get("type", "unknown"))
                            break
                if active_stresses:
                    patterns.append(
                        SynchronicityPattern(
                            kind="stress_pulse_window",
                            strength=min(1.0, len(active_stresses) / max(len(stress), 1)),
                            description="Recent stress events fall inside the current pulse window",
                            evidence={
                                "pulse_id": pulse.get("id", "unknown"),
                                "stresses": active_stresses[:10],
                            },
                        )
                    )

        # Cluster stress by organ and severity.
        clusters = self._cluster_stress_events(stress)
        if clusters:
            cluster_strength = min(1.0, len(clusters) / 5.0)
            patterns.append(
                SynchronicityPattern(
                    kind="stress_cluster",
                    strength=cluster_strength,
                    description=f"{len(clusters)} stress clusters detected",
                    evidence={"clusters": clusters},
                )
            )

        # Simple signal balance score.
        overall_health = self._numeric_average(health)
        overall_finance = self._numeric_average(finance)
        if overall_health and overall_finance:
            balance = max(0.0, 1.0 - abs(overall_health - overall_finance) / 50.0)
            patterns.append(
                SynchronicityPattern(
                    kind="signal_balance",
                    strength=balance,
                    description="Overall health and finance signal balance",
                    evidence={
                        "health_average": round(overall_health, 2),
                        "finance_average": round(overall_finance, 2),
                    },
                )
            )

        patterns.sort(key=lambda item: item.strength, reverse=True)
        self.history.append(
            {
                "captured_at": snapshot["captured_at"],
                "patterns": [pattern.__dict__ for pattern in patterns],
            }
        )
        self.history = self.history[-50:]
        return patterns

    def income_opportunities(self, patterns: Optional[List[SynchronicityPattern]] = None) -> List[str]:
        """Map patterns into income opportunities."""

        if patterns is None:
            patterns = self.detect_synchronicity()

        opportunities = list(self.INCOME_OPPORTUNITIES)

        if patterns:
            strongest = patterns[0]
            if strongest.kind == "health_finance_alignment":
                opportunities.append("Bundle health and finance reporting into a paid dashboard")
            if strongest.kind == "stress_pulse_resonance":
                opportunities.append("Sell continuity planning based on stress/pulse resilience")
            if strongest.kind == "signal_balance":
                opportunities.append("Create a subscription for holistic organism balance reports")

        return opportunities

    def _numeric_average(self, data: Dict[str, Any]) -> float:
        values: List[float] = []
        for value in data.values():
            if isinstance(value, (int, float)):
                values.append(float(value))
            elif isinstance(value, dict) and "score" in value and isinstance(value["score"], (int, float)):
                values.append(float(value["score"]))
        return sum(values) / len(values) if values else 0.0

    def _cluster_stress_events(self, stress: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        clusters: List[List[Dict[str, Any]]] = []
        by_organ: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for item in stress:
            by_organ[item.get("affected_organ", "unknown")].append(item)

        for organ, items in by_organ.items():
            if len(items) >= 2:
                clusters.append(items)

        # Cluster similar severities across different organs.
        sorted_stress = sorted(stress, key=lambda item: item.get("severity", 0), reverse=True)
        rolling: List[Dict[str, Any]] = []
        for item in sorted_stress:
            if not rolling:
                rolling.append(item)
                continue
            if abs(float(rolling[-1].get("severity", 0)) - float(item.get("severity", 0))) <= 5:
                rolling.append(item)
            else:
                if len(rolling) >= 2:
                    clusters.append(list(rolling))
                rolling = [item]
        if len(rolling) >= 2:
            clusters.append(list(rolling))

        return clusters

    def generate_report(self, snapshot: Optional[Dict[str, Any]] = None) -> str:
        patterns = self.detect_synchronicity(snapshot)
        opportunities = self.income_opportunities(patterns)
        overall_score = sum(p.strength for p in patterns) / len(patterns) * 100 if patterns else 0.0

        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("IXPANSION SYNCHRONICITY REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Agent: {self.name} v{self.version}")
        lines.append(f"Captured: {datetime.now().isoformat()}")
        lines.append(f"Overall synchronicity score: {overall_score:.1f}/100")
        lines.append("")
        lines.append("Top patterns:")
        if patterns:
            for pattern in patterns[:5]:
                lines.append(f"- {pattern.kind}: {pattern.strength:.2f} - {pattern.description}")
        else:
            lines.append("- No significant patterns detected")
        lines.append("")
        lines.append("Income opportunities:")
        for item in opportunities[:6]:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("History entries: " + str(len(self.history)))
        return "\n".join(lines)

    def run_cycle(self, snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        patterns = self.detect_synchronicity(snapshot)
        opportunities = self.income_opportunities(patterns)
        return {
            "patterns": [pattern.__dict__ for pattern in patterns],
            "opportunities": opportunities,
            "report": self.generate_report(snapshot),
        }


if __name__ == "__main__":
    agent = SynchronicityAgent()
    result = agent.run_cycle()
    print(result["report"])
