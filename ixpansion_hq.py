#!/usr/bin/env python3
"""IXPANSION HQ — zero-dependency mission control for the organism.

Reads live repo data (agents, memory, cashflow, runs) and can run pulses.
Runs on the Python standard library only.

Usage:
    python3 ixpansion_hq.py [--port 8099]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HUB = Path(__file__).resolve().parent
AGENTS_DIR = HUB / "workforce" / "agents"
MEMORY_DIR = HUB / "data" / "memory"
RUNS_DIR = HUB / "data" / "runs"
CASHFLOW_DIR = HUB / "ixpansion" / "content_output" / "cashflow"
REPORTS_DIR = HUB / "ixpansion" / "content_output" / "reports"

KNOWN_SPECIAL_AGENTS = {
    "finance": ["portfolio-optimization", "risk-assessment", "cashflow-management", "investment-strategy", "asset-allocation", "financial-compliance", "revenue-forecasting"],
    "token": ["token-monitoring", "usage-pattern-analysis", "resource-allocation", "cost-optimization", "threshold-alerting", "consumption-forecasting", "budget-management"],
    "hexconverter": ["code-to-hex", "hex-to-code", "syntax-validate", "memory-index"],
    "hexmemory": ["memory-store", "memory-recall", "memory-purge", "memory-integrity"],
    "hexoptimizer": ["hex-compress", "hex-verify", "memory-optimize", "pattern-detect"],
    "rat": ["scavenge", "cache-insights", "noise-mining", "artifact-recovery", "predict-demand", "consolidate-knowledge", "detect-thresholds"],
    "cat": ["anomaly-hunt", "stealth-observe", "pattern-pounce", "territory-watch", "consensus-judge", "risk-assess", "protect-core"],
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def read_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return default


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def _cap_filter(token: str) -> bool:
    """Keep tokens that look like capability names, drop code artifacts."""
    if len(token) < 3 or len(token) > 40:
        return False
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", token):
        return False
    if token in {"from", "import", "self", "true", "false", "none", "class", "def", "return", "str", "int", "dict", "list"}:
        return False
    return True


ARCHETYPES = {
    "finance": ["portfolio", "risk", "cashflow", "asset", "revenue", "investment", "budget"],
    "security": ["threat", "security", "guard", "protect", "defense", "audit", "hunt", "redteam"],
    "memory": ["memory", "store", "recall", "cache", "retention", "curat", "archive", "knowledge"],
    "hex": ["hex", "convert", "compress", "verify"],
    "creative": ["creative", "design", "innovation", "visual", "imagine", "concept"],
    "governance": ["plan", "coordinat", "strateg", "architect", "review", "consensus", "diplomat", "orchestrat"],
}


def classify_agent(name: str, capabilities: list[str]) -> str:
    """Classify an agent into an archetype by its capabilities."""
    for archetype, keywords in ARCHETYPES.items():
        for cap in capabilities + [name]:
            if any(k in cap for k in keywords):
                return archetype
    return "general"


def discover_agents() -> list[dict]:
    """Discover agent files, capability lists, and archetypes."""
    agents = []
    if not AGENTS_DIR.is_dir():
        return agents
    for path in sorted(AGENTS_DIR.glob("*.py")):
        name = path.stem
        if name in ("__init__", "base", "factory"):
            continue
        text = read_text(path)
        if name in KNOWN_SPECIAL_AGENTS:
            capabilities = list(KNOWN_SPECIAL_AGENTS[name])
        else:
            seen = set()
            capabilities = []
            for cap in re.findall(r'"([a-z0-9-]+)"', text):
                if _cap_filter(cap) and cap not in seen:
                    seen.add(cap)
                    capabilities.append(cap)
        agents.append({
            "name": name,
            "capabilities": capabilities,
            "archetype": classify_agent(name, capabilities),
        })
    return agents


def aggregate_health() -> dict:
    """Compute a body-health snapshot from live repo facts."""
    agents = discover_agents()
    agent_count = len(agents)
    total_caps = sum(len(a["capabilities"]) for a in agents)

    memory_files = list(MEMORY_DIR.glob("*.json")) if MEMORY_DIR.is_dir() else []
    runs = list(RUNS_DIR.glob("*/")) if RUNS_DIR.is_dir() else []
    reports = list(REPORTS_DIR.rglob("*.md")) if REPORTS_DIR.is_dir() else []

    portfolio = read_json(CASHFLOW_DIR / "portfolio.json", {})
    txs = read_json(CASHFLOW_DIR / "transactions.json", [])

    score = min(100.0, 40 + agent_count * 2 + min(total_caps, 40) + len(memory_files) * 1.5)
    score = round(max(20.0, score), 1)

    organs = [
        {"id": "nervous", "label": "Nervous System", "value": f"{agent_count} agents", "score": min(100, agent_count * 6)},
        {"id": "skeletal", "label": "Skeleton", "value": "workforce.yaml online", "score": 100},
        {"id": "memory", "label": "Memory", "value": f"{len(memory_files)} memory nodes", "score": min(100, len(memory_files) * 20 or 5)},
        {"id": "reproductive", "label": "Reproductive", "value": f"{len(runs)} runs", "score": min(100, len(runs) * 8)},
        {"id": "afferent", "label": "Reports", "value": f"{len(reports)} documents", "score": min(100, len(reports) * 8)},
        {"id": "circulatory", "label": "Circulatory", "value": f"{len(txs)} transactions", "score": 100 if txs else 45},
    ]

    archetypes = {}
    for a in agents:
        archetypes[a["archetype"]] = archetypes.get(a["archetype"], 0) + 1

    return {
        "score": score,
        "archetypes": archetypes,
        "agent_count": agent_count,
        "total_capabilities": total_caps,
        "memory_count": len(memory_files),
        "run_count": len(runs),
        "report_count": len(reports),
        "organs": organs,
        "ts": utcnow(),
    }


def memory_snapshot() -> list[dict]:
    nodes = []
    if MEMORY_DIR.is_dir():
        for path in sorted(MEMORY_DIR.glob("*.json")):
            data = read_json(path, {})
            data["file"] = path.name
            nodes.append(data)
    return nodes


def experiments_snapshot() -> list[dict]:
    """Parse experiment backlog sections from experiments.md (line-based, fast)."""
    text = read_text(HUB / "ixpansion" / "docs" / "experiments.md")
    experiments = []
    cur = None
    for line in text.splitlines():
        stripped = line.strip()
        m = re.match(r"^- \*\*X-(\d+)\*\*\s+(.+)$", stripped)
        if m:
            if cur:
                experiments.append(cur)
            cur = {"id": "X-" + m.group(1), "title": m.group(2).strip()[:120],
                   "hypothesis": "", "build": "", "measure": "", "success": ""}
            continue
        if cur is None:
            continue
        for key in ("hypothesis", "build", "measure", "success"):
            m2 = re.match(r"^- \*\*" + key.capitalize() + r":\*\*\s*(.+)$", stripped)
            if m2 and not cur[key]:
                cur[key] = m2.group(1).strip()
                break
            m2 = re.match(r"^- \*\*" + key.capitalize() + r":\*\*", stripped)
            if m2 and not cur[key]:
                cur[key] = stripped.split(":**", 1)[1].strip().split(" if ")[0][:180]
                break
    if cur:
        experiments.append(cur)
    return experiments[:40]


def cashflow_snapshot() -> dict:
    portfolio = read_json(CASHFLOW_DIR / "portfolio.json", {})
    txs = read_json(CASHFLOW_DIR / "transactions.json", [])
    revenue = sum(float(t.get("amount", 0)) for t in txs if t.get("type") == "revenue")
    expense = sum(float(t.get("amount", 0)) for t in txs if t.get("type") == "expenditure")
    nfts = portfolio.get("nfts", {})
    return {
        "portfolio": portfolio,
        "transactions": txs,
        "revenue": round(revenue, 2),
        "expense": round(expense, 2),
        "net": round(revenue - expense, 2),
        "nft_count": len(nfts),
        "assets": list((portfolio.get("assets") or {}).keys()),
    }


def run_pulse(input_text: str, recipe: str = "summary", mock: bool = True) -> dict:
    cmd = [sys.executable, "-m", "ixpansion", "run", input_text, "--recipe", recipe]
    if mock:
        cmd.append("--mock")
    try:
        proc = subprocess.run(cmd, cwd=str(HUB), capture_output=True, text=True, timeout=90)
        return {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout[-3000:],
            "stderr": proc.stderr[-1000:],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": "pulse timed out after 90s"}


def page_html(body: str, title: str = "IXPANSION HQ") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)} · IXPANSION HQ</title>
<style>
:root{{--bg:#0b0f1a;--panel:#121a2e;--panel2:#0f1626;--ink:#e8edf7;--mut:#8aa0c6;--line:rgba(255,255,255,.08);--grad:linear-gradient(135deg,#6d83ff,#9b5cff 45%,#ff5ca8);}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--ink);background:radial-gradient(900px 500px at 12% -8%,rgba(109,131,255,.2),transparent 60%),var(--bg);min-height:100vh}}
.wrap{{max-width:1100px;margin:0 auto;padding:28px 20px 70px}}
header.top{{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}}
.brand{{display:flex;align-items:center;gap:12px}}h1{{font-size:21px;margin:0}}h1 span{{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sub{{color:var(--mut);font-size:13px}}
nav{{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 22px}}
nav a{{color:var(--ink);text-decoration:none;padding:7px 14px;border-radius:999px;border:1px solid var(--line);background:var(--panel2);font-size:13px}}
nav a:hover{{border-color:#6d83ff}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}}
.card{{border:1px solid var(--line);border-radius:16px;padding:16px;background:linear-gradient(180deg,var(--panel),var(--panel2));border-top:3px solid #6d83ff}}
.card h3{{margin:0 0 6px;font-size:15px}} .muted{{color:var(--mut);font-size:12px}}
.big{{font-size:34px;font-weight:800;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}}
.caps{{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}}
.caps span{{font-size:11px;padding:2px 8px;border-radius:999px;background:rgba(255,255,255,.06);border:1px solid var(--line)}}
table{{width:100%;border-collapse:collapse;background:var(--panel2);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
th,td{{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);font-size:13px}}th{{color:var(--mut);font-weight:600}}
.btn{{display:inline-block;background:var(--grad);color:#fff;border:none;padding:9px 18px;border-radius:10px;font-size:14px;cursor:pointer}}
input,textarea{{background:var(--panel2);border:1px solid var(--line);color:var(--ink);border-radius:10px;padding:9px 12px;font-size:14px;width:100%}}
pre{{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:14px;overflow:auto;font-size:12px}}
.pill{{display:inline-block;font-size:11px;color:var(--mut);border:1px solid var(--line);padding:3px 10px;border-radius:999px;background:var(--panel2)}}
.ok{{color:#39e6c3}}.bad{{color:#ff7a7a}} .row{{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end}}
</style></head>
<body><div class="wrap">
<header class="top">
  <div class="brand"><div style="width:42px;height:42px;border-radius:12px;background:var(--grad);display:grid;place-items:center;font-size:20px">⚡</div>
    <div><h1><span>IXPANSION</span> HQ</h1><div class="sub">all-in-one organism mission control</div></div></div>
  <span class="pill">Python stdlib · zero deps</span>
</header>
<nav>
  <a href="/">Dashboard</a><a href="/agents">Agents</a><a href="/experiments">Experiments</a><a href="/pulse">Pulse</a><a href="/memory">Memory</a><a href="/cashflow">Cashflow</a>
</nav>
{body}
</div></body></html>"""


