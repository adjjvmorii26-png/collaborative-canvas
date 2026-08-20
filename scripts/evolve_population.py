#!/usr/bin/env python3
"""Evolutionary breeding loop for IXPANSION organism."""

import random
import sys
import os

# Ensure we can import from the project
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workforce.agents import build_team, TEAM

# Get all unique capabilities from the system
all_system_caps = set()
for agent_name in TEAM:
    for cap in TEAM[agent_name].capabilities:
        all_system_caps.add(cap)

# Additional capability pool for evolution
evolution_pool = sorted(all_system_caps) + [
    "neural-link", "quantum-process", "distributed-ledger",
    "auto-scale", "self-heal", "adaptive-learning", "predictive-optimization"
]

def mutate_agent(agent_name, mutation_rate):
    """Mutate an agent's capabilities."""
    if agent_name not in TEAM:
        return list(TEAM[agent_name].capabilities)
    
    agent_class = TEAM[agent_name]
    current_caps = set(agent_class.capabilities)
    new_caps = set()
    
    # Keep each capability with probability (1 - mutation_rate)
    for cap in current_caps:
        if random.random() > mutation_rate:
            new_caps.add(cap)
    
    # Add new random capabilities
    num_new = random.randint(0, min(3, len(evolution_pool)))
    for _ in range(num_new):
        cap = random.choice(evolution_pool)
        new_caps.add(cap)
    
    # Ensure minimum 3 capabilities
    if len(new_caps) < 3:
        available = [c for c in evolution_pool if c not in new_caps]
        if available:
            new_caps.add(random.choice(available))
    
    return list(new_caps)

def breed_agents(parent1_name, parent2_name):
    """Breed two agents to create offspring with combined capabilities."""
    if parent1_name not in TEAM or parent2_name not in TEAM:
        return None
    
    parent1_caps = set(TEAM[parent1_name].capabilities)
    parent2_caps = set(TEAM[parent2_name].capabilities)
    child_caps = set()
    
    # Crossover: take capabilities from both parents
    all_caps = list(parent1_caps | parent2_caps)
    random.shuffle(all_caps)
    half = len(all_caps) // 2
    child_caps.update(all_caps[:half])
    
    # Add some new random capabilities
    num_new = random.randint(0, 2)
    potential_new = ["neural-link", "quantum-process", "auto-scale", "self-heal"]
    for _ in range(num_new):
        new_cap = random.choice(potential_new)
        if new_cap not in child_caps:
            child_caps.add(new_cap)
    
    return sorted(list(child_caps))

def evolve_population(mutation_rate=0.1, cycles=1, goal=""):
    """Run evolution cycle on the workforce."""
    try:
        team = build_team(None, None, None, None, f"evolution-{cycles}")
    except Exception as e:
        # Fallback: create a minimal team
        from workforce.agents import TEAM as TEAM_FALLBACK
        team = {name: type("Agent", {"capabilities": random.sample(list(all_system_caps), random.randint(3, 7))},) for name in random.sample(list(TEAM.keys()), min(5, len(TEAM)))}
    
    results = {
        "generation": 0,
        "mutation_rate": mutation_rate,
        "cycles": cycles,
        "goal": goal,
        "capabilities_gained": [],
        "capabilities_lost": [],
        "organism_fitness": 98.0,
        "agent_evolution": {},
    }
    
    for cycle in range(cycles):
        results["generation"] = cycle
        cycle_gained = []
        cycle_lost = []
        
        for agent_name in list(TEAM.keys()):
            old_caps = set(TEAM[agent_name].capabilities)
            new_caps = mutate_agent(agent_name, mutation_rate)
            TEAM[agent_name].capabilities = new_caps
            
            lost = old_caps - set(TEAM[agent_name].capabilities)
            gained = set(TEAM[agent_name].capabilities) - old_caps
            
            cycle_lost.extend(lost)
            cycle_gained.extend(gained)
        
        results["capabilities_gained"] = list(set(results["capabilities_gained"] + cycle_gained))
        results["capabilities_lost"] = list(set(results["capabilities_lost"] + cycle_lost))
        
        # Calculate fitness
        all_caps = set()
        active_agents = 0
        for agent_name in TEAM:
            all_caps.update(TEAM[agent_name].capabilities)
            if TEAM[agent_name].capabilities:
                active_agents += 1
        
        capability_diversity = len(all_caps) / max(1, len(all_system_caps))
        agent_ratio = active_agents / max(1, len(TEAM))
        results["organism_fitness"] = round(98.0 * (0.8 * capability_diversity + 0.2 * agent_ratio), 2)
        
        results["agent_evolution"][f"cycle-{cycle}"] = {
            "agents_mutated": len(TEAM),
            "capabilities_gained_cycle": len(cycle_gained),
            "capabilities_lost_cycle": len(cycle_lost),
            "fitness": results["organism_fitness"],
        }
    
    results["total_unique_gained"] = len(set(results["capabilities_gained"]))
    results["total_unique_lost"] = len(set(results["capabilities_lost"]))
    
    return results

def run_evolution(args):
    mutation_rate = max(0.0, min(1.0, float(args.get("mutation_rate", 0.1))))
    cycles = max(1, int(args.get("cycles", 1)))
    goal = args.get("goal", "")
    return evolve_population(mutation_rate=mutation_rate, cycles=cycles, goal=goal)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-rate", type=float, default=0.1)
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--goal", type=str, default="")
    args = parser.parse_args()
    results = run_evolution(vars(args))
    
    print("=" * 60)
    print("IXPANSION EVOLUTIONARY BREEDING LOOP")
    print("=" * 60)
    print(f"Mutation rate: {results['mutation_rate']}")
    print(f"Cycles: {results['cycles']}")
    print(f"Goal: {results['goal'] or 'none'}")
    print()
    print(f"Generation: {results['generation'] + 1}/{results['cycles']}")
    print()
    print(f"Capabilities gained: {results['total_unique_gained']}")
    print(f"Capabilities lost: {results['total_unique_lost']}")
    print(f"Organism fitness: {results['organism_fitness']}")
    print()
    print("Agent Evolution Details:")
    for cycle_data in results["agent_evolution"].values():
        print(f"  Cycle {cycle_data['cycle']}: "
              f"{cycle_data['agents_mutated']} agents, "
              f"{cycle_data['capabilities_gained_cycle']} gained, "
              f"{cycle_data['capabilities_lost_cycle']} lost, "
              f"fitness={cycle_data['fitness']}")
    print()
    print("Final Capabilities Overview:")
    # Don't try to build_team here to avoid import issues
    print(f"  (System has {len(all_system_caps)} total unique capabilities in the ecosystem)")
    print()
    print("=" * 60)
