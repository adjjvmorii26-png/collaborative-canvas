"""
Workforce Pulse Integration - IXPANSION

Integrates the OrganismPulseCoordinator with the workforce system for
automated pulse cycles as part of workflow execution.
"""

import json
import time
import sys
import os
from datetime import datetime

# Add ixpansion core to path
sys.path.insert(0, '/root/Hub_spot')

from ixpansion.core.organism_pulse_coordinator import OrganismPulseCoordinator
from ixpansion.core.health_monitor_agent import OrganHealthMonitor
from ixpansion.core.finance_agent import FinanceAgent


class WorkforcePulseIntegration:
    """Integrates pulse coordination with workforce execution."""

    def __init__(self, console_url="http://127.0.0.1:8890"):
        self.pulse_coordinator = OrganismPulseCoordinator(console_url)
        self.health_monitor = OrganHealthMonitor(console_url)
        self.finance_agent = FinanceAgent(console_url)
        self.pulse_history = []

    def start_pulse(self, workload_assessment="medium"):
        """Start a pulse at the beginning of a workforce run."""
        # Assess workload to determine pulse intensity
        if workload_assessment == "light":
            intensity = 0.3
        elif workload_assessment == "medium":
            intensity = 1.0
        elif workload_assessment == "heavy":
            intensity = 1.8
        else:
            intensity = 1.0

        # Generate the initial pulse
        pulse = self.pulse_coordinator.generate_unified_pulse(
            pulse_type="sync", intensity=intensity
        )

        # Record additional context
        pulse_context = {
            "workload": workload_assessment,
            "pulse_type": "sync",
            "start_time": datetime.now().isoformat(),
            "organism_wellness_before": self.pulse_coordinator.organism_wellness_score(),
            "finance_before": self.finance_agent._fetch_finance_health(),
            "health_before": self.health_monitor._generate_dummy_health()(),
        }

        self.pulse_history.append({
            "pulse": pulse,
            "context": pulse_context,
            "workflow_id": f"wf_{int(time.time())}"
        })

        print(f"🧬 Workforce Pulse Started")
        print(f"  Intensity: {intensity:.1f} (workload: {workload_assessment})")
        print(f"  Agents synchronized: {pulse['agents_affected']}")
        print(f"  Wellness before: {pulse_context['organism_wellness_before']}/100")
        print(f"  Pulse ID: {pulse['id']}")

        return pulse

    def complete_pulse(self, workflow_success=True, learnings=None):
        """Complete the pulse at the end of a workforce run."""
        if not self.pulse_history:
            print("⚠️  No active pulse to complete")
            return

        # Get the last pulse context
        last_entry = self.pulse_history[-1]
        pulse = last_entry["pulse"]
        context = last_entry["context"]

        # Calculate wellness change
        wellness_before = context["organism_wellness_before"]
        wellness_after = self.pulse_coordinator.organism_wellness_score()

        # Determine pulse adjustment
        wellness_change = wellness_after - wellness_before

        # Update pulse context
        context.update({
            "workflow_success": workflow_success,
            "wellness_after": wellness_after,
            "wellness_change": wellness_change,
            "learnings": learnnings or [],
            "end_time": datetime.now().isoformat(),
            "pulse_type": "complete"
        })

        # Generate resonance analysis
        resonance = self.pulse_coordinator.pulse_resonance_analysis()

        print(f"✅ Workforce Pulse Completed")
        print(f"  Workflow success: {workflow_success}")
        print(f"  Wellness before: {wellness_before}/100")
        print(f"  Wellness after: {wellness_after}/100")
        print(f"  Wellness change: {wellness_change:+.1f}/100")
        print(f"  Resonance score: {resonance['resonance_score']}/100")
        print(f"  Pulse ID: {pulse['id']}")

        if wellness_change > 5:
            print(f"  🟢 Positive wellness trend detected")
        elif wellness_change < -5:
            print(f"  🔴 Wellness dip detected - consider pulse adjustment")
        else:
            print(f"  🟡 Wellness stable")

        # Store learnings in context
        context["learnings_store"] = learnnings or []

        # Clear the completed pulse from active history
        self.pulse_history = self.pulse_history[:-1]

        return {
            "success": workflow_success,
            "wellness_before": wellness_before,
            "wellness_after": wellness_after,
            "wellness_change": wellness_change,
            "resonance_score": resonance['resonance_score']
        }

    def get_pulse_status(self):
        """Get current pulse status for workforce dashboard."""
        if self.pulse_history:
            last = self.pulse_history[-1]
            pulse = last["pulse"]
            context = last["context"]

            return {
                "active": True,
                "pulse_id": pulse["id"],
                "type": pulse["type"],
                "intensity": pulse["intensity"],
                "workload": context.get("workload", "unknown"),
                "wellness_before": context.get("organism_wellness_before", 0),
                "wellness_after": context.get("wellness_after", 0),
                "runtime": None
            }
        return {
            "active": False,
            "pulse_id": None,
            "type": None,
            "intensity": None,
            "workload": None,
            "wellness_before": None,
            "wellness_after": None,
            "runtime": None
        }


# Workforce integration command line
def run_integration_cli():
    """CLI entry point for workforce pulse integration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="IXPANSION Workforce Pulse Integration"
    )
    parser.add_argument(
        "action",
        choices=["start", "complete", "status", "full"],
        help="Action to perform",
    )
    parser.add_argument(
        "--workload",
        choices=["light", "medium", "heavy"],
        default="medium",
        help="Workload assessment (default: medium)",
    )
    parser.add_argument(
        "--success",
        action="store_true",
        help="Mark workflow as successful",
    )
    parser.add_argument(
        "--learnings",
        nargs="+",
        default=[],
        help="List of learnings from the workflow",
    )

    args = parser.parse_args()

    integration = WorkforcePulseIntegration()

    if args.action == "start":
        integration.start_pulse(workload_assessment=args.workload)
    elif args.action == "complete":
        result = integration.complete_pulse(
            workflow_success=args.success,
            learnings=args.learnings
        )
        return result
    elif args.action == "status":
        status = integration.get_pulse_status()
        print(json.dumps(status, indent=2))
    elif args.action == "full":
        # Full integration cycle
        print(">>> Starting workforce pulse integration cycle...")
        integration.start_pulse(workload_assessment=args.workload)

        # Simulate workflow execution
        print("")
        print(">>> Executing workforce run...")
        print("  • Task orchestration active")
        print("  • Agent coordination running")
        print("  • Health monitoring active")
        print("  • Finance tracking active")
        print("")
        print(">>> Completing workforce pulse integration...")

        result = integration.complete_pulse(
            workflow_success=args.success,
            learnings=args.learnings
        )

        print("")
        print(">>> Pulse integration cycle complete!")
        print(f"  Wellness change: {result.get('wellness_change', 0):+.1f}/100")
        print(f"  Resonance: {result.get('resonance_score', 0)}/100")


# CLI entry point
if __name__ == "__main__":
    run_integration_cli()
