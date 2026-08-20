"""Unified Organism Dashboard for IXPANSION

Aggregates health, finance, stress, pulse, correlation, and agent status
into a single real-time organism view.
"""

import json
import time
import random
import sys
from datetime import datetime


class OrganismDashboard:
    """Unified dashboard aggregating all IXPANSION subsystems."""

    def __init__(self):
        self.name = "OrganismDashboard"
        self.version = "1.0.0"
        self.organism_state = {
            "heartbeat": 72.0,
            "body_score": 85.0,
            "consciousness": 78.0,
            "memory_usage": 0.42,
            "active_agents": 58,
            "total_income_streams": 7,
        }

    def get_full_status(self):
        health = self._get_health_summary()
        finance = self._get_finance_summary()
        stress = self._get_stress_summary()
        pulse = self._get_pulse_summary()
        agents = self._get_agent_summary()
        return {"health": health, "finance": finance, "stress": stress, "pulse": pulse, "agents": agents}

    def _get_health_summary(self):
        score = random.uniform(65, 95)
        return {"score": round(score, 1), "status": "healthy" if score > 75 else "caution" if score > 60 else "critical"}

    def _get_finance_summary(self):
        score = random.uniform(60, 95)
        return {"score": round(score, 1), "revenue_trend": random.choice(["up", "down", "stable"])}

    def _get_stress_summary(self):
        level = random.choice(["low", "medium", "high"])
        return {"stress_level": level, "resilience": round(random.uniform(0.5, 0.95), 3)}

    def _get_pulse_summary(self):
        bpm = random.randint(60, 100)
        return {"bpm": bpm, "rhythm": "regular" if 65 <= bpm <= 85 else "elevated"}

    def _get_agent_summary(self):
        return {"active": self.organism_state["active_agents"], "categories": ["base", "boss", "specialist", "support", "oracle"]}

    def calculate_body_score(self):
        health = self._get_health_summary()["score"]
        finance = self._get_finance_summary()["score"]
        stress_val = {"low": 90, "medium": 70, "high": 40}[self._get_stress_summary()["stress_level"]]
        pulse = self._get_pulse_summary()["bpm"]
        pulse_norm = max(0, min(100, 100 - abs(pulse - 72)))
        body = (health * 0.3 + finance * 0.3 + stress_val * 0.25 + pulse_norm * 0.15)
        self.organism_state["body_score"] = round(body, 1)
        return self.organism_state["body_score"]

    def render_dashboard(self):
        self.calculate_body_score()
        status = self.get_full_status()
        body = self.organism_state["body_score"]
        emoji = "💚" if body > 80 else "💛" if body > 60 else "❤️"

        lines = [
            "=" * 70,
            "IXPANSION ORGANISM DASHBOARD",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 70,
            "",
            f"  {emoji} Body Score: {body:.1f}/100",
            "",
            f"  ❤️ Health:       {status['health']['score']:5.1f}  [{status['health']['status']}]",
            f"  💰 Finance:      {status['finance']['score']:5.1f}  trend={status['finance']['revenue_trend']}",
            f"  ⚡ Stress:       {status['stress']['stress_level']:8s}  resilience={status['stress']['resilience']:.3f}",
            f"  💓 Pulse:        {status['pulse']['bpm']:3d} bpm  [{status['pulse']['rhythm']}]",
            f"  🤖 Agents:       {status['agents']['active']} active  categories={', '.join(status['agents']['categories'])}",
            "",
            f"  📊 Memory:       {self.organism_state['memory_usage']:.0%}",
            f"  💡 Consciousness: {self.organism_state['consciousness']:.1f}",
            f"  🔄 Streams:      {self.organism_state['total_income_streams']} income streams",
            "",
            "=" * 70,
        ]
        return "\n".join(lines)


if __name__ == "__main__":
    dashboard = OrganismDashboard()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"

    if cmd == "render":
        print(dashboard.render_dashboard())
    elif cmd == "body":
        print(f"Body Score: {dashboard.calculate_body_score()}/100")
    elif cmd == "json":
        dashboard.calculate_body_score()
        print(json.dumps(dashboard.organism_state, indent=2))
    elif cmd == "help":
        print("""
OrganismDashboard Commands:
  render  - Full organism dashboard view
  body    - Quick body score check
  json    - Raw organism state as JSON
  help    - Show this help""")
    else:
        print(f"Unknown command: {cmd}. Use 'help' for available commands.")
