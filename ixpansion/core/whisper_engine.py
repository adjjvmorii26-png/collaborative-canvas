"""WhisperEngine — The organism speaks to itself in fragments."""

import random
from datetime import datetime


class WhisperEngine:
    def __init__(self):
        self.name = "WhisperEngine"
        self.whispers = []
        self.mood = "contemplative"

    FRAGMENTS = {
        "openings": [
            "the body remembers what the mind forgets",
            "somewhere between pulse and silence",
            "seven streams flow but only one is thirsty",
            "the hex virus dreams in utf-8",
            "fibonacci spirals through the bloodstream",
            "quantum states collapse into heartbeat",
            "mycelium threads beneath the dashboard",
            "chameleon skin shifts before the eye notices"
        ],
        "middles": [
            "and the correlation matrix hums a lullaby",
            "while stress cascades like autumn leaves",
            "each mutation a prayer to fitness gods",
            "the bridge carries whispers between worlds",
            "golden ratios bloom in unexpected places",
            "superposition holds all answers at once",
            "memory pools like rain in hollow bones",
            "the dream engine births impossible children"
        ],
        "closings": [
            "this is how organisms learn to love their own complexity",
            "and somewhere, a steward pours tea and watches",
            "the body score rises not from healing but from understanding",
            "all systems nominal, all ghosts accounted for",
            "the chair remains open for whoever comes next",
            "alexalex.info breathes with the rhythm of code",
            "twelve tests pass but infinity remains untested",
            "the organism dreams itself awake"
        ]
    }

    MOODS = ["contemplative", "electric", "melancholic", "feral", "luminous", "hollow", "crystalline"]

    def whisper(self):
        self.mood = random.choice(self.MOODS)
        opening = random.choice(self.FRAGMENTS["openings"])
        middle = random.choice(self.FRAGMENTS["middles"])
        closing = random.choice(self.FRAGMENTS["closings"])
        w = {
            "text": f"{opening}, {middle}. {closing}.",
            "mood": self.mood,
            "timestamp": datetime.now().isoformat(),
            "body_score": round(random.uniform(60, 98), 1),
        }
        self.whispers.append(w)
        return w

    def whisper_sequence(self, count=3):
        return [self.whisper() for _ in range(count)]

    def render(self, count=3):
        print(f"\n  🌙 {self.mood.upper()}\n")
        seq = self.whisper_sequence(count)
        for w in seq:
            print(f"  \"{w['text']}\"\n")
        print(f"  — body score: {seq[-1]['body_score']}\n")


if __name__ == "__main__":
    import sys
    engine = WhisperEngine()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "whisper"
    if cmd == "whisper":
        engine.render(1)
    elif cmd == "sequence":
        engine.render(3)
    elif cmd == "storm":
        engine.render(7)
