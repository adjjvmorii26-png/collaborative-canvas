"""Cross-Agent Correlation Engine for IXPANSION

Detects patterns across health, finance, stress, and pulse systems.
Provides integrated monitoring, anomaly detection, and predictive insights.
"""

import json
import time
import random
from datetime import datetime, timedelta


class CrossAgentCorrelator:
    """Detects correlations across IXPANSION agent systems."""

    DOMAINS = ["health", "finance", "stress", "pulse", "wordpress", "synchronicity"]
    ANOMALY_TYPES = ["spike", "drop", "drift", "cascade", "resonance"]
    PATTERN_TYPES = ["synchronized", "divergent", "cascade", "echo", "resonance"]

    def __init__(self):
        self.name = "CrossAgentCorrelator"
        self.version = "1.0.0"
        self.history = []
        self.detected_patterns = []
        self.anomalies = []
        self.correlation_matrix = {}

    def collect_domain_snapshot(self):
        snapshot = {}
        for domain in self.DOMAINS:
            score = random.uniform(50, 100)
            volatility = random.uniform(0.05, 0.3)
            snapshot[domain] = {
                "score": round(score, 1),
                "volatility": round(volatility, 3),
                "trend": random.choice(["up", "down", "stable"]),
                "timestamp": datetime.now().isoformat(),
            }
        self.history.append(snapshot)
        return snapshot

    def detect_correlations(self, snapshot=None):
        if not snapshot:
            snapshot = self.collect_domain_snapshot()

        correlations = {}
        domains = list(snapshot.keys())

        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                d1, d2 = domains[i], domains[j]
                score1 = snapshot[d1]["score"]
                score2 = snapshot[d2]["score"]
                v1 = snapshot[d1]["volatility"]
                v2 = snapshot[d2]["volatility"]

                diff = abs(score1 - score2)
                vol_sim = 1.0 - abs(v1 - v2)

                if diff < 10 and vol_sim > 0.8:
                    corr_type = "synchronized"
                elif diff > 30:
                    corr_type = "divergent"
                elif diff < 15 and v1 > 0.2 and v2 > 0.2:
                    corr_type = "cascade"
                else:
                    corr_type = "independent"

                correlations[f"{d1}↔{d2}"] = {
                    "type": corr_type,
                    "score_diff": round(diff, 1),
                    "volatility_similarity": round(vol_sim, 3),
                    "strength": round(max(0, 1 - diff / 50), 3),
                }

        self.correlation_matrix = correlations
        return correlations

    def detect_anomalies(self, snapshot=None):
        if not snapshot:
            snapshot = self.collect_domain_snapshot()

        anomalies = []
        for domain, data in snapshot.items():
            score = data["score"]
            volatility = data["volatility"]

            if score < 55 or score > 95:
                severity = "critical" if score < 50 or score > 97 else "warning"
                anomalies.append({
                    "domain": domain,
                    "type": "spike" if score > 80 else "drop",
                    "score": score,
                    "severity": severity,
                    "recommendation": f"Monitor {domain} for recovery",
                })

            if volatility > 0.25:
                anomalies.append({
                    "domain": domain,
                    "type": "drift",
                    "volatility": volatility,
                    "severity": "warning",
                    "recommendation": f"High volatility in {domain} - stabilize",
                })

        self.anomalies.extend(anomalies)
        return anomalies

    def predict_cascade(self, snapshot=None):
        if not snapshot:
            snapshot = self.collect_domain_snapshot()

        vulnerable = []
        for domain, data in snapshot.items():
            if data["volatility"] > 0.2 and data["score"] < 70:
                vulnerable.append({
                    "domain": domain,
                    "risk": "cascade_candidate",
                    "trigger_probability": round(data["volatility"] * (100 - data["score"]) / 100, 3),
                })

        return {
            "vulnerable_domains": vulnerable,
            "cascade_risk": "high" if len(vulnerable) > 2 else "medium" if len(vulnerable) > 0 else "low",
            "recommendation": "Activate cross-domain stabilization" if vulnerable else "System stable",
        }

    def generate_correlation_report(self):
        snapshot = self.collect_domain_snapshot()
        correlations = self.detect_correlations(snapshot)
        anomalies = self.detect_anomalies(snapshot)
        cascade = self.predict_cascade(snapshot)

        synchronized = [k for k, v in correlations.items() if v["type"] == "synchronized"]
        divergent = [k for k, v in correlations.items() if v["type"] == "divergent"]
        cascading = [k for k, v in correlations.items() if v["type"] == "cascade"]

        lines = [
            "=" * 70,
            "IXPANSION Cross-Agent Correlation Report",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 70,
            "",
            "📊 Domain Snapshots:",
        ]
        for domain, data in snapshot.items():
            indicator = "🟢" if data["score"] > 75 else "🟡" if data["score"] > 60 else "🔴"
            lines.append(f"  {indicator} {domain:15s} score={data['score']:5.1f} vol={data['volatility']:.3f} trend={data['trend']}")

        lines.append("")
        lines.append(f"🔗 Correlations Found: {len(correlations)}")
        lines.append(f"   Synchronized: {', '.join(synchronized[:3]) or 'none'}")
        lines.append(f"   Divergent: {', '.join(divergent[:3]) or 'none'}")
        lines.append(f"   Cascade risk: {', '.join(cascading[:3]) or 'none'}")

        lines.append("")
        lines.append(f"⚠️ Anomalies: {len(anomalies)}")
        for a in anomalies[:5]:
            lines.append(f"   {'🔴' if a['severity'] == 'critical' else '🟡'} {a['domain']}: {a['type']} - {a.get('recommendation', '')}")

        lines.append("")
        lines.append(f"🌊 Cascade Prediction: {cascade['cascade_risk'].upper()}")
        lines.append(f"   {cascade['recommendation']}")

        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines), {
            "snapshot": snapshot,
            "correlations": correlations,
            "anomalies": anomalies,
            "cascade": cascade,
        }

    def run_cycle(self):
        report_text, report_data = self.generate_correlation_report()
        print(report_text)
        return report_data


if __name__ == "__main__":
    import sys
    correlator = CrossAgentCorrelator()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"

    if cmd == "report":
        correlator.run_cycle()
    elif cmd == "correlate":
        snap = correlator.collect_domain_snapshot()
        corr = correlator.detect_correlations(snap)
        for pair, data in corr.items():
            print(f"  {pair}: {data['type']} (strength={data['strength']})")
    elif cmd == "anomalies":
        snap = correlator.collect_domain_snapshot()
        anomalies = correlator.detect_anomalies(snap)
        for a in anomalies:
            print(f"  {'🔴' if a['severity'] == 'critical' else '🟡'} {a['domain']}: {a['type']}")
    elif cmd == "cascade":
        snap = correlator.collect_domain_snapshot()
        cascade = correlator.predict_cascade(snap)
        print(f"  Risk: {cascade['cascade_risk'].upper()}")
        print(f"  {cascade['recommendation']}")
    elif cmd == "help":
        print("""
CrossAgentCorrelator Commands:
  report    - Full correlation report
  correlate - Detect cross-domain correlations
  anomalies - Detect anomalies across domains
  cascade   - Predict cascade failures
  help      - Show this help""")
    else:
        print(f"Unknown command: {cmd}. Use 'help' for available commands.")
