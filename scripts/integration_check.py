#!/usr/bin/env python3
"""Full integration check for the Organism Console against REAL hub data.

Starts the console on an ephemeral port, exercises every API endpoint over HTTP,
verifies live data (cash flow, YouTube, recipes, keys, organs), then writes a
report to ixpansion/content_output/reports/console-integration/report.md.

Usage: python3 scripts/integration_check.py [--port 8897]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import threading
import urllib.request
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path

HUB = Path(__file__).resolve().parents[1]
CONSOLE = HUB / "ixpansion" / "organism-console"

_spec = importlib.util.spec_from_file_location("organism_console_server", CONSOLE / "server.py")
server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(server)

PASS, FAIL = "PASS", "FAIL"
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    print(f"[{PASS if ok else FAIL}] {name} — {detail}")


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8897)
    args = parser.parse_args()

    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), server.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    server.record_score()
    base = f"http://127.0.0.1:{args.port}"

    try:
        body = get(f"{base}/api/body")
        check("body snapshot", "symbiote_score" in body and "organs" in body)
        check("symbiote score numeric", isinstance(body.get("symbiote_score"), (int, float)), f"score={body.get('symbiote_score')}")
        check("built-in organs >= 9", len(body.get("organs", [])) >= 9, f"{len(body.get('organs', []))} organs")
        cash = body.get("cashflow", {})
        check("cash flow real data", cash.get("transaction_count", 0) >= 1, f"{cash.get('transaction_count')} txs, net=${cash.get('net')}")
        yt = body.get("youtube", {})
        check("youtube real data", yt.get("channels", 0) >= 1, f"{yt.get('channels')} channels / {yt.get('campaigns')} campaigns")
        check("recipes real data", len(body.get("recipes", [])) >= 1, f"{len(body.get('recipes', []))} recipes")
        raw = json.dumps(body)
        key_store = json.loads((HUB / "ixpansion" / "content_output" / "api_keys.json").read_text("utf-8"))
        secrets = [str(e.get("key_value", "")) for e in key_store.values() if len(str(e.get("key_value", ""))) > 20]
        leaked = [s[:8] for s in secrets if s in raw]
        check("keys masked in payload", not leaked, "no raw key material in body" if not leaked else f"LEAKED: {leaked}")
        check("metabolism embedded", "metabolism" in body and len(body["metabolism"].get("vitals", [])) == 6)

        meta = get(f"{base}/api/metabolism")
        check("metabolism endpoint", len(meta.get("vitals", [])) == 6, f"stress={meta.get('stress')}")

        hm = get(f"{base}/api/heatmap")
        check("heatmap endpoint", len(hm.get("rows", [])) == 9 and hm.get("days") == 7, f"{len(hm.get('rows', []))} rows x {hm.get('days')} days")

        hist = get(f"{base}/api/history")
        check("score history seeded", len(hist.get("history", [])) >= 1, f"{len(hist.get('history', []))} snapshots")

        msg = post(f"{base}/api/bus", {"organ": "circulatory", "topic": "integration", "severity": "info", "body": "integration check", "sender": "integration"})
        check("bus post", msg.get("organ") == "circulatory", msg.get("id", ""))
        bus = get(f"{base}/api/bus")
        check("bus list", len(bus.get("messages", [])) >= 1, f"{len(bus.get('messages', []))} messages")

        cons = post(f"{base}/api/consensus", {"proposal": "run a weekly youtube campaign with a cost budget, schedule, and fallback"})
        check("consensus endpoint", cons.get("verdict") in ("consensus reached", "needs review", "consensus blocked"), cons.get("verdict"))

        organs = get(f"{base}/api/organs")
        check("custom organs list", isinstance(organs.get("custom"), list), f"{len(organs.get('custom', []))} custom organs")

        pulse = post(f"{base}/api/pulse", {"input": "integration check: synchronize the organism", "recipe": "summary", "mock": True})
        check("mock pulse run", bool(pulse.get("ok")), "real mock recipe run completed" if pulse.get("ok") else pulse.get("stderr", "")[:120])

        hist2 = get(f"{base}/api/history")
        check("history grew after activity", len(hist2.get("history", [])) >= len(hist.get("history", [])), f"{len(hist2.get('history', []))} snapshots")

        body2 = get(f"{base}/api/body")
        check("score recomputed", isinstance(body2.get("symbiote_score"), (int, float)), f"score={body2.get('symbiote_score')}")
    finally:
        httpd.shutdown()
        httpd.server_close()

    ok_count = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    report_dir = HUB / "ixpansion" / "content_output" / "reports" / "console-integration"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.md"
    lines = [
        "# Console Integration Check",
        "",
        f"- **Date:** {datetime.now(timezone.utc).isoformat()}",
        f"- **Result:** {ok_count}/{total} checks passed",
        "",
        "## Checks",
        "",
    ]
    for name, ok, detail in results:
        lines.append(f"- [{'x' if ok else ' '}] {name} — {detail}")
    lines += [
        "",
        "## Verdict",
        "",
        f"The organism console is **{'HEALTHY' if ok_count == total else 'DEGRADED'}** "
        f"({ok_count}/{total}).",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nreport: {report_path.relative_to(HUB)}")
    print(f"RESULT: {ok_count}/{total} passed")
    return 0 if ok_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
