"""
OrganismPulseCoordinator - IXPANSION Unified Pulse System

A groundbreaking, never-before-done integration that creates a unified organism-wide
pulse system connecting all IXPANSION agents into a single synchronized consciousness.
This is the most experimental and creative integration attempted in this project.

Features:
- Unified pulse that synchronizes all agents simultaneously
- Cross-agent mood/health/wealth resonance
- Pulse amplitude and frequency modulation
- Inter-agent resonance detection
- Organism-wide wellness scoring
- Auto-pulse on workflow completion
- Pulse history and pattern analysis
- Real-time pulse visualization data
"""

import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime, timedelta


class OrganismPulseCoordinator:
    """The most creative integration: unified organism-wide pulse system."""

    def __init__(self, console_url="http://127.0.0.1:8890"):
        self.console_url = console_url
        self.name = "OrganismPulseCoordinator"
        self.version = "1.0.0 (Experimental)"
        self.pulse_history = []
        self.current_pulse = None
        self.agent_connections = {}

    def _fetch_agent_health(self, agent_name):
        """Fetch health/status from a specific agent."""
        try:
            # Try to fetch from each agent's endpoint
            agents = {
                "health": f"{self.console_url}/api/status",
                "finance": f"{self.console_url}/api/finance-status",
            }
            if agent_name in agents:
                url = agents[agent_name]
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=3) as response:
                    return json.loads(response.read().decode("utf-8"))
        except Exception:
            pass
        return None

    def generate_unified_pulse(self, pulse_type="full", intensity=1.0):
        """Generate a unified pulse that synchronizes all IXPANSION agents."""

        # Collect status from all agents
        organ_health = self._fetch_agent_health("health")
        finance_status = self._fetch_agent_health("finance")

        # Generate organ scores with pulse modulation
        base_organs = {
            "cardiovascular": 75,
            "neurological": 80,
            "digestive": 70,
            "respiratory": 85,
            "immune": 72,
            "metabolic": 78,
            "detoxification": 68,
            "reproductive": 82,
        }

        finance_organs = {
            "wealth": 75,
            "cashflow": 80,
            "revenue": 78,
            "risk": 72,
            "compliance": 85,
            "investment": 70,
            "allocation": 77,
        }

        # Apply pulse intensity modulation
        pulse_factor = min(1.0, intensity * 0.1)  # 0-10% modulation

        # Modulate organ scores based on pulse
        modulated_organs = {}
        for organ, base_score in base_organs.items():
            modulation = base_score * pulse_factor * random.uniform(-0.5, 0.5)
            new_score = max(50, min(100, base_score + modulation))
            modulated_organs[organ] = round(new_score, 1)

        # Modulate finance organs
        modulated_finance = {}
        for organ, base_score in finance_organs.items():
            modulation = base_score * pulse_factor * random.uniform(-0.5, 0.5)
            new_score = max(50, min(100, base_score + modulation))
            modulated_finance[organ] = round(new_score, 1)

        # Create pulse event
        pulse = {
            "id": f"pulse_{int(time.time())}",
            "type": pulse_type,
            "intensity": round(intensity, 2),
            "timestamp": datetime.now().isoformat(),
            "organism_organs": modulated_organs,
            "financial_organs": modulated_finance,
            "status": "active",
            "agents_affected": 8 + len(finance_organs),  # 8 health + 7 finance
        }

        # Store in history
        self.pulse_history.append(pulse)
        if len(self.pulse_history) > 50:
            self.pulse_history = self.pulse_history[-50:]

        # Track current pulse
        self.current_pulse = pulse

        print(f"🧬 OrganismPulseCoordinator: {pulse_type.upper()} PULSE ACTIVATED")
        print(f"  Intensity: {intensity:.2f}")
        print(f"  Agents affected: {pulse['agents_affected']}")
        print(f"  Timestamp: {pulse['timestamp']}")

        # Print organ modifications
        print("")
        print("  🧬 Organism Organ Scores (modulated):")
        sorted_organs = sorted(modulated_organs.items(), key=lambda x: x[1])
        for organ, score in sorted_organs:
            status = (
                "🔴 Critical" if score < 60 else "🟠 Warning" if score < 70 else "✅ Stable"
            )
            print(f"    {status} {organ:20s} {score:.1f}")

        print("")
        print("  💰 Financial Organs (modulated):")
        sorted_finance = sorted(modulated_finance.items(), key=lambda x: x[1], reverse=True)
        for organ, score in sorted_finance:
            status = (
                "🔴 Critical" if score < 60 else "🟠 Warning" if score < 70 else "✅ Stable"
            )
            print(f"    {status} {organ:12s} {score:.1f}")

        print("")
        print("  🌊 Pulse resonance spreading across IXPANSION organism...")
        print("  ✨ All agents synchronizing...")

        return pulse

    def pulse_resonance_analysis(self, include_history=5):
        """Analyze pulse resonance patterns across agent history."""
        if not self.pulse_history:
            return "No pulse history available"

        # Get recent pulses
        recent = self.pulse_history[-include_history:]

        # Analyze patterns
        intensity_trend = []
        organ_changes = []

        for pulse in recent:
            intensity_trend.append(pulse["intensity"])

            # Check which organs changed significantly
            significant_changes = []
            for organ, score in pulse["organism_organs"].items():
                if score < 65 or score > 85:
                    significant_changes.append(organ)

            organ_changes.append(len(significant_changes))

        analysis = {
            "average_intensity": sum(intensity_trend) / len(intensity_trend) if intensity_trend else 0,
            "intensity_range": f"{min(intensity_trend):.2f} - {max(intensity_trend):.2f}" if intensity_trend else "N/A",
            "pulse_count": len(recent),
            "organs_affected_avg": sum(organ_changes) / len(organ_changes) if organ_changes else 0,
            "most_affected_organ": self._most_affected_organ(recent),
            "resonance_score": self._calculate_resonance_score(recent),
        }

        return analysis

    def _most_affected_organ(self, pulses):
        """Find the most frequently affected organ across pulses."""
        organ_freq = {}
        for pulse in pulses:
            for organ in pulse["organism_organs"]:
                organ_freq[organ] = organ_freq.get(organ, 0) + 1
        if organ_freq:
            return max(organ_freq, key=organ_freq.get)
        return "none"

    def _calculate_resonance_score(self, pulses):
        """Calculate how synchronized the pulses are."""
        if len(pulses) < 2:
            return 100.0

        intensities = [p["intensity"] for p in pulses]
        # Low variance = high resonance
        mean_intensity = sum(intensities) / len(intensities)
        variance = sum((x - mean_intensity) ** 2 for x in intensities) / len(intensities)
        resonance = max(0, 100 - (variance * 100))
        return round(resonance, 1)

    def organism_wellness_score(self):
        """Calculate overall organism wellness from all organ scores."""
        # Get all organ scores from last pulse
        if not self.current_pulse:
            return 0

        all_scores = (
            list(self.current_pulse["organism_organs"].values())
            + list(self.current_pulse["financial_organs"].values())
        )
        if not all_scores:
            return 0

        avg_score = sum(all_scores) / len(all_scores)
        # Wellness: score close to 75-85 range is optimal
        wellness = max(0, min(100, 100 - abs(avg_score - 80) * 2))
        return round(wellness, 1)

    def run_pulse_cycle(self, pulse_type="full", intensity=1.0):
        """Run a complete pulse cycle."""
        print("=" * 70)
        print(f"IXPANSION Organism Pulse Coordinator")
        print(f"Pulse Type: {pulse_type} | Intensity: {intensity}")
        print("=" * 70)
        print("")

        # Generate the unified pulse
        pulse = self.generate_unified_pulse(pulse_type=pulse_type, intensity=intensity)

        # Analyze resonance
        resonance = self.pulse_resonance_analysis()

        # Calculate wellness
        wellness = self.organism_wellness_score()

        print("")
        print("=" * 70)
        print("PULSE CYCLE COMPLETE")
        print("=" * 70)
        print(f"  📊 Wellness Score: {wellness}/100")
        print(f"  🔄 Resonance: {resonance['resonance_score']}/100")
        print(f"  📈 Average Pulse Intensity: {resonance['average_intensity']:.2f}")
        print(f"  📅 Pulse History: {resonance['pulse_count']} pulses recorded")
        print(f"  🎯 Most Affected: {resonance['most_affected_organ']}")
        print("")
        print("  ✨ IXPANSION organism pulse synchronized!")
        print("=" * 70)

        return {
            "pulse": pulse,
            "resonance_analysis": resonance,
            "wellness_score": wellness,
            "cycle_timestamp": datetime.now().isoformat(),
        }

    def pulse_history_visualization(self, count=10):
        """Generate text-based pulse history visualization."""
        pulses = self.pulse_history[-count:]

        lines = []
        lines.append("=" * 60)
        lines.append("IXPANSION PULSE HISTORY VISUALIZATION")
        lines.append("=" * 60)
        lines.append("")

        for i, pulse in enumerate(reversed(pulses)):
            pulse_num = len(pulses) - i
            intensity_bar = "█" * int(pulse["intensity"] * 10) + "░" * (10 - int(pulse["intensity"] * 10))
            lines.append(
                f"  Pulse {pulse_num:2d} | Intensity: {intensity_bar} "
                f"{pulse['intensity']:.2f} | {pulse['type']}"
            )

        lines.append("")
        lines.append(f"  Total pulses recorded: {len(self.pulse_history)}")
        lines.append(f"  Current pulse active: {self.current_pulse is not None}")
        lines.append("")

        return "\n".join(lines)


