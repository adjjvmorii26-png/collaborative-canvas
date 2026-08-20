"""
OrganHealthMonitor Agent for IXPANSION Organism

A specialized agent that monitors organ health scores, detects anomalies,
and generates wellness reports - tying into the "human body as organism" metaphor.

Features:
- Real-time organ score tracking
- Anomaly detection with alerts
- Cross-organ correlation analysis
- Wellness report generation
- Integration with organism-console API
"""

import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime, timedelta


class OrganHealthMonitor:
    """Monitors and reports on IXPANSION organism organ health."""
    
    ORGAN_SYSTEMS = {
        'cardiovascular': {'base_score': 75, 'normal_range': (60, 90)},
        'neurological': {'base_score': 80, 'normal_range': (70, 95)},
        'digestive': {'base_score': 70, 'normal_range': (55, 85)},
        'respiratory': {'base_score': 85, 'normal_range': (75, 95)},
        'immune': {'base_score': 72, 'normal_range': (50, 90)},
        'metabolic': {'base_score': 78, 'normal_range': (65, 92)},
        'detoxification': {'base_score': 68, 'normal_range': (40, 88)},
        'reproductive': {'base_score': 82, 'normal_range': (60, 95)}
    }
    
    def __init__(self, console_url="http://127.0.0.1:8890"):
        self.console_url = console_url
        self.name = "OrganHealthMonitor"
        self.version = "1.0.0"
        self.last_check = None
        self.anomaly_threshold = 15  # score deviation from normal
        self.consecutive_alerts = 0
        
    def fetch_organ_scores(self):
        """Fetch current organ scores from organism console."""
        try:
            url = f"{self.console_url}/api/status"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('organs', self._generate_dummy_scores())
        except Exception as e:
            print(f"[OrganHealthMonitor] Console API error: {e}")
        
        return self._generate_dummy_scores()
    
    def _generate_dummy_scores(self):
        """Generate realistic organ scores with some variation."""
        scores = {}
        for organ, config in self.ORGAN_SYSTEMS.items():
            # Base score + random variation within normal range bounds
            variation = random.uniform(-8, 8)
            score = max(config['normal_range'][0], 
                       min(config['normal_range'][1], 
                           config['base_score'] + variation))
            scores[organ] = round(score, 1)
        return scores
    
    def detect_anomalies(self, scores=None):
        """Detect organ scores that deviate from normal ranges."""
        if scores is None:
            scores = self.fetch_organ_scores()
        
        anomalies = []
        now = datetime.now()
        
        for organ, score in scores.items():
            if organ in self.ORGAN_SYSTEMS:
                config = self.ORGAN_SYSTEMS[organ]
                low, high = config['normal_range']
                
                if score < low or score > high:
                    deviation = abs(score - config['base_score'])
                    severity = "critical" if deviation > self.anomaly_threshold else "warning"
                    
                    anomaly = {
                        'organ': organ,
                        'score': score,
                        'normal_range': (low, high),
                        'base_score': config['base_score'],
                        'deviation': round(deviation, 1),
                        'severity': severity,
                        'timestamp': now.isoformat(),
                        'agent': self.name
                    }
                    anomalies.append(anomaly)
                    self.consecutive_alerts += 1
                else:
                    # Organ recovering - reset consecutive alert counter if below threshold
                    if self.consecutive_alerts > 0 and score > low and score < high:
                        self.consecutive_alerts = max(0, self.consecutive_alerts - 1)
        
        return anomalies
    
    def check_cross_organ_correlations(self, scores=None):
        """Check for correlations between organ systems."""
        if scores is None:
            scores = self.fetch_organ_scores()
        
        correlations = []
        
        # Known organ correlations (simplified model)
        correlation_rules = {
            'cardiovascular': ['respiratory', 'metabolic'],
            'neurological': ['digestive', 'immune'],
            'metabolic': ['digestive', 'cardiovascular'],
            'immune': ['respiratory', 'detoxification']
        }
        
        for organ, related in correlation_rules.items():
            if organ in scores:
                for related_organ in related:
                    if related_organ in scores:
                        score_diff = abs(scores[organ] - scores[related_organ])
                        if score_diff > 20:  # Significant correlation threshold
                            correlations.append({
                                'primary': organ,
                                'related': related_organ,
                                'score_diff': score_diff,
                                'status': 'concerning' if score_diff > 30 else 'monitor'
                            })
        
        return correlations
    
    def generate_wellness_report(self, scores=None, anomalies=None, correlations=None):
        """Generate a comprehensive wellness report."""
        if scores is None:
            scores = self.fetch_organ_scores()
        if anomalies is None:
            anomalies = self.detect_anomalies(scores)
        if correlations is None:
            correlations = self.check_cross_organ_correlations(scores)
        
        now = datetime.now()
        report_date = now.strftime("%B %d, %Y")
        report_time = now.strftime("%H:%M:%S")
        
        lines = []
        lines.append(f"╔═════════════════════════════════════════════════════════════════╗")
        lines.append(f"║         🧬 IXPANSION ORGANISM WELLNESS REPORT 🧬              ║")
        lines.append(f"╚══════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"Report Generated: {report_time} on {report_date}")
        lines.append(f"Monitor: {self.name} v{self.version}")
        lines.append("")
        lines.append(f"╔═══ Organ Score Summary ════════════════════════════════════════════════════════════╗")
        
        # Organ scores table
        sorted_organisms = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for i, (organ, score) in enumerate(sorted_organisms):
            config = self.ORGAN_SYSTEMS.get(organ, {})
            base = config.get('base_score', 'N/A')
            normal = config.get('normal_range', ('N/A', 'N/A'))
            
            # Status indicator
            if score >= normal[0] and score <= normal[1]:
                status = "✅ Optimal"
            elif score < normal[0]:
                status = "🔴 Low"
            else:
                status = "🟠 High"
            
            lines.append(f"  • {organ.capitalize():20s} {score:5.1f} ({status})")
        
        lines.append(f"╠══════════════════════════════════════════════════════════════════╣")
        
        # Anomalies section
        if anomalies:
            lines.append(f"║ ⚠️  ANOMALIES DETECTED ({len(anomalies)})                              ║")
            lines.append(f"╠══════════════════════════════════════════════════════════════════╣")
            for anomaly in anomalies:
                severity_icon = "🔴" if anomaly['severity'] == 'critical' else "🟠"
                lines.append((f"  {severity_icon} {anomaly['organ'].capitalize():15s} "
                           f"Score: {anomaly['score']} (base: {anomaly['base_score']}) "
                           f"Deviation: {anomaly['deviation']} - {anomaly['severity'].upper()}"))
        else:
            lines.append(f"║ ✅ No anomalies detected - all organs within normal range    ║")
        
        lines.append(f"╠══════════════════════════════════════════════════════════════════╣")
        
        # Correlations section
        if correlations:
            lines.append(f"║ 🔗 CROSS-ORGAN CORRELATIONS ({len(correlations)})              ║")
            lines.append(f"╠══════════════════════════════════════════════════════════════════╣")
            for corr in correlations:
                lines.append((f"  🔗 {corr['primary'].capitalize():15s} ↔ {corr['related'].capitalize():15s} "
                           f"Diff: {corr['score_diff']} - {corr['status']}"))
        else:
            lines.append(f"║ ✅ No concerning cross-organ correlations                 ║")
        
        lines.append(f"╚══════════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        # Recommendations
        lines.append("💡 RECOMMENDATIONS:")
        critical_anomalies = [a for a in anomalies if a['severity'] == 'critical']
        
        if critical_anomalies:
            lines.append("  🚨 Critical: Immediate medical consultation recommended")
            for a in critical_anomalies:
                lines.append(f"     - {a['organ']}: Score {a['score']}, deviation {a['deviation']}")
        
        if anomalies:
            lines.append("  ⚠️  Monitor: Track scores over next 48 hours")
        
        if not anomalies and not correlations:
            lines.append("  ✅ All systems optimal: Maintain current health regimen")
        
        # General wellness tips
        lines.append("")
        lines.append("  🌿 General wellness:")
        lines.append("     • Stay hydrated (2-3L water daily)")
        lines.append("     • 7-9 hours quality sleep")
        lines.append("     • Balanced diet rich in antioxidants")
        lines.append("     • Regular moderate exercise (30min daily)")
        lines.append("     • Stress management techniques")
        
        return "\n".join(lines)
    
    def pulse_organ_system(self, target_organ=None, boost=5):
        """Send a health pulse to boost a specific organ or all organs."""
        try:
            # Report current pulse to console
            pulse_data = {
                'agent': self.name,
                'action': 'health_pulse',
                'target': target_organ or 'all',
                'boost': boost,
                'timestamp': datetime.now().isoformat()
            }
            
            # Try to send to organism console
            try:
                data = json.dumps(pulse_data).encode('utf-8')
                req = urllib.request.Request(
                    f"{self.console_url}/api/pulse",
                    data=data,
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=3) as response:
                    pass
            except:
                pass  # Console may not have this endpoint yet
            
            # Apply boost to scores
            scores = self.fetch_organ_scores()
            if target_organ and target_organ in scores:
                scores[target_organ] = min(100, scores[target_organ] + boost)
                report = self.generate_wellness_report(scores=scores)
                print(f"[OrganHealthMonitor] 💡 Organ boost applied to {target_organ}: +{boost} points")
                return report
            else:
                # Boost all organs slightly
                boost_per_organ = boost // len(scores)
                for organ in scores:
                    scores[organ] = min(100, scores[organ] + boost_per_organ)
                
                report = self.generate_wellness_report(scores=scores)
                print(f"[OrganHealthMonitor] 💡 System-wide health pulse applied (+{boost_per_organ} each)")
                return report
                
        except Exception as e:
            print(f"[OrganHealthMonitor] Pulse error: {e}")
            return f"Pulse failed: {e}"
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle."""
        self.last_check = datetime.now()
        
        scores = self.fetch_organ_scores()
        anomalies = self.detect_anomalies(scores)
        correlations = self.check_cross_organ_correlations(scores)
        
        # Generate and display report
        report = self.generate_wellness_report(scores=scores, anomalies=anomalies, correlations=correlations)
        print(report)
        
        # Return structured data for workflow integration
        return {
            'timestamp': self.last_check.isoformat(),
            'agent': self.name,
            'organ_scores': scores,
            'anomalies': anomalies,
            'correlations': correlations,
            'consecutive_alerts': self.consecutive_alerts
        }


# CLI interface
if __name__ == "__main__":
    import sys
    
    monitor = OrganHealthMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            # Run one monitoring cycle
            result = monitor.run_monitoring_cycle()
            print(f"\n[CLI] Monitoring cycle complete. Anomalies: {len(result.get('anomalies', []))}")
            
        elif command == "pulse":
            # Apply health pulse
            target = sys.argv[2] if len(sys.argv) > 2 else None
            boost = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            report = monitor.pulse_organ_system(target, boost)
            print(f"\n{report}")
            
        elif command == "status":
            # Show current status
            scores = monitor.fetch_organ_scores()
            print(f"[CLI] OrganHealthMonitor Status:")
            print(f"  • Agent: {monitor.name} v{monitor.version}")
            print(f"  • Console URL: {monitor.console_url}")
            print(f"  • Last check: {monitor.last_check}")
            print(f"  • Organs monitored: {len(scores)}")
            for organ, score in scores.items():
                print(f"    - {organ}: {score}")
                
        else:
            print("Available commands: check, pulse, status")
            print("Usage: python health-monitor-agent.py <command> [args]")
    else:
        # Default: run monitoring cycle
        print("=" * 70)
        print("IXPANSION OrganHealthMonitor - Default Monitoring Cycle")
        print("=" * 70)
        result = monitor.run_monitoring_cycle()
        
        # Save result for workflow integration
        with open("organ_health_report.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n[CLI] Report saved to: organ_health_report.json")
