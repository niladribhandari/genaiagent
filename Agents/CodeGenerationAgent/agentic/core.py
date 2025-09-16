"""Core agentic framework components."""

import asyncio
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import uuid


class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentGoal:
    """Represents a goal that an agent should accomplish."""
    id: str
    description: str
    priority: Priority
    success_criteria: Dict[str, Any]
    context: Dict[str, Any]
    deadline: Optional[datetime] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class AgentResult:
    """Result of agent execution."""
    agent_id: str
    goal_id: str
    success: bool
    result: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAgent:
    """Base class for all agents in the agentic system."""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"Agent.{name}")
        self.execution_history: List[AgentResult] = []
    
    async def execute(self, goal: AgentGoal) -> AgentResult:
        """Execute a goal and return the result."""
        self.status = AgentStatus.WORKING
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.info(f"Executing goal: {goal.description}")
            result_data = await self._execute_goal(goal)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            result = AgentResult(
                agent_id=self.agent_id,
                goal_id=goal.id,
                success=True,
                result=result_data,
                execution_time=execution_time
            )
            
            self.status = AgentStatus.COMPLETED
            self.execution_history.append(result)
            self.logger.info(f"Goal completed successfully in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            result = AgentResult(
                agent_id=self.agent_id,
                goal_id=goal.id,
                success=False,
                result={},
                error_message=str(e),
                execution_time=execution_time
            )
            
            self.status = AgentStatus.FAILED
            self.execution_history.append(result)
            self.logger.error(f"Goal failed after {execution_time:.2f}s: {e}")
            
            return result
    
    async def _execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Override this method in subclasses to implement specific logic."""
        raise NotImplementedError("Subclasses must implement _execute_goal method")
    
    def can_handle_goal(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the given goal."""
        # Override in subclasses for more specific logic
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "executions_count": len(self.execution_history),
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate based on execution history."""
        if not self.execution_history:
            return 0.0
        
        successful = sum(1 for result in self.execution_history if result.success)
        return successful / len(self.execution_history)


class AgentOrchestrator:
    """Orchestrates multiple agents to accomplish complex goals."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self.goal_queue: List[AgentGoal] = []
        self.completed_goals: List[AgentResult] = []
        self.logger = logging.getLogger("AgentOrchestrator")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the orchestrator."""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            self.logger.info(f"Unregistered agent: {agent.name}")
    
    async def execute_goal(self, goal: AgentGoal) -> AgentResult:
        """Execute a single goal using the best available agent."""
        self.logger.info(f"Executing goal: {goal.description}")
        
        # Find the best agent for this goal
        agent = self._select_agent_for_goal(goal)
        if not agent:
            return AgentResult(
                agent_id="orchestrator",
                goal_id=goal.id,
                success=False,
                result={},
                error_message="No suitable agent found for goal"
            )
        
        # Execute the goal
        result = await agent.execute(goal)
        self.completed_goals.append(result)
        
        return result
    
    async def execute_goals(self, goals: List[AgentGoal]) -> List[AgentResult]:
        """Execute multiple goals, handling dependencies."""
        self.goal_queue.extend(goals)
        results = []
        
        # Sort goals by priority and dependencies
        sorted_goals = self._sort_goals_by_priority_and_dependencies(goals)
        
        for goal in sorted_goals:
            result = await self.execute_goal(goal)
            results.append(result)
            
            # If a high-priority goal fails, consider stopping
            if not result.success and goal.priority in [Priority.HIGH, Priority.CRITICAL]:
                self.logger.warning(f"High-priority goal failed: {goal.description}")
        
        return results
    
    def _select_agent_for_goal(self, goal: AgentGoal) -> Optional[BaseAgent]:
        """Select the best agent for executing a goal."""
        suitable_agents = [
            agent for agent in self.agents.values() 
            if agent.can_handle_goal(goal) and agent.status == AgentStatus.IDLE
        ]
        
        if not suitable_agents:
            # If no idle agents, try to find any suitable agent
            suitable_agents = [
                agent for agent in self.agents.values() 
                if agent.can_handle_goal(goal)
            ]
        
        if not suitable_agents:
            return None
        
        # Select agent with highest success rate
        return max(suitable_agents, key=lambda a: a._calculate_success_rate())
    
    def _sort_goals_by_priority_and_dependencies(self, goals: List[AgentGoal]) -> List[AgentGoal]:
        """Sort goals by priority and dependency order."""
        # Simple implementation: sort by priority first, then by dependencies
        return sorted(goals, key=lambda g: (-g.priority.value, len(g.dependencies)))
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get status of the orchestrator and all agents."""
        return {
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()},
            "goals_in_queue": len(self.goal_queue),
            "completed_goals": len(self.completed_goals),
            "success_rate": self._calculate_overall_success_rate()
        }
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all completed goals."""
        if not self.completed_goals:
            return 0.0
        
        successful = sum(1 for result in self.completed_goals if result.success)
        return successful / len(self.completed_goals)
