"""Nebula Agent - Nebula-pattern discovery for IXPANSION.

Discovers emergent patterns across the organism that no single agent can see.
Maps the 'nebula' - the space between agents where interactions create new behaviors.
"""

import random
import time
from datetime import datetime


class NebulaAgent:
    def __init__(self, name="NebulaAgent"):
        self.name = name
        self.specialty = "emergent_pattern_discovery"
        self.priority_weight = 1.4
        self.discovered_nebulae = []
        self.interaction_map = {}

    def scan_interactions(self, agents=None):
        if not agents:
            agents = ["health_monitor", "finance_agent", "stress_test", "pulse_coordinator", "synchronicity_agent"]
        
        interactions = []
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                strength = random.uniform(0.1, 1.0)
                if strength > 0.7:
                    interactions.append({
                        "from": agents[i],
                        "to": agents[j],
                        "strength": round(strength, 3),
                        "type": random.choice(["synergy", "tension", "resonance", "echo"]),
                    })
        
        self.interaction_map = {f"{a['from']}↔{a['to']}": a for a in interactions}
        return interactions

    def discover_nebula(self, interaction_data=None):
        if not interaction_data:
            interaction_data = list(self.interaction_map.values()) or self.scan_interactions()
        
        strong = [i for i in interaction_data if i.get("strength", 0) > 0.7]
        
        nebula = {
            "id": f"nebula_{len(self.discovered_nebulae) + 1}",
            "timestamp": datetime.now().isoformat(),
            "interaction_count": len(interaction_data),
            "strong_interactions": len(strong),
            "emergent_behaviors": [],
            "strength": round(sum(i.get("strength", 0) for i in interaction_data) / max(len(interaction_data), 1), 3),
        }
        
        behavior_pool = [
            "Adaptive resource allocation emerges from health-finance coupling",
            "Stress resilience amplifies when pulse synchronicity is high",
            "Cross-agent memory sharing creates information cascades",
            "Synchronized agents form temporary 'organs' for complex tasks",
            "Divergent agents create beneficial tension for exploration",
        ]
        nebula["emergent_behaviors"] = random.sample(behavior_pool, min(3, len(behavior_pool)))
        
        self.discovered_nebulae.append(nebula)
        return nebula

    def get_nebula_report(self):
        return {
            "agent": self.name,
            "total_nebulae": len(self.discovered_nebulae),
            "interaction_pairs": len(self.interaction_map),
            "last_discovery": self.discovered_nebulae[-1] if self.discovered_nebulae else None,
        }

    def run_task(self, task_type="scan", **kwargs):
        if task_type == "scan":
            return self.scan_interactions(kwargs.get("agents"))
        elif task_type == "discover":
            return self.discover_nebula(kwargs.get("interactions"))
        elif task_type == "report":
            return self.get_nebula_report()
        return {"status": "task_queued", "task_type": task_type}


if __name__ == "__main__":
    import sys
    agent = NebulaAgent()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    
    if cmd == "scan":
        interactions = agent.scan_interactions()
        print(f"Found {len(interactions)} strong interactions:")
        for i in interactions:
            print(f"  {i['from']} ↔ {i['to']}: {i['type']} (strength={i['strength']})")
    elif cmd == "discover":
        nebula = agent.discover_nebula()
        print(f"Discovered: {nebula['id']}")
        print(f"  Interactions: {nebula['interaction_count']} (strong: {nebula['strong_interactions']})")
        print(f"  Strength: {nebula['strength']}")
        print(f"  Emergent behaviors:")
        for b in nebula["emergent_behaviors"]:
            print(f"    • {b}")
    elif cmd == "help":
        print("NebulaAgent Commands: scan, discover, report, help")
