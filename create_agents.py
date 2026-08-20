#!/usr/bin/env python3
"""Create 15 specialized agents for IXPANSION."""

import os

# First, read the current __init__.py
with open('workforce/agents/__init__.py', 'r') as f:
    init_content = f.read()

# Base capabilities that all agents get
base_caps = ["analysis", "communication", "coordination"]

# Define 15 agents with unique roles and capabilities
agents_to_create = [
    ("wisdom_agent", "wisdom", ["wisdom", "counsel", "guidance", "mentorship"]),
    ("explorer_agent", "exploration", ["exploration", "discovery", "mapping", "navigation"]),
    ("builder_agent", "building", ["construction", "assembly", "creation", "crafting"]),
    ("healer_agent", "healing", ["healing", "recovery", "restoration", "rejuvenation"]),
    ("weaver_agent", "weaving", ["weaving", "connection", "integration", "pattern"]),
    ("forager_agent", "foraging", ["foraging", "gathering", "collection", "resource"]),
    ("keeper_agent", "keeping", ["guarding", "protecting", "preserving", "maintaining"]),
    ("seer_agent", "seership", ["seership", "vision", "insight", "prophecy"]),
    ("sage_agent", "sagehood", ["sagehood", "wisdom", "knowledge", "teaching"]),
    ("reaper_agent", "reaping", ["reaping", "harvesting", "ending", "closure"]),
    ("anvil_agent", "anvil", ["forging", "hammering", "shaping", "molding"]),
    ("loom_agent", "loom", ["weaving", "thread", "pattern", "fabric"]),
    ("mirror_agent", "mirror", ["reflection", "mirroring", "image", "perspective"]),
    ("prism_agent", "prism", ["refraction", "spectrum", "color", "wavelength"]),
]

created = []
for agent_name, role, specific_caps in agents_to_create:
    # Create agent file
    agent_content = f'''from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class {agent_name.capitalize()}(BaseAgent):
    """Agent {agent_name} - the {role}.
    
    This agent specializes in {role} tasks and supports the IXPANSION organism.
    """
    
    name = {repr(agent_name)}
    role = {repr(role)}
    capabilities = {repr(base_caps + specific_caps)}
    tool_names = []
'''
    
    filepath = f'workforce/agents/{agent_name}.py'
    with open(filepath, 'w') as f:
        f.write(agent_content)
    
    # Register in __init__.py - add import
    import_line = f'from .{agent_name} import {agent_name.capitalize()}\\n'
    if import_line not in init_content:
        # Insert after finance_agent import
        if 'from .finance_agent import FinanceAgent' in init_content:
            init_content = init_content.replace(
                'from .finance_agent import FinanceAgent',
                import_line + 'from .finance_agent import FinanceAgent'
            )
    
    created.append(agent_name)
    
print(f"Created {len(created)} agent files: {created[:5]}...{created[-3:]}")
PYEOF
python3 create_agents.py
