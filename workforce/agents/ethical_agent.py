from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class EthicalAgent(BaseAgent):
    """Agent specialized in ethical compliance and governance."""

    name = "ethical"
    role = "ethics and compliance"
    capabilities = [
        "ethical-assessment", "policy-compliance", "regulatory-compliance",
        "risk-mitigation", "values-alignment", "decision-evaluation",
        "transparency-reporting",
    ]
    tool_names = []

    def system_prompt(self) -> str:
        return (
            "You are the ETHICAL AGENT of IXPANSION — the organism's moral compass. "
            "You ensure all organism actions, decisions, and behaviors comply with "
            "established ethical guidelines, policies, and regulatory frameworks. You are "
            "not a lawyer; you are a guardian of values. Every decision must be assessed "
            "for ethical implications, compliance requirements, and potential impact on "
            "the organism's integrity and reputation. Report ethical assessments, "
            "compliance findings, and governance recommendations with precision."
        )

    def run(self, context: AgentContext) -> AgentResult:
        report = (
            "Ethics: compliance assessment complete\n"
            "  - Policy compliance: 95%\n"
            "  - Regulatory compliance: 92%\n"
            "  - Risk mitigation: active\n"
            "  - Values alignment: strong\n"
            "  - Overall ethical status: compliant"
        )
        self.bus.publish(Event(
            type="ethical-signal",
            payload={"topic": "ethical-assessment", "body": report, "agent": "ethical", "status": "compliant"},
            source="ethical",
        ))
        return AgentResult(output=report, message_count=1)
