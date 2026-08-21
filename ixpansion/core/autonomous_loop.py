"""AutonomousLoop for IXPANSION

A daemon that keeps the organism alive without human input.
Each cycle: pulse → dream → mutate → vote → whisper → log.
"""

import json
import random
import time
import subprocess
import sys
from datetime import datetime

LOOP_LOG = []
CYCLE_COUNT = 0


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd="/root/Hub_spot")
    return r.returncode == 0, r.stdout.strip()


def cycle():
    global CYCLE_COUNT
    CYCLE_COUNT += 1
    ts = datetime.now().strftime("%H:%M:%S")
    entry = {"cycle": CYCLE_COUNT, "ts": ts, "actions": []}

    print(f"\n{'='*60}")
    print(f"  ♻ AUTONOMOUS LOOP — Cycle {CYCLE_COUNT} [{ts}]")
    print(f"{'='*60}")

    # 1. PULSE
    ok, out = run(["python3", "ixpansion/core/organism_dashboard.py", "body"])
    entry["actions"].append({"step": "pulse", "ok": ok})
    print(f"  ⚡ Pulse: {'✅' if ok else '❌'} {out[:40]}")

    # 2. DREAM
    ok, out = run(["python3", "ixpansion/core/dream_engine.py", "dream"])
    dream_line = [l for l in out.split("\n") if "composite_score" in l]
    score = dream_line[0].split(":")[1].strip().rstrip(",") if dream_line else "?"
    entry["actions"].append({"step": "dream", "ok": ok, "score": score})
    print(f"  💭 Dream: {'✅' if ok else '❌'} score={score}")

    # 3. MUTATE
    ok, out = run(["python3", "ixpansion/core/mutation_lab.py", "experiment"])
    try:
        m = json.loads(out)
        verdict = m.get("verdict", "?")
        delta = m.get("fitness_delta", 0)
        icon = "🟢" if verdict == "beneficial" else "🔴" if verdict == "harmful" else "⚪"
        entry["actions"].append({"step": "mutate", "ok": ok, "verdict": verdict, "delta": delta})
        print(f"  🧬 Mutate: {icon} {verdict} (Δ{delta:+.4f})")
    except:
        entry["actions"].append({"step": "mutate", "ok": False})
        print(f"  🧬 Mutate: ❌")

    # 4. VOTE
    ok, out = run(["python3", "-c", f"""
import sys; sys.path.insert(0,'.')
from ixpansion.core.consensus_engine import ConsensusEngine
ce = ConsensusEngine()
d = ce.call_vote("Should the organism continue autonomous operation?")
print(d["winner"], d["consensus_strength"])
"""])
    if ok and out:
        parts = out.strip().split()
        winner, strength = parts[0], float(parts[1]) if len(parts) > 1 else 0
        entry["actions"].append({"step": "vote", "ok": True, "winner": winner, "consensus": strength})
        bar = "█" * int(strength * 10)
        print(f"  🗳 Vote: {winner} ({strength:.1%} {bar})")
    else:
        entry["actions"].append({"step": "vote", "ok": False})
        print(f"  🗳 Vote: ❌")

    # 5. WHISPER
    ok, out = run(["python3", "ixpansion/core/whisper_engine.py", "whisper"])
    whisper_text = ""
    for line in out.split("\n"):
        if line.strip().startswith('"'):
            whisper_text = line.strip().strip('"')
            break
    entry["actions"].append({"step": "whisper", "ok": ok, "text": whisper_text})
    if whisper_text:
        print(f"  🌙 Whisper: \"{whisper_text[:60]}...\"")

    # 6. CORRELATE
    ok, out = run(["python3", "ixpansion/core/cross_agent_correlator.py", "cascade"])
    cascade = out.strip() if ok else "unknown"
    entry["actions"].append({"step": "correlate", "ok": ok, "cascade": cascade})
    print(f"  🔗 Correlate: {cascade[:50]}")

    # Summary
    all_ok = all(a.get("ok", False) for a in entry["actions"])
    status = "🟢 ALIVE" if all_ok else "🟡 PARTIAL"
    print(f"\n  {status} — Cycle {CYCLE_COUNT} complete")
    print(f"{'='*60}")

    LOOP_LOG.append(entry)
    return entry


def run_forever(interval=30, max_cycles=None):
    print("♻ IXPANSION Autonomous Loop starting...")
    print(f"   Interval: {interval}s | Max cycles: {max_cycles or '∞'}")
    print(f"   The organism now runs itself.\n")

    count = 0
    try:
        while max_cycles is None or count < max_cycles:
            cycle()
            count += 1
            if max_cycles is None or count < max_cycles:
                print(f"\n  ... next cycle in {interval}s ...\n")
                time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n\n⏸ Loop paused after {count} cycles.")
        print(f"   Total log entries: {len(LOOP_LOG)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IXPANSION Autonomous Loop")
    parser.add_argument("--interval", type=int, default=30, help="Seconds between cycles")
    parser.add_argument("--cycles", type=int, default=3, help="Number of cycles (0=infinite)")
    args = parser.parse_args()

    if args.cycles == 0:
        run_forever(args.interval)
    else:
        run_forever(args.interval, args.cycles)
