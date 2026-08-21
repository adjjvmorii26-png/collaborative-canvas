"""ConsensusEngine for IXPANSION

Multiple agents vote on organism decisions using different reasoning models.
The organism reaches consensus through weighted voting, not hierarchy.
"""

import json
import random
import math
from datetime import datetime


class ConsensusEngine:
    def __init__(self):
        self.name = "ConsensusEngine"
        self.version = "1.0.0"
        self.decisions = []
        self.voting_history = []

    REASONING_MODELS = {
        "analytical": {"weight": 1.2, "description": "Data-driven, logical"},
        "intuitive": {"weight": 0.9, "description": "Pattern-based, holistic"},
        "adversarial": {"weight": 1.1, "description": "Challenges assumptions"},
        "empathetic": {"weight": 0.8, "description": "Considers impact on agents"},
        "temporal": {"weight": 1.0, "description": "Long-term consequences"},
        "experimental": {"weight": 0.7, "description": "What if we just tried it?"},
    }

    VOTER_POOL = [
        {"agent": "NebulaAgent", "model": "intuitive", "bias": 0.05},
        {"agent": "QuantumAgent", "model": "experimental", "bias": -0.03},
        {"agent": "MyceliumAgent", "model": "empathetic", "bias": 0.02},
        {"agent": "ChameleonAgent", "model": "adaptive", "weight_override": 1.3},
        {"agent": "FibonacciAgent", "model": "analytical", "bias": 0.04},
        {"agent": "OrionAgent", "model": "temporal", "bias": 0.06},
        {"agent": "CodeGenAgent", "model": "analytical", "bias": -0.01},
        {"agent": "HealthMonitor", "model": "empathetic", "bias": 0.03},
        {"agent": "FinanceAgent", "model": "analytical", "bias": 0.02},
        {"agent": "StressTest", "model": "adversarial", "bias": -0.05},
    ]

    def call_vote(self, question, options=None, context=None):
        """Call a vote across all agents on a yes/no or multi-option decision."""
        if not options:
            options = ["yes", "no"]
        
        votes = []
        total_weight = 0
        
        for voter in self.VOTER_POOL:
            model = voter["model"]
            model_info = self.REASONING_MODELS.get(model, {"weight": 1.0})
            weight = voter.get("weight_override", model_info["weight"])
            
            # Simulate voting based on model characteristics
            base_probability = random.uniform(0.3, 0.9)
            bias_adjustment = voter.get("bias", 0)
            vote_probability = max(0.05, min(0.95, base_probability + bias_adjustment))
            
            choice = random.choices(options, weights=[vote_probability, 1 - vote_probability], k=1)[0] if len(options) == 2 else random.choice(options)
            
            confidence = round(random.uniform(0.4, 0.95), 2)
            reasoning = self._generate_reasoning(model, choice, question)
            
            vote = {
                "agent": voter["agent"],
                "model": model,
                "choice": choice,
                "confidence": confidence,
                "weight": weight,
                "reasoning": reasoning,
            }
            votes.append(vote)
            total_weight += weight * confidence

        # Tally results
        tally = {}
        for v in votes:
            key = v["choice"]
            if key not in tally:
                tally[key] = {"count": 0, "weighted_score": 0}
            tally[key]["count"] += 1
            tally[key]["weighted_score"] += v["weight"] * v["confidence"]

        winner = max(tally, key=lambda k: tally[k]["weighted_score"])
        
        decision = {
            "question": question,
            "options": options,
            "context": context,
            "winner": winner,
            "tally": {k: {"votes": v["count"], "score": round(v["weighted_score"], 2)} for k, v in tally.items()},
            "total_voters": len(votes),
            "consensus_strength": round(tally[winner]["weighted_score"] / max(total_weight, 0.01), 3),
            "votes": votes,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.decisions.append(decision)
        return decision

    def _generate_reasoning(self, model, choice, question):
        reasons = {
            "analytical": f"Data suggests {choice} optimizes expected outcome for: {question[:40]}",
            "intuitive": f"Pattern recognition points toward {choice} as the natural path",
            "adversarial": f"Challenging the alternative — {choice} survives scrutiny better",
            "empathetic": f"Consider agent wellbeing — {choice} minimizes disruption",
            "temporal": f"Long-term trajectory favors {choice} despite short-term cost",
            "experimental": f"Untested territory — {choice} generates the most learning",
            "adaptive": f"Context demands flexibility — {choice} preserves optionality",
        }
        return reasons.get(model, f"Voting {choice} based on {model} assessment")

    def get_report(self):
        if not self.decisions:
            return {"engine": self.name, "decisions_made": 0}
        
        avg_consensus = sum(d["consensus_strength"] for d in self.decisions) / len(self.decisions)
        return {
            "engine": self.name,
            "decisions_made": len(self.decisions),
            "average_consensus": round(avg_consensus, 3),
            "last_decision": self.decisions[-1]["question"][:50],
            "last_winner": self.decisions[-1]["winner"],
        }

    def run_cycle(self):
        """Run a demonstration voting cycle."""
        questions = [
            ("Should the organism prioritize health over finance this cycle?", ["yes", "no"]),
            ("Should we generate a new specialist agent?", ["yes", "no"]),
            ("Which domain needs the most attention?", ["health", "finance", "stress", "pulse"]),
        ]
        
        print("=" * 70)
        print("IXPANSION ConsensusEngine — Organism Decision Vote")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        for q, opts in questions:
            d = self.call_vote(q, opts)
            strength_bar = "█" * int(d["consensus_strength"] * 20)
            print(f"  📊 {q}")
            print(f"     Winner: {d['winner']} (consensus: {d['consensus_strength']:.1%} {strength_bar})")
            print(f"     Tally: {json.dumps(d['tally'])}")
            print()
            
            # Show a sample reasoning
            sample = random.choice(d["votes"])
            print(f"     💭 {sample['agent']} ({sample['model']}): \"{sample['reasoning']}\"")
            print()

        report = self.get_report()
        print(f"  Total decisions this session: {report['decisions_made']}")
        print(f"  Average consensus strength: {report['average_consensus']:.1%}")
        print()
        print("=" * 70)


if __name__ == "__main__":
    import sys
    engine = ConsensusEngine()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cycle"

    if cmd == "cycle":
        engine.run_cycle()
    elif cmd == "vote":
        q = sys.argv[2] if len(sys.argv) > 2 else "Default question?"
        opts = sys.argv[3].split(",") if len(sys.argv) > 3 else ["yes", "no"]
        d = engine.call_vote(q, opts)
        print(json.dumps({k: v for k, v in d.items() if k != "votes"}, indent=2))
    elif cmd == "report":
        print(json.dumps(engine.get_report(), indent=2))
    elif cmd == "help":
        print("ConsensusEngine Commands: cycle, vote <question> [options], report, help")
