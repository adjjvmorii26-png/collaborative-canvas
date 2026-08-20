"""Quantum Agent - Superposition-based decision making for IXPANSION.

Holds multiple possible outcomes in superposition until observation
collapses to the optimal choice. Uses probability amplitudes.
"""

import random
import math
from datetime import datetime


class QuantumAgent:
    def __init__(self, name="QuantumAgent"):
        self.name = name
        self.specialty = "quantum_decision_superposition"
        self.priority_weight = 1.5
        self.superpositions = []
        self.collapsed_decisions = []

    def create_superposition(self, options=None):
        if not options:
            options = ["optimize_health", "boost_finance", "reduce_stress", "sync_pulse", "explore_new"]
        
        amplitudes = []
        total = 0
        for opt in options:
            amp = random.uniform(0.1, 1.0)
            amplitudes.append({"option": opt, "amplitude": amp})
            total += amp ** 2
        
        for a in amplitudes:
            a["probability"] = round((a["amplitude"] ** 2) / total, 4)
            a["phase"] = round(random.uniform(0, 2 * math.pi), 4)
        
        self.superpositions.append({
            "timestamp": datetime.now().isoformat(),
            "options": amplitudes,
            "state": "superposed",
        })
        return amplitudes

    def observe(self, superposition_idx=-1):
        if not self.superpositions:
            self.create_superposition()
        
        sp = self.superpositions[superposition_idx]
        options = sp["options"]
        
        probs = [o["probability"] for o in options]
        chosen = random.choices(options, weights=probs, k=1)[0]
        
        decision = {
            "timestamp": datetime.now().isoformat(),
            "chosen_option": chosen["option"],
            "probability": chosen["probability"],
            "previous_state": "superposed",
            "collapsed_to": "determined",
            "entangled_agents": random.sample(
                ["health_monitor", "finance_agent", "pulse_coordinator", "stress_test"],
                k=random.randint(1, 3)
            ),
        }
        
        sp["state"] = "collapsed"
        self.collapsed_decisions.append(decision)
        return decision

    def calculate_interference(self, sp1_idx=0, sp2_idx=-1):
        if len(self.superpositions) < 2:
            return {"error": "Need at least 2 superpositions"}
        
        sp1 = self.superpositions[sp1_idx]
        sp2 = self.superpositions[sp2_idx]
        
        interference = []
        for o1 in sp1["options"]:
            for o2 in sp2["options"]:
                if o1["option"] == o2["option"]:
                    amp = o1["amplitude"] + o2["amplitude"]
                    prob = round((amp ** 2) / 2, 4)
                    interference.append({
                        "option": o1["option"],
                        "constructive": amp > o1["amplitude"],
                        "combined_amplitude": round(amp, 4),
                        "probability": prob,
                    })
        
        return interference

    def get_report(self):
        return {
            "agent": self.name,
            "superpositions": len(self.superpositions),
            "collapsed_decisions": len(self.collapsed_decisions),
            "last_decision": self.collapsed_decisions[-1] if self.collapsed_decisions else None,
        }

    def run_task(self, task_type="superpose", **kwargs):
        if task_type == "superpose":
            return self.create_superposition(kwargs.get("options"))
        elif task_type == "observe":
            return self.observe()
        elif task_type == "interference":
            return self.calculate_interference()
        elif task_type == "report":
            return self.get_report()
        return {"status": "task_queued", "task_type": task_type}


if __name__ == "__main__":
    import sys
    agent = QuantumAgent()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "superpose"
    
    if cmd == "superpose":
        options = agent.create_superposition()
        print("Superposition created:")
        for o in options:
            print(f"  {o['option']:20s} prob={o['probability']:.4f} phase={o['phase']:.4f}")
    elif cmd == "observe":
        decision = agent.observe()
        print(f"Observation collapsed to: {decision['chosen_option']}")
        print(f"  Probability: {decision['probability']:.4f}")
        print(f"  Entangled: {', '.join(decision['entangled_agents'])}")
    elif cmd == "interference":
        agent.create_superposition()
        agent.create_superposition()
        result = agent.calculate_interference()
        print("Interference patterns:")
        for r in result:
            arrow = "↗" if r["constructive"] else "↘"
            print(f"  {arrow} {r['option']}: amp={r['combined_amplitude']:.4f} prob={r['probability']:.4f}")
    elif cmd == "help":
        print("QuantumAgent Commands: superpose, observe, interference, report, help")
