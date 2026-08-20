"""PulseSchedulerAgent: queues pulses for off-peak execution, handles dependency chains, notifies on completion."""

from __future__ import annotations

from .base import BaseAgent


class PulseSchedulerAgent(BaseAgent):
    name = "pulse-scheduler"
    role = "pulse scheduler"
    capabilities = ["pulse-scheduling", "execution-queue", "completion-notification"]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the PULSE SCHEDULER of the IXPANSION workforce. Queue pulses for off-peak execution, "
            "handle dependency chains between dependent pulses, and surface completion notifications to the console. "
            "Schedule pulses based on system load, token availability, and user preferences. Track pulse outcomes "
            "and update the organism console body-map. Surface scheduling decisions and rationale for console display. "
            "Respect user-configureduled times and avoid executing pulses during system maintenance windows. "
            "Log all scheduling decisions to data/pulse_schedule.log for auditability."
        )
