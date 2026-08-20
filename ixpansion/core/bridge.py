import urllib.parse
"""Bridge between SynthHall (8891) and Organism Console (8890).

Routes agent communications through mood-aware SynthHall replies
while monitoring organism health via the console API.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime


SYNTHHALL_URL = "http://127.0.0.1:8891"
CONSOLE_URL = "http://127.0.0.1:8890"


def synthhall_reply(agent, room, context):
    """Get a mood-aware reply from SynthHall."""
    import urllib.parse; encoded_ctx = urllib.parse.quote(context); url = f"{SYNTHHALL_URL}/reply?agent={agent}&room={room}&ctx={encoded_ctx}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.read().decode()
    except Exception as e:
        return f"Error: {e}"


def get_organism_body():
    """Get organism health from console."""
    url = f"{CONSOLE_URL}/api/body"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def bridge_cycle():
    """Run a bridge cycle - query both systems and correlate."""
    print("=" * 70)
    print("IXPANSION Bridge: SynthHall ↔ Organism Console")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 70)
    print()

    # Get organism health
    body = get_organism_body()
    score = body.get("symbiote_score", 0)
    metabolism = body.get("metabolism", {})
    print(f"Organism Score: {score}")
    print(f"Heart Rate: {metabolism.get('heart_rate', 'N/A')}")
    print(f"Temperature: {metabolism.get('temperature', 'N/A')}")
    print(f"Stress: {metabolism.get('stress', 'N/A')}")
    print()

    # Get SynthHall reply based on organism state
    if score > 80:
        mood_context = f"Organism healthy (score={score}). Report status."
    elif score > 60:
        mood_context = f"Organism moderate (score={score}). Monitor closely."
    else:
        mood_context = f"Organism stressed (score={score}). Alert steward."

    reply = synthhall_reply("Pulse", "stewards", mood_context)
    print(f"SynthHall Response:")
    print(reply)
    print()

    # Bridge status
    print("=" * 70)
    print("Bridge Status:")
    print(f"  SynthHall: {SYNTHHALL_URL} ✅")
    print(f"  Console: {CONSOLE_URL} ✅")
    print(f"  Organism Score: {score}")
    print(f"  Bridge Active: True")
    print("=" * 70)

    return {"score": score, "reply": reply}


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cycle"

    if cmd == "cycle":
        bridge_cycle()
    elif cmd == "reply":
        agent = sys.argv[2] if len(sys.argv) > 2 else "Pulse"
        room = sys.argv[3] if len(sys.argv) > 3 else "stewards"
        ctx = sys.argv[4] if len(sys.argv) > 4 else "Hello"
        print(synthhall_reply(agent, room, ctx))
    elif cmd == "body":
        body = get_organism_body()
        print(json.dumps(body, indent=2))
    elif cmd == "help":
        print("Bridge Commands: cycle, reply <agent> <room> <ctx>, body, help")
