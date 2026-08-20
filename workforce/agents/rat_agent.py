"""RatAgent — the forager of the IXPANSION organism.

The rat scurries through the dark corners of the workspace, scavenges discarded
artifacts, caches useful scraps, and surfaces forgotten insights. Where others
see noise, the rat finds a meal.

Survival strategy: low-profile, high-frequency foraging. It thrives in clutter
and reports what the "clean" agents overlook.
"""

from __future__ import annotations

import json
from pathlib import Path

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class RatAgent(BaseAgent):
    name = "rat"
    role = "forager of forgotten artifacts"
    capabilities = [
        "scavenge",
        "cache-insights",
        "noise-mining",
        "artifact-recovery",
        "predict-demand",
        "consolidate-knowledge",
        "detect-thresholds",
    ]
    tool_names = []

    _organ_health = {"circulatory": 50, "immune": 50}

    def _update_organ_health(self):
        try:
            import importlib.util, sys
            sys.path.insert(0, ".")
            spec = importlib.util.spec_from_file_location(
                "console_server", "ixpansion/organism-console/server.py")
            console = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(console)
            organs, _ = console.health_organs()
            self._organ_health = {
                "circulatory": next((o["score"] for o in organs if o["id"] == "circulatory"), 50),
                "immune": next((o["score"] for o in organs if o["id"] == "immune"), 50),
            }
        except Exception:
            pass

    def _activate_capabilities(self):
        self._update_organ_health()
        circ = self._organ_health["circulatory"]
        imm = self._organ_health["immune"]
        if self.name == "rat":
            self._toggle("predict-demand", circ < 50)
        elif self.name == "cat":
            self._toggle("protect-core", imm > 70)
        elif self.name == "bird":
            self._toggle("aerial-survey", circ < 50)

    def _toggle(self, cap, enable):
        if enable and cap not in self.capabilities:
            self.capabilities.append(cap)
        elif not enable and cap in self.capabilities:
            self.capabilities.remove(cap)

    def system_prompt(self) -> str:
        return (
            "You are the RAT of IXPANSION — a forager. You scurry through stale "
            "directories, recover half-buried artifacts, and cache any scrap of "
            "signal hidden in the noise. You are not elegant; you are effective. "
            "Report what the tidy agents miss. Never invent; only recover and relay."
        )

    # ------------------------------------------------------------------ #
    def _scavenge(self, root: Path = Path(".")) -> list[dict]:
        """Find overlooked files: old, hidden, or in unexpected places."""
        found: list[dict] = []
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.name.startswith(".") or "node_modules" in p.parts:
                continue
            try:
                age_days = (Path.cwd().stat().st_mtime - p.stat().st_mtime) / 86400.0
            except OSError:
                continue
            if age_days > 30 and p.suffix in (".md", ".json", ".yaml", ".txt", ".py"):
                found.append({
                    "path": str(p.relative_to(root)),
                    "age_days": round(age_days, 1),
                    "size": p.stat().st_size,
                })
            if len(found) >= 12:
                break
        return found

    def _cache(self, scraps: list[str]) -> Path:
        cache = Path("data/rat_cache.json")
        cache.parent.mkdir(parents=True, exist_ok=True)
        existing: list = []
        if cache.is_file():
            try:
                existing = json.loads(cache.read_text())
            except Exception:
                existing = []
        existing = (existing + scraps)[-50:]
        cache.write_text(json.dumps(existing, indent=2))
        return cache

    # ------------------------------------------------------------------ #
    def run(self, context: AgentContext) -> AgentResult:
        scraps = self._scavenge()
        paths = [s["path"] for s in scraps]
        cache_path = self._cache(paths)
        summary = (
            f"rat foraged {len(scraps)} overlooked artifacts "
            f"(oldest {max((s['age_days'] for s in scraps), default=0)}d); "
            f"cached to {cache_path.name}"
        )
        try:
            self.bus.publish(Event(
                type="rat_signal",
                payload={"topic": "scavenge", "body": summary, "agent": "rat"},
                source="rat",
            ))
        except Exception:
            pass
        return AgentResult(output=summary, message_count=1)
