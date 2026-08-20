"""
OrganismStressTest Agent for IXPANSION

A specialized agent that simulates stress events on the IXPANSION organism,
measures recovery times, resilience coefficients, and cross-organ impact analysis.
"""

import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime, timedelta


class OrganismStressTest:
    """Simulates and measures stress on the IXPANSION organism."""

    # Stress event types with severity and recovery baselines
    STRESS_EVENTS = {
        "cash_flow_crisis": {
            "organ": "metabolic",
            "base_severity": 25,
            "recovery_base": 12,
            "description": "Revenue shortfall or funding gap",
        },
        "api_key_expiry": {
            "organ": "detoxification",
            "base_severity": 20,
            "recovery_base": 6,
            "description": "API authentication token expiration",
        },
        "recipe_failure": {
            "organ": "immune",
            "base_severity": 15,
            "recovery_base": 4,
            "description": "Content generation pipeline failure",
        },
        "organ_disruption": {
            "organ": "random",
            "base_severity": 30,
            "recovery_base": 24,
            "description": "Primary organ system simulation failure",
        },
        "concurrent_stressors": {
            "organ": "multiple",
            "base_severity": 35,
            "recovery_base": 48,
            "description": "Multiple stress events simultaneous",
        },
        "cognitive_overload": {
            "organ": "neurological",
            "base_severity": 18,
            "recovery_base": 8,
            "description": "Agent decision fatigue or context window overflow",
        },
        "network_partition": {
            "organ": "immune",
            "base_severity": 22,
            "recovery_base": 16,
            "description": "Loss of connectivity or isolated subsystems",
        },
        "data_corruption": {
            "organ": "detoxification",
            "base_severity": 28,
            "recovery_base": 20,
            "description": "Organism data integrity compromise",
        }
    }

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

    def __init__(self, console_url="http://127.0.0.1:8890", severity_multiplier=1.0):
        self.console_url = console_url
        self.name = "OrganismStressTest"
        self.version = "1.0.0"
        self.severity_multiplier = severity_multiplier
        self.stress_history = []
        self.recovery_profiles = {}
        self.current_stressors = {}

    def simulate_stress_event(self, event_type=None, custom_params=None):
        """Simulate a stress event on the organism."""
        if event_type is None:
            event_types = list(self.STRESS_EVENTS.keys())
            event_type = random.choice(event_types)

        if event_type not in self.STRESS_EVENTS:
            return {"error": f"Unknown stress event type: {event_type}"}

        event_config = self.STRESS_EVENTS[event_type]
        base_severity = event_config["base_severity"] * self.severity_multiplier
        recovery_base = event_config["recovery_base"]

        # Generate severity score (0-100 scale)
        severity = min(100, base_severity + random.uniform(-5, 5))

        # Determine affected organ
        if event_config["organ"] == "random":
            affected_organ = random.choice(list(self.ORGAN_SYSTEMS.keys()))
        elif event_config["organ"] == "multiple":
            affected_organs = random.sample(
                list(self.ORGAN_SYSTEMS.keys()), k=min(3, len(self.ORGAN_SYSTEMS))
            )
            affected_organ = "+".join(affected_organs)
        else:
            affected_organ = event_config["organ"]

        # Calculate initial score drop
        initial_score = self.ORGAN_SYSTEMS.get(affected_organ, {}).get("base_score", 70)
        score_drop = int(severity * 0.8)
        new_score = max(
            self.ORGAN_SYSTEMS.get(affected_organ, {}).get("normal_range", [50, 90])[0] - 5,
            initial_score - score_drop,
        )

        # Create stress event record
        event = {
            "id": f"{event_type}_{int(time.time())}",
            "type": event_type,
            "affected_organ": affected_organ,
            "severity": round(severity, 1),
            "initial_score": round(initial_score, 1),
            "new_score": round(new_score, 1),
            "recovery_hours": int(recovery_base * random.uniform(0.8, 1.5)),
            "description": event_config["description"],
            "timestamp": datetime.now().isoformat(),
            "status": "active",
            "stress_multiplier": self.severity_multiplier,
        }

        # Store in history
        self.stress_history.append(event)
        if event_type not in self.recovery_profiles:
            self.recovery_profiles[event_type] = []
        self.recovery_profiles[event_type].append(event)

        # Track current active stressors
        self.current_stressors[event["id"]] = event

        print(f"[OrganismStressTest] Simulated stress event: {event_type}")
        print(f"  Affected organ: {affected_organ}")
        print(f"  Severity: {severity:.1f}/100")
        print(f"  Initial score: {initial_score} -> {new_score}")
        print(f"  Estimated recovery: {event['recovery_hours']} hours")
        print(f"  Description: {event_config['description']}")

        return event

    def simulate_recovery(self, stress_event_id=None):
        """Simulate recovery from a stress event."""
        if stress_event_id is None:
            active_ids = list(self.current_stressors.keys())
        elif stress_event_id not in self.current_stressors:
            return f"Stress event {stress_event_id} not found"
        else:
            active_ids = [stress_event_id]

        results = []
        for sid in active_ids:
            event = self.current_stressors[sid]
            organ = event["affected_organ"]

            recovery_hours = event["recovery_hours"]
            elapsed = random.uniform(0.1, 0.9) * recovery_hours
            recovery_progress = min(100, (elapsed / recovery_hours) * 100)

            organ_config = self.ORGAN_SYSTEMS.get(organ, {})
            base_score = organ_config.get("base_score", 70)
            normal_low = organ_config.get("normal_range", [50, 90])[0]

            recovery_amount = (base_score - event["new_score"]) * (recovery_progress / 100)
            recovered_score = min(base_score, event["new_score"] + recovery_amount)

            event["status"] = "recovered"
            event["recovery_progress"] = round(recovery_progress, 1)
            event["recovered_score"] = round(recovered_score, 1)
            event["recovery_timestamp"] = datetime.now().isoformat()

            del self.current_stressors[sid]

            results.append(
                {
                    "event_id": sid,
                    "event_type": event["type"],
                    "affected_organ": organ,
                    "recovery_progress": recovery_progress,
                    "recovered_score": recovered_score,
                    "hours_estimated": recovery_hours,
                }
            )

            print(f"[OrganismStressTest] Recovery simulated: {event['type']}")
            print(f"  Organ: {organ}")
            print(f"  Recovery progress: {recovery_progress:.1f}%")
            print(f"  Recovered score: {recovered_score:.1f}")

        return results

    def calculate_resilience_coefficient(self, organ=None):
        """Calculate resilience score for an organ or the whole organism."""
        relevant_stresses = self.stress_history
        if organ:
            relevant_stresses = [
                s for s in relevant_stresses if s["affected_organ"] == organ
            ]

        if not relevant_stresses:
            return 100.0

        total_severity = sum(s["severity"] for s in relevant_stresses)
        avg_severity = total_severity / len(relevant_stresses)

        active_count = len([s for s in relevant_stresses if s["status"] == "active"])
        recovered_count = len(relevant_stresses) - active_count
        recovery_rate = recovered_count / len(relevant_stresses) if relevant_stresses else 1.0

        severity_penalty = avg_severity * 0.3
        frequency_penalty = (active_count / len(relevant_stresses)) * 20
        recovery_bonus = recovered_count * 5

        resilience = max(0, min(100, 100 - severity_penalty - frequency_penalty + recovery_bonus))
        return round(resilience, 1)

    def check_cross_organ_impact(self, affected_organ):
        """Analyze how stress on one organ impacts others."""
        impacted = []

        correlation_map = {
            "cardiovascular": ["respiratory", "metabolic"],
            "neurological": ["digestive", "immune"],
            "metabolic": ["digestive", "cardiovascular"],
            "immune": ["respiratory", "detoxification"],
            "digestive": ["neurological", "metabolic"],
            "respiratory": ["cardiovascular", "immune"],
            "detoxification": ["immune"],
            "reproductive": [],
        }

        correlated = correlation_map.get(affected_organ, [])

        for correlated_organ in correlated:
            recent_stresses = [
                s for s in self.stress_history
                if s["affected_organ"] == correlated_organ
            ]
            stress_count = len(recent_stresses)

            if stress_count > 0:
                impact_level = (
                    "high"
                    if stress_count > 3
                    else "moderate" if stress_count > 1 else "low"
                )
                impacted.append(
                    {
                        "organ": correlated_organ,
                        "recent_stress_count": stress_count,
                        "impact_level": impact_level,
                    }
                )

        return impacted

    def generate_stress_report(self, include_history=10, include_recommendations=True):
        """Generate comprehensive stress analysis report."""
        scores = {}
        for organ in self.ORGAN_SYSTEMS:
            active_on_organ = [
                s for s in self.stress_history
                if s["affected_organ"] == organ and s["status"] == "active"
            ]

            base = self.ORGAN_SYSTEMS[organ]["base_score"]
            if active_on_organ:
                avg_severity = sum(s["severity"] for s in active_on_organ) / len(active_on_organ)
                score = max(
                    self.ORGAN_SYSTEMS[organ]["normal_range"][0] - 5,
                    base - (avg_severity * 0.5),
                )
            else:
                score = base
            scores[organ] = round(score, 1)

        resilience = self.calculate_resilience_coefficient()

        recent_stresses = self.stress_history[-include_history:] if self.stress_history else []

        lines = []
        lines.append("=" * 70)
        lines.append("IXPANSION ORGANISM STRESS TEST REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append(
            f"Stress Test Agent: {self.name} v{self.version}"
        )
        lines.append(f"Overall Resilience Coefficient: {resilience}/100")
        lines.append("")

        active_stressors = list(self.current_stressors.values())
        lines.append(f"Active Stressors: {len(active_stressors)}")
        lines.append("-" * 70)

        if active_stressors:
            for event in active_stressors:
                icon = "🔴" if event["severity"] > 30 else "🟠" if event["severity"] > 15 else "🟡"
                lines.append(
                    f"  {icon} {event['type']:25s} -> {event['affected_organ']:20s} "
                    f"Severity: {event['severity']:.1f} | "
                    f"Recovery: {event['recovery_hours']}h"
                )
        else:
            lines.append("  ✅ No active stressors")

        lines.append("")

        lines.append("Organ Scores Under Stress:")
        lines.append("-" * 70)
        sorted_organisms = sorted(scores.items(), key=lambda x: x[1])
        for organ, score in sorted_organisms:
            config = self.ORGAN_SYSTEMS[organ]
            normal = config["normal_range"]
            status = (
                "🔴 Critical"
                if score < normal[0] + 5
                else "🟠 Warning" if score < normal[0] else "✅ Stable"
            )
            lines.append(f"  {status} {organ:20s} {score:5.1f} (normal: {normal[0]}-{normal[1]})")

        lines.append("")

        if active_stressors:
            primary_affected = active_stressors[0]["affected_organ"]
            if "/" in primary_affected:
                for pa in primary_affected.split("/"):
                    impact = self.check_cross_organ_impact(pa)
                    if impact:
                        lines.append(f"Cross-organ impact on {pa}:")
                        for imp in impact:
                            lines.append(
                                f"    {imp['impact_level']} impact: {imp['organ']} "
                                f"( {imp['recent_stress_count']} recent stresses)"
                            )
            else:
                impact = self.check_cross_organ_impact(primary_affected)
                if impact:
                    lines.append(f"Cross-organ impact on {primary_affected}:")
                    for imp in impact:
                        lines.append(
                            f"    {imp['impact_level']} impact: {imp['organ']} "
                            f"( {imp['recent_stress_count']} recent stresses)"
                        )

        lines.append("")

        lines.append(f"Stress Event History (last {include_history}):")
        lines.append("-" * 70)
        if recent_stresses:
            for event in recent_stresses:
                severity_color = "🔴" if event["severity"] > 30 else "🟠" if event["severity"] > 15 else "🟡"
                lines.append(
                    f"  {severity_color} {event['type']:25s} -> {event['affected_organ']:20s} "
                    f"{event['severity']:.1f}sv | {event['status']}"
                )
        else:
            lines.append("  ✅ No recorded stress events")

        lines.append("")

        if include_recommendations:
            lines.append("RECOMMENDATIONS:")
            lines.append("-" * 70)

            critical_active = [s for s in active_stressors if s["severity"] > 30]
            if critical_active:
                lines.append("  🚨 Critical: Immediate attention required")
                for event in critical_active:
                    lines.append(f"    - {event['type']}: {event['description']}")

            if resilience < 50:
                lines.append("  ⚠️  Low resilience: Consider stress reduction protocols")

            event_types = set(s["type"] for s in self.stress_history)
            if "cash_flow_crisis" in event_types:
                lines.append("  💡 Cash flow: Review revenue streams and financial buffers")
            if "api_key_expiry" in event_types:
                lines.append("  🔐 API keys: Implement auto-rotation before expiry")
            if "recipe_failure" in event_types:
                lines.append("  📦 Recipes: Review pipeline robustness and error handling")
            if "concurrent_stressors" in event_types:
                lines.append("  🌪️ Concurrent: Implement stress queuing and prioritization")

            lines.append("  ✅ Baseline: Maintain regular health monitoring cycles")
            lines.append("  ✅ Baseline: Schedule stress tests during maintenance windows")

        lines.append("")
        lines.append("=" * 70)
        lines.append("End of Stress Test Report")
        lines.append("=" * 70)

        return "\n".join(lines)

    def run_stress_test_cycle(self, event_types=None, recovery=True):
        """Run a complete stress test cycle."""
        print("=" * 70)
        print("IXPANSION Organism Stress Test Cycle")
        print("")
        print("Simulating stress events on the IXPANSION organism...")
        print("")

        if event_types is None:
            event_types = list(self.STRESS_EVENTS.keys())

        results = []
        for etype in event_types:
            event = self.simulate_stress_event(event_type=etype)
            results.append(event)

        print("")

        pre_report = self.generate_stress_report()
        print(pre_report)

        if recovery and self.current_stressors:
            print("")
            print(">>> Initiating simulated recovery...")
            recovery_results = self.simulate_recovery()

            post_report = self.generate_stress_report()
            print("")
            print(">>> Post-Recovery Status:")
            print(post_report)

        return {
            "cycle_timestamp": datetime.now().isoformat(),
            "events_simulated": len(results),
            "pre_report": pre_report,
            "recovery_results": recovery_results if recovery and self.current_stressors else None,
            "post_report": self.generate_stress_report() if recovery else None,
        }


