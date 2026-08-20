"""Export IXPANSION catalog + sample reports as JSON fixtures for the Control Room UI.

Run from the repo root:  python3 ixpansion/control-room/scripts/export_fixtures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from ixpansion.core.engine import Engine  # noqa: E402
from ixpansion.core.recipe import Recipe  # noqa: E402
from ixpansion.core.router import route, load_catalog  # noqa: E402
from ixpansion.services.llm import make_provider  # noqa: E402

RECIPES_DIR = ROOT / "ixpansion" / "content_output" / "recipes"
OUT_DIR = ROOT / "ixpansion" / "content_output" / "reports" / "control-room-demo"
DATA_DIR = ROOT / "ixpansion" / "control-room" / "src" / "data"

SAMPLES = {
    "summary": "Q3 revenue up 12% driven by enterprise renewals; churn down 3 points; hiring freeze lifted in Q4.",
    "research-brief": "Market research: AI coding assistants in enterprise dev teams, 2026.",
    "release-note": "Version 2.4 ships: new router API, faster cold start, bug fixes for queue backpressure.",
    "redteam-scan": "Scan the checkout flow for prompt-injection, SSRF, and mass-assignment risks.",
    "reuse-scan": "Audit the repo for duplicated logic across services/ and utils/.",
    "organism-sync": "Sync the workforce plan from docs/experiments.md into the org registry.",
}


def main() -> int:
    catalog = []
    for path in sorted(RECIPES_DIR.glob("*.yaml")):
        r = Recipe.load(path)
        catalog.append(
            {
                "name": r.name,
                "description": r.description or "",
                "tags": list(r.tags),
                "steps": [{"name": s.name, "prompt": s.prompt, "max_tokens": s.max_tokens} for s in r.steps],
                "step_count": len(r.steps),
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = Engine(make_provider(mock=True), output_dir=str(OUT_DIR))
    reports = []
    for recipe_name, sample in SAMPLES.items():
        result = engine.run(Recipe.load(RECIPES_DIR / f"{recipe_name}.yaml"), sample, out_name=recipe_name)
        text = Path(result.report_path).read_text(encoding="utf-8")
        reports.append(
            {
                "recipe": recipe_name,
                "input": sample,
                "steps": result.steps,
                "provider": result.provider,
                "path": str(result.report_path).replace(str(ROOT) + "/", ""),
                "text": text,
            }
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    (DATA_DIR / "reports.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(f"exported {len(catalog)} recipes and {len(reports)} reports -> {DATA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
