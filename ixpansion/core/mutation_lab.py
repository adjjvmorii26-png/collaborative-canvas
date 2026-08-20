"""MutationLab for IXPANSION

Runs controlled experiments on the organism: mutates agent parameters,
measures fitness deltas, keeps beneficial mutations, reverts harmful ones.
"""

import json
import random
import time
from datetime import datetime


class MutationLab:
    def __init__(self):
        self.name = "MutationLab"
        self.version = "1.0.0"
        self.experiments = []
        self.beneficial_mutations = []
        self.harmful_mutations = []
        self.generation = 0

    MUTATION_TYPES = [
        "priority_weight_shift",
        "skill_expansion",
        "domain_crossover",
        "threshold_adjustment",
        "timing_offset",
        "correlation_boost",
    ]

    AGENT_POOL = [
        {"name": "NebulaAgent", "base_fitness": 0.72, "params": {"priority_weight": 1.4, "scan_depth": 3}},
        {"name": "QuantumAgent", "base_fitness": 0.68, "params": {"priority_weight": 1.5, "superposition_size": 5}},
        {"name": "MyceliumAgent", "base_fitness": 0.75, "params": {"priority_weight": 1.3, "network_nodes": 7}},
        {"name": "ChameleonAgent", "base_fitness": 0.70, "params": {"priority_weight": 1.2, "adaptation_speed": 0.8}},
        {"name": "FibonacciAgent", "base_fitness": 0.65, "params": {"priority_weight": 1.3, "spiral_points": 8}},
        {"name": "CodeGenAgent", "base_fitness": 0.60, "params": {"priority_weight": 1.5, "template_depth": 3}},
    ]

    def mutate(self, agent):
        """Apply a random mutation to an agent's parameters."""
        mutation_type = random.choice(self.MUTATION_TYPES)
        mutated = json.loads(json.dumps(agent))  # deep copy
        mutated["mutation_type"] = mutation_type
        mutated["generation"] = self.generation + 1

        if mutation_type == "priority_weight_shift":
            delta = random.uniform(-0.3, 0.3)
            old = mutated["params"]["priority_weight"]
            mutated["params"]["priority_weight"] = round(max(0.5, min(2.0, old + delta)), 2)
            mutated["delta"] = round(mutated["params"]["priority_weight"] - old, 3)

        elif mutation_type == "skill_expansion":
            new_skills = ["predictive_modeling", "cross_domain_fusion", "temporal_awareness"]
            mutated["params"]["extra_skill"] = random.choice(new_skills)
            mutated["delta"] = 0.05

        elif mutation_type == "domain_crossover":
            domains = ["health", "finance", "stress", "pulse"]
            mutated["params"]["crossover_domain"] = random.choice(domains)
            mutated["delta"] = random.uniform(0.02, 0.08)

        elif mutation_type == "threshold_adjustment":
            key = random.choice(list(mutated["params"].keys()))
            if isinstance(mutated["params"][key], (int, float)):
                old = mutated["params"][key]
                mutated["params"][key] = round(old * random.uniform(0.8, 1.2), 2)
                mutated["delta"] = round(abs(mutated["params"][key] - old) / max(abs(old), 1), 3)
            else:
                mutated["delta"] = 0.01

        elif mutation_type == "timing_offset":
            mutated["params"]["timing_offset_ms"] = random.randint(-500, 500)
            mutated["delta"] = abs(mutated["params"]["timing_offset_ms"]) / 1000

        elif mutation_type == "correlation_boost":
            mutated["params"]["correlation_boost"] = round(random.uniform(0.1, 0.5), 2)
            mutated["delta"] = mutated["params"]["correlation_boost"]

        return mutated

    def measure_fitness(self, agent):
        """Simulate fitness measurement after mutation."""
        base = agent.get("base_fitness", 0.6)
        weight_bonus = (agent["params"].get("priority_weight", 1.0) - 1.0) * 0.1
        noise = random.uniform(-0.08, 0.08)
        return round(max(0.1, min(1.0, base + weight_bonus + noise)), 3)

    def run_experiment(self, batch_size=3):
        """Run a batch of mutations and evaluate results."""
        self.generation += 1
        results = []

        for _ in range(batch_size):
            original = random.choice(self.AGENT_POOL)
            mutated = self.mutate(original)

            pre_fitness = self.measure_fitness(original)
            post_fitness = self.measure_fitness(mutated)
            delta = round(post_fitness - pre_fitness, 4)

            experiment = {
                "generation": self.generation,
                "agent": original["name"],
                "mutation_type": mutated["mutation_type"],
                "params_before": original["params"],
                "params_after": mutated["params"],
                "pre_fitness": pre_fitness,
                "post_fitness": post_fitness,
                "fitness_delta": delta,
                "verdict": "beneficial" if delta > 0 else "harmful" if delta < -0.02 else "neutral",
                "timestamp": datetime.now().isoformat(),
            }

            if experiment["verdict"] == "beneficial":
                self.beneficial_mutations.append(experiment)
            elif experiment["verdict"] == "harmful":
                self.harmful_mutations.append(experiment)

            results.append(experiment)
            self.experiments.append(experiment)

        return results

    def get_best_mutation(self):
        """Return the single most beneficial mutation found."""
        if not self.beneficial_mutations:
            return None
        return max(self.beneficial_mutations, key=lambda x: x["fitness_delta"])

    def get_report(self):
        total = len(self.experiments)
        beneficial = len(self.beneficial_mutations)
        harmful = len(self.harmful_mutations)
        neutral = total - beneficial - harmful
        avg_delta = (
            sum(e["fitness_delta"] for e in self.experiments) / total if total else 0
        )
        best = self.get_best_mutation()
        return {
            "engine": self.name,
            "generation": self.generation,
            "total_experiments": total,
            "beneficial": beneficial,
            "harmful": harmful,
            "neutral": neutral,
            "success_rate": round(beneficial / total * 100, 1) if total else 0,
            "average_delta": round(avg_delta, 4),
            "best_mutation": {
                "agent": best["agent"],
                "type": best["mutation_type"],
                "delta": best["fitness_delta"],
            } if best else None,
        }

    def run_cycle(self, batch_size=6):
        print("=" * 70)
        print("IXPANSION MutationLab — Controlled Evolution Experiment")
        print(f"Generation: {self.generation + 1}")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()

        results = self.run_experiment(batch_size)

        for i, e in enumerate(results, 1):
            icon = "🟢" if e["verdict"] == "beneficial" else "🔴" if e["verdict"] == "harmful" else "⚪"
            arrow = "↑" if e["fitness_delta"] > 0 else "↓" if e["fitness_delta"] < 0 else "→"
            print(
                f"  {icon} Exp {i}: {e['agent']:16s} {e['mutation_type']}"
                f"\n     Fitness: {e['pre_fitness']:.3f} → {e['post_fitness']:.3f} "
                f"({arrow}{abs(e['fitness_delta']):.4f}) [{e['verdict']}]"
            )
            print()

        report = self.get_report()
        print(f"  Generation {report['generation']} Summary:")
        print(f"    Beneficial: {report['beneficial']}  Harmful: {report['harmful']}  Neutral: {report['neutral']}")
        print(f"    Success Rate: {report['success_rate']}%")
        print(f"    Average Delta: {report['average_delta']:+.4f}")

        best = report.get("best_mutation")
        if best:
            print(f"    ⭐ Best: {best['agent']} — {best['type']} (+{best['delta']:.4f})")

        print()
        print("=" * 70)
        return results


if __name__ == "__main__":
    import sys
    lab = MutationLab()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cycle"

    if cmd == "cycle":
        batch = int(sys.argv[2]) if len(sys.argv) > 2 else 6
        lab.run_cycle(batch)
    elif cmd == "experiment":
        results = lab.run_experiment(1)
        print(json.dumps(results[0], indent=2))
    elif cmd == "best":
        best = lab.get_best_mutation()
        if best:
            print(json.dumps(best, indent=2))
        else:
            print("No beneficial mutations found yet")
    elif cmd == "report":
        print(json.dumps(lab.get_report(), indent=2))
    elif cmd == "help":
        print("MutationLab Commands: cycle [n], experiment, best, report, help")