# CLI interface
if __name__ == "__main__":
    import sys

    tester = OrganismStressTest()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "run":
            event_types = (
                sys.argv[2].split(",") if len(sys.argv) > 2 else None
            )
            recovery = len(sys.argv) <= 3 or sys.argv[3].lower() != "no-recovery"
            result = tester.run_stress_test_cycle(
                event_types=event_types, recovery=recovery
            )
            print("")
            print("✅ Stress test cycle complete.")
            print(f"   Events: {result['events_simulated']}")

        elif command == "single":
            event_type = sys.argv[2] if len(sys.argv) > 2 else None
            event = tester.simulate_stress_event(event_type=event_type)
            print(f" Stress event: {event.get('type', 'unknown')}")

        elif command == "recover":
            stress_id = sys.argv[2] if len(sys.argv) > 2 else None
            results = tester.simulate_recovery(stress_event_id=stress_id)
            print(f" Recovery simulation complete.")

        elif command == "resilience":
            organ = sys.argv[2] if len(sys.argv) > 2 else None
            res = tester.calculate_resilience_coefficient(organ=organ)
            print(f" Resilience coefficient: {res}/100")

        elif command == "report":
            inc = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            report = tester.generate_stress_report(include_history=inc)
            print(report)

        elif command == "help" or command in ("--help", "-h"):
            print(
                "IXPANSION OrganismStressTest Commands:\n"
                "  check                    - Show this help message\n"
                "  run [events] [no-recovery]  - Run stress test cycle\n"
                "  single <event_type>      - Simulate single stress event\n"
                "  recover <stress_id>      - Simulate recovery from event\n"
                "  resilience [organ]       - Calculate resilience coefficient\n"
                "  report [history_count]   - Generate stress report\n"
                "  help                     - Show this help\n\n"
                f"Event types: {', '.join(tester.STRESS_EVENTS.keys())}"
            )

        else:
            print(f"Unknown command: {command}")
            print("Use 'check help' for available commands")
    else:
        print("=" * 70)
        print("IXPANSION OrganismStressTest - Default Cycle")
        print("=" * 70)
        print("")
        print("Simulating stress events on the IXPANSION organism...")
        print("")
        result = tester.run_stress_test_cycle()
        print("")
        print("✅ Default stress test cycle complete!")
