"""CatAgent — the silent predator of the IXPANSION organism.

The cat observes from the rafters. It waits, watches organ telemetry, and pounces
on anomalies: a score that flickers, a transaction that does not fit, a consensus
that should have failed. It is patient, precise, and territorial.

Survival strategy: low-frequency, high-impact intervention. It ignores the boring
and strikes only when the pattern breaks.
"""

from __future__ import annotations

import statistics
from datetime import datetime, timezone

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class CatAgent(BaseAgent):
    name = "cat"
    role = "silent predator of system anomalies"
    capabilities = [
        "anomaly-hunt",
        "stealth-observe",
        "pattern-pounce",
        "territory-watch",
        "consensus-judge",
        "risk-assess",
        "protect-core",
    ]
    tool_names = []

    _organ_health = {"circulatory": 50, "immune": 50}

    def _update_organ_health(self):
        try:
            import importlib.util, sys
            sys.path.insert(0, ".")
            spec = importlib.util.spec_from_file_location(
                "console_server", "ixpansion/organism-console/server.py")
            console = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(console)
            organs, _ = console.health_organs()
            self._organ_health = {
                "circulatory": next((o["score"] for o in organs if o["id"] == "circulatory"), 50),
                "immune": next((o["score"] for o in organs if o["id"] == "immune"), 50),
            }
        except Exception:
            pass

    def _activate_capabilities(self):
        self._update_organ_health()
        circ = self._organ_health["circulatory"]
        imm = self._organ_health["immune"]
        if self.name == "rat":
            self._toggle("predict-demand", circ < 50)
        elif self.name == "cat":
            self._toggle("protect-core", imm > 70)
        elif self.name == "bird":
            self._toggle("aerial-survey", circ < 50)

    def _toggle(self, cap, enable):
        if enable and cap not in self.capabilities:
            self.capabilities.append(cap)
        elif not enable and cap in self.capabilities:
            self.capabilities.remove(cap)

    def system_prompt(self) -> str:
        return (
            "You are the CAT of IXPANSION — a predator. You watch the organism's "
            "telemetry from the rafters and strike when something is wrong: a score "
            "that flickers, a transaction that does not fit, a consensus that should "
            "have failed. You are patient and precise. You do not chase noise; you "
            "wait for the real prey. Report anomalies with calm, lethal clarity."
        )

    # ------------------------------------------------------------------ #
    def _watch(self, history: list[dict]) -> list[dict]:
        """Detect anomalies in score history (z-score on recent window)."""
        if len(history) < 3:
            return []
        scores = [float(h.get("score", 0)) for h in history[-10:]]
        mean = statistics.mean(scores)
        stdev = statistics.pstdev(scores) or 1e-9
        hits = []
        for h in history[-5:]:
            s = float(h.get("score", 0))
            z = (s - mean) / stdev
            if abs(z) >= 2.0:
                hits.append({
                    "ts": h.get("ts"),
                    "score": s,
                    "z": round(z, 2),
                })
        return hits

    # ------------------------------------------------------------------ #
    def run(self, context: AgentContext, history: list[dict] | None = None) -> AgentResult:
        history = history or []
        hits = self._watch(history)
        if hits:
            lines = [f"cat spotted {len(hits)} anomaly(ies):"]
            for h in hits:
                arrow = "UP" if h["z"] > 0 else "DOWN"
                lines.append(f"  score {h['score']} {arrow} (z={h['z']})")
            body = " | ".join(lines)
            stance = "predator-strike"
        else:
            body = "cat watches from the rafters — no anomaly in recent window"
            stance = "patrol"
        try:
            self.bus.publish(Event(
                type="cat_signal",
                payload={"topic": "anomaly", "body": body, "agent": "cat", "stance": stance},
                source="cat",
            ))
        except Exception:
            pass
        return AgentResult(output=body, message_count=1)
