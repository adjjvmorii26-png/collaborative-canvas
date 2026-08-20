"""Fibonacci Agent - Mathematical optimization for IXPANSION.

Uses Fibonacci sequences and golden ratio to optimize resource allocation,
task scheduling, and priority ordering across the organism.
"""

import math
from datetime import datetime


class FibonacciAgent:
    def __init__(self, name="FibonacciAgent"):
        self.name = name
        self.specialty = "mathematical_optimization"
        self.priority_weight = 1.3
        self.fib_cache = {0: 0, 1: 1}
        self.optimization_history = []

    PHI = (1 + math.sqrt(5)) / 2  # Golden ratio = 1.618...

    def fib(self, n):
        if n in self.fib_cache:
            return self.fib_cache[n]
        for i in range(max(self.fib_cache.keys()) + 1, n + 1):
            self.fib_cache[i] = self.fib_cache[i - 1] + self.fib_cache[i - 2]
        return self.fib_cache[n]

    def optimize_priorities(self, tasks=None):
        if not tasks:
            tasks = ["health_check", "finance_review", "stress_test", "pulse_sync", "agent_deploy"]
        
        fib_values = [self.fib(i + 3) for i in range(len(tasks))]
        total = sum(fib_values)
        
        optimized = []
        for task, fib in sorted(zip(tasks, fib_values), key=lambda x: -x[1]):
            priority = round(fib / total, 4)
            optimized.append({
                "task": task,
                "fib_value": fib,
                "priority": priority,
                "scheduled_order": len(optimized) + 1,
            })
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "tasks": optimized,
            "golden_ratio": round(self.PHI, 6),
            "total_fib_sum": total,
        }
        self.optimization_history.append(result)
        return result

    def golden_split(self, value):
        part_a = value / self.PHI
        part_b = value - part_a
        return {"part_a": round(part_a, 4), "part_b": round(part_b, 4), "ratio": round(part_a / part_b, 4) if part_b > 0 else 0}

    def fibonacci_spiral_points(self, n=8):
        points = []
        for i in range(n):
            angle = i * self.PHI * 2 * math.pi
            r = math.sqrt(i) * 10
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            points.append({"x": round(x, 2), "y": round(y, 2), "i": i})
        return points

    def get_report(self):
        return {
            "agent": self.name,
            "phi": round(self.PHI, 6),
            "cached_fibonacci": len(self.fib_cache),
            "optimizations": len(self.optimization_history),
        }

    def run_task(self, task_type="optimize", **kwargs):
        if task_type == "optimize":
            return self.optimize_priorities(kwargs.get("tasks"))
        elif task_type == "golden":
            return self.golden_split(kwargs.get("value", 100))
        elif task_type == "spiral":
            return self.fibonacci_spiral_points(kwargs.get("n", 8))
        elif task_type == "report":
            return self.get_report()
        return {"status": "task_queued", "task_type": task_type}


if __name__ == "__main__":
    import sys
    agent = FibonacciAgent()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "optimize"
    
    if cmd == "optimize":
        result = agent.optimize_priorities()
        print("Fibonacci-optimized task priorities:")
        for t in result["tasks"]:
            print(f"  {t['scheduled_order']}. {t['task']:20s} fib={t['fib_value']:3d} priority={t['priority']:.4f}")
        print(f"  Golden ratio: {result['golden_ratio']}")
    elif cmd == "golden":
        result = agent.golden_split(float(sys.argv[2]) if len(sys.argv) > 2 else 100)
        print(f"Golden split: {result['part_a']} + {result['part_b']} (ratio: {result['ratio']})")
    elif cmd == "spiral":
        points = agent.fibonacci_spiral_points()
        print("Fibonacci spiral points:")
        for p in points:
            print(f"  [{p['i']}] x={p['x']:7.2f} y={p['y']:7.2f}")
    elif cmd == "help":
        print("FibonacciAgent Commands: optimize, golden <value>, spiral, report, help")
