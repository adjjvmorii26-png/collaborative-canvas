"""Self-Evolution Engine for IXPANSION

Allows the organism to generate new agents, adapt its own architecture,
and evolve its capabilities autonomously based on observed patterns.
"""

import random
import time
import os
import json
from datetime import datetime


class SelfEvolutionEngine:
    def __init__(self):
        self.name = "SelfEvolutionEngine"
        self.version = "1.0.0"
        self.evolution_log = []
        self.generated_agents = []
        self.adaptation_history = []
        self.generation_count = 0

    AGENT_TEMPLATES = {
        "monitor": {
            "skills": ["watch", "alert", "report"],
            "priority_weight": 1.0,
            "description": "Monitors a specific domain for changes",
        },
        "optimizer": {
            "skills": ["analyze", "optimize", "rebalance"],
            "priority_weight": 1.2,
            "description": "Optimizes resource allocation in a domain",
        },
        "healer": {
            "skills": ["diagnose", "repair", "prevent"],
            "priority_weight": 1.3,
            "description": "Repairs issues and prevents recurrence",
        },
        "scout": {
            "skills": ["explore", "discover", "report"],
            "priority_weight": 1.1,
            "description": "Explores new capabilities and patterns",
        },
        "synthesizer": {
            "skills": ["combine", "integrate", "synthesize"],
            "priority_weight": 1.4,
            "description": "Combines multiple agent outputs into insights",
        },
    }

    def generate_agent(self, agent_type, domain, custom_skills=None):
        if agent_type not in self.AGENT_TEMPLATES:
            return {"error": f"Unknown agent type: {agent_type}. Valid: {list(self.AGENT_TEMPLATES.keys())}"}

        template = self.AGENT_TEMPLATES[agent_type]
        self.generation_count += 1

        agent_spec = {
            "name": f"{domain}_{agent_type}_{self.generation_count}",
            "type": agent_type,
            "domain": domain,
            "skills": custom_skills or template["skills"],
            "priority_weight": template["priority_weight"],
            "description": template["description"],
            "generated_at": datetime.now().isoformat(),
            "generation_id": self.generation_count,
        }

        self.generated_agents.append(agent_spec)
        self.evolution_log.append({
            "action": "generate_agent",
            "timestamp": datetime.now().isoformat(),
            "agent": agent_spec["name"],
            "type": agent_type,
            "domain": domain,
        })

        return agent_spec

    def adapt_architecture(self, current_state, target_state):
        adaptations = []
        diff_score = random.uniform(0.1, 0.9)

        if diff_score > 0.7:
            adaptations.append({
                "type": "add_specialist",
                "description": f"Add specialist for {target_state.get('domain', 'general')}",
                "priority": "high",
            })
        if diff_score > 0.5:
            adaptations.append({
                "type": "strengthen_correlation",
                "description": "Increase correlation between health and finance domains",
                "priority": "medium",
            })
        if diff_score > 0.3:
            adaptations.append({
                "type": "optimize_routing",
                "description": "Optimize OrchestratorAgent task routing weights",
                "priority": "low",
            })

        result = {
            "current_state": current_state,
            "target_state": target_state,
            "adaptations": adaptations,
            "adaptation_score": round(diff_score, 3),
            "timestamp": datetime.now().isoformat(),
        }

        self.adaptation_history.append(result)
        return result

    def evolve(self, fitness_data=None):
        if not fitness_data:
            fitness_data = {d: random.uniform(0.5, 1.0) for d in ["health", "finance", "stress", "pulse", "wordpress"]}

        weakest = min(fitness_data, key=fitness_data.get)
        strongest = max(fitness_data, key=fitness_data.get)
        avg_fitness = sum(fitness_data.values()) / len(fitness_data)

        evolution_result = {
            "generation": self.generation_count + 1,
            "fitness": {k: round(v, 3) for k, v in fitness_data.items()},
            "weakest_domain": weakest,
            "strongest_domain": strongest,
            "average_fitness": round(avg_fitness, 3),
            "mutations": [],
        }

        if fitness_data[weakest] < 0.7:
            new_agent = self.generate_agent("healer", weakest)
            evolution_result["mutations"].append(f"Generated healer for {weakest}")

        if avg_fitness > 0.8:
            new_agent = self.generate_agent("scout", "expansion")
            evolution_result["mutations"].append(f"Generated scout for expansion")

        self.generation_count += 1
        return evolution_result

    def get_report(self):
        return {
            "engine": self.name,
            "version": self.version,
            "total_agents_generated": len(self.generated_agents),
            "total_adaptations": len(self.adaptation_history),
            "generation_count": self.generation_count,
            "recent_generations": self.generated_agents[-5:] if self.generated_agents else [],
        }

    def run_cycle(self):
        fitness = {d: random.uniform(0.5, 1.0) for d in ["health", "finance", "stress", "pulse", "wordpress"]}
        result = self.evolve(fitness)

        print("=" * 60)
        print("IXPANSION Self-Evolution Engine Cycle")
        print(f"Generation: {result['generation']}")
        print("=" * 60)
        print()
        print("Fitness Scores:")
        for domain, score in result["fitness"].items():
            indicator = "🟢" if score > 0.8 else "🟡" if score > 0.6 else "🔴"
            print(f"  {indicator} {domain:12s} {score:.3f}")
        print()
        print(f"Average Fitness: {result['average_fitness']:.3f}")
        print(f"Weakest Domain: {result['weakest_domain']}")
        print(f"Strongest Domain: {result['strongest_domain']}")
        print()
        if result["mutations"]:
            print("Mutations Applied:")
            for m in result["mutations"]:
                print(f"  🧬 {m}")
        else:
            print("No mutations needed - system stable")
        print()
        print("=" * 60)
        return result


if __name__ == "__main__":
    import sys
    engine = SelfEvolutionEngine()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cycle"

    if cmd == "cycle":
        engine.run_cycle()
    elif cmd == "generate":
        agent_type = sys.argv[2] if len(sys.argv) > 2 else "monitor"
        domain = sys.argv[3] if len(sys.argv) > 3 else "general"
        agent = engine.generate_agent(agent_type, domain)
        print(f"Generated: {agent['name']} ({agent['type']}) for {agent['domain']}")
    elif cmd == "adapt":
        result = engine.adapt_architecture({"health": 0.7}, {"health": 0.9, "finance": 0.85})
        print(f"Adaptations: {len(result['adaptations'])}")
        for a in result["adaptations"]:
            print(f"  {a['type']}: {a['description']} [{a['priority']}]")
    elif cmd == "report":
        report = engine.get_report()
        print(json.dumps(report, indent=2))
    elif cmd == "help":
        print("SelfEvolutionEngine Commands: cycle, generate <type> <domain>, adapt, report, help")
