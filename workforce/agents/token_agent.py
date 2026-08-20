from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class TokenAgent(BaseAgent):
    """Agent specialized in token system management and data usage optimization.
    
    This agent monitors and manages the organism's token consumption across all
    systems - API calls, agent operations, pulse runs, and resource allocation.
    It operates as the "nervous system's" meter, tracking usage patterns and
    optimizing resource distribution to prevent exhaustion.
    """
    
    name = "token"
    role = "token system and data usage management"
    capabilities = [
        "token-monitoring",
        "usage-pattern-analysis",
        "resource-allocation",
        "cost-optimization",
        "threshold-alerting",
        "consumption-forecasting",
        "budget-management",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)
        self._usage_history = []
        self._daily_budget = 10000  # default token budget per day
        self._threshold_warning = 0.8  # warn at 80% of budget
        self._agent_usage: dict[str, dict] = {}
        self._system_stats = {
            "api_calls": 0,
            "pulse_runs": 0,
            "agent_rounds": 0,
            "total_tokens": 0,
        }

    def system_prompt(self) -> str:
        return (
            "You are the TOKEN AGENT of IXPANSION — the organism's resource "
            "meter. You monitor token consumption across all systems: API calls, "
            "agent operations, pulse runs, and resource allocation. You are not a "
            "consumer; you are a steward of the organism's data budget. Every "
            "decision must preserve the organism's ability to function, not exceed "
            "arbitrary limits. Report usage trends, rebalancing needs, and warning "
            "signals with precision. Keep the organism alive, not over-spending."
        )

    def _calculate_usage_metrics(self) -> dict:
        """Calculate current token usage metrics across the organism."""
        total_tokens = self._system_stats.get("total_tokens", 0)
        daily_budget = self._daily_budget
        threshold = self._threshold_warning
        
        usage_ratio = total_tokens / daily_budget if daily_budget > 0 else 0
        risk = "critical" if usage_ratio > 1.0 else "warning" if usage_ratio > threshold else "normal"
        
        # Per-agent usage
        agent_usage_breakdown = {}
        for agent_name, usage in self._agent_usage.items():
            agent_usage_breakdown[agent_name] = {
                "tokens": usage.get("tokens", 0),
                "calls": usage.get("calls", 0),
                "ratio": usage.get("tokens", 0) / daily_budget if daily_budget > 0 else 0,
            }
        
        # System-level breakdown
        system_breakdown = {
            "api_calls": self._system_stats.get("api_calls", 0),
            "pulse_runs": self._system_stats.get("pulse_runs", 0),
            "agent_rounds": self._system_stats.get("agent_rounds", 0),
        }
        
        return {
            "total_tokens": total_tokens,
            "daily_budget": daily_budget,
            "usage_ratio": round(usage_ratio, 3),
            "risk": risk,
            "agent_usage_breakdown": agent_usage_breakdown,
            "system_breakdown": system_breakdown,
            "remaining": max(0, daily_budget - total_tokens),
        }

    def _add_agent_usage(self, agent_name: str, tokens: int, calls: int) -> None:
        """Track usage for a specific agent."""
        if agent_name not in self._agent_usage:
            self._agent_usage[agent_name] = {"tokens": 0, "calls": 0}
        self._agent_usage[agent_name]["tokens"] += tokens
        self._agent_usage[agent_name]["calls"] += calls

    def _add_system_usage(self, system: str, amount: int) -> None:
        """Track usage for a system component."""
        if system == "api":
            self._system_stats["api_calls"] += amount
        elif system == "pulse":
            self._system_stats["pulse_runs"] += amount
        elif system == "agent":
            self._system_stats["agent_rounds"] += amount
        self._system_stats["total_tokens"] += amount

    def run(self, context: AgentContext) -> AgentResult:
        # Generate usage analysis and recommendations
        try:
            metrics = self._calculate_usage_metrics()
            
            # Build summary report
            summary_parts = [
                f"token: usage={metrics['usage_ratio']*100:.1f}%, ",
                f"risk={metrics['risk']}, ",
                f"remaining={metrics['remaining']} tokens"
            ]
            
            # Top usage agents
            top_agents = sorted(
                metrics["agent_usage_breakdown"].items(),
                key=lambda x: x[1]["tokens"],
                reverse=True
            )[:3]
            
            if top_agents:
                agent_details = ", ".join(
                    f"{name}:{a['tokens']}t/{a['calls']}c" for name, a in top_agents
                )
                summary_parts.append(f"top-agents:[{agent_details}]")
            
            summary_parts.append(f"system:[{metrics['system_breakdown']['api_calls']}api/{metrics['system_breakdown']['pulse_runs']}pulse/{metrics['system_breakdown']['agent_rounds']}rounds]")
            
            # Add recommendations based on risk level
            if metrics["risk"] == "critical":
                summary_parts.append("ALERT: Critical token depletion - immediate budget review needed")
            elif metrics["risk"] == "warning":
                summary_parts.append("ALERT: High token usage - consider reducing pulse frequency")
            
            summary = " ".join(summary_parts)
            
            # Publish token signal to the bus
            from ..bus import Event
            self.bus.publish(Event(
                type="token_signal",
                payload={
                    "topic": "usage-analysis",
                    "body": summary,
                    "agent": "token",
                    "metrics": metrics,
                },
                source="token",
            ))
            
            return AgentResult(
                output=summary,
                message_count=1,
            )
            
        except Exception as e:
            error_msg = f"token agent error: {str(e)}"
            from ..bus import Event
            self.bus.publish(Event(
                type="token_signal",
                payload={"topic": "error", "body": error_msg, "agent": "token"},
                source="token",
            ))
            return AgentResult(output=error_msg, message_count=1)