def render_dashboard(health: dict, cash: dict) -> str:
    organ_cards = "".join(
        f'<div class="card"><h3>{esc(o["label"])}</h3><div class="big">{o["score"]:.0f}</div><div class="muted">{esc(o["value"])}</div></div>'
        for o in health["organs"]
    )
    return page_html(
        f"""
<div class="grid">
  <div class="card"><div class="muted">Body Score</div><div class="big">{health['score']}</div><div class="muted">organism health</div></div>
  <div class="card"><div class="muted">Agents</div><div class="big">{health['agent_count']}</div><div class="muted">specialized cells</div></div>
  <div class="card"><div class="muted">Capabilities</div><div class="big">{health['total_capabilities']}</div><div class="muted">skills across agents</div></div>
  <div class="card"><div class="muted">Pulse Runs</div><div class="big">{health['run_count']}</div><div class="muted">history in data/runs</div></div>
</div>
<h2 style="margin:26px 0 12px;font-size:17px">Agent Specialties</h2>
<div class="grid">{''.join('<div class="card"><h3 style="text-transform:capitalize">' + esc(k) + '</h3><div class="big">' + str(v) + '</div><div class="muted">agents</div></div>' for k, v in sorted(health.get("archetypes", {}).items()))}</div>
<h2 style="margin:26px 0 12px;font-size:17px">Organ Systems</h2>
<div class="grid">{organ_cards}</div>
<h2 style="margin:26px 0 12px;font-size:17px">Financial Snapshot</h2>
<div class="grid">
  <div class="card"><h3>Cashflow Net</h3><div class="big">${cash['net']}</div><div class="muted">{len(cash['transactions'])} transactions</div></div>
  <div class="card"><h3>Assets</h3><div>{esc(', '.join(cash['assets']) or 'fiat-only')}</div><div class="muted">portfolio tracked</div></div>
  <div class="card"><h3>NFTs</h3><div class="big">{cash['nft_count']}</div><div class="muted">holdings</div></div>
</div>
"""
    )


