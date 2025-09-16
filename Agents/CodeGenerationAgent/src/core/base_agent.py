"""Base agent class with common functionality."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

from .interfaces import GenerationContext


@dataclass
class AgentGoal:
    """Represents a goal for an agent to achieve."""
    description: str
    priority: int
    context: Dict[str, Any]
    

@dataclass
class AgentTask:
    """Represents a task for an agent to execute."""
    name: str
    action: str
    parameters: Dict[str, Any]


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, agent_name: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def analyze_situation(self, context: Dict[str, Any]) -> List[AgentGoal]:
        """Analyze the current situation and determine goals."""
        pass
    
    @abstractmethod
    async def plan_actions(self, goals: List[AgentGoal]) -> List[AgentTask]:
        """Plan actions to achieve the given goals."""
        pass
    
    @abstractmethod
    async def process_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Process a specific goal and return results."""
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            'id': self.agent_id,
            'name': self.agent_name,
            'config': self.config
        }
