"""Audit: export an execution trace as markdown."""

from __future__ import annotations

from pathlib import Path

from .memory import Memory


def export_audit(memory: Memory, run_id: str, out_dir: str = "data/audit") -> str:
    msgs = memory.get_messages(run_id)
    path = Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    f = path / f"{run_id}.md"
    f.write_text(
        "\n\n".join(f"**{m['agent']}/{m['role']}**: {m['content'][:500]}" for m in msgs),
        encoding="utf-8",
    )
    return str(f)
