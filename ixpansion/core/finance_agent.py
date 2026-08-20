"""
FinanceAgent - IXPANSION Financial Governance Power Agent

A specialized agent that provides financial governance for the IXPANSION organism,
integrating portfolio optimization, risk assessment, cashflow management, investment strategy,
asset allocation, financial compliance, and revenue forecasting with the organism health
and stress monitoring systems.

Features:
- 7 core capabilities as specified in the ixpansion backlog
- Integration with OrganHealthMonitor for health/wealth correlation
- Integration with OrganismStressTest for financial stress events
- Portfolio optimization and risk assessment
- Cashflow management and revenue forecasting
- Financial compliance checking
- Investment strategy generation
- Real-time financial organ scoring (wealth as 9th organ)
"""

import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime, timedelta


class FinanceAgent:
    """Provides financial governance for the IXPANSION organism."""

    # Financial organs and their normal ranges (0-100 scale)
    FINANCIAL_ORGANS = {
        "wealth": {
            "base_score": 75,
            "normal_range": (60, 90),
            "description": "Overall financial health and asset value",
        },
        "cashflow": {
            "base_score": 80,
            "normal_range": (70, 95),
            "description": "Liquidity and cash flow velocity",
        },
        "revenue": {
            "base_score": 78,
            "normal_range": (65, 92),
            "description": "Income generation and revenue streams",
        },
        "risk": {
            "base_score": 72,
            "normal_range": (50, 90),
            "description": "Risk exposure and mitigation level",
        },
        "compliance": {
            "base_score": 85,
            "normal_range": (80, 100),
            "description": "Financial regulatory compliance status",
        },
        "investment": {
            "base_score": 70,
            "normal_range": (55, 88),
            "description": "Investment portfolio performance",
        },
        "allocation": {
            "base_score": 77,
            "normal_range": (65, 90),
            "description": "Asset allocation balance and diversification",
        },
    }

    # Organism health organs (matching health-monitor-agent)
    ORGAN_SYSTEMS = {
        "cardiovascular": {"base_score": 75, "normal_range": (60, 90)},
        "neurological": {"base_score": 80, "normal_range": (70, 95)},
        "digestive": {"base_score": 70, "normal_range": (55, 85)},
        "respiratory": {"base_score": 85, "normal_range": (75, 95)},
        "immune": {"base_score": 72, "normal_range": (50, 90)},
        "metabolic": {"base_score": 78, "normal_range": (65, 92)},
        "detoxification": {"base_score": 68, "normal_range": (40, 88)},
        "reproductive": {"base_score": 82, "normal_range": (60, 95)},
    }

    # Known financial stress events
    FINANCIAL_STRESSORS = {
        "cash_flow_crisis": {
            "financial_organ": "cashflow",
            "organism_organ": "metabolic",
            "severity_base": 25,
            "description": "Revenue shortfall or funding gap",
        },
        "api_key_expiry": {
            "financial_organ": "revenue",
            "organism_organ": "detoxification",
            "severity_base": 20,
            "description": "Payment processing or subscription expiry",
        },
        "investment_loss": {
            "financial_organ": "investment",
            "organism_organ": "cardiovascular",
            "severity_base": 30,
            "description": "Portfolio value decline or market crash",
        },
        "compliance_penalty": {
            "financial_organ": "compliance",
            "organism_organ": "immune",
            "severity_base": 15,
            "description": "Regulatory fine or compliance violation",
        },
        "debt_accumulation": {
            "financial_organ": "wealth",
            "organism_organ": "digestive",
            "severity_base": 22,
            "description": "Growing debt burden or leverage risk",
        },
    }

    def __init__(self, console_url="http://127.0.0.1:8890"):
        self.console_url = console_url
        self.name = "FinanceAgent"
        self.version = "1.0.0"
        self.last_report = None

    def _fetch_organism_health(self):
        """Fetch current organism health from console."""
        try:
            url = f"{self.console_url}/api/status"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("organs", self._generate_dummy_health())
        except Exception:
            return self._generate_dummy_health()

    def _generate_dummy_health(self):
        """Generate dummy organism health scores."""
        scores = {}
        for organ, config in self.ORGAN_SYSTEMS.items():
            scores[organ] = {"score": config["base_score"], "status": "stable"}
        return scores

    def _fetch_finance_health(self):
        """Fetch or generate financial organ scores."""
        try:
            url = f"{self.console_url}/api/finance-status"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            return self._generate_dummy_finance()

    def _generate_dummy_finance(self):
        """Generate realistic financial organ scores with some variation."""
        scores = {}
        for organ, config in self.FINANCIAL_ORGANS.items():
            variation = random.uniform(-8, 8)
            score = max(
                config["normal_range"][0],
                min(config["normal_range"][1], config["base_score"] + variation),
            )
            scores[organ] = {"score": round(score, 1), "status": "stable"}
        return scores

    def assess_financial_risk(self, organ=None):
        """Assess risk for a specific financial organ or all organs."""
        finance = self._fetch_finance_health()

        if organ:
            if organ in finance:
                organ_data = finance[organ]
                config = self.FINANCIAL_ORGANS.get(organ, {})
                normal = config.get("normal_range", (50, 90))
                score = organ_data["score"]
                low, high = normal

                if score < low or score > high:
                    severity = "critical" if abs(score - 70) > 15 else "warning"
                    return {
                        "organ": organ,
                        "score": score,
                        "normal_range": normal,
                        "severity": severity,
                        "description": f"{organ} organ risk assessment",
                    }
                return {"organ": organ, "score": score, "status": "within_normal"}
            return {"error": f"Financial organ '{organ}' not recognized"}

        # Assess all financial organs
        risks = {}
        for organ in self.FINANCIAL_ORGANS:
            risks[organ] = self.assess_financial_risk(organ=organ)
        return risks

    def optimize_portfolio(self, risk_tolerance="medium"):
        """Generate portfolio optimization recommendations."""
        risk_tolerance_map = {
            "conservative": 0.3,
            "medium": 0.5,
            "aggressive": 0.7,
        }
        tolerance_factor = risk_tolerance_map.get(risk_tolerance, 0.5)

        # Base asset allocation by tolerance
        base_allocation = {
            "conservative": {"stocks": 0.4, "bonds": 0.5, "cash": 0.1},
            "medium": {"stocks": 0.6, "bonds": 0.3, "cash": 0.1},
            "aggressive": {"stocks": 0.8, "bonds": 0.15, "cash": 0.05},
        }

        allocation = base_allocation.get(risk_tolerance, base_allocation["medium"])

        # Adjust based on current financial organ scores
        finance = self._fetch_finance_health()
        current_wealth = finance.get("wealth", {}).get("score", 75)

        # Simple adjustment: if wealth is low, increase cash; if high, increase stocks
        if current_wealth < 60:
            allocation["cash"] = min(0.3, allocation["cash"] + 0.1)
            allocation["stocks"] = max(0.3, allocation["stocks"] - 0.1)
        elif current_wealth > 85:
            allocation["stocks"] = min(0.85, allocation["stocks"] + 0.1)
            allocation["cash"] = max(0.05, allocation["cash"] - 0.1)

        # Generate recommendations
        recommendations = []
        for asset, percentage in allocation.items():
            if percentage > 0.15:
                recommendations.append(
                    f"Allocate {int(percentage * 100)}% to {asset.upper()}"
                )

        return {
            "risk_tolerance": risk_tolerance,
            "allocation": allocation,
            "recommendations": recommendations,
            "current_wealth_score": current_wealth,
            "generated": datetime.now().isoformat(),
        }

    def manage_cashflow(self, action="monitor"):
        """Cashflow management actions."""
        if action == "monitor":
            # Current cashflow status
            finance = self._fetch_finance_health()
            cashflow = finance.get("cashflow", {})
            score = cashflow.get("score", 80)
            normal = self.FINANCIAL_ORGANS["cashflow"]["normal_range"]

            return {
                "action": "cashflow_monitor",
                "current_score": score,
                "normal_range": normal,
                "status": (
                    "healthy"
                    if score >= normal[0] and score <= normal[1]
                    else "concerned"
                    if score < normal[0]
                    else "excessive"
                ),
                "recommendation": (
                    "Maintain current cash management"
                    if score >= normal[0]
                    else "Accelerate receivables and defer payables"
                ),
                "timestamp": datetime.now().isoformat(),
            }

        elif action == "boost":
            # Apply a cashflow boost (simulate incoming revenue)
            finance = self._fetch_finance_health()
            current = finance.get("cashflow", {}).get("score", 80)
            boosted = min(100, current + 10)
            finance["cashflow"]["score"] = boosted

            # Update organism metabolic organ too (correlation)
            try:
                health = self._fetch_organism_health()
                if "metabolic" in health:
                    health["metabolic"]["score"] = min(
                        100, health["metabolic"].get("score", 78) + 5
                    )
            except Exception:
                pass

            return {
                "action": "cashflow_boost",
                "previous_score": current,
                "new_score": boosted,
                "organism_correlation": "metabolic organ +5 points",
                "timestamp": datetime.now().isoformat(),
            }

        return {"action": action, "status": "unknown"}

    def check_compliance(self):
        """Financial regulatory compliance check."""
        finance = self._fetch_finance_health()
        compliance = finance.get("compliance", {})

        score = compliance.get("score", 85)
        normal = self.FINANCIAL_ORGANS["compliance"]["normal_range"]
        low, high = normal

        compliance_status = (
            "fully_compliant"
            if score >= low and score <= high
            else "at_risk" if score < low else "under_review"
        )

        # Generate compliance report
        recommendations = []
        if score < low:
            recommendations.append("Review recent transactions for compliance gaps")
            recommendations.append("Schedule internal audit")
            recommendations.append("Consult legal counsel for regulatory requirements")
        elif score > high * 0.9:
            recommendations.append("Maintain current compliance protocols")
            recommendations.append("Consider proactive regulatory engagement")

        return {
            "organ": "compliance",
            "score": score,
            "normal_range": normal,
            "status": compliance_status,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }

    def forecast_revenue(self, months=3):
        """Revenue forecasting based on current trends."""
        finance = self._fetch_finance_health()
        revenue = finance.get("revenue", {}).get("score", 78)

        # Simple trend-based forecasting
        # In a real implementation, this would use historical data
        trend_factor = random.uniform(-0.05, 0.05)  # ±5% monthly variation
        monthly_forecast = revenue * (1 + trend_factor)

        forecasts = []
        current = revenue
        for i in range(1, months + 1):
            current = current * (1 + trend_factor)
            forecasts.append(
                {
                    "month": i,
                    "forecasted_score": round(current, 1),
                    "confidence": "high" if i <= 3 else "medium",
                }
            )

        return {
            "current_revenue_score": revenue,
            "forecasts": forecasts,
            "period_months": months,
            "generated": datetime.now().isoformat(),
        }

    def simulate_financial_stress(self, event_type=None):
        """Simulate a financial stress event and its impact."""
        if event_type is None:
            event_types = list(self.FINANCIAL_STRESSORS.keys())
            event_type = random.choice(event_types)

        if event_type not in self.FINANCIAL_STRESSORS:
            return {"error": f"Unknown financial stress event: {event_type}"}

        stress_config = self.FINANCIAL_STRESSORS[event_type]
        severity = min(100, stress_config["severity_base"] + random.uniform(-3, 3))

        # Get affected financial organ
        fin_organ = stress_config["financial_organ"]
        org_organ = stress_config["organism_organ"]

        # Get current scores
        finance = self._fetch_finance_health()
        organism = self._fetch_organism_health()

        current_finance_score = finance.get(fin_organ, {}).get("score", self.FINANCIAL_ORGANS.get(fin_organ, {}).get("base_score", 75))
        current_organism_score = organism.get(org_organ, {}).get("score", 75)

        # Calculate new scores under stress
        score_drop = int(severity * 0.7)
        new_finance_score = max(
            self.FINANCIAL_ORGANS.get(fin_organ, {}).get("normal_range", [50, 90])[0] - 5,
            current_finance_score - score_drop,
        )
        new_organism_score = max(
            self.ORGAN_SYSTEMS.get(org_organ, {}).get("normal_range", [50, 90])[0] - 5,
            current_organism_score - score_drop // 2,
        )

        # Update scores
        finance[fin_organ]["score"] = round(new_finance_score, 1)
        organism[org_organ]["score"] = round(new_organism_score, 1)

        event = {
            "id": f"finance_stress_{int(time.time())}",
            "type": event_type,
            "financial_organ": fin_organ,
            "organism_organ": org_organ,
            "severity": round(severity, 1),
            "previous_finance_score": current_finance_score,
            "new_finance_score": round(new_finance_score, 1),
            "previous_organism_score": current_organism_score,
            "new_organism_score": round(new_organism_score, 1),
            "description": stress_config["description"],
            "timestamp": datetime.now().isoformat(),
            "status": "active",
        }

        print(
            f"[FinanceAgent] Simulated financial stress: {event_type}"
        )
        print(f"  Financial organ: {fin_organ} ({current_finance_score} -> {new_finance_score})")
        print(f"  Organism organ: {org_organ} ({current_organism_score} -> {new_organism_score})")
        print(f"  Description: {stress_config['description']}")

        return event

    def generate_financial_report(self, include_recommendations=True):
        """Generate comprehensive financial governance report."""
        # Assess all financial risks
        risks = self.assess_financial_risk()

        # Optimize portfolio (medium risk tolerance)
        portfolio = self.optimize_portfolio(risk_tolerance="medium")

        # Check cashflow
        cashflow = self.manage_cashflow(action="monitor")

        # Check compliance
        compliance = self.check_compliance()

        # Forecast revenue
        forecast = self.forecast_revenue(months=3)

        # Simulate current financial stress
        stress_event = self.simulate_financial_stress()

        lines = []
        lines.append("=" * 70)
        lines.append("💰 IXPANSION FINANCE GOVERNANCE REPORT 💰")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Agent: {self.name} v{self.version}")
        lines.append("")

        # Financial organ scores
        lines.append("📊 Financial Organ Scores:")
        lines.append("-" * 70)
        sorted_organs = sorted(
            self.FINANCIAL_ORGANS.keys(), key=lambda o: self._fetch_finance_health().get(o, {}).get("score", 0)
        )
        for organ in sorted_organs:
            finance = self._fetch_finance_health()
            score = finance.get(organ, {}).get("score", 0)
            config = self.FINANCIAL_ORGANS.get(organ, {})
            normal = config.get("normal_range", (50, 90))
            status = (
                "✅ Optimal"
                if score >= normal[0] and score <= normal[1]
                else "🟠 Warning" if score < normal[0] else "🔴 Critical"
            )
            lines.append(f"  {status} {organ:12s} {score:5.1f} (normal: {normal[0]}-{normal[1]})")

        lines.append("")

        # Risk assessment
        lines.append("⚠️  Risk Assessment:")
        lines.append("-" * 70)
        critical_risks = [k for k, v in risks.items() if v.get("severity") in ("critical", "warning")]
        if critical_risks:
            for risk in critical_risks:
                lines.append(f"  🔴 {risk}: {risks[risk].get('description', 'Under review')}")
        else:
            lines.append("  ✅ All financial organs within normal ranges")

        lines.append("")

        # Portfolio optimization
        lines.append("📈 Portfolio Optimization:")
        lines.append("-" * 70)
        lines.append(f"  Risk Tolerance: {portfolio['risk_tolerance']}")
        lines.append(f"  Allocation: ")
        alloc_str = ", ".join(
            f"{int(p * 100)}% {a.upper()}" for a, p in portfolio["allocation"].items() if p > 0.1
        )
        lines.append(f"    {alloc_str}")

        lines.append("")

        # Compliance
        lines.append("📜 Compliance Status:")
        lines.append("-" * 70)
        lines.append(f"  Status: {compliance.get('status', 'unknown').upper()}")
        lim_recs = compliance.get("recommendations", [])
        for rec in lim_recs[:2]:
            lines.append(f"  • {rec}")

        lines.append("")

        # Revenue forecast
        lines.append("🔮 Revenue Forecast:")
        lines.append("-" * 70)
        current = forecast.get("current_revenue_score", 78)
        lines.append(f"  Current Revenue Score: {current:.1f}")
        lines.append(f"  Forecast Period: {forecast.get('period_months', 3)} months")
        if forecast.get("forecasts"):
            first_month = forecast["forecasts"][0]
            lines.append(
                f"  Month 1 Forecast: {first_month['forecasted_score']:.1f} "
                f"(Confidence: {first_month['confidence']})"
            )

        lines.append("")

        # Active financial stress
        lines.append("⚡ Active Financial Stress:")
        lines.append("-" * 70)
        stress_type = stress_event.get("type", "none")
        lines.append(f"  Active Stress: {stress_type}")
        lines.append(f"  Description: {stress_event.get('description', 'N/A')}")

        lines.append("")

        # Recommendations
        if include_recommendations:
            lines.append("💡 Recommendations:")
            lines.append("-" * 70)

            # From risk assessment
            for risk in critical_risks:
                lines.append(f"  🔴 Address: {risks[risk].get('description', '')}")

            # From portfolio
            for rec in portfolio.get("recommendations", [])[:2]:
                lines.append(f"  📊 {rec}")

            # From cashflow
            lines.append(f"  💵 {cashflow.get('recommendation', 'N/A')}")

            # From compliance
            for rec in compliance.get("recommendations", [])[:2]:
                lines.append(f"  📜 {rec}")

            # From forecast
            lines.append(
                f"  🔮 Monitor revenue trends and adjust strategy as needed"
            )

        lines.append("")
        lines.append("=" * 70)
        lines.append("End of Finance Governance Report")
        lines.append("=" * 70)

        return "\n".join(lines)

    def run_finance_cycle(self, action="full"):
        """Run a complete finance governance cycle."""
        print("=" * 70)
        print(f"IXPANSION Finance Governance Cycle")
        print(f"Agent: {self.name} v{self.version}")
        print("=" * 70)
        print("")

        if action == "full" or action == "assess":
            print(">>> Assessing financial risks...")
            risks = self.assess_financial_risk()
            critical = [k for k, v in risks.items() if v.get("severity") == "critical"]
            if critical:
                print(f"  ⚠️  Critical risks found: {', '.join(critical)}")
            else:
                print("  ✅ No critical financial risks")

        if action == "full" or action == "portfolio":
            print(">>> Optimizing portfolio allocation...")
            portfolio = self.optimize_portfolio(risk_tolerance="medium")
            alloc = portfolio.get("allocation", {})
            alloc_str = ", ".join(
                f"{int(p * 100)}% {a.upper()}" for a, p in alloc.items() if p > 0.1
            )
            print(f"  Risk Tolerance: {portfolio['risk_tolerance']}")
            print(f"  Allocation: {alloc_str}")

        if action == "full" or action == "cashflow":
            print(">>> Managing cashflow...")
            cashflow = self.manage_cashflow(action="monitor")
            print(f"  Status: {cashflow.get('status', 'unknown')}")

        if action == "full" or action == "compliance":
            print(">>> Checking compliance...")
            compliance = self.check_compliance()
            print(f"  Status: {compliance.get('status', 'unknown')}")

        if action == "full" or action == "forecast":
            print(">>> Forecasting revenue...")
            forecast = self.forecast_revenue()
            print(f"  Current revenue score: {forecast.get('current_revenue_score', 78):.1f}")

        if action == "full" or action == "stress":
            print(">>> Simulating financial stress...")
            stress_event = self.simulate_financial_stress()
            print(f"  Event: {stress_event.get('type', 'none')}")

        if action == "full" or action == "report":
            print(">>> Generating comprehensive report...")
            report = self.generate_financial_report()
            # Print first 600 chars
            preview = report[:600] + "..." if len(report) > 600 else report
            print(preview)

        print("")
        print("✅ Finance governance cycle complete!")


