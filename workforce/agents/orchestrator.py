import json
import time
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, "/root/Hub_spot")

from ixpansion.core.organism_pulse_coordinator import OrganismPulseCoordinator
from ixpansion.core.health_monitor_agent import OrganHealthMonitor
from ixpansion.core.finance_agent import FinanceAgent
from ixpansion.core.stress_test_agent import OrganismStressTest
from ixpansion.core.wordpress_agent import WordPressAgent


class OrchestratorAgent:
    """Central orchestrator for the IXPANSION organism agent network."""

    def __init__(self, console_url="http://127.0.0.1:8890", pulse_coordinator_url="http://127.0.0.1:8890"):
        self.pulse_coordinator = OrganismPulseCoordinator(pulse_coordinator_url)
        self.health_monitor = OrganHealthMonitor(console_url)
        self.finance_agent = FinanceAgent(console_url)
        self.stress_test = OrganismStressTest(console_url)
        self.wordpress_agent = WordPressAgent(console_url)
        self.name = "Orchestrator"
        self.version = "1.0.0 (Experimental)"
        self.task_queue = []
        self.completed_tasks = []
        self.agent_capabilities = {
            "health_monitor": {
                "capabilities": ["organ_health_scanning", "anomaly_detection", "wellness_reporting", "health_pulsing"],
                "priority_weight": 1.0,
                "typical_tasks": ["check_health", "monitor_organs", "generate_wellness_report", "health_pulsing"],
            },
            "finance_agent": {
                "capabilities": ["assess_financial_risk", "optimize_portfolio", "manage_cashflow", "check_compliance", "forecast_revenue", "simulate_financial_stress"],
                "priority_weight": 1.2,
                "typical_tasks": ["assess_financial_risk", "optimize_portfolio", "manage_cashflow", "check_compliance", "forecast_revenue", "simulate_financial_stress"],
            },
            "stress_test": {
                "capabilities": ["simulate_stress_event", "simulate_recovery", "calculate_resilience_coefficient", "check_cross_organ_impact", "generate_stress_report"],
                "priority_weight": 0.9,
                "typical_tasks": ["simulate_stress_event", "simulate_recovery", "calculate_resilience_coefficient", "check_cross_organ_impact", "generate_stress_report"],
            },
            "wordpress_agent": {
                "capabilities": ["check_health", "get_site_info", "analyze_content_freshness", "check_plugin_status", "check_theme_status", "generate_domain_report"],
                "priority_weight": 0.8,
                "typical_tasks": ["check_health", "get_site_info", "analyze_content_freshness", "check_plugin_status", "check_theme_status", "generate_domain_report"],
            },
            "pulse_coordinator": {
                "capabilities": ["run_pulse_cycle", "check_resonance", "get_wellness_score", "generate_history"],
                "priority_weight": 1.1,
                "typical_tasks": ["run_pulse_cycle", "check_resonance", "get_wellness_score", "generate_history"],
            },
        }

        self.task_history = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "average_response_time": 0,
            "success_rate": 1.0,
            "agent_distribution": {},
        }

    def assess_agent_capabilities(self, agent_name):
        if agent_name in self.agent_capabilities:
            return self.agent_capabilities[agent_name]
        return None

    def route_task(self, task_type, priority="normal", **kwargs):
        task_categories = {
            "health": ["check_health", "monitor_organs", "generate_wellness_report"],
            "finance": ["assess_financial_risk", "optimize_portfolio", "manage_cashflow"],
            "stress": ["simulate_stress_event", "simulate_recovery", "check_resilience"],
            "domain": ["check_health", "get_site_info", "analyze_content_freshness"],
            "pulse": ["run_pulse_cycle", "check_resonance", "get_wellness_score"],
        }

        agent_scores = {}
        for agent_name, capabilities in self.agent_capabilities.items():
            if task_type in capabilities["typical_tasks"]:
                base_score = 1.0
                weight = capabilities["priority_weight"]
                load_factor = 1.0
                specificity = 1.0 if task_type in capabilities["typical_tasks"] else 0.5
                total_score = base_score * weight * load_factor * specificity
                agent_scores[agent_name] = total_score

        if not agent_scores:
            return {"error": f"No agent capable of handling task: {task_type}"}

        best_agent = max(agent_scores, key=agent_scores.get)
        best_score = agent_scores[best_agent]

        result = self._execute_task(best_agent, task_type, **kwargs)

        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "assigned_agent": best_agent,
            "score": best_score,
            "result_summary": str(result)[:100] if result else "no result",
            "priority": priority,
        })

        self.performance_metrics["tasks_completed"] += 1
        self._update_agent_distribution(best_agent)

        return {
            "task_type": task_type,
            "assigned_agent": best_agent,
            "score": best_score,
            "result": result,
            "routed_at": datetime.now().isoformat(),
            "priority": priority,
        }

    def _execute_task(self, agent_name, task_type, **kwargs):
        agent_map = {
            "health_monitor": ("ixpansion.core.health_monitor_agent", "OrganHealthMonitor"),
            "finance_agent": ("ixpansion.core.finance_agent", "FinanceAgent"),
            "stress_test": ("ixpansion.core.stress_test_agent", "OrganismStressTest"),
            "wordpress_agent": ("ixpansion.core.wordpress_agent", "WordPressAgent"),
        }

        if agent_name not in agent_map:
            return {"error": f"Unknown agent: {agent_name}"}

        module_name, class_name = agent_map[agent_name]
        try:
            module = __import__(module_name, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            agent = agent_class()

            task_map = {
                "check_health": lambda: agent.run_finance_cycle(action="check") if agent_name == "finance_agent" else agent.run_monitoring_cycle(),
                "monitor_organs": lambda: agent.run_monitoring_cycle(),
                "assess_risk": lambda: agent.assess_financial_risk(),
                "optimize_portfolio": lambda: agent.optimize_portfolio(kwargs.get("risk_tolerance", "medium")),
                "boost_cashflow": lambda: agent.manage_cashflow(action="boost"),
                "check_resilience": lambda: st.calculate_resilience_coefficient() if agent_name == "stress_test" else 0,
                "run_stress_test": lambda: st.simulate_stress_event(),
                "simulate_recovery": lambda: st.simulate_recovery(),
                "check_health": lambda: wa.check_health(),
                "get_site_info": lambda: wa.get_site_info(),
                "run_pulse_cycle": lambda: pc.run_pulse_cycle(),
            }

            execute_fn = task_map.get(task_type)
            if execute_fn:
                return execute_fn()
            else:
                return {"status": "task_queued", "details": f"Task {task_type} queued for {agent_name}"}
        except Exception as e:
            return {"error": str(e)}

    def _update_agent_distribution(self, agent_name):
        if agent_name not in self.performance_metrics["agent_distribution"]:
            self.performance_metrics["agent_distribution"][agent_name] = 0
        self.performance_metrics["agent_distribution"][agent_name] += 1

    def get_orchestrator_status(self):
        return {
            "orchestrator_name": self.name,
            "version": self.version,
            "tasks_completed": self.performance_metrics["tasks_completed"],
            "agent_distribution": self.performance_metrics["agent_distribution"],
            "task_queue_length": len(self.task_queue),
            "success_rate": self.performance_metrics["success_rate"],
            "last_task": self.task_history[-1] if self.task_history else None,
        }

    def start_workflow(self, workflow_name, tasks=None):
        workflows = {
            "daily_operations": [
                {"task": "run_pulse_cycle", "agent": "pulse_coordinator"},
                {"task": "check_health", "agent": "health_monitor"},
                {"task": "assess_risk", "agent": "finance_agent"},
            ],
            "health_check": [
                {"task": "check_health", "agent": "health_monitor"},
                {"task": "assess_risk", "agent": "finance_agent"},
            ],
        }

        workflow_tasks = workflows.get(workflow_name, tasks or [])

        results = []
        for task in workflow_tasks:
            result = self.route_task(task["task"], priority="normal", **{"agent": task["agent"]})
            results.append(result)

        return {
            "workflow_name": workflow_name,
            "tasks_executed": len(tasks) if tasks else 0,
            "results": results,
            "workflow_complete": all(r.get("result", {}).get("status", "") != "error" for r in results),
            "completed_at": datetime.now().isoformat(),
        }