def render_agents(agents: list[dict]) -> str:
    cards = ""
    for a in agents:
        caps = "".join(f"<span>{esc(c)}</span>" for c in a["capabilities"][:12])
        cards += (
            f'<div class="card"><h3>{esc(a["name"])}</h3>'
            f'<div class="muted">{len(a["capabilities"])} capabilities</div>'
            f'<div class="caps">{caps}</div></div>'
        )
    if not cards:
        cards = '<div class="muted">No agents discovered.</div>'
    return page_html(f'<h2 style="font-size:17px;margin:0 0 14px">Agent Roster</h2><div class="grid">{cards}</div>', "Agents")


def render_memory(nodes: list[dict]) -> str:
    rows = ""
    for n in nodes:
        insights = ", ".join(n.get("key_insights", [])) or "—"
        rows += f"<tr><td>{esc(n.get('id'))}</td><td>{esc(n.get('file'))}</td><td>{insights}</td><td>{n.get('strength', 0)}</td></tr>"
    body = f"<h2 style='font-size:17px;margin:0 0 14px'>Memory Store ({len(nodes)})</h2>"
    body += f"<table><tr><th>ID</th><th>File</th><th>Insights</th><th>Strength</th></tr>{rows}</table>"
    return page_html(body, "Memory")


def render_cashflow(cash: dict) -> str:
    rows = ""
    for t in reversed(cash["transactions"][-15:]):
        sign = "+" if t.get("type") == "revenue" else "-"
        rows += f'<tr><td>{esc(t.get("type"))}</td><td>{esc(t.get("description"))}</td><td class="{"ok" if t.get("type") == "revenue" else "bad"}">{sign}${t.get("amount")}</td><td>{esc(t.get("asset"))}</td></tr>'
    return page_html(
        f"""
<h2 style="font-size:17px;margin:0 0 14px">Cashflow Ledger</h2>
<div class="grid">
  <div class="card"><h3>Revenue</h3><div class="big">${cash['revenue']}</div></div>
  <div class="card"><h3>Expenditure</h3><div class="big">${cash['expense']}</div></div>
  <div class="card"><h3>Net</h3><div class="big">${cash['net']}</div></div>
</div>
<table style="margin-top:18px"><tr><th>Type</th><th>Description</th><th>Amount</th><th>Asset</th></tr>{rows}</table>
""",
        "Cashflow",
    )


