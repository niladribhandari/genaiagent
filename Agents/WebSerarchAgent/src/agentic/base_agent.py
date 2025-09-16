"""
Base Agent framework for Agentic AI Web Search system.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AgentCapability:
    """Defines a specific capability of an agent."""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class AgentGoal:
    """Represents a goal for an agent to achieve."""
    id: str
    description: str
    target_outcome: str
    priority: int = 5  # 1-10, 10 being highest
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Web Search system.
    Implements core agentic AI principles: autonomy, goal-oriented behavior, and collaboration.
    """
    
    def __init__(self, name: str, capabilities: List[AgentCapability]):
        """
        Initialize the base agent.
        
        Args:
            name: Unique name for the agent
            capabilities: List of capabilities this agent possesses
        """
        self.name = name
        self.capabilities = {cap.name: cap for cap in capabilities}
        self.status = "idle"  # idle, working, error, completed
        self.current_goal: Optional[AgentGoal] = None
        self.execution_history: List[Dict[str, Any]] = []
        self.collaboration_network: Dict[str, 'BaseAgent'] = {}
        
        logger.info(f"Initialized agent: {self.name} with capabilities: {list(self.capabilities.keys())}")
    
    def add_capability(self, capability: AgentCapability):
        """Add a new capability to the agent."""
        self.capabilities[capability.name] = capability
        logger.info(f"Added capability '{capability.name}' to agent {self.name}")
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability."""
        return capability_name in self.capabilities
    
    def connect_agent(self, agent: 'BaseAgent'):
        """Connect to another agent for collaboration."""
        self.collaboration_network[agent.name] = agent
        agent.collaboration_network[self.name] = self
        logger.info(f"Connected agents: {self.name} <-> {agent.name}")
    
    async def set_goal(self, goal: AgentGoal):
        """Set a goal for the agent to achieve."""
        self.current_goal = goal
        self.status = "working"
        
        logger.info(f"Agent {self.name} received goal: {goal.description}")
        
        try:
            result = await self.execute_goal(goal)
            self.status = "completed"
            
            # Record execution history
            self.execution_history.append({
                "goal_id": goal.id,
                "goal_description": goal.description,
                "result": result,
                "timestamp": datetime.now(),
                "status": "completed"
            })
            
            return result
            
        except Exception as e:
            self.status = "error"
            logger.error(f"Agent {self.name} failed to achieve goal: {str(e)}")
            
            self.execution_history.append({
                "goal_id": goal.id,
                "goal_description": goal.description,
                "error": str(e),
                "timestamp": datetime.now(),
                "status": "error"
            })
            
            raise
    
    @abstractmethod
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """
        Execute a specific goal. Must be implemented by subclasses.
        
        Args:
            goal: The goal to achieve
            
        Returns:
            Dictionary containing the results of goal execution
        """
        pass
    
    async def collaborate(self, agent_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request collaboration from another agent.
        
        Args:
            agent_name: Name of the agent to collaborate with
            request: Details of what is being requested
            
        Returns:
            Response from the collaborating agent
        """
        if agent_name not in self.collaboration_network:
            raise ValueError(f"No connection to agent: {agent_name}")
        
        collaborating_agent = self.collaboration_network[agent_name]
        
        logger.info(f"Agent {self.name} requesting collaboration from {agent_name}")
        
        # Create a collaboration goal
        collab_goal = AgentGoal(
            id=f"collab_{self.name}_{agent_name}_{datetime.now().timestamp()}",
            description=f"Collaboration request from {self.name}",
            target_outcome=request.get("target_outcome", ""),
            context=request
        )
        
        return await collaborating_agent.set_goal(collab_goal)
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get detailed status report of the agent."""
        return {
            "name": self.name,
            "status": self.status,
            "capabilities": list(self.capabilities.keys()),
            "current_goal": self.current_goal.description if self.current_goal else None,
            "connected_agents": list(self.collaboration_network.keys()),
            "execution_history_count": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }
    
    async def adapt_strategy(self, feedback: Dict[str, Any]):
        """
        Adapt agent strategy based on feedback.
        This enables learning and improvement over time.
        """
        logger.info(f"Agent {self.name} adapting strategy based on feedback")
        
        # Base implementation - can be overridden by subclasses
        if feedback.get("success_rate", 1.0) < 0.7:
            logger.warning(f"Agent {self.name} has low success rate, considering strategy adaptation")
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', status='{self.status}')>"
