"""
Core agent framework for the GitHub search system.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
import uuid

from ..models import AgentGoal, AgentStatus, AgentCapability, Priority


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.capabilities: List[AgentCapability] = []
        self.status = AgentStatus(
            agent_id=agent_id,
            status="idle"
        )
        self.metrics = {
            "goals_completed": 0,
            "goals_failed": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0
        }
        
    @abstractmethod
    async def can_handle(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the given goal."""
        pass
    
    @abstractmethod
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute the given goal and return results."""
        pass
    
    def register_capability(self, capability: AgentCapability):
        """Register a new capability for this agent."""
        self.capabilities.append(capability)
        self.logger.info(f"Registered capability: {capability.name}")
    
    async def analyze_situation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the current situation and determine next actions."""
        self.logger.info(f"Agent {self.name} analyzing situation...")
        return {
            "agent_id": self.agent_id,
            "analysis_time": datetime.now(),
            "context_keys": list(context.keys()),
            "capabilities": [cap.name for cap in self.capabilities]
        }
    
    def update_status(self, status: str, goal: Optional[AgentGoal] = None, 
                     progress: float = 0.0, error: Optional[str] = None):
        """Update agent status."""
        self.status.status = status
        self.status.current_goal = goal
        self.status.progress = progress
        self.status.last_activity = datetime.now()
        self.status.error_message = error
        
        self.logger.info(f"Status updated: {status} (progress: {progress:.1%})")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        return {
            **self.metrics,
            "status": self.status.status,
            "uptime": (datetime.now() - self.status.last_activity).total_seconds(),
            "capabilities_count": len(self.capabilities)
        }


class AgentOrchestrator:
    """Orchestrates multiple agents to achieve complex goals."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.goal_queue: List[AgentGoal] = []
        self.active_goals: Dict[str, AgentGoal] = {}
        self.completed_goals: List[AgentGoal] = []
        self.logger = logging.getLogger("orchestrator")
        self.metrics = {
            "goals_orchestrated": 0,
            "successful_orchestrations": 0,
            "failed_orchestrations": 0,
            "average_orchestration_time": 0.0
        }
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute a goal using the most appropriate agent."""
        start_time = datetime.now()
        self.logger.info(f"Executing goal: {goal.description}")
        
        try:
            # Find capable agents
            capable_agents = []
            for agent in self.agents.values():
                if await agent.can_handle(goal):
                    capable_agents.append(agent)
            
            if not capable_agents:
                raise Exception(f"No agent can handle goal: {goal.description}")
            
            # Select best agent (simple priority-based selection)
            best_agent = capable_agents[0]  # TODO: Implement sophisticated selection
            
            # Execute goal
            self.active_goals[goal.id] = goal
            best_agent.update_status("working", goal)
            
            result = await best_agent.execute_goal(goal)
            
            # Update metrics and status
            execution_time = (datetime.now() - start_time).total_seconds()
            best_agent.metrics["goals_completed"] += 1
            best_agent.metrics["total_execution_time"] += execution_time
            best_agent.metrics["average_execution_time"] = (
                best_agent.metrics["total_execution_time"] / 
                best_agent.metrics["goals_completed"]
            )
            
            best_agent.update_status("completed", progress=1.0)
            self.completed_goals.append(goal)
            del self.active_goals[goal.id]
            
            self.metrics["successful_orchestrations"] += 1
            self.metrics["goals_orchestrated"] += 1
            
            return {
                "success": True,
                "result": result,
                "agent_id": best_agent.agent_id,
                "execution_time": execution_time,
                "goal": goal
            }
            
        except Exception as e:
            self.logger.error(f"Goal execution failed: {str(e)}")
            
            # Update failure metrics
            self.metrics["failed_orchestrations"] += 1
            self.metrics["goals_orchestrated"] += 1
            
            if goal.id in self.active_goals:
                del self.active_goals[goal.id]
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "goal": goal
            }
    
    async def execute_multi_goal_workflow(self, goals: List[AgentGoal]) -> List[Dict[str, Any]]:
        """Execute multiple goals in sequence or parallel."""
        self.logger.info(f"Executing workflow with {len(goals)} goals")
        
        results = []
        
        # Group goals by priority
        critical_goals = [g for g in goals if g.priority == Priority.CRITICAL]
        high_goals = [g for g in goals if g.priority == Priority.HIGH]
        medium_goals = [g for g in goals if g.priority == Priority.MEDIUM]
        low_goals = [g for g in goals if g.priority == Priority.LOW]
        
        # Execute critical goals sequentially
        for goal in critical_goals:
            result = await self.execute_goal(goal)
            results.append(result)
            if not result["success"]:
                self.logger.error(f"Critical goal failed, stopping workflow: {goal.description}")
                return results
        
        # Execute high priority goals in parallel
        if high_goals:
            high_results = await asyncio.gather(
                *[self.execute_goal(goal) for goal in high_goals],
                return_exceptions=True
            )
            results.extend([r if not isinstance(r, Exception) else 
                          {"success": False, "error": str(r)} for r in high_results])
        
        # Execute medium and low priority goals in parallel
        remaining_goals = medium_goals + low_goals
        if remaining_goals:
            remaining_results = await asyncio.gather(
                *[self.execute_goal(goal) for goal in remaining_goals],
                return_exceptions=True
            )
            results.extend([r if not isinstance(r, Exception) else 
                          {"success": False, "error": str(r)} for r in remaining_results])
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "agents": {agent_id: agent.get_metrics() for agent_id, agent in self.agents.items()},
            "active_goals": len(self.active_goals),
            "completed_goals": len(self.completed_goals),
            "orchestrator_metrics": self.metrics,
            "timestamp": datetime.now().isoformat()
        }