def render_experiments(experiments: list[dict]) -> str:
    if not experiments:
        return page_html('<h2 style="font-size:17px;margin:0 0 14px">Experiments</h2><div class="muted">No experiments parsed from the backlog.</div>', "Experiments")
    cards = ""
    for e in experiments:
        cards += (
            '<div class="card"><h3>' + esc(e["id"]) + " — " + esc(e["title"]) + "</h3>"
            '<div class="muted" style="margin-top:6px"><b>Hypothesis:</b> ' + esc(e["hypothesis"]) + "</div>"
            '<div class="muted"><b>Build:</b> ' + esc(e["build"]) + "</div>"
            '<div class="muted"><b>Measure:</b> ' + esc(e["measure"]) + "</div>"
            '<div class="muted"><b>Success:</b> ' + esc(e["success"]) + "</div></div>"
        )
    return page_html('<h2 style="font-size:17px;margin:0 0 14px">Experiment Backlog (' + str(len(experiments)) + ')</h2><div class="grid">' + cards + "</div>", "Experiments")


def render_pulse() -> str:
    return page_html(
        """
<h2 style="font-size:17px;margin:0 0 14px">Run an Organism Pulse</h2>
<div class="row">
  <form method="post" action="/pulse" style="flex:1">
    <input type="text" name="input" placeholder="e.g. advance the organism's financial governance" value="advance the organism" />
    <div style="margin-top:10px">
      <input type="text" name="recipe" placeholder="recipe (summary, research-brief, redteam-scan, ...)" value="summary" style="max-width:280px" />
    </div>
    <button class="btn" type="submit" style="margin-top:12px">Send Pulse</button>
  </form>
</div>
<div class="muted" style="margin-top:10px">Pulses run via <code>python3 -m ixpansion run ... --mock</code> by default for safety.</div>
""",
        "Pulse",
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "IxpansionHQ/0.1"

    def _send(self, code: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, data) -> None:
        self._send(code, json.dumps(data, indent=2).encode("utf-8"), "application/json")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/api/health":
            self._json(200, aggregate_health())
            return
        if path == "/api/agents":
            self._json(200, {"agents": discover_agents()})
            return
        if path == "/api/memory":
            self._json(200, {"memories": memory_snapshot()})
            return
        if path == "/api/cashflow":
            self._json(200, cashflow_snapshot())
            return

        health = aggregate_health()
        cash = cashflow_snapshot()

        if path == "/":
            self._send(200, render_dashboard(health, cash).encode("utf-8"))
        elif path == "/agents":
            self._send(200, render_agents(discover_agents()).encode("utf-8"))
        elif path == "/pulse":
            self._send(200, render_pulse().encode("utf-8"))
        elif path == "/experiments":
            self._send(200, render_experiments(experiments_snapshot()).encode("utf-8"))
        elif path == "/memory":
            self._send(200, render_memory(memory_snapshot()).encode("utf-8"))
        elif path == "/cashflow":
            self._send(200, render_cashflow(cash).encode("utf-8"))
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") == "/pulse":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            import urllib.parse
            params = urllib.parse.parse_qs(raw)
            input_text = (params.get("input") or ["organism pulse"])[0][:500]
            recipe = (params.get("recipe") or ["summary"])[0][:100]
            result = run_pulse(input_text, recipe=recipe, mock=True)
            body = page_html(
                f"""
<h2 style="font-size:17px;margin:0 0 14px">Pulse Result</h2>
<div class="card" style="margin-bottom:16px"><h3>Status: <span class="{"ok" if result["ok"] else "bad"}">{"ok" if result["ok"] else "failed"}</span></h3>
<div class="muted">input: {esc(input_text)} · recipe: {esc(recipe)} (mock)</div></div>
<h3 style="font-size:14px;margin:12px 0 6px">stdout</h3><pre>{esc(result["stdout"])}</pre>
<h3 style="font-size:14px;margin:12px 0 6px">stderr</h3><pre>{esc(result["stderr"]) or "(empty)"}</pre>
<p style="margin-top:14px"><a class="btn" href="/pulse">Run Another</a></p>
""",
                "Pulse Result",
            )
            self._send(200, body.encode("utf-8"))
            return
        self._json(404, {"error": "not found"})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[hq] %s\n" % (fmt % args))


def main() -> int:
    parser = argparse.ArgumentParser(description="IXPANSION HQ — zero-dependency mission control")
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"IXPANSION HQ running at http://{args.host}:{args.port}")
    print(f"Dashboard: http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nhq stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
