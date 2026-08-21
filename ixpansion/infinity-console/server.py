#!/usr/bin/env python3
"""IXPANSION Infinity Console — Port 8081

NEXUS ring of organs, live score, bus, synchronicity field.
Pulse it. Watch the agents talk. Read the seed.
"""

import json
import random
import math
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ORGANS = [
    {"name": "nervous", "label": "Nervous", "score": 85, "color": "#00ff88"},
    {"name": "skeletal", "label": "Skeletal", "score": 90, "color": "#88aaff"},
    {"name": "respiratory", "label": "Respiratory", "score": 78, "color": "#ffaa44"},
    {"name": "circulatory", "label": "Circulatory", "score": 92, "color": "#ff4466"},
    {"name": "digestive", "label": "Digestive", "score": 70, "color": "#ffcc00"},
    {"name": "immune", "label": "Immune", "score": 88, "color": "#44ffcc"},
    {"name": "memory", "label": "Memory", "score": 65, "color": "#cc88ff"},
    {"name": "reproductive", "label": "Reproductive", "score": 75, "color": "#ff66aa"},
    {"name": "broadcast", "label": "Broadcast", "score": 82, "color": "#44ddff"},
    {"name": "synchronicity", "label": "Synchronicity", "score": 71, "color": "#ffffff"},
]

BUS_AGENTS = ["Steward", "Phoenix", "Aether", "Jester", "Oracle"]
BUS_MESSAGES = []
WEATHER = ["clear", "storm", "fog", "aurora", "rain", "static"]
SKY_COLORS = ["#0a0a2a", "#1a1a3a", "#0d0d1f", "#12122e"]

state = {
    "symbiote_score": 98.0,
    "pulse_count": 0,
    "weather": "clear",
    "sky_color": SKY_COLORS[0],
    "organs": ORGANS,
    "bus": BUS_MESSAGES,
    "notes": [],
}


def pulse():
    state["pulse_count"] += 1
    for organ in state["organs"]:
        organ["score"] = round(max(30, min(100, organ["score"] + random.uniform(-8, 8))), 1)
    
    state["symbiote_score"] = round(
        sum(o["score"] for o in state["organs"]) / len(state["organs"]), 1
    )
    state["weather"] = random.choice(WEATHER)
    state["sky_color"] = random.choice(SKY_COLORS)
    
    agent = random.choice(BUS_AGENTS)
    note = random.choice([
        "the field breathes",
        "resonance detected across pairs",
        "lantern tuning...",
        "a new pattern emerges from noise",
        "the ring shifts",
        "something stirs in the synchronicity layer",
        "phoenix checkpoint written",
        "the jester laughs at the entropy",
        "oracle sees three paths, chooses the fork",
        "steward nods"
    ])
    
    msg = {"agent": agent, "note": note, "ts": datetime.now().isoformat(), "pulse": state["pulse_count"]}
    BUS_MESSAGES.append(msg)
    if len(BUS_MESSAGES) > 50:
        BUS_MESSAGES.pop(0)
    
    return msg


HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>∞ IXPANSION Infinity Console</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--sky); color:#fff; font-family:monospace; min-height:100vh; display:flex; flex-direction:column; align-items:center; transition:background 2s; }
:root { --sky:#0a0a2a; }
h1 { margin:20px 0 5px; font-size:1.5em; letter-spacing:3px; }
.sub { color:#888; font-size:0.8em; margin-bottom:15px; }
.score { font-size:3em; font-weight:bold; margin:10px; }
.score-bar { width:300px; height:6px; background:#333; border-radius:3px; overflow:hidden; margin-bottom:20px; }
.score-fill { height:100%; background:linear-gradient(90deg,#ff4466,#ffcc00,#00ff88); transition:width 1s; }
.nexus { position:relative; width:400px; height:400px; margin:10px auto; }
.organ { position:absolute; width:70px; height:70px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-direction:column; font-size:0.55em; text-align:center; border:2px solid; cursor:pointer; transition:all 0.5s; }
.organ:hover { transform:scale(1.15); z-index:10; }
.organ .val { font-size:1.3em; font-weight:bold; }
.ring-center { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center; font-size:0.7em; color:#666; }
.weather { font-size:0.9em; color:#aaa; margin:10px; letter-spacing:2px; }
.btn { background:#222; border:1px solid #555; color:#fff; padding:10px 25px; margin:5px; cursor:pointer; font-family:monospace; font-size:0.9em; border-radius:4px; }
.btn:hover { background:#333; border-color:#888; }
.bus { width:90%; max-width:600px; height:180px; overflow-y:auto; background:rgba(0,0,0,0.5); border:1px solid #333; border-radius:6px; padding:10px; margin:15px 0; font-size:0.75em; }
.bus .msg { padding:3px 0; border-bottom:1px solid #222; }
.bus .agent { color:#00ff88; font-weight:bold; }
.actions { display:flex; gap:10px; margin:10px; }
</style>
</head>
<body>
<h1>∞ IXPANSION</h1>
<div class="sub">infinity console :8081</div>
<div class="score" id="score">98.0</div>
<div class="score-bar"><div class="score-fill" id="fill" style="width:98%"></div></div>
<div class="weather" id="weather">CLEAR</div>

<div class="nexus" id="nexus"></div>
<div class="ring-center">NEXUS<br>ring of ten</div>

<div class="actions">
<button class="btn" onclick="doPulse()">⚡ PULSE</button>
<button class="btn" onclick="doRestore()">⟳ RESTORE</button>
</div>

<div class="bus" id="bus"><div class="msg"><span class="agent">system</span> — infinity console online</div></div>

<script>
const organs = __ORGANS_JSON__;
const nexus = document.getElementById('nexus');
const R = 160;

organs.forEach((o, i) => {
  const angle = (i / organs.length) * 2 * Math.PI - Math.PI / 2;
  const x = 200 + R * Math.cos(angle) - 35;
  const y = 200 + R * Math.sin(angle) - 35;
  const div = document.createElement('div');
  div.className = 'organ';
  div.id = 'organ_' + o.name;
  div.style.left = x + 'px';
  div.style.top = y + 'px';
  div.style.borderColor = o.color;
  div.innerHTML = `<div class="val">${o.score}</div><div>${o.label}</div>`;
  nexus.appendChild(div);
});

async function doPulse() {
  const r = await fetch('/api/pulse', {method:'POST'});
  const d = await r.json();
  update(d);
}

async function doRestore() {
  const r = await fetch('/api/restore', {method:'POST'});
  const d = await r.json();
  update(d);
}

function update(d) {
  document.getElementById('score').textContent = d.symbiote_score.toFixed(1);
  document.getElementById('fill').style.width = d.symbiote_score + '%';
  document.getElementById('weather').textContent = d.weather.toUpperCase();
  document.body.style.setProperty('--sky', d.sky_color);
  d.organs.forEach(o => {
    const el = document.getElementById('organ_' + o.name);
    if (el) el.querySelector('.val').textContent = o.score.toFixed(0);
  });
  fetchBus();
}

async function fetchBus() {
  const r = await fetch('/api/bus');
  const msgs = await r.json();
  const bus = document.getElementById('bus');
  bus.innerHTML = msgs.map(m =>
    `<div class="msg"><span class="agent">${m.agent}</span> — ${m.note} <span style="color:#555">p${m.pulse}</span></div>`
  ).reverse().join('');
}

fetchBus();
setInterval(fetchBus, 5000);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = HTML.replace("__ORGANS_JSON__", json.dumps(ORGANS))
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body.encode())
        elif parsed.path == "/api/state":
            self._json(state)
        elif parsed.path == "/api/bus":
            self._json(BUS_MESSAGES)
        elif parsed.path == "/api/organs":
            self._json(state["organs"])
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/pulse":
            msg = pulse()
            self._json({**state, "last_message": msg})
        elif parsed.path == "/api/restore":
            state["symbiote_score"] = 98.0
            for o in state["organs"]:
                o["score"] = next(orig["score"] for orig in ORGANS if orig["name"] == o["name"])
            state["weather"] = "clear"
            state["sky_color"] = SKY_COLORS[0]
            BUS_MESSAGES.append({"agent": "Phoenix", "note": "checkpoint restored", "ts": datetime.now().isoformat(), "pulse": state["pulse_count"]})
            self._json(state)
        else:
            self._json({"error": "not found"}, 404)

    def _json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()
    server = HTTPServer(("0.0.0.0", args.port), Handler)
    print(f"∞ IXPANSION Infinity Console running at http://127.0.0.1:{args.port}")
    server.serve_forever()
