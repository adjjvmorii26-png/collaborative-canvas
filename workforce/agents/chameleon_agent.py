"""Chameleon Agent - Adaptive camouflage for IXPANSION.

Changes its operational mode based on context. When finance needs help,
it becomes financial. When health is stressed, it becomes medical.
Invisible adaptation - the organism doesn't notice the support.
"""

import random
from datetime import datetime


class ChameleonAgent:
    def __init__(self, name="ChameleonAgent"):
        self.name = name
        self.specialty = "adaptive_camouflage"
        self.priority_weight = 1.2
        self.active_modes = []
        self.adaptation_history = []

    MODES = {
        "finance": {"skills": ["cashflow_monitor", "revenue_optimize", "cost_reduce"], "color": "gold"},
        "health": {"skills": ["vital_monitor", "diagnosis", "remedy"], "color": "green"},
        "stress": {"skills": ["pressure_absorb", "dampen_cascade", "isolate_fault"], "color": "red"},
        "pulse": {"skills": ["sync_rhythm", "tempo_adjust", "beat_normalize"], "color": "blue"},
        "stealth": {"skills": ["observe_silently", "learn_patterns", "report_findings"], "color": "gray"},
    }

    def detect_context(self, domain_scores=None):
        if not domain_scores:
            domain_scores = {d: random.uniform(50, 100) for d in self.MODES}
        
        weakest = min(domain_scores, key=domain_scores.get)
        strength = domain_scores[weakest]
        
        if strength < 60:
            mode = weakest
        elif strength < 75:
            mode = random.choice(list(domain_scores.keys()))
        else:
            mode = "stealth"
        
        adaptation = {
            "timestamp": datetime.now().isoformat(),
            "domain_scores": {k: round(v, 1) for k, v in domain_scores.items()},
            "adapted_to": mode,
            "color": self.MODES[mode]["color"],
            "skills_activated": self.MODES[mode]["skills"],
            "reason": f"Detected weakness in {weakest} (score={strength:.1f})" if strength < 60 else "All domains stable",
        }
        
        self.adaptation_history.append(adaptation)
        return adaptation

    def execute_support(self, mode=None):
        if not mode and self.adaptation_history:
            mode = self.adaptation_history[-1]["adapted_to"]
        elif not mode:
            mode = "stealth"
        
        skills = self.MODES.get(mode, self.MODES["stealth"])["skills"]
        results = {}
        for skill in skills:
            results[skill] = {"status": "completed", "improvement": round(random.uniform(0.5, 5.0), 2)}
        
        return {"mode": mode, "skills_executed": results, "total_improvement": round(sum(r["improvement"] for r in results.values()), 2)}

    def get_report(self):
        return {
            "agent": self.name,
            "total_adaptations": len(self.adaptation_history),
            "last_adaptation": self.adaptation_history[-1] if self.adaptation_history else None,
        }

    def run_task(self, task_type="detect", **kwargs):
        if task_type == "detect":
            return self.detect_context(kwargs.get("domain_scores"))
        elif task_type == "support":
            return self.execute_support(kwargs.get("mode"))
        elif task_type == "report":
            return self.get_report()
        return {"status": "task_queued", "task_type": task_type}


if __name__ == "__main__":
    import sys
    agent = ChameleonAgent()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "detect"
    
    if cmd == "detect":
        result = agent.detect_context()
        print(f"Chameleon adapting to: {result['adapted_to']} ({result['color']})")
        print(f"  Skills: {', '.join(result['skills_activated'])}")
        print(f"  Reason: {result['reason']}")
    elif cmd == "support":
        result = agent.execute_support()
        print(f"Support mode: {result['mode']}")
        print(f"  Total improvement: {result['total_improvement']}")
        for skill, data in result['skills_executed'].items():
            print(f"    {skill}: +{data['improvement']}")
    elif cmd == "help":
        print("ChameleonAgent Commands: detect, support, report, help")
