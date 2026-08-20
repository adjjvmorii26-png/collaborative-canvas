from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class Explorer_agent(BaseAgent):
    """Agent explorer_agent - the exploration.
    
    This agent specializes in exploration tasks.
    """
    
    name = 'explorer_agent'
    role = 'exploration'
    capabilities = ['analysis', 'communication', 'coordination', 'exploration', 'discovery', 'mapping']
    tool_names = []
