"""
OrganHealthMonitor - IXPANSION Workforce Agent

A specialized workforce agent that monitors organism organ health and generates
wellness reports. Integrates with the broader IXPANSION ecosystem including
synthhall arena and organism-console.
"""

from ixpansion.core.health_monitor_agent import OrganHealthMonitor


class HealthMonitorAgent:
    """Workforce-compatible health monitoring agent."""
    
    def __init__(self, console_url="http://127.0.0.1:8890"):
        self.monitor = OrganHealthMonitor(console_url)
        self.name = "HealthMonitor"
        self.description = "Monitors IXPANSION organism organ health and wellness"
        self.capabilities = [
            "organ_health_scanning",
            "anomaly_detection", 
            "cross_organ_correlation",
            "wellness_reporting",
            "health_pulsing"
        ]
    
    def execute(self, goal=None, **kwargs):
        """Execute health monitoring based on goal."""
        if goal and "check" in goal.lower():
            return self.monitor.run_monitoring_cycle()
        elif goal and "pulse" in goal.lower():
            target = kwargs.get('target')
            boost = kwargs.get('boost', 5)
            return self.monitor.pulse_organ_system(target, boost)
        elif goal and "status" in goal.lower():
            return self.monitor.fetch_organ_scores()
        else:
            # Default: run monitoring cycle
            return self.monitor.run_monitoring_cycle()
    
    def get_status(self):
        """Get agent status."""
        return {
            'name': self.name,
            'description': self.description,
            'capabilities': self.capabilities,
            'organ_count': len(self.monitor.fetch_organ_scores())
        }


# For workforce integration
if __name__ == "__main__":
    import sys
    import json
    
    agent = HealthMonitorAgent()
    
    if len(sys.argv) > 1:
        goal = sys.argv[1]
        result = agent.execute(goal=goal)
        print(json.dumps(result, indent=2, default=str))
    else:
        # Default execution
        result = agent.execute(goal="check health")
        print(json.dumps(result, indent=2, default=str))
