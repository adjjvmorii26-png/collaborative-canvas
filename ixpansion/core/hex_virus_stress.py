"""
HexVirusStress Agent for IXPANSION

A specialized agent that simulates hex-encoded UTF-8 virus stress events on the IXPANSION organism.
Tests organism resilience against binary/encoded attack vectors that attempt to corrupt
or misinterpret data through hex encoding schemes.

Features:
- Hex-encoded virus simulation events
- UTF-8 decoding corruption stress

5 New Stress Event Types:
  1. hex_virus - Hex-encoded UTF-8 virus injection attempt
  2. data_corruption - Binary data corruption in payload streams
  3. resource_exhaustion - CPU/memory resource exhaustion attack
  4. cross_organ_trigger - Stress propagating across org boundaries
  5. timing_attack - Timing-based synchronization disruption

Severity Levels:
  - low: (50, 70)
  - medium: (65, 80)
  - high: (75, 95)
  - critical: (85, 100)

Expanded Stress Types List:
  hex_virus, data_corruption, resource_exhaustion, cross_organ_trigger, timing_attack
- Binary data flood simulations
- Organism data integrity analysis
- Hex string pattern recognition stress
- Recovery from encoding-based attacks
"""

import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime, timedelta


class HexVirusStressTest:
    """Simulates hex-encoded UTF-8 virus stress events."""

    HEX_VIRUS_EVENTS = {
        "hex_injection": {
            "organism_organ": "digestive",
            "base_severity": 15,
            "description": "Hex-encoded data injection attempt",
        },
        "utf8_corruption": {
            "organism_organ": "immune",
            "base_severity": 22,
            "description": "UTF-8 byte corruption attack",
        },
        "binary_flood": {
            "organism_organ": "cardiovascular",
            "base_severity": 28,
            "description": "Binary data flood through organism pipes",
        },
        "hex_overflow": {
            "organism_organ": "metabolic",
            "base_severity": 25,
            "description": "Hex string length overflow event",
        },
        "misencoded_unicode": {
            "organism_organ": "neurological",
            "base_severity": 18,
            "description": "Misencoded UTF-8 character sequence",
        },
        "hex_payload": {
            "organism_organ": "detoxification",
            "base_severity": 20,
            "description": "Hex-encoded payload execution attempt",
        },
        "checksum_bypass": {
            "organism_organ": "reproductive",
            "base_severity": 12,
            "description": "Hex checksum bypass attempt",
        },
        "endian_swap": {
            "organism_organ": "cardiovascular",
            "base_severity": 16,
            "description": "Byte order swap in organism data",
        },
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
        self.name = "HexVirusStressTest"
        self.version = "1.0.0"
        self.severity_multiplier = severity_multiplier
        self.stress_history = []
        self.recovery_profiles = {}
        self.current_stressors = {}

    def simulate_hex_virus_event(self, event_type=None, custom_params=None):
        """Simulate a hex-encoded virus stress event."""
        if event_type is None:
            event_types = list(self.HEX_VIRUS_EVENTS.keys())
            event_type = random.choice(event_types)

        if event_type not in self.HEX_VIRUS_EVENTS:
            return {"error": f"Unknown hex virus event: {event_type}"}

        event_config = self.HEX_VIRUS_EVENTS[event_type]
        base_severity = event_config["base_severity"] * self.severity_multiplier
        severity = min(100, base_severity + random.uniform(-3, 3))

        affected_organ = event_config["organism_organ"]

        # Get current scores
        organism = self._fetch_organism_health()
        current_score = organism.get(affected_organ, {}).get("score", 75)

        # Calculate new score under hex virus stress
        score_drop = int(severity * 0.75)
        new_score = max(
            self.ORGAN_SYSTEMS.get(affected_organ, {}).get("normal_range", [50, 90])[0] - 5,
            current_score - score_drop,
        )

        # Create event record
        event = {
            "id": f"hex_virus_{int(time.time())}_{event_type}",
            "type": event_type,
            "affected_organ": affected_organ,
            "severity": round(severity, 1),
            "initial_score": round(current_score, 1),
            "new_score": round(new_score, 1),
            "description": event_config["description"],
            "timestamp": datetime.now().isoformat(),
            "status": "active",
        }

        # Store in history
        self.stress_history.append(event)
        if event_type not in self.recovery_profiles:
            self.recovery_profiles[event_type] = []
        self.recovery_profiles[event_type].append(event)

        # Track current active stressors
        self.current_stressors[event["id"]] = event

        print(f"[HexVirusStress] 🦠 Hex virus simulated: {event_type}")
        print(f"  • Affected organ: {affected_organ}")
        print(f"  • Severity: {severity:.1f}/100")
        print(f"  • Initial score: {current_score} → {new_score}")
        print(f"  • Description: {event_config['description']}")

        return event

    def simulate_hex_decoding_failure(self, event_type=None):
        """Simulate hex decoding failure across multiple organs."""
        if event_type is None:
            event_types = list(self.HEX_VIRUS_EVENTS.keys())
            event_type = random.choice(event_types)

        if event_type not in self.HEX_VIRUS_EVENTS:
            return {"error": f"Unknown event: {event_type}"}

        # Get affected organ
        organ = self.HEX_VIRUS_EVENTS[event_type]["organism_organ"]

        # Simulate decoding failure affecting multiple organs
        organs_affected = [organ]
        # Add organs correlated to the primary organ
        correlation_map = {
            "digestive": ["immune", "metabolic"],
            "immune": ["digestive", "respiratory"],
            "cardiovascular": ["neurological", "metabolic"],
            "metabolic": ["cardiovascular", "digestive"],
            "neurological": ["cardiovascular", "immune"],
            "respiratory": ["immune"],
            "detoxification": ["immune"],
            "reproductive": [],
        }

        correlated = correlation_map.get(organ, [])
        for correlated_organ in correlated:
            if random.random() > 0.5:
                organs_affected.append(correlated_organ)

        # Get current scores
        organism = self._fetch_organism_health()

        # Calculate scores under hex decoding failure
        new_scores = {}
        for organ_name in organs_affected:
            current = organism.get(organ_name, {}).get("score", self.ORGAN_SYSTEMS.get(organ_name, {}).get("base_score", 75))
            # Hex corruption reduces score more severely
            score_drop = int(60 * 0.8)  # 60% severity base
            new_score = max(
                self.ORGAN_SYSTEMS.get(organ_name, {}).get("normal_range", [50, 90])[0] - 10,
                current - score_drop,
            )
            new_scores[organ_name] = round(new_score, 1)

        # Update organism scores
        for organ_name, new_score in new_scores.items():
            organism[organ_name]["score"] = new_score

        event = {
            "id": f"hex_decode_fail_{int(time.time())}",
            "type": f"hex_decode_{event_type}",
            "affected_organ": "+".join(organs_affected) if len(organs_affected) > 1 else organs_affected[0],
            "severity": min(100, 60 + random.uniform(-3, 3)),
            "organs_affected": organs_affected,
            "new_scores": new_scores,
            "description": f"Hex decoding failure: {self.HEX_VIRUS_EVENTS[event_type]['description']}",
            "timestamp": datetime.now().isoformat(),
            "status": "active",
        }

        # Store in history
        self.stress_history.append(event)
        if event_type not in self.recovery_profiles:
            self.recovery_profiles[event_type] = []
        self.recovery_profiles[event_type].append(event)

        self.current_stressors[event["id"]] = event

        print(f"[HexVirusStress] 🦠 Hex decoding failure: {event_type}")
        print(f"  • Affected organs: {', '.join(organs_affected)}")
        for organ, score in new_scores.items():
            print(f"  • {organ}: {score}")
        print(f"  • Description: {event['description']}")

        return event

    def _fetch_organism_health(self):
        """Fetch organism health from console."""
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
        for organ, config in {
            "cardiovascular": {"base_score": 75, "normal_range": (60, 90)},
            "neurological": {"base_score": 80, "normal_range": (70, 95)},
            "digestive": {"base_score": 70, "normal_range": (55, 85)},
            "respiratory": {"base_score": 85, "normal_range": (75, 95)},
            "immune": {"base_score": 72, "normal_range": (50, 90)},
            "metabolic": {"base_score": 78, "normal_range": (65, 92)},
            "detoxification": {"base_score": 68, "normal_range": (40, 88)},
            "reproductive": {"base_score": 82, "normal_range": (60, 95)},
        }.items():
            scores[organ] = {"score": config["base_score"], "status": "stable"}
        return scores

    def calculate_hex_resilience(self, organ=None):
        """Calculate resilience against hex virus attacks."""
        relevant_stresses = self.stress_history
        if organ:
            relevant_stresses = [s for s in relevant_stresses if s["affected_organ"] == organ or organ in s.get("affected_organ", "")]

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

    def generate_hex_virus_report(self, include_history=10):
        """Generate hex virus stress report."""
        # Calculate current organ scores under stress
        scores = {}
        for organ in self.ORGAN_SYSTEMS:
            active_on_organ = [s for s in self.stress_history if s["affected_organ"] == organ and s["status"] == "active"]

            base = self.ORGAN_SYSTEMS[organ]["base_score"]
            if active_on_organ:
                avg_severity = sum(s["severity"] for s in active_on_organ) / len(active_on_organ)
                score = max(self.ORGAN_SYSTEMS[organ]["normal_range"][0] - 5,
                           base - (avg_severity * 0.5))
            else:
                score = base
            scores[organ] = round(score, 1)

        resilience = self.calculate_hex_resilience()

        recent_stresses = self.stress_history[-include_history:] if self.stress_history else []

        lines = []
        lines.append("=" * 70)
        lines.append("🦠 IXPANSION HEX VIRUS STRESS TEST REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Stress Test Agent: {self.name} v{self.version}")
        lines.append(f"Hex Resilience Coefficient: {resilience}/100")
        lines.append("")

        lines.append(f"⚠️  Active Hex Virus Stressors: {len(self.current_stressors)}")
        lines.append("-" * 70)

        if self.current_stressors:
            for event in self.current_stressors.values():
                icon = "🔴" if event["severity"] > 30 else "🟠" if event["severity"] > 15 else "🟡"
                lines.append(f"  {icon} {event['type']:25s} → {event['affected_organ']:20s} "
                           f"Severity: {event['severity']:.1f} | Recovery: {event['recovery_hours'] if 'recovery_hours' in event else 'N/A'}h")
        else:
            lines.append("  ✅ No active hex virus stressors")

        lines.append("")

        lines.append("📊 Organism Organ Scores Under Hex Stress:")
        lines.append("-" * 70)
        sorted_organisms = sorted(scores.items(), key=lambda x: x[1])
        for organ, score in sorted_organisms:
            config = self.ORGAN_SYSTEMS[organ]
            normal = config["normal_range"]
            status = "🔴 Critical" if score < normal[0] + 5 else "🟠 Warning" if score < normal[0] else "✅ Stable"
            lines.append(f"  {status} {organ:20s} {score:5.1f} (normal: {normal[0]}-{normal[1]})")

        lines.append("")

        lines.append(f"📝 Hex Virus History (last {include_history}):")
        lines.append("-" * 70)
        if recent_stresses:
            for event in recent_stresses:
                severity_color = "🔴" if event["severity"] > 30 else "🟠" if event["severity"] > 15 else "🟡"
                lines.append(f"  {severity_color} {event['type']:25s} → {event['affected_organ']:20s} "
                           f"{event['severity']:.1f}sv | {event['status']}")
        else:
            lines.append("  ✅ No recorded hex virus events")

        lines.append("")

        lines.append("💡 RECOMMENDATIONS:")
        lines.append("-" * 70)

        critical_events = [s for s in self.current_stressors.values() if s["severity"] > 30]
        if critical_events:
            lines.append("  🚨 Critical: Immediate hex decodification required")
            for event in critical_events:
                lines.append(f"    - {event['type']}: {event['description']}")

        if resilience < 50:
            lines.append("  ⚠️  Low hex resilience: Consider encoding validation protocols")

        lines.append("  🔐 Hex validation: Implement input sanitization for hex strings")
        lines.append("  🔐 UTF-8 validation: Ensure proper byte sequence encoding")
        lines.append("  🔐 Binary limits: Set maximum data flow thresholds")
        lines.append("  ✅ Baseline: Maintain regular health monitoring cycles")

        lines.append("")
        lines.append("=" * 70)
        lines.append("End of Hex Virus Stress Test Report")
        lines.append("=" * 70)

        return "\n".join(lines)

    def run_hex_virus_cycle(self, event_types=None, recovery=True):
        """Run a complete hex virus stress test cycle."""
        print("=" * 70)
        print(f"IXPANSION Hex Virus Stress Test Cycle")
        print(f"Agent: {self.name} v{self.version}")
        print("=" * 70)
        print("")
        print("Simulating hex-encoded virus events on the IXPANSION organism...")
        print("")

        if event_types is None:
            event_types = list(self.HEX_VIRUS_EVENTS.keys())

        results = []
        for etype in event_types:
            event = self.simulate_hex_virus_event(event_type=etype)
            results.append(event)

        print("")

        report = self.generate_hex_virus_report()
        print(report)

        if recovery and self.current_stressors:
            print("")
            print(">>> Initiating simulated hex virus recovery...")
            recovery_results = self.simulate_hex_decoding_failure()

            # Generate post-recovery report
            post_report = self.generate_hex_virus_report()
            print("")
            print(">>> Post-Hex-Virus Recovery Status:")
            # Print just key lines
            post_lines = post_report.split("\n")
            for line in post_lines[20:35]:
                print(line)

        return {
            "cycle_timestamp": datetime.now().isoformat(),
            "events_simulated": len(results),
            "pre_report": self.generate_hex_virus_report(),
            "recovery_results": recovery_results if recovery and self.current_stressors else None,
            "post_report": self.generate_hex_virus_report() if recovery else None,
            "resilience": self.calculate_hex_resilience(),
        }


# CLI interface
if __name__ == "__main__":
    import sys

    tester = HexVirusStressTest()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "run":
            event_types = sys.argv[2].split(",") if len(sys.argv) > 2 else None
            recovery = len(sys.argv) <= 3 or sys.argv[3].lower() != "no-recovery"
            result = tester.run_hex_virus_cycle(event_types=event_types, recovery=recovery)
            print("")
            print("✅ Hex virus test cycle complete.")
            print(f"   Events: {result['events_simulated']}")

        elif command == "single":
            event_type = sys.argv[2] if len(sys.argv) > 2 else None
            event = tester.simulate_hex_virus_event(event_type=event_type)
            print(f"  Hex virus: {event.get('type', 'unknown')}")

        elif command == "recover":
            stress_id = sys.argv[2] if len(sys.argv) > 2 else None
            results = tester.simulate_hex_decoding_failure(stress_event_id=stress_id)
            print(f"  Hex recovery simulation complete.")

        elif command == "resilience":
            organ = sys.argv[2] if len(sys.argv) > 2 else None
            res = tester.calculate_hex_resilience(organ=organ)
            print(f"  Hex resilience coefficient: {res}/100")

        elif command == "report":
            inc = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            report = tester.generate_hex_virus_report(include_history=inc)
            print(report)

        elif command == "help" or command in ("--help", "-h"):
            print("""
IXPANSION HexVirusStress Commands:
  check                    - Show this help message
  run [events] [no-recovery]  - Run hex virus stress test cycle
  single <event_type>      - Simulate single hex virus event
  recover <stress_id>      - Simulate recovery from event
  resilience [organ]       - Calculate hex resilience coefficient
  report [history_count]   - Generate hex virus report
  help                     - Show this help

Hex virus event types: """ + ', '.join(tester.HEX_VIRUS_EVENTS.keys()))

        else:
            print(f"Unknown command: {command}")
            print("Use 'check help' for available commands")
    else:
        print("=" * 70)
        print("IXPANSION HexVirusStress - Default Cycle")
        print("=" * 70)
        print("")
        print("Simulating hex-encoded virus events on the IXPANSION organism...")
        print("")
        result = tester.run_hex_virus_cycle()
        print("")
        print("✅ Default hex virus test cycle complete!")
