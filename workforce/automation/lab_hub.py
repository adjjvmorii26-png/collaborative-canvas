"""Laboratory automation hub for IXPANSION.

This module keeps the workspace organized while running coordinated
health, finance, pulse, and synchronicity checks. It also writes
artifacts that can be used as income-planning material.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ixpansion.core.finance_agent import FinanceAgent
from ixpansion.core.health_monitor_agent import OrganHealthMonitor
from ixpansion.core.organism_pulse_coordinator import OrganismPulseCoordinator
from ixpansion.core.synchronicity_agent import SynchronicityAgent
from ixpansion.core.stress_test_agent import OrganismStressTest
from ixpansion.core.wordpress_agent import WordPressAgent


ROOT = Path("/root/Hub_spot")
RUNTIME_DIR = ROOT / "data" / "runs"
REPORT_DIR = ROOT / "ixpansion" / "content_output" / "reports"


@dataclass
class CleanupResult:
    pycache_dirs_removed: int
    temp_files_removed: int
    stale_logs_removed: int


class WorkspaceCleaner:
    def __init__(self, root: Path = ROOT) -> None:
        self.root = root

    def clean(self) -> CleanupResult:
        pycache_dirs_removed = 0
        temp_files_removed = 0
        stale_logs_removed = 0

        for path in self.root.rglob("__pycache__"):
            if ".git" in path.parts:
                continue
            shutil.rmtree(path, ignore_errors=True)
            pycache_dirs_removed += 1

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if ".git" in path.parts:
                continue
            name = path.name
            if name.endswith((".tmp", ".swp", "~", ".cache")):
                try:
                    path.unlink()
                    temp_files_removed += 1
                except OSError:
                    pass
            if name.endswith(".log") and path.stat().st_size < 1024 * 64:
                try:
                    path.unlink()
                    stale_logs_removed += 1
                except OSError:
                    pass

        return CleanupResult(
            pycache_dirs_removed=pycache_dirs_removed,
            temp_files_removed=temp_files_removed,
            stale_logs_removed=stale_logs_removed,
        )


class LabAutomationHub:
    """Coordinates all major IXPANSION automation tasks."""

    def __init__(self, console_url: str = "http://127.0.0.1:8890") -> None:
        self.console_url = console_url
        self.cleaner = WorkspaceCleaner()
        self.health = OrganHealthMonitor(console_url)
        self.finance = FinanceAgent(console_url)
        self.stress = OrganismStressTest(console_url)
        self.wordpress = WordPressAgent("alexalex.info", console_url)
        self.pulse = OrganismPulseCoordinator(console_url)
        self.synchronicity = SynchronicityAgent(console_url)

    def _ensure_dirs(self) -> None:
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    def _snapshot(self, pulse: Dict[str, Any] | None = None, include_domain: bool = False) -> Dict[str, Any]:
        pulse = pulse or self.pulse.current_pulse or {
            "id": "idle",
            "type": "idle",
            "intensity": 0.0,
            "timestamp": datetime.now().isoformat(),
            "status": "inactive",
        }
        return {
            "health": self.health.fetch_organ_scores(),
            "finance": self.finance._fetch_finance_health(),
            "stress": list(self.stress.stress_history),
            "pulse": pulse,
            "domain": (
                {
                    "health": self.wordpress.check_health(),
                    "freshness": self.wordpress.analyze_content_freshness(),
                }
                if include_domain
                else {
                    "domain": self.wordpress.base_url,
                    "status": "deferred",
                    "note": "Live domain inspection is optional to keep the automation cycle fast.",
                }
            ),
            "captured_at": datetime.now().isoformat(),
        }

    def run_cleanup(self) -> Dict[str, Any]:
        result = self.cleaner.clean()
        return {
            "pycache_dirs_removed": result.pycache_dirs_removed,
            "temp_files_removed": result.temp_files_removed,
            "stale_logs_removed": result.stale_logs_removed,
        }

    def build_income_plan(self, snapshot: Dict[str, Any], patterns: List[Any]) -> List[str]:
        opportunities = self.synchronicity.income_opportunities(patterns)
        health_avg = self._avg_numeric(snapshot.get("health", {}))
        finance_avg = self._avg_numeric(snapshot.get("finance", {}))
        opportunities.append(f"Package health/finance dashboard when combined score exceeds {round((health_avg + finance_avg) / 2, 1)}")
        opportunities.append("Create a recurring 'organism report' content product for subscribers")
        opportunities.append("Offer resilience and continuity assessments for founders")
        opportunities.append("Bundle alexalex.info content around system growth and automation")
        return list(dict.fromkeys(opportunities))

    def _avg_numeric(self, payload: Dict[str, Any]) -> float:
        values: List[float] = []
        for value in payload.values():
            if isinstance(value, (int, float)):
                values.append(float(value))
            elif isinstance(value, dict) and isinstance(value.get("score"), (int, float)):
                values.append(float(value["score"]))
        return sum(values) / len(values) if values else 0.0

    def run_cycle(self) -> Dict[str, Any]:
        self._ensure_dirs()

        cleanup = self.run_cleanup()

        # Use pulse as a coordination layer for the lab run.
        pulse = self.pulse.generate_unified_pulse(pulse_type="sync", intensity=0.6)
        snapshot = self._snapshot(pulse=pulse, include_domain=False)
        patterns = self.synchronicity.detect_synchronicity(snapshot)
        report = self.synchronicity.generate_report(snapshot)
        income_plan = self.build_income_plan(snapshot, patterns)

        wellness = self.pulse.organism_wellness_score()

        artifact = {
            "timestamp": datetime.now().isoformat(),
            "cleanup": cleanup,
            "synchronicity_patterns": [pattern.__dict__ for pattern in patterns],
            "synchronicity_report": report,
            "income_plan": income_plan,
            "wellness_score": wellness,
            "pulse": pulse,
            "snapshot": snapshot,
        }

        run_id = datetime.now().strftime("%Y%m%d%H%M%S")
        runtime_file = RUNTIME_DIR / f"lab_automation_{run_id}.json"
        report_file = REPORT_DIR / f"lab_automation_{run_id}.md"

        runtime_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        report_file.write_text(self.render_markdown(artifact, report), encoding="utf-8")

        return {
            "run_id": run_id,
            "runtime_file": str(runtime_file),
            "report_file": str(report_file),
            "cleanup": cleanup,
            "wellness_score": wellness,
            "patterns_found": len(patterns),
            "income_plan": income_plan,
        }

    def render_markdown(self, artifact: Dict[str, Any], synchronicity_report: str) -> str:
        lines = [
            "# IXPANSION Lab Automation Report",
            "",
            f"- Generated: {artifact['timestamp']}",
            f"- Wellness score: {artifact['wellness_score']}",
            f"- Patterns found: {len(artifact['synchronicity_patterns'])}",
            "",
            "## Cleanup",
            f"- __pycache__ removed: {artifact['cleanup']['pycache_dirs_removed']}",
            f"- Temp files removed: {artifact['cleanup']['temp_files_removed']}",
            f"- Small logs removed: {artifact['cleanup']['stale_logs_removed']}",
            "",
            "## Income Plan",
        ]
        for item in artifact["income_plan"]:
            lines.append(f"- {item}")
        lines += [
            "",
            "## Synchronicity Report",
            "",
            synchronicity_report,
        ]
        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="IXPANSION lab automation hub")
    parser.add_argument("action", choices=["run", "cleanup", "report", "income"])
    args = parser.parse_args()

    hub = LabAutomationHub()

    if args.action == "cleanup":
        result = hub.run_cleanup()
        print(json.dumps(result, indent=2))
        return

    if args.action == "run":
        result = hub.run_cycle()
        print(json.dumps(result, indent=2))
        return

    snapshot = hub._snapshot(include_domain=False)
    patterns = hub.synchronicity.detect_synchronicity(snapshot)

    if args.action == "report":
        print(hub.synchronicity.generate_report(snapshot))
        return

    if args.action == "income":
        print(json.dumps(hub.build_income_plan(snapshot, patterns), indent=2))
        return


if __name__ == "__main__":
    main()
