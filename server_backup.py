#!/usr/bin/env python3
"""Organism Console — a self-contained IXPANSION body map.

Maps the hub to a living organism:
  nervous   = agent workforce (the cells)
  skeletal  = config / repo integrity
  respiratory = LLM providers + API keys (the breath)
  circulatory = cash flow (the blood)
  digestive = recipes (behaviors)
  immune    = red-team / safety scans
  memory    = generated reports
  reproductive = experiment backlog
  broadcast = YouTube channels + ad campaigns

Run:  python3 ixpansion/organism-console/server.py [--port 8890]
No third-party dependencies; only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HUB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HUB))
CONSOLE = Path(__file__).resolve().parent
CONTENT = HUB / "ixpansion" / "content_output"
RECIPES = CONTENT / "recipes"
REPORTS = CONTENT / "reports"
CASHFLOW = CONTENT / "cashflow"
YOUTUBE = CONTENT / "youtube"
CONSOLE_DATA = CONTENT / "console"
RUNS = HUB / "data" / "runs"
WORKFORCE_YAML = HUB / "workforce.yaml"
ENV_FILE = HUB / ".env"
EXPERIMENTS = HUB / "ixpansion" / "docs" / "experiments.md"

PROVIDER_PATTERNS = {
    "openai": {
        "model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
    },
    "xai": {
        "model": "grok-3-mini",
        "base_url": "https://api.x.ai/v1",
        "env_key": "XAI_API_KEY",
    },
}

ORGAN_META = [
    {"id": "nervous", "label": "Nervous System", "accent": "#6d83ff", "icon": "neuron", "blurb": "Agents think, plan, and coordinate as cells."},
    {"id": "skeletal", "label": "Skeleton", "accent": "#8aa0c6", "icon": "frame", "blurb": "Config and repo integrity hold the body upright."},
    {"id": "respiratory", "label": "Respiratory System", "accent": "#39e6c3", "icon": "breath", "blurb": "LLM providers and API keys are the breath."},
    {"id": "circulatory", "label": "Circulatory System", "accent": "#ff5ca8", "icon": "blood", "blurb": "Cash flow moves energy through the organism."},
    {"id": "digestive", "label": "Digestive System", "accent": "#ffce6a", "icon": "enzyme", "blurb": "Recipes transform raw inputs into reports."},
    {"id": "immune", "label": "Immune System", "accent": "#ff7a7a", "icon": "shield", "blurb": "Red-team and safety scans reject toxins."},
    {"id": "memory", "label": "Memory", "accent": "#9cb4ff", "icon": "synapse", "blurb": "Generated reports become long-term memory."},
    {"id": "reproductive", "label": "Reproductive System", "accent": "#b08bff", "icon": "seed", "blurb": "The experiment backlog births new organisms."},
    {"id": "broadcast", "label": "Broadcast System", "accent": "#ff8f5c", "icon": "signal", "blurb": "YouTube channels and ad campaigns reach the world."},
]

AGENT_CAPABILITIES = [
    "planning", "research", "code", "review", "summarize", "design",
    "test", "docs", "redteam", "devops", "recruit", "architecture",
    "analytics", "curate",
]


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


def count_files(directory: Path, suffix: str = "*") -> int:
    if not directory.is_dir():
        return 0
    return len(list(directory.glob(suffix)))


def last_modified(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        return None


def parse_provider() -> dict:
    text = read_text(WORKFORCE_YAML)
    provider = re.search(r"^provider:\s*(\S+)", text, re.M)
    model = re.search(r"^llm:\s*\n\s+model:\s*(\S+)", text, re.M)
    base_url = re.search(r"^llm:\s*\n\s+base_url:\s*(\S+)", text, re.M)
    return {
        "provider": provider.group(1) if provider else "unknown",
        "model": model.group(1) if model else "unknown",
        "base_url": base_url.group(1) if base_url else "",
    }


def set_provider(provider: str) -> dict:
    if provider not in PROVIDER_PATTERNS:
        raise ValueError(f"unknown provider {provider}")
    text = read_text(WORKFORCE_YAML)
    pat = PROVIDER_PATTERNS[provider]
    text = re.sub(r"^provider:\s*\S+", f"provider: {provider}", text, flags=re.M)
    text = re.sub(r"^(\s+model:\s*)\S+", rf"\g<1>{pat['model']}", text, flags=re.M)
    text = re.sub(r"^(\s+base_url:\s*)\S+", rf"\g<1>{pat['base_url']}", text, flags=re.M)
    WORKFORCE_YAML.write_text(text, encoding="utf-8")
    return parse_provider()


def env_has_key(key: str) -> bool:
    env_value = read_text(ENV_FILE)
    return bool(re.search(rf"^{key}=(.+)$", env_value, re.M))


def api_keys_summary() -> dict:
    data = read_json(CONTENT / "api_keys.json", {})
    if not isinstance(data, dict):
        data = {}
    by_type: dict[str, int] = {}
    for entry in data.values():
        t = entry.get("key_type", "custom")
        by_type[t] = by_type.get(t, 0) + 1
    keys = []
    for entry in data.values():
        keys.append({
            "id": entry.get("id"),
            "key_type": entry.get("key_type", "custom"),
            "name": entry.get("name", entry.get("id", "")),
            "description": entry.get("description", ""),
            "created_at": entry.get("created_at"),
            "last_used": entry.get("last_used"),
            "usage_count": entry.get("usage_count", 0),
        })
    return {"count": len(keys), "by_type": by_type, "keys": keys}


def cashflow_summary() -> dict:
    txs = read_json(CASHFLOW / "transactions.json", [])
    if not isinstance(txs, list):
        txs = []
    revenue = 0.0
    expenditure = 0.0
    by_asset: dict[str, float] = {}
    for tx in txs:
        try:
            amount = float(tx.get("amount", 0))
        except (TypeError, ValueError):
            amount = 0.0
        asset = tx.get("asset", "fiat")
        by_asset[asset] = by_asset.get(asset, 0.0) + amount
        if tx.get("type") == "revenue":
            revenue += amount
        elif tx.get("type") == "expenditure":
            expenditure += amount
    portfolio = read_json(CASHFLOW / "portfolio.json", {})
    return {
        "revenue": round(revenue, 2),
        "expenditure": round(expenditure, 2),
        "net": round(revenue - expenditure, 2),
        "transaction_count": len(txs),
        "by_asset": {k: round(v, 2) for k, v in by_asset.items()},
        "portfolio_assets": list((portfolio.get("assets") or {}).keys()),
        "portfolio_nfts": len((portfolio.get("nfts") or {})),
        "detail": f"net \${revenue - expenditure:.2f} across {len(txs)} txs, assets: {', '.join((portfolio.get('assets') or {}).keys()) or 'fiat'}",
    }


def youtube_summary() -> dict:
    channels = read_json(YOUTUBE / "channels.json", [])
    campaigns = read_json(YOUTUBE / "campaigns.json", [])
    if not isinstance(campaigns, list):
        campaigns = []
    spend = 0.0
    impressions = 0
    clicks = 0
    for camp in campaigns:
        try:
            spend += float(camp.get("spend", 0))
        except (TypeError, ValueError):
            pass
        impressions += int(camp.get("impressions", 0) or 0)
        clicks += int(camp.get("clicks", 0) or 0)
    ctr = round(clicks / impressions, 4) if impressions else 0.0
    return {
        "channels": len(channels) if isinstance(channels, list) else 0,
        "campaigns": len(campaigns),
        "spend": round(spend, 2),
        "impressions": impressions,
        "clicks": clicks,
        "ctr": ctr,
    }


def recipes_atoms() -> list[dict]:
    atoms = []
    for path in sorted(RECIPES.glob("*.yaml")):
        text = read_text(path)
        name = path.stem
        steps = re.findall(r"^\s*-\s+name:\s*(\S+)", text, re.M) or []
        description = ""
        m = re.search(r"^description:\s*(.+)$", text, re.M)
        if m:
            description = m.group(1).strip()
        atoms.append({
            "id": f"{name}-{len(atoms)}",
            "recipe": name,
            "description": description,
            "steps": steps,
            "file": str(path.relative_to(HUB)),
            "modified": last_modified(path),
        })
    return atoms


def pulse_ledger(limit: int = 10) -> list[dict]:
    pulses = []
    if RUNS.is_dir():
        for run_dir in sorted(RUNS.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            report = run_dir / "report.md"
            if report.is_file():
                pulses.append({
                    "id": run_dir.name,
                    "report": str(report.relative_to(HUB)),
                    "modified": last_modified(report),
                })
            if len(pulses) >= limit:
                break
    reports = sorted(REPORTS.glob("**/*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in reports[:limit]:
        pulses.append({
            "id": f"report-{len(pulses)}",
            "report": str(path.relative_to(HUB)),
            "modified": last_modified(path),
        })
    return pulses


def health_organs() -> list[dict]:
    provider = parse_provider()
    keys = api_keys_summary()
    cash = cashflow_summary()
    yt = youtube_summary()
    atoms = recipes_atoms()
    agents = count_files(HUB / "workforce" / "agents", "*.py")
    experiments_text = read_text(EXPERIMENTS)
    backlog = experiments_text.count("### X-")
    reports_count = count_files(REPORTS, "*.md")
    immune_reports = list(REPORTS.glob("**/redteam*")) + list(REPORTS.glob("**/*redteam*"))

    def clamp(v: float) -> float:
        return max(0.0, min(100.0, round(v, 1)))

    organ_data = {
        "nervous": {"score": clamp(agents * 6), "detail": f"{agents} agent cells", "value": agents},
        "skeletal": {"score": 100.0 if WORKFORCE_YAML.is_file() else 40.0, "detail": "config online" if WORKFORCE_YAML.is_file() else "config missing", "value": 1},
        "respiratory": {
            # LLM breath + keys (existing)
            "base_score": clamp(60 + keys["by_type"].get("xai", 0) * 15 + keys["by_type"].get("openai", 0) * 10),
            "base_detail": f"{provider['provider']} / {provider['model']} + {keys['count']} keys",
            "base_value": keys["count"],
            # Crypto keyword awareness in keys
            # Crypto keyword awareness in keys
            "crypto_keywords": ["btc", "eth", "sol", "usdt", "nft"],
            # Crypto-aware if crypto terms appear in key types
            "crypto_aware": any(
                kw in (keys.get("by_type", "0") or "0") or
                (keys.get("count", 0) > 0 and any((kw in str(keys.get("count", 0)).lower() for kw in ["btc", "eth", "sol", "usdt", "nft"]))
                for kw in ["btc", "eth", "sol", "usdt", "nft"]),

        },
        "circulatory": {
            # Cash flow core
            "base_score": clamp(100 if cash["transaction_count"] else 45),
            "base_detail": f"net ${cash['net']} across {cash['transaction_count']} txs",
            "base_value": cash["transaction_count"],
            # Crypto/NFT enrichment from portfolio
            "crypto_assets_count": len(cash.get("portfolio_assets", [])),
            "crypto_nft_count": cash["portfolio_nfts"],
            "crypto_total_value": (
                str(Decimal(cash.get("portfolio_value", "0"))) 
                if cash.get("portfolio_value") 
                else "0"
            ),
            # Enhance detail/score with crypto presence
            "detail": "net \${:.2f} across {} txs".format(cash["net"], cash["transaction_count"]) + (" · crypto active" if cash.get("portfolio_assets") else ""),
            "value": cash["transaction_count"],
            "score": clamp(100 if cash["transaction_count"] else 45),
        },
        "digestive": {
            "score": clamp(len(atoms) * 16),
            "detail": f"{len(atoms)} recipes / {sum(len(a['steps']) for a in atoms)} atoms",
            "value": len(atoms),
        },
        "immune": {
            "score": 80.0 if immune_reports else 55.0,
            "detail": f"{len(immune_reports)} red-team reports",
            "value": len(immune_reports),
        },
        "memory": {
            "score": clamp(reports_count * 8),
            "detail": f"{reports_count} reports in memory",
            "value": reports_count,
        },
        "reproductive": {
            "score": clamp(backlog * 8),
            "detail": f"{backlog} experiments in backlog",
            "value": backlog,
        },
        "broadcast": {
            "score": clamp(yt["channels"] * 30 + yt["campaigns"] * 8),
            "detail": f"{yt['channels']} channels / {yt['campaigns']} campaigns",
            "value": yt["campaigns"],
        },
    }

    organs = []
    for meta in ORGAN_META:
        data = organ_data[meta["id"]]
        organs.append({**meta, **data})
    for custom in custom_organs():
        source_path = Path(custom["source"])
        if not source_path.is_absolute():
            source_path = HUB / source_path
        try:
            hits = len(list(source_path.rglob("*"))) if source_path.is_dir() else (1 if source_path.exists() else 0)
        except OSError:
            hits = 0
        organs.append({
            "id": custom.get("id"),
            "label": custom.get("label"),
            "accent": custom.get("accent", "#8be9fd"),
            "icon": custom.get("icon", "cell"),
            "blurb": custom.get("blurb", ""),
            "score": clamp(hits * 8),
            "detail": f"{hits} source hits",
            "value": hits,
            "custom": True,
        })
    overall = sum(o["score"] for o in organs) / len(organs) if organs else 0.0
    return organs, round(overall, 1)


def run_pulse(input_text: str, recipe: str = "summary", mock: bool = True) -> dict:
    cmd = [sys.executable, "-m", "ixpansion", "run", input_text, "--recipe", recipe]
    if mock:
        cmd.append("--mock")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(HUB),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": "pulse timed out after 120s"}


def body_snapshot() -> dict:
    organs, score = health_organs()
    return {
        "ts": utcnow(),
        "symbiote_score": score,
        "metabolism": metabolism(),
    "creatures": creatures(),
        "organs": organs,
        "provider": parse_provider(),
        "keys": api_keys_summary(),
        "cashflow": cashflow_summary(),
        "youtube": youtube_summary(),
        "recipes": recipes_atoms(),
        "pulses": pulse_ledger(),
        "agents": {
            "capabilities": AGENT_CAPABILITIES,
            "count": count_files(HUB / "workforce" / "agents", "*.py"),
        },
    }


def clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, round(float(v), 1)))


def _age_days(ts: str) -> float:
    """Approximate age of an ISO timestamp in days (UTC)."""
    if not ts:
        return 999.0
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
    except Exception:
        return 999.0


def _status(score: float) -> str:
    return "healthy" if score >= 75 else ("warning" if score >= 40 else "critical")


# ------------------------------------------------------------------ #
# Metabolism — the organism's vital signs
# ------------------------------------------------------------------ #

def _pulse_frequency() -> float:
    """Heart rate: pulses per day averaged over the last 7 days."""
    events = []
    if RUNS.is_dir():
        events += [p.stat().st_mtime for p in RUNS.glob("*/report.md")]
    events += [p.stat().st_mtime for p in REPORTS.glob("**/*.md")]
    week_ago = time.time() - 7 * 86400.0
    recent = [m for m in events if m >= week_ago]
    return round(len(recent) / 7.0, 2)


def metabolism() -> dict:
    provider = parse_provider()
    keys = api_keys_summary()
    cash = cashflow_summary()
    organs, score = health_organs()

    heart_rate = _pulse_frequency()

    hot_files = 0
    for base in (HUB / "workforce", CONTENT, HUB / "data"):
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file():
                    try:
                        if time.time() - p.stat().st_mtime < 86400.0:
                            hot_files += 1
                    except OSError:
                        pass
    temperature = clamp(hot_files / 40.0 * 100.0)

    active = provider["provider"]
    pat = PROVIDER_PATTERNS.get(active)
    if pat and env_has_key(pat["env_key"]):
        oxygen = 70 + (30 if keys["count"] else 0)
    elif keys["count"]:
        oxygen = 40
    else:
        oxygen = 20
    oxygen = clamp(oxygen)

    net = cash["net"]
    if net >= 0:
        blood = 100.0
    else:
        blood = clamp(100.0 - abs(net) * 0.1)
    blood = max(blood, 5.0)

    immunity = 80.0 if len([p for p in REPORTS.glob("**/*redteam*")]) else 55.0

    stress = 0.0
    if cash["expenditure"] > 0 and net < 0:
        stress += 40
    if oxygen < 70:
        stress += 20
    if temperature > 80:
        stress += 15
    if score < 60:
        stress += 25
    stress = clamp(stress)

    hr_status = "healthy" if heart_rate >= 0.5 else ("warning" if heart_rate >= 0.12 else "critical")
    vitals = [
        {"key": "heart_rate", "label": "Heart rate", "value": f"{heart_rate}/day",
         "score": clamp(heart_rate * 50), "status": hr_status},
        {"key": "temperature", "label": "Temperature", "value": f"{temperature:.0f}% busy",
         "score": temperature, "status": _status(temperature)},
        {"key": "oxygen", "label": "Oxygen", "value": f"{oxygen:.0f}% (LLM breath)",
         "score": oxygen, "status": _status(oxygen)},
        {"key": "blood", "label": "Blood pressure", "value": f"{blood:.0f}% (net ${fmt_net(net)})",
         "score": blood, "status": _status(blood)},
        {"key": "immunity", "label": "Immunity", "value": f"{immunity:.0f}% defense",
         "score": immunity, "status": _status(immunity)},
        {"key": "stress", "label": "Stress index", "value": f"{stress:.0f}/100",
         "score": stress, "status": _status(100 - stress)},
    ]
    return {
        "ts": utcnow(),
        "heart_rate": heart_rate,
        "temperature": temperature,
        "oxygen": oxygen,
        "blood": blood,
        "stress": stress,
        "burn_rate": round(cash["expenditure"] / 30.0, 2) if cash["expenditure"] else 0.0,
        "vitals": vitals,
    }


def fmt_net(net: float) -> str:
    sign = "-" if net < 0 else ""
    return f"{sign}${abs(net):,.2f}"


# ------------------------------------------------------------------ #
# Heatmap — per-organ activity over the last 7 days
# ------------------------------------------------------------------ #

ORGAN_SOURCES = {
    "nervous": [HUB / "workforce" / "agents"],
    "skeletal": [WORKFORCE_YAML, HUB / ".git" / "HEAD"],
    "respiratory": [ENV_FILE, CONTENT / "api_keys.json"],
    "circulatory": [CASHFLOW],
    "digestive": [RECIPES],
    "immune": [REPORTS],
    "memory": [REPORTS],
    "reproductive": [EXPERIMENTS],
    "broadcast": [YOUTUBE],
}


def _file_activity(dirs: list[Path], days: int = 7) -> list[int]:
    buckets = [0] * days
    for entry in dirs:
        if not entry.exists():
            continue
        if entry.is_dir():
            for p in entry.rglob("*"):
                if p.is_file():
                    try:
                        age = (time.time() - p.stat().st_mtime) / 86400.0
                    except OSError:
                        continue
                    if 0 <= age < days:
                        buckets[int(age)] += 1
        else:
            try:
                age = (time.time() - entry.stat().st_mtime) / 86400.0
            except OSError:
                continue
            if 0 <= age < days:
                buckets[int(age)] += 1
    return buckets


def heatmap() -> dict:
    days = 7
    rows = []
    max_hits = 1
    for meta in ORGAN_META:
        buckets = _file_activity(ORGAN_SOURCES.get(meta["id"], []), days)
        total = sum(buckets)
        max_hits = max(max_hits, total or 1)
        rows.append({
            "id": meta["id"],
            "label": meta["label"],
            "accent": meta["accent"],
            "buckets": buckets,
            "total": total,
        })
    for msg in bus_list(200):
        row = next((r for r in rows if r["id"] == msg.get("organ")), None)
        if row is None:
            continue
        age = _age_days(msg.get("ts", ""))
        if 0 <= age < days:
            row["buckets"][int(age)] += 1
            row["total"] += 1
            max_hits = max(max_hits, row["total"])
    for row in rows:
        row["buckets"] = [clamp((b / max_hits) * 100.0) for b in row["buckets"]]
    return {"days": days, "max_hits": max_hits, "rows": rows, "generated": utcnow()}


# ------------------------------------------------------------------ #
# Agent message bus — organs whisper to each other
# ------------------------------------------------------------------ #

BUS_MAX = 200


def _bus_path() -> Path:
    return CONSOLE_DATA / "bus.json"


def bus_list(limit: int = 50) -> list[dict]:
    data = read_json(_bus_path(), [])
    if not isinstance(data, list):
        data = []
    data.sort(key=lambda m: m.get("ts", ""), reverse=True)
    return data[:limit]


def bus_post(payload: dict) -> dict:
    from ixpansion.services.bodylink import post_signal

    return post_signal(
        organ=payload.get("organ", "nervous"),
        topic=payload.get("topic", "signal"),
        severity=payload.get("severity", "info"),
        body=payload.get("body", ""),
        sender=payload.get("sender", "console"),
        data_dir=CONSOLE_DATA,
    )


# ------------------------------------------------------------------ #
# Cross-agent consensus — the nervous system votes
# ------------------------------------------------------------------ #

CONSENSUS_AGENTS = [
    {"id": "token-analyst", "approve": ["cost", "budget", "efficient", "cheap", "tokens"],
     "reject": ["unlimited", "no budget", "burn"], "signal": "cost posture"},
    {"id": "memory-curator", "approve": ["report", "memory", "reuse", "archive", "recipe"],
     "reject": [], "signal": "memory reuse"},
    {"id": "reputation-tracker", "approve": ["campaign", "channel", "youtube", "ad", "ctr"],
     "reject": [], "signal": "broadcast reach"},
    {"id": "task-router", "approve": ["recipe", "route", "pipeline", "run", "task"],
     "reject": [], "signal": "route availability"},
    {"id": "pulse-scheduler", "approve": ["schedule", "frequency", "daily", "cron", "pulse"],
     "reject": [], "signal": "schedulability"},
    {"id": "console-agent", "approve": ["console", "organism", "body", "organ", "monitor"],
     "reject": [], "signal": "body alignment"},
    {"id": "fallback-engine", "approve": ["fallback", "rollback", "resilience", "backup", "recovery"],
     "reject": [], "signal": "resilience"},
]


def consensus(proposal: str) -> dict:
    text = (proposal or "").lower()
    votes = []
    for agent in CONSENSUS_AGENTS:
        approve_hits = sum(1 for kw in agent["approve"] if kw in text)
        reject_hits = sum(1 for kw in agent["reject"] if kw in text)
        if approve_hits > reject_hits:
            stance = "approve"
            confidence = 0.5 + min(approve_hits, 2) * 0.2
        elif reject_hits > approve_hits:
            stance = "reject"
            confidence = 0.5 + min(reject_hits, 2) * 0.2
        else:
            stance = "abstain"
            confidence = 0.3
        votes.append({
            "agent": agent["id"],
            "stance": stance,
            "confidence": clamp(confidence, 0.1, 0.95),
            "signal": agent["signal"],
        })
    approves = sum(1 for v in votes if v["stance"] == "approve")
    rejects = sum(1 for v in votes if v["stance"] == "reject")
    abstains = len(votes) - approves - rejects
    if rejects and approves == 0:
        verdict = "consensus blocked"
    elif approves > rejects and approves >= 3:
        verdict = "consensus reached"
    elif rejects >= 2 and rejects >= approves:
        verdict = "consensus blocked"
    else:
        verdict = "needs review"
    avg_conf = round(sum(v["confidence"] for v in votes) / len(votes), 2)
    return {
        "verdict": verdict,
        "approve": approves,
        "reject": rejects,
        "abstain": abstains,
        "confidence": avg_conf,
        "proposal": (proposal or "")[:300],
        "votes": votes,
        "ts": utcnow(),
    }


# ------------------------------------------------------------------ #
# Custom organ registry — let the body grow new organs
# ------------------------------------------------------------------ #

def _organs_path() -> Path:
    return CONSOLE_DATA / "organs.json"


def custom_organs() -> list[dict]:
    data = read_json(_organs_path(), [])
    return data if isinstance(data, list) else []


def register_organ(payload: dict) -> dict:
    organ_id = re.sub(r"[^a-z0-9_-]", "", (payload.get("id") or "").lower())
    label = (payload.get("label") or organ_id).strip()
    source = (payload.get("source") or "").strip()
    if not organ_id or not label or not source:
        raise ValueError("id, label, and source are required")
    accent = payload.get("accent") or "#8be9fd"
    if not re.match(r"^#[0-9a-fA-F]{6}$", accent):
        accent = "#8be9fd"
    entry = {
        "id": organ_id,
        "label": label[:40],
        "accent": accent,
        "icon": (payload.get("icon") or "cell")[:12],
        "blurb": (payload.get("blurb") or "Custom organ monitored by the console.")[:120],
        "source": source[:200],
        "custom": True,
    }
    CONSOLE_DATA.mkdir(parents=True, exist_ok=True)
    data = [o for o in custom_organs() if o["id"] != organ_id]
    data.append(entry)
    _organs_path().write_text(json.dumps(data, indent=2), encoding="utf-8")
    return entry


def record_score() -> dict:
    """Snapshot the current symbiote score into the trend history (best-effort)."""
    try:
        from ixpansion.services.bodylink import record_score as _record

        organs, score = health_organs()
        provider = parse_provider()
        return _record(
            score,
            {"organs": len(organs), "provider": provider["provider"], "model": provider["model"]},
            data_dir=CONSOLE_DATA,
        )
    except Exception:
        return {"ok": False}


def score_history(limit: int = 60) -> list[dict]:
    from ixpansion.services.bodylink import score_history as _history

    return _history(limit=limit, data_dir=CONSOLE_DATA)


def creatures() -> dict:
    """The three experimental creature-agents (rat, cat, bird) and their live mood."""
    organs, score = health_organs()
    bus_msgs = bus_list(limit=200)
    history = score_history(limit=14)

    # Rat: thrives on clutter / low-score organs (forages the weak)
    rat_target = min(organs, key=lambda o: o.get("score", 100)) if organs else None
    rat_mood = "foraging" if score < 80 else "resting"
    rat_note = f"scavenging {rat_target['id']} (score {rat_target['score']:.0f})" if rat_target else "no organ to forage"

    # Cat: watches for anomalies in recent score history
    scores = [float(h.get("score", 0)) for h in history if isinstance(h, dict)]
    cat_stance = "patrol"
    cat_note = "silence above the body"
    if len(scores) >= 3:
        import statistics as _st
        mean = _st.mean(scores)
        stdev = _st.pstdev(scores) or 1e-9
        last_z = (scores[-1] - mean) / stdev
        if abs(last_z) >= 2.0:
            cat_stance = "pounce"
            cat_note = f"anomaly! score {scores[-1]:.0f} z={last_z:+.1f}"
        elif abs(last_z) >= 1.0:
            cat_stance = "tense"
            cat_note = f"twitching z={last_z:+.1f}"

    # Bird: broadcasts from the healthiest organ, flies above all
    bird_top = max(organs, key=lambda o: o.get("score", 0)) if organs else None
    bird_mood = "singing" if score >= 60 else "silent"
    bird_note = f"surveying {len(organs)} organs, strongest wing on {bird_top['id']}" if bird_top else "no organs in view"

    signals = [m for m in bus_msgs if m.get("sender") == "workforce"]
    return {
        "ts": utcnow(),
        "rat": {"mood": rat_mood, "note": rat_note, "target": rat_target["id"] if rat_target else None},
        "cat": {"stance": cat_stance, "note": cat_note},
        "bird": {"mood": bird_mood, "note": bird_note, "top": bird_top["id"] if bird_top else None},
        "recent_workforce_signals": len(signals),
        "creatures_active": 3,
    }


def write_key(payload: dict) -> dict:
    from ixpansion.services.integration import APIKeyManager

    manager = APIKeyManager(str(CONTENT))
    entry = manager.add_key(
        name=payload.get("name", "API Key"),
        key_type=payload.get("key_type", "custom"),
        key_value=payload.get("key_value", ""),
        description=payload.get("description", ""),
        expires_at=payload.get("expires_at"),
    )
    return {"ok": True, "id": entry["id"], "key_type": entry["key_type"]}


class Handler(BaseHTTPRequestHandler):
    server_version = "OrganismConsole/0.1"

    def _send(self, code: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, data) -> None:
        self._send(code, json.dumps(data, indent=2).encode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = (CONSOLE / "index.html").read_bytes()
            self._send(200, body, "text/html; charset=utf-8")
            return
        if parsed.path == "/api/body":
            self._json(200, body_snapshot())
            return
        if parsed.path == "/api/pulses":
            self._json(200, {"pulses": pulse_ledger()})
            return
        if parsed.path == "/api/metabolism":
            self._json(200, metabolism())
            return
        if parsed.path == "/api/heatmap":
            self._json(200, heatmap())
            return
        if parsed.path == "/api/bus":
            self._json(200, {"messages": bus_list()})
            return
        if parsed.path == "/api/organs":
            self._json(200, {"custom": custom_organs()})
            return
        if parsed.path == "/api/history":
            self._json(200, {"history": score_history()})
            return
        if parsed.path == "/api/creatures":
            self._json(200, creatures())
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid JSON"})
            return

        if parsed.path == "/api/provider":
            try:
                self._json(200, {"ok": True, "provider": set_provider(payload.get("provider", ""))})
                record_score()
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
            return

        if parsed.path == "/api/keys":
            try:
                self._json(201, write_key(payload))
                record_score()
            except Exception as exc:
                self._json(400, {"error": str(exc)})
            return

        if parsed.path == "/api/pulse":
            result = run_pulse(
                payload.get("input", "Organism pulse"),
                payload.get("recipe", "summary"),
                payload.get("mock", True),
            )
            try:
                record_score()
            except Exception:
                pass
            self._json(200, result)
            return

        if parsed.path == "/api/bus":
            try:
                self._json(201, bus_post(payload))
                record_score()
            except Exception as exc:
                self._json(400, {"error": str(exc)})
            return

        if parsed.path == "/api/consensus":
            self._json(200, consensus(payload.get("proposal", "")))
            return

        if parsed.path == "/api/organs":
            try:
                self._json(201, register_organ(payload))
                record_score()
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
            return

        self._json(404, {"error": "not found"})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[organism] %s\n" % (fmt % args))


def main() -> int:
    parser = argparse.ArgumentParser(description="IXPANSION Organism Console")
    parser.add_argument("--port", type=int, default=8890)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        record_score()
    except Exception:
        pass
    print(f"Organism Console running at http://{args.host}:{args.port}")
    print(f"Symbiote API: http://{args.host}:{args.port}/api/body")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nconsole stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
