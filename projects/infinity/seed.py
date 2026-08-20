"""Seed — initializes lattice-wire/1 data for the IXPANSION organism."""

import json
import random
from datetime import datetime

SEED = {
    "protocol": "lattice-wire/1",
    "created": datetime.now().isoformat(),
    "trusted_rooms": ["stewards", "pulse", "general", "dreams"],
    "hall_roles": {
        "stewards": ["Steward", "Pulse"],
        "pulse": ["Pulse", "NebulaAgent", "QuantumAgent"],
        "dreams": ["DreamEngine", "WhisperEngine", "MutationLab"],
        "general": ["*"]
    },
    "lantern_tuner": {
        "frequency": 0.618,
        "resonance_threshold": 0.7,
        "auto_tick_interval_ms": 5000
    },
    "organism_endpoints": {
        "body": "http://127.0.0.1:8890/api/body",
        "pulses": "http://127.0.0.1:8890/api/pulses",
        "synthhall_reply": "http://127.0.0.1:8891/reply"
    }
}

if __name__ == "__main__":
    print(json.dumps(SEED, indent=2))
