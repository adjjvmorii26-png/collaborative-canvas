"""Mycelium Agent - Fungal network data routing for IXPANSION.

Models after mycelium networks: distributes information underground
(invisible to individual agents) connecting all parts of the organism.
Optimizes information flow paths like nutrient distribution.
"""

import random
import math
from datetime import datetime


class MyceliumAgent:
    def __init__(self, name="MyceliumAgent"):
        self.name = name
        self.specialty = "underground_data_routing"
        self.priority_weight = 1.3
        self.network_nodes = {}
        self.nutrient_flows = []
        self.connection_strength = {}

    def initialize_network(self, nodes=None):
        if not nodes:
            nodes = ["health", "finance", "stress", "pulse", "wordpress", "synchronicity", "synthhall"]
        
        self.network_nodes = {}
        for node in nodes:
            self.network_nodes[node] = {
                "nutrient_level": round(random.uniform(0.3, 1.0), 3),
                "connections": [],
                "health": random.choice(["thriving", "stable", "stressed"]),
            }
        
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() > 0.4:
                    strength = round(random.uniform(0.2, 1.0), 3)
                    self.connection_strength[f"{nodes[i]}↔{nodes[j]}"] = strength
                    self.network_nodes[nodes[i]]["connections"].append(nodes[j])
                    self.network_nodes[nodes[j]]["connections"].append(nodes[i])
        
        return self.network_nodes

    def route_information(self, source, destination, info):
        path = [source]
        current = source
        visited = {source}
        
        for _ in range(10):
            neighbors = self.network_nodes.get(current, {}).get("connections", [])
            unvisited = [n for n in neighbors if n not in visited]
            if not unvisited:
                break
            
            weights = [self.connection_strength.get(f"{current}↔{n}", 0.5) for n in unvisited]
            current = random.choices(unvisited, weights=weights, k=1)[0]
            path.append(current)
            visited.add(current)
            
            if current == destination:
                break
        
        flow = {
            "source": source,
            "destination": destination,
            "path": path,
            "hops": len(path) - 1,
            "reached": current == destination,
            "efficiency": round(1.0 / max(len(path) - 1, 1), 3),
            "timestamp": datetime.now().isoformat(),
        }
        self.nutrient_flows.append(flow)
        return flow

    def optimize_network(self):
        optimizations = []
        for pair, strength in self.connection_strength.items():
            if strength < 0.3:
                optimizations.append({
                    "action": "strengthen",
                    "connection": pair,
                    "current_strength": strength,
                    "target_strength": round(strength + 0.3, 3),
                })
            elif strength > 0.9:
                optimizations.append({
                    "action": "prune_redundant",
                    "connection": pair,
                    "current_strength": strength,
                })
        
        return {
            "optimizations": optimizations,
            "total_connections": len(self.connection_strength),
            "avg_strength": round(sum(self.connection_strength.values()) / max(len(self.connection_strength), 1), 3),
        }

    def get_network_health(self):
        if not self.network_nodes:
            return {"status": "uninitialized"}
        
        thriving = sum(1 for n in self.network_nodes.values() if n["health"] == "thriving")
        total = len(self.network_nodes)
        avg_nutrients = sum(n["nutrient_level"] for n in self.network_nodes.values()) / total
        
        return {
            "nodes": total,
            "thriving": thriving,
            "health_ratio": round(thriving / total, 3),
            "avg_nutrients": round(avg_nutrients, 3),
            "connections": len(self.connection_strength),
        }

    def run_task(self, task_type="init", **kwargs):
        if task_type == "init":
            return self.initialize_network(kwargs.get("nodes"))
        elif task_type == "route":
            return self.route_information(
                kwargs.get("source", "health"),
                kwargs.get("dest", "finance"),
                kwargs.get("info", "status_update"),
            )
        elif task_type == "optimize":
            return self.optimize_network()
        elif task_type == "health":
            return self.get_network_health()
        return {"status": "task_queued", "task_type": task_type}


if __name__ == "__main__":
    import sys
    agent = MyceliumAgent()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "init"
    
    if cmd == "init":
        nodes = agent.initialize_network()
        print(f"Network initialized: {len(nodes)} nodes, {len(agent.connection_strength)} connections")
    elif cmd == "route":
        agent.initialize_network()
        flow = agent.route_information("health", "synthhall", "status_update")
        print(f"Route: {' → '.join(flow['path'])}")
        print(f"  Hops: {flow['hops']}, Reached: {flow['reached']}, Efficiency: {flow['efficiency']}")
    elif cmd == "optimize":
        agent.initialize_network()
        result = agent.optimize_network()
        print(f"Optimizations: {len(result['optimizations'])}")
        print(f"  Avg strength: {result['avg_strength']}")
    elif cmd == "health":
        agent.initialize_network()
        h = agent.get_network_health()
        print(f"Nodes: {h['nodes']}, Thriving: {h['thriving']}, Connections: {h['connections']}")
    elif cmd == "help":
        print("MyceliumAgent Commands: init, route, optimize, health, help")