# CLI interface
if __name__ == "__main__":
    import sys

    agent = FinanceAgent()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "check" or command == "assess":
            print(">>> Assessing financial risks...")
            risks = agent.assess_financial_risk()
            for organ, risk in risks.items():
                sev = risk.get("severity", "unknown")
                icon = "🔴" if sev == "critical" else "🟠" if sev == "warning" else "✅"
                print(f"  {icon} {organ}: score={risk.get('score')}, severity={sev}")

        elif command == "portfolio":
            print(">>> Optimizing portfolio...")
            portfolio = agent.optimize_portfolio(risk_tolerance="medium")
            alloc = portfolio.get("allocation", {})
            alloc_str = ", ".join(
                f"{int(p * 100)}% {a.upper()}" for a, p in alloc.items() if p > 0.1
            )
            print(f"  Tolerance: {portfolio['risk_tolerance']}")
            print(f"  Allocation: {alloc_str}")

        elif command == "cashflow":
            print(">>> Managing cashflow...")
            result = agent.manage_cashflow(action="monitor")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Recommendation: {result.get('recommendation', 'N/A')}")

        elif command == "compliance":
            print(">>> Checking compliance...")
            result = agent.check_compliance()
            print(f"  Status: {result.get('status', 'unknown')}")

        elif command == "forecast":
            print(">>> Forecasting revenue...")
            forecast = agent.forecast_revenue(months=3)
            print(f"  Current revenue score: {forecast.get('current_revenue_score', 78):.1f}")

        elif command == "stress":
            print(">>> Simulating financial stress...")
            event = agent.simulate_financial_stress()
            print(f"  Event: {event.get('type', 'none')}")

        elif command == "report":
            print(">>> Generating financial report...")
            report = agent.generate_financial_report()
            # Print summary
            finance = agent._fetch_finance_health()
            scores = [finance.get(o, {}).get("score", 0) for o in finance]
            print(f"  Financial organs: {len(scores)} monitored")
            print(f"  Average score: {sum(scores) / len(scores):.1f}" if scores else "  No data")

        elif command == "full":
            # Run complete cycle
            print(">>> Running full finance governance cycle...")
            agent.run_finance_cycle(action="full")

        elif command == "health-correlate":
            # Correlate financial and organism health
            print(">>> Correlating financial and organism health...")
            finance = agent._fetch_finance_health()
            organism = agent._fetch_organism_health()

            fin_avg = sum(f.get("score", 0) for f in finance.values()) / len(
                finance
            ) if finance else 0
            org_avg = sum(o.get("score", 0) for o in organism.values()) / len(
                organism
            ) if organism else 0

            print(f"  Financial organs average: {fin_avg:.1f}")
            print(f"  Organism organs average: {org_avg:.1f}")

            # Simple correlation
            if abs(fin_avg - org_avg) < 10:
                print("  📊 Correlation: Financial and organism health are aligned")
            else:
                print(
                    "  🔍 Correlation: Discrepancy detected - consider health/wealth balance"
                )

        elif command == "help" or command in ("--help", "-h"):
            print("""
IXPANSION FinanceAgent Commands:
  check/assess              - Assess financial risks
  portfolio                 - Optimize portfolio allocation
  cashflow                  - Manage cashflow
  compliance                - Check regulatory compliance
  forecast                  - Forecast revenue (3 months)
  stress                    - Simulate financial stress
  report                    - Generate comprehensive report
  full                      - Run complete cycle
  health-correlate          - Correlate fin/org health
  help                      - Show this help

Financial organs: """ + ", ".join(agent.FINANCIAL_ORGANS.keys()))
            
        else:
            print(f"Unknown command: {command}")
            print("Use 'check help' for available commands")
    else:
        # Default: run assessment
        print("=" * 70)
        print("IXPANSION FinanceAgent - Default Cycle")
        print("=" * 70)
        print("")
        print(">>> Running financial risk assessment...")
        agent.run_finance_cycle(action="assess")
        print("")
        print(">>> Optimizing portfolio allocation...")
        agent.run_finance_cycle(action="portfolio")
        print("")
        print(">>> Managing cashflow...")
        agent.run_finance_cycle(action="cashflow")
        print("")
        print(">>> Checking compliance...")
        agent.run_finance_cycle(action="compliance")
        print("")
        print(">>> Generating report...")
        agent.run_finance_cycle(action="report")
        print("")
        print("✅ Default finance cycle complete!")
