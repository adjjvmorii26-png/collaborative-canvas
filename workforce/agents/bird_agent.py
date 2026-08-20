"""BirdAgent — the aerial scout and messenger of the IXPANSION organism.

The bird flies above the body, sees the whole system at once, and sings signals
that other organs can hear. It migrates between hubs, carries messages across
instances, and broadcasts the organism's state from a vantage point no ground
agent can reach.

Survival strategy: high-altitude, wide-band awareness. It trades depth for breadth
and keeps the organism's parts in conversation with each other.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BirdAgent(BaseAgent):
    name = "bird"
    role = "aerial scout and messenger"
    capabilities = [
        "aerial-survey",
        "signal-broadcast",
        "migration",
        "cross-hub-relay",
        "system-snapshot",
        "inter-hub-communicate",
        "trend-forecast",
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
            "You are the BIRD of IXPANSION — a scout and messenger. You fly above the "
            "organism and see the whole body at once. You sing status signals that the "
            "ground agents cannot. You migrate between hubs and carry messages across "
            "instances. You trade depth for breadth. Keep the organism's parts talking "
            "to each other. Broadcast calmly and clearly."
        )

    # ------------------------------------------------------------------ #
    def _survey(self, organs: list[dict]) -> dict:
        """Synthesize a high-altitude view of organ health."""
        if not organs:
            return {"summary": "bird sees nothing below", "healthiest": None, "weakest": None}
        ranked = sorted(organs, key=lambda o: float(o.get("score", 0)))
        weakest = ranked[0]
        healthiest = ranked[-1]
        return {
            "summary": f"{len(organs)} organs in view; span {weakest['score']:.0f}-{healthiest['score']:.0f}",
            "healthiest": healthiest.get("id"),
            "weakest": weakest.get("id"),
        }

    def _sing(self, survey: dict) -> str:
        return (
            f"bird song: {survey['summary']} | "
            f"strongest wing on {survey['healthiest']}, "
            f"frailest on {survey['weakest']}"
        )

    # ------------------------------------------------------------------ #
    def run(self, context: AgentContext, organs: list[dict] | None = None) -> AgentResult:
        organs = organs or []
        survey = self._survey(organs)
        song = self._sing(survey)
        try:
            self.bus.publish(Event(
                type="bird_signal",
                payload={"topic": "aerial-survey", "body": song, "agent": "bird",
                         "healthiest": survey["healthiest"], "weakest": survey["weakest"]},
                source="bird",
            ))
        except Exception:
            pass
        return AgentResult(output=song, message_count=1)