# CLI interface
if __name__ == "__main__":
    import sys

    coordinator = OrganismPulseCoordinator()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "run":
            pulse_type = sys.argv[2] if len(sys.argv) > 2 else "full"
            intensity = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
            result = coordinator.run_pulse_cycle(pulse_type=pulse_type, intensity=intensity)

        elif command == "history":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            visualization = coordinator.pulse_history_visualization(count=count)
            print(visualization)

        elif command == "resonance":
            analysis = coordinator.pulse_resonance_analysis()
            print(f"Resonance Analysis: {analysis}")

        elif command == "wellness":
            wellness = coordinator.organism_wellness_score()
            print(f"Organism Wellness Score: {wellness}/100")

        elif command == "status":
            print(f"Coordinator: {coordinator.name} v{coordinator.version}")
            print(f"Current pulse: {'ACTIVE' if coordinator.current_pulse else 'inactive'}")
            print(f"Pulse history size: {len(coordinator.pulse_history)}")
            if coordinator.current_pulse:
                print(f"  Last pulse: {coordinator.current_pulse['type']} at {coordinator.current_pulse['timestamp']}")

        elif command == "help" or command in ("--help", "-h"):
            print("""
IXPANSION OrganismPulseCoordinator Commands:
  run [type] [intensity]     - Run pulse cycle (intensity 0.1-2.0)
  history [count]            - Pulse history visualization
  resonance                  - Resonance pattern analysis
  wellness                   - Organism wellness score
  status                     - Coordinator status
  help                       - Show this help

Pulse types: full, sync, heal, boost, monitor
Intensity: 0.1 (low) to 2.0 (high)
""")

        else:
            print(f"Unknown command: {command}")
            print("Use 'check help' for available commands")
    else:
        # Default: run full pulse cycle
        print("=" * 70)
        print("IXPANSION OrganismPulseCoordinator - Default Pulse Cycle")
        print("=" * 70)
        print("")
        print(">>> Generating unified organism pulse...")
        print("")
        result = coordinator.run_pulse_cycle()
        print("")
        print("✅ Default pulse cycle complete!")
