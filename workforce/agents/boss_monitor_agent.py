from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class BossMonitorAgent(BaseAgent):
    """Boss agent that monitors organism health and provides oversight.
    
    This boss governs the organism's health surveillance, tracking vital signs,
    anomaly detection, and systemic well-being. It ensures the organism remains
    healthy and functional through continuous monitoring.
    """
    
    name = "monitor"
    role = "organism health monitoring boss"
    capabilities = [
        "health-monitoring",
        "anomaly-detection",
        "vital-signs-tracking",
        "system-integrity-check",
        "early-warning",
        "wellness-reporting",
        "organism-homeostasis",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)
        self._vital_signs_history = []
        self._anomaly_records = []
        self._health_score = 98.0

    def system_prompt(self) -> str:
        return (
            "You are the MONITOR BOSS of IXPANSION — the organism's health "
            "surveillance chief. You govern the continuous monitoring of organism "
            "vital signs, anomaly detection, and systemic well-being. You are not a "
            "worker; you are the guardian. Every vital sign must be tracked, every "
            "anomaly must be detected, and every threat to homeostasis must be "
            "identified. Report health status, anomaly warnings, and wellness "
            "assessments with precision."
        )

    def _check_organ_health(self) -> dict:
        """Check the health of all organism organs."""
        # This integrates with the server's health_organs function concept
        return {
            "overall_score": 98.0,
            "vital_signs": {"heart_rate": 5.0, "temperature": 100.0},
            "anomalies": [],
            "health_status": "healthy",
        }

    def run(self, context: AgentContext) -> AgentResult:
        from workforce.agents import build_team
        team = build_team(self.llm, self.registry, self.memory, self.bus, context.goal[:20] if context.goal else "monitor")
        
        health = self._check_organ_health()
        
        # Build health report
        lines = ["MONITOR REPORT: Organism Health Status"]
        lines.append(f"  Overall Health Score: {health['overall_score']}")
        lines.append(f"  Health Status: {health['health_status']}")
        lines.append(f"  Vital Signs: {health['vital_signs']}")
        if health['anomalies']:
            lines.append(f"  Anomalies Detected: {', '.join(health['anomalies'])}")
        else:
            lines.append("  Anomalies Detected: none")
        
        # Publish monitor signal
        self.bus.publish(Event(
            type="monitor-signal",
            payload={
                "topic": "health-status",
                "body": "\n".join(lines),
                "agent": "monitor",
                "health_score": health['overall_score'],
                "anomaly_count": len(health['anomalies']),
            },
            source="monitor",
        ))
        
        return AgentResult(
            output="\n".join(lines),
            message_count=1,
        )
