#!/usr/bin/env python3
"""Memory consolidation script for IXPANSION organism.

This script extracts key insights from pulse results and stores them
as persistent memory nodes that survive across runs.

Usage:
    python3 scripts/consolidate_memory.py <pulse_report_path>
    
Example:
    python3 scripts/consolidate_memory.py data/runs/abc1234/report.md
"""

import json
import os
import sys
from datetime import datetime


MEMORY_DIR = "data/memory"


def extract_insights(pulse_data: dict) -> list:
    """Extract key insights from pulse data."""
    insights = []
    
    # Check pulse success
    if pulse_data.get("ok"):
        insights.append("pulse-success")
    
    # Check for errors
    if pulse_data.get("stderr"):
        insights.append("errors-detected")
    
    # Check metabolism/vitals
    metabolism = pulse_data.get("metabolism", {})
    if metabolism:
        vitals = metabolism.get("vitals", [])
        if vitals:
            insights.append("vitals-monitored")
    
    # Check creatures/agents
    creatures = pulse_data.get("creatures", {})
    if creatures:
        insights.append("agents-active")
    
    # Check organs
    organs = pulse_data.get("organs", [])
    if organs:
        insights.append("organs-monitored")
    
    return insights


def calculate_strength(pulse_data: dict) -> float:
    """Calculate memory strength based on pulse success and data richness."""
    strength = 0.5  # base
    
    if pulse_data.get("ok"):
        strength += 0.3
    
    # Richer data = higher strength
    if pulse_data.get("metabolism"):
        strength += 0.1
    
    if pulse_data.get("creatures"):
        strength += 0.1
    
    if pulse_data.get("organs"):
        strength += 0.1
    
    # Cap at 1.0
    return min(1.0, strength)


def store_pulse_memory(pulse_id: str, pulse_data: dict) -> dict:
    """Store pulse results as persistent memory node."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    insights = extract_insights(pulse_data)
    strength = calculate_strength(pulse_data)
    
    memory_node = {
        "id": f"pulse-{pulse_id}",
        "type": "pulse-report",
        "key_insights": insights,
        "strength": strength,
        "created": datetime.now().isoformat(),
        "resolved": False,
        "pulse_data_summary": {
            "ok": pulse_data.get("ok"),
            "symbiote_score": pulse_data.get("symbiote_score", 0),
            "organ_count": len(pulse_data.get("organs", [])),
        }
    }
    
    memory_path = os.path.join(MEMORY_DIR, f"{memory_node['id']}.json")
    with open(memory_path, 'w') as f:
        json.dump(memory_node, f, indent=2)
    
    return memory_node


def recall_memory(memory_id: str = None) -> list:
    """Retrieve memory nodes from storage."""
    memories = []
    
    if not os.path.exists(MEMORY_DIR):
        return memories
    
    for filename in sorted(os.listdir(MEMORY_DIR)):
        if filename.endswith('.json'):
            memory_path = os.path.join(MEMORY_DIR, filename)
            try:
                with open(memory_path, 'r') as f:
                    memory = json.load(f)
                    if memory_id is None or memory.get("id") == memory_id:
                        memories.append(memory)
            except (json.JSONDecodeError, IOError):
                continue
    
    # Sort by strength (highest first), then by creation date
    memories.sort(key=lambda m: (m.get("strength", 0), m.get("created", "")), reverse=True)
    return memories


def list_memories() -> list:
    """List all memory nodes."""
    memories = []
    if os.path.exists(MEMORY_DIR):
        for filename in sorted(os.listdir(MEMORY_DIR)):
            if filename.endswith('.json'):
                memory_path = os.path.join(MEMORY_DIR, filename)
                try:
                    with open(memory_path, 'r') as f:
                        memory = json.load(f)
                        memories.append(memory)
                except (json.JSONDecodeError, IOError):
                    continue
    return memories


def get_memory_stats() -> dict:
    """Get statistics about the memory store."""
    memories = list_memories()
    
    if not memories:
        return {
            "total_memories": 0,
            "average_strength": 0,
            "resolved": 0,
            "unresolved": 0,
        }
    
    total = len(memories)
    avg_strength = sum(m.get("strength", 0) for m in memories) / total
    resolved = sum(1 for m in memories if m.get("resolved"))
    unresolved = total - resolved
    
    return {
        "total_memories": total,
        "average_strength": round(avg_strength, 2),
        "resolved": resolved,
        "unresolved": unresolved,
    }


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/consolidate_memory.py <pulse_report_path>")
        print("Or: python3 scripts/consolidate_memory.py --list  # list all memories")
        print("Or: python3 scripts/consolidate_memory.py --stats  # get memory stats")
        return
    
    arg = sys.argv[1]
    
    if arg == "--list":
        memories = list_memories()
        print(f"Total memories: {len(memories)}")
        for m in memories:
            print(f"  {m['id']}: strength={m.get('strength', 0):.1f}, insights={m.get('key_insights', [])}")
    
    elif arg == "--stats":
        stats = get_memory_stats()
        print(f"Memory Stats: {json.dumps(stats, indent=2)}")
    
    else:
        # Store a new memory
        pulse_id = arg
        # Try to find and read the pulse report
        pulse_report_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        pulse_data = {}
        if pulse_report_path and os.path.exists(pulse_report_path):
            try:
                with open(pulse_report_path, 'r') as f:
                    # Try to parse as JSON or treat as text
                    content = f.read()
                    try:
                        pulse_data = json.loads(content)
                    except json.JSONDecodeError:
                        # Treat as text report - extract basic info
                        pulse_data = {"ok": "report" in content.lower(), "stderr": ""}
            except IOError:
                pulse_data = {"ok": False, "stderr": "could not read report"}
        elif pulse_id:
            # Assume pulse_id is already the data or we'll use minimal data
            pulse_data = {"ok": True, "stderr": ""}
        
        memory_node = store_pulse_memory(pulse_id, pulse_data)
        print(f"Memory stored: {memory_node['id']}")
        print(f"  Strength: {memory_node['strength']:.1f}")
        print(f"  Insights: {', '.join(memory_node['key_insights'])}")


if __name__ == "__main__":
    main()
