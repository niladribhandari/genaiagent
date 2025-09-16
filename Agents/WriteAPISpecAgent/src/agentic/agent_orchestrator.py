"""
Agent Orchestrator for API Specification Writing System
Manages coordination and collaboration between multiple agents
"""

import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from .base_agent import BaseAgent, Goal, AgentResult, GoalStatus, AgentCapability


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowStep:
    """Represents a step in an agent workflow."""
    step_id: str
    agent_name: str
    goal: Goal
    dependencies: List[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[AgentResult] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class AgentWorkflow:
    """Represents a complete workflow with multiple steps."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Orchestrates collaboration between multiple agents to achieve complex goals.
    
    The orchestrator manages agent registration, workflow coordination,
    goal delegation, and result aggregation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent orchestrator."""
        self.config = config or {}
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, AgentWorkflow] = {}
        self.completed_workflows: List[AgentWorkflow] = []
        self.failed_workflows: List[AgentWorkflow] = []
        
        # Orchestrator state
        self.is_running = True
        self.max_concurrent_workflows = self.config.get("max_concurrent_workflows", 10)
        self.max_concurrent_goals_per_agent = self.config.get("max_concurrent_goals_per_agent", 3)
        
        # Performance tracking
        self.total_workflows = 0
        self.successful_workflows = 0
        self.total_goals_executed = 0
        self.successful_goals = 0
        
        # Setup logging
        self.logger = logging.getLogger("orchestrator")
        self.logger.setLevel(logging.INFO)
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        if agent.name in self.registered_agents:
            self.logger.warning(f"Agent {agent.name} is already registered. Updating registration.")
        
        self.registered_agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name} with capabilities: {[cap.value for cap in agent.capabilities]}")
    
    def unregister_agent(self, agent_name: str):
        """Unregister an agent from the orchestrator."""
        if agent_name in self.registered_agents:
            del self.registered_agents[agent_name]
            self.logger.info(f"Unregistered agent: {agent_name}")
        else:
            self.logger.warning(f"Attempted to unregister non-existent agent: {agent_name}")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a registered agent by name."""
        return self.registered_agents.get(agent_name)
    
    def find_capable_agents(self, goal: Goal) -> List[BaseAgent]:
        """Find all agents capable of handling a specific goal."""
        capable_agents = []
        
        for agent in self.registered_agents.values():
            if agent.is_active and agent.can_handle_goal(goal):
                capable_agents.append(agent)
        
        return capable_agents
    
    def select_best_agent(self, goal: Goal) -> Optional[BaseAgent]:
        """Select the best agent for a specific goal based on performance and availability."""
        capable_agents = self.find_capable_agents(goal)
        
        if not capable_agents:
            return None
        
        # Score agents based on performance and availability
        scored_agents = []
        
        for agent in capable_agents:
            metrics = agent.get_performance_metrics()
            
            # Calculate score based on success rate, speed, and current load
            success_rate = metrics.get("success_rate", 0.0)
            avg_time = metrics.get("average_execution_time", float('inf'))
            current_load = len(agent.current_goals)
            
            # Higher score is better
            score = (
                success_rate * 0.5 +  # Success rate weight
                (1.0 / (avg_time + 1)) * 0.3 +  # Speed weight (inverse of time)
                (1.0 / (current_load + 1)) * 0.2  # Availability weight
            )
            
            scored_agents.append((agent, score))
        
        # Sort by score (highest first) and return best agent
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents[0][0]
    
    async def execute_goal(self, goal: Goal, preferred_agent: Optional[str] = None) -> AgentResult:
        """Execute a single goal using the most appropriate agent."""
        if preferred_agent and preferred_agent in self.registered_agents:
            agent = self.registered_agents[preferred_agent]
            if agent.can_handle_goal(goal):
                selected_agent = agent
            else:
                self.logger.warning(
                    f"Preferred agent {preferred_agent} cannot handle goal {goal.objective}. "
                    "Selecting alternative agent."
                )
                selected_agent = self.select_best_agent(goal)
        else:
            selected_agent = self.select_best_agent(goal)
        
        if not selected_agent:
            return AgentResult(
                success=False,
                error=f"No capable agent found for goal: {goal.objective}",
                metadata={"goal_id": goal.goal_id}
            )
        
        # Check agent availability
        if len(selected_agent.current_goals) >= self.max_concurrent_goals_per_agent:
            return AgentResult(
                success=False,
                error=f"Agent {selected_agent.name} is at maximum capacity",
                metadata={"goal_id": goal.goal_id, "agent_name": selected_agent.name}
            )
        
        self.logger.info(f"Executing goal '{goal.objective}' with agent '{selected_agent.name}'")
        
        try:
            result = await selected_agent._execute_with_tracking(goal)
            
            # Update orchestrator statistics
            self.total_goals_executed += 1
            if result.success:
                self.successful_goals += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing goal '{goal.objective}': {str(e)}")
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"goal_id": goal.goal_id, "agent_name": selected_agent.name}
            )
    
    async def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new workflow with multiple coordinated steps.
        
        Args:
            name: Workflow name
            description: Workflow description
            steps: List of step definitions
            metadata: Additional workflow metadata
            
        Returns:
            Workflow ID
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        workflow_steps = []
        step_id_mapping = {}  # Map for flexible dependency resolution
        
        for i, step_def in enumerate(steps):
            step_id = f"{workflow_id}_step_{i+1}"
            step_id_mapping[i] = step_id  # Map index to actual ID
            
            goal = Goal(
                objective=step_def["objective"],
                parameters=step_def.get("parameters", {}),
                priority=step_def.get("priority", "medium"),
                context=step_def.get("context", {})
            )
            
            # Resolve dependencies flexibly
            resolved_dependencies = self._resolve_dependencies(
                step_def.get("dependencies", []), 
                step_id_mapping, 
                workflow_id, 
                i
            )
            
            workflow_step = WorkflowStep(
                step_id=step_id,
                agent_name=step_def.get("preferred_agent", ""),
                goal=goal,
                dependencies=resolved_dependencies,
                max_retries=step_def.get("max_retries", 3)
            )
            
            workflow_steps.append(workflow_step)
        
        workflow = AgentWorkflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps,
            metadata=metadata or {}
        )
        
        self.active_workflows[workflow_id] = workflow
        self.logger.info(f"Created workflow: {name} ({workflow_id}) with {len(steps)} steps")
        
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str) -> AgentResult:
        """Execute a complete workflow with dependency management."""
        if workflow_id not in self.active_workflows:
            return AgentResult(
                success=False,
                error=f"Workflow not found: {workflow_id}"
            )
        
        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        self.logger.info(f"Starting workflow execution: {workflow.name} ({workflow_id})")
        
        try:
            # Execute steps with dependency resolution
            executed_steps = set()
            step_results = {}
            
            while len(executed_steps) < len(workflow.steps):
                # Find steps ready for execution
                ready_steps = []
                
                for step in workflow.steps:
                    if (step.step_id not in executed_steps and 
                        step.status == WorkflowStatus.PENDING and
                        all(dep in executed_steps for dep in step.dependencies)):
                        ready_steps.append(step)
                
                if not ready_steps:
                    # Check if we're stuck due to failed dependencies
                    remaining_steps = [s for s in workflow.steps if s.step_id not in executed_steps]
                    if remaining_steps:
                        workflow.status = WorkflowStatus.FAILED
                        return AgentResult(
                            success=False,
                            error="Workflow deadlock: no steps can be executed due to failed dependencies",
                            metadata={"workflow_id": workflow_id}
                        )
                    break
                
                # Execute ready steps concurrently
                step_tasks = []
                for step in ready_steps:
                    step.status = WorkflowStatus.RUNNING
                    
                    # Add results from previous steps to goal context
                    step.goal.context.update(step_results)
                    
                    # Execute step
                    task = self._execute_workflow_step(step)
                    step_tasks.append((step, task))
                
                # Wait for all ready steps to complete
                for step, task in step_tasks:
                    result = await task
                    step.result = result
                    
                    if result.success:
                        step.status = WorkflowStatus.COMPLETED
                        step_results[step.step_id] = result.data
                        executed_steps.add(step.step_id)
                        
                        self.logger.info(f"Completed workflow step: {step.step_id}")
                    else:
                        step.status = WorkflowStatus.FAILED
                        
                        # Retry logic
                        if step.retry_count < step.max_retries:
                            step.retry_count += 1
                            step.status = WorkflowStatus.PENDING
                            self.logger.warning(
                                f"Retrying workflow step: {step.step_id} "
                                f"(attempt {step.retry_count}/{step.max_retries})"
                            )
                        else:
                            # Step failed permanently
                            self.logger.error(f"Workflow step failed permanently: {step.step_id}")
                            workflow.status = WorkflowStatus.FAILED
                            
                            return AgentResult(
                                success=False,
                                error=f"Workflow step failed: {step.step_id} - {result.error}",
                                metadata={
                                    "workflow_id": workflow_id,
                                    "failed_step": step.step_id,
                                    "step_results": step_results
                                }
                            )
            
            # Workflow completed successfully
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            # Move to completed workflows
            self.completed_workflows.append(workflow)
            del self.active_workflows[workflow_id]
            
            # Update statistics
            self.total_workflows += 1
            self.successful_workflows += 1
            
            self.logger.info(f"Workflow completed successfully: {workflow.name} ({workflow_id})")
            
            return AgentResult(
                success=True,
                data=step_results,
                metadata={
                    "workflow_id": workflow_id,
                    "workflow_name": workflow.name,
                    "total_steps": len(workflow.steps),
                    "execution_time": (workflow.completed_at - workflow.started_at).total_seconds()
                }
            )
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            
            self.failed_workflows.append(workflow)
            del self.active_workflows[workflow_id]
            
            self.total_workflows += 1
            
            self.logger.error(f"Workflow execution failed: {workflow.name} ({workflow_id}) - {str(e)}")
            
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"workflow_id": workflow_id}
            )
    
    async def _execute_workflow_step(self, step: WorkflowStep) -> AgentResult:
        """Execute a single workflow step."""
        preferred_agent = step.agent_name if step.agent_name else None
        return await self.execute_goal(step.goal, preferred_agent)
    
    async def coordinate_agents(
        self,
        primary_agent: str,
        supporting_agents: List[str],
        goal: Goal
    ) -> AgentResult:
        """Coordinate multiple agents to work on a complex goal."""
        # Create a workflow for agent coordination
        workflow_steps = []
        
        # Primary agent step
        workflow_steps.append({
            "objective": goal.objective,
            "parameters": goal.parameters,
            "context": goal.context,
            "preferred_agent": primary_agent,
            "priority": "high"
        })
        
        # Supporting agent steps
        for i, agent_name in enumerate(supporting_agents):
            workflow_steps.append({
                "objective": f"support_{goal.objective}",
                "parameters": goal.parameters,
                "context": goal.context,
                "preferred_agent": agent_name,
                "dependencies": [f"coordination_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_step_1"],
                "priority": "medium"
            })
        
        # Create and execute coordination workflow
        workflow_id = await self.create_workflow(
            name=f"Agent Coordination: {goal.objective}",
            description=f"Coordinated execution between {primary_agent} and supporting agents",
            steps=workflow_steps,
            metadata={
                "coordination_type": "multi_agent",
                "primary_agent": primary_agent,
                "supporting_agents": supporting_agents
            }
        )
        
        return await self.execute_workflow(workflow_id)
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current status of the orchestrator."""
        return {
            "is_running": self.is_running,
            "registered_agents": len(self.registered_agents),
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.completed_workflows),
            "failed_workflows": len(self.failed_workflows),
            "total_workflows": self.total_workflows,
            "successful_workflows": self.successful_workflows,
            "workflow_success_rate": (
                self.successful_workflows / self.total_workflows
                if self.total_workflows > 0 else 0.0
            ),
            "total_goals_executed": self.total_goals_executed,
            "successful_goals": self.successful_goals,
            "goal_success_rate": (
                self.successful_goals / self.total_goals_executed
                if self.total_goals_executed > 0 else 0.0
            )
        }
    
    def get_agent_status_summary(self) -> Dict[str, Any]:
        """Get status summary of all registered agents."""
        agent_summaries = {}
        
        for agent_name, agent in self.registered_agents.items():
            agent_summaries[agent_name] = agent.get_capability_summary()
        
        return {
            "total_agents": len(self.registered_agents),
            "active_agents": len([a for a in self.registered_agents.values() if a.is_active]),
            "agents": agent_summaries
        }
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause an active workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.PAUSED
            self.logger.info(f"Paused workflow: {workflow.name} ({workflow_id})")
            return True
        return False
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            if workflow.status == WorkflowStatus.PAUSED:
                workflow.status = WorkflowStatus.RUNNING
                self.logger.info(f"Resumed workflow: {workflow.name} ({workflow_id})")
                return True
        return False
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            
            self.failed_workflows.append(workflow)
            del self.active_workflows[workflow_id]
            
            self.logger.info(f"Cancelled workflow: {workflow.name} ({workflow_id})")
            return True
        return False
    
    async def shutdown(self):
        """Shutdown the orchestrator and cleanup resources."""
        self.is_running = False
        
        # Cancel all active workflows
        active_workflow_ids = list(self.active_workflows.keys())
        for workflow_id in active_workflow_ids:
            await self.cancel_workflow(workflow_id)
        
        # Deactivate all agents
        for agent in self.registered_agents.values():
            agent.deactivate()
        
        self.logger.info("Orchestrator shutdown completed")

    def _resolve_dependencies(self, dependencies: List, step_id_mapping: Dict[int, str], 
                            workflow_id: str, current_step_index: int) -> List[str]:
        """
        Flexibly resolve dependencies using multiple patterns:
        1. Numeric indices (0, 1, 2) -> actual step IDs
        2. Relative references (prev, previous) -> previous step
        3. Named references (step_1, step_2) -> actual step IDs
        4. Sequential pattern -> auto-dependency on previous step
        """
        resolved = []
        
        for dep in dependencies:
            if isinstance(dep, int):
                # Numeric index dependency
                if dep in step_id_mapping:
                    resolved.append(step_id_mapping[dep])
                elif dep < current_step_index:
                    # Reference to earlier step by index
                    resolved.append(f"{workflow_id}_step_{dep + 1}")
                    
            elif isinstance(dep, str):
                if dep.isdigit():
                    # String numeric dependency
                    idx = int(dep)
                    if idx < current_step_index:
                        resolved.append(f"{workflow_id}_step_{idx + 1}")
                        
                elif dep in ["prev", "previous"]:
                    # Previous step dependency
                    if current_step_index > 0:
                        resolved.append(f"{workflow_id}_step_{current_step_index}")
                        
                elif dep.startswith("step_"):
                    # Named step dependency
                    try:
                        step_num = int(dep.split("_")[1])
                        if step_num <= current_step_index:
                            resolved.append(f"{workflow_id}_step_{step_num}")
                    except (IndexError, ValueError):
                        # Invalid format, skip
                        pass
                        
                elif dep.startswith(workflow_id):
                    # Already resolved dependency
                    resolved.append(dep)
                    
                else:
                    # Legacy hardcoded dependency - try to map it
                    if "step_1" in dep and current_step_index > 0:
                        resolved.append(f"{workflow_id}_step_1")
                    elif "step_2" in dep and current_step_index > 1:
                        resolved.append(f"{workflow_id}_step_2")
                    elif "step_3" in dep and current_step_index > 2:
                        resolved.append(f"{workflow_id}_step_3")
                    elif "step_4" in dep and current_step_index > 3:
                        resolved.append(f"{workflow_id}_step_4")
        
        return resolved


# Utility functions for workflow creation

def create_simple_workflow(
    name: str,
    goals: List[Goal],
    agent_assignments: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """Create a simple workflow from a list of goals."""
    workflow_steps = []
    
    for i, goal in enumerate(goals):
        step = {
            "objective": goal.objective,
            "parameters": goal.parameters,
            "context": goal.context,
            "priority": goal.priority
        }
        
        if agent_assignments and str(i) in agent_assignments:
            step["preferred_agent"] = agent_assignments[str(i)]
        
        workflow_steps.append(step)
    
    return workflow_steps


def create_sequential_workflow(
    name: str,
    goals: List[Goal],
    agent_assignments: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """Create a sequential workflow where each step depends on the previous."""
    workflow_steps = []
    
    for i, goal in enumerate(goals):
        step = {
            "objective": goal.objective,
            "parameters": goal.parameters,
            "context": goal.context,
            "priority": goal.priority
        }
        
        if agent_assignments and str(i) in agent_assignments:
            step["preferred_agent"] = agent_assignments[str(i)]
        
        # Add dependency on previous step (except for first step)
        if i > 0:
            step["dependencies"] = [f"step_{i}"]
        
        workflow_steps.append(step)
    
    return workflow_steps
