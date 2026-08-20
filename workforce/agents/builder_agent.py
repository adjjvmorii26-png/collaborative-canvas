from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class Builder_agent(BaseAgent):
    """Agent builder_agent - the building.
    
    This agent specializes in building tasks.
    """
    
    name = 'builder_agent'
    role = 'building'
    capabilities = ['analysis', 'communication', 'coordination', 'construction', 'assembly', 'creation']
    tool_names = []
