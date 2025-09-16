"""
AgenticAI-based Review Agent Core
Implements autonomous, intelligent code review capabilities with adaptive behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Protocol, Callable
import logging
import asyncio
from pathlib import Path
import json


class AgentState(Enum):
    """Possible states for an AI agent."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    FAILED = "failed"
    COMPLETED = "completed"


class Priority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AgentGoal:
    """Represents a goal for an AI agent."""
    id: str
    description: str
    priority: Priority
    success_criteria: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0
    completed: bool = False


@dataclass
class AgentTask:
    """Represents a task that contributes to achieving a goal."""
    id: str
    goal_id: str
    description: str
    task_type: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    priority: Priority = Priority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    completed: bool = False
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentMemory:
    """Agent memory for learning and adaptation."""
    experiences: List[Dict[str, Any]] = field(default_factory=list)
    patterns: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class AgentCapability(Protocol):
    """Protocol defining agent capabilities."""
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this capability can handle the given task."""
        ...
    
    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task and return results."""
        ...
    
    def learn_from_result(self, task: AgentTask, result: Dict[str, Any]) -> None:
        """Learn from the execution result."""
        ...


class BaseAgent(ABC):
    """Base class for all AI agents in the system."""
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = name
        self.config = config
        self.state = AgentState.IDLE
        self.goals: List[AgentGoal] = []
        self.tasks: List[AgentTask] = []
        self.memory = AgentMemory()
        self.capabilities: List[AgentCapability] = []
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    @abstractmethod
    async def analyze_situation(self, context: Dict[str, Any]) -> List[AgentGoal]:
        """Analyze the current situation and determine goals."""
        pass
    
    @abstractmethod
    async def plan_actions(self, goals: List[AgentGoal]) -> List[AgentTask]:
        """Create a plan to achieve the given goals."""
        pass
    
    async def execute_plan(self) -> Dict[str, Any]:
        """Execute the planned tasks."""
        self.state = AgentState.EXECUTING
        results = {}
        
        try:
            # Sort tasks by priority and dependencies
            sorted_tasks = self._sort_tasks_by_priority()
            
            for task in sorted_tasks:
                if not self._dependencies_satisfied(task):
                    self.logger.warning(f"Dependencies not satisfied for task {task.id}")
                    continue
                
                # Find capable handler
                capability = self._find_capability_for_task(task)
                if not capability:
                    task.error = f"No capability found for task type: {task.task_type}"
                    self.logger.error(task.error)
                    continue
                
                # Execute task
                self.logger.info(f"Executing task: {task.description}")
                try:
                    result = await capability.execute(task, self._get_execution_context())
                    task.result = result
                    task.completed = True
                    results[task.id] = result
                    
                    # Learn from result
                    capability.learn_from_result(task, result)
                    self._update_memory(task, result)
                    
                except Exception as e:
                    task.error = str(e)
                    self.logger.error(f"Task {task.id} failed: {e}")
                    
        except Exception as e:
            self.state = AgentState.FAILED
            self.logger.error(f"Plan execution failed: {e}")
            raise
        
        self.state = AgentState.COMPLETED
        return results
    
    def _sort_tasks_by_priority(self) -> List[AgentTask]:
        """Sort tasks by priority and dependencies."""
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1, 
            Priority.MEDIUM: 2,
            Priority.LOW: 3
        }
        
        return sorted(self.tasks, key=lambda t: (
            priority_order[t.priority],
            len(t.dependencies)
        ))
    
    def _dependencies_satisfied(self, task: AgentTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            dep_task = next((t for t in self.tasks if t.id == dep_id), None)
            if not dep_task or not dep_task.completed:
                return False
        return True
    
    def _find_capability_for_task(self, task: AgentTask) -> Optional[AgentCapability]:
        """Find a capability that can handle the given task."""
        for capability in self.capabilities:
            if capability.can_handle(task):
                return capability
        return None
    
    def _get_execution_context(self) -> Dict[str, Any]:
        """Get current execution context."""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "memory": self.memory,
            "config": self.config
        }
    
    def _update_memory(self, task: AgentTask, result: Dict[str, Any]) -> None:
        """Update agent memory with task experience."""
        experience = {
            "task_id": task.id,
            "task_type": task.task_type,
            "input": task.input_data,
            "output": result,
            "success": task.completed and not task.error,
            "timestamp": "now"  # Would use actual timestamp
        }
        self.memory.experiences.append(experience)
        
        # Update performance metrics
        task_type = task.task_type
        if task_type not in self.memory.performance_metrics:
            self.memory.performance_metrics[task_type] = 0.0
        
        success_rate = len([e for e in self.memory.experiences 
                          if e["task_type"] == task_type and e["success"]]) / \
                      len([e for e in self.memory.experiences 
                          if e["task_type"] == task_type])
        
        self.memory.performance_metrics[task_type] = success_rate
    
    async def learn_and_adapt(self) -> None:
        """Learn from experiences and adapt behavior."""
        self.state = AgentState.LEARNING
        
        # Analyze performance patterns
        for task_type, success_rate in self.memory.performance_metrics.items():
            if success_rate < 0.8:  # Low success rate threshold
                self.logger.warning(f"Low success rate for {task_type}: {success_rate}")
                # Could implement adaptive behavior here
        
        # Update preferences based on successful patterns
        successful_experiences = [e for e in self.memory.experiences if e["success"]]
        if successful_experiences:
            # Analyze patterns in successful executions
            self._extract_success_patterns(successful_experiences)
    
    def _extract_success_patterns(self, experiences: List[Dict[str, Any]]) -> None:
        """Extract patterns from successful experiences."""
        # Group by task type
        by_type = {}
        for exp in experiences:
            task_type = exp["task_type"]
            if task_type not in by_type:
                by_type[task_type] = []
            by_type[task_type].append(exp)
        
        # Find common patterns
        for task_type, type_experiences in by_type.items():
            if len(type_experiences) >= 3:  # Need sufficient data
                # Could implement pattern recognition here
                self.memory.patterns[task_type] = {
                    "count": len(type_experiences),
                    "success_rate": 1.0,  # These are all successful
                    "last_updated": "now"
                }


class AgentOrchestrator:
    """Orchestrates multiple AI agents working together."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self.shared_memory: Dict[str, Any] = {}
        self.collaboration_graph: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent: BaseAgent, collaborators: List[str] = None) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        self.collaboration_graph[agent.agent_id] = collaborators or []
        self.logger.info(f"Registered agent: {agent.name}")
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """
        Execute a goal using autonomous agent coordination.
        
        Args:
            goal: The main goal to achieve
            
        Returns:
            Comprehensive results from all agent analyses
        """
        self.logger.info(f"Executing goal: {goal.description}")
        
        try:
            # Phase 1: File Discovery
            discovery_results = await self._execute_file_discovery(goal.context)
            
            # Phase 2: Parallel Analysis by Specialized Agents
            analysis_results = await self._execute_parallel_analysis(
                discovery_results, goal.context
            )
            
            # Phase 3: Report Generation and Synthesis
            final_results = await self._execute_report_generation(
                analysis_results, goal.context
            )
            
            self.logger.info("Goal execution completed successfully")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Goal execution failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _execute_file_discovery(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file discovery phase."""
        discovery_agent = self._get_agent_by_type("file_discovery")
        if not discovery_agent:
            raise ValueError("File discovery agent not found")
        
        discovery_results = await discovery_agent.analyze(context)
        
        # Update context with discovered files
        context["files"] = discovery_results.get("discovered_files", [])
        context["file_classification"] = discovery_results.get("classification", {})
        
        return discovery_results
    
    async def _execute_parallel_analysis(self, discovery_results: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute parallel analysis by specialized agents."""
        analysis_tasks = []
        
        # Code Quality Analysis
        quality_agent = self._get_agent_by_type("code_quality")
        if quality_agent:
            analysis_tasks.append(
                self._run_agent_analysis(quality_agent, context, "code_quality_agent")
            )
        
        # Security Analysis
        security_agent = self._get_agent_by_type("security")
        if security_agent:
            analysis_tasks.append(
                self._run_agent_analysis(security_agent, context, "security_analysis_agent")
            )
        
        # Compliance Analysis
        compliance_agent = self._get_agent_by_type("compliance")
        if compliance_agent:
            analysis_tasks.append(
                self._run_agent_analysis(compliance_agent, context, "compliance_agent")
            )
        
        # Execute all analyses in parallel
        if self.config.get("parallel_processing", True):
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        else:
            # Sequential execution
            analysis_results = []
            for task in analysis_tasks:
                result = await task
                analysis_results.append(result)
        
        # Combine results
        combined_results = {}
        agent_names = ["code_quality_agent", "security_analysis_agent", "compliance_agent"]
        
        for i, result in enumerate(analysis_results):
            if i < len(agent_names):
                agent_name = agent_names[i]
                if isinstance(result, Exception):
                    combined_results[agent_name] = {"error": str(result)}
                    self.logger.error(f"Agent {agent_name} failed: {result}")
                else:
                    combined_results[agent_name] = result
        
        return combined_results
    
    async def _execute_report_generation(self, analysis_results: Dict[str, Any],
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation and synthesis."""
        report_agent = self._get_agent_by_type("reporting")
        if not report_agent:
            self.logger.warning("Report generation agent not found")
            return {"analysis_results": analysis_results}
        
        # Prepare context for report generation
        report_context = context.copy()
        report_context["agent_results"] = analysis_results
        
        report_results = await report_agent.analyze(report_context)
        
        return report_results
    
    async def _run_agent_analysis(self, agent: BaseAgent, context: Dict[str, Any], 
                                agent_name: str) -> Dict[str, Any]:
        """Run analysis for a specific agent with timeout."""
        try:
            timeout = self.config.get("agent_timeout", 300)  # 5 minutes default
            result = await asyncio.wait_for(agent.analyze(context), timeout=timeout)
            
            self.logger.info(f"Agent {agent_name} completed analysis")
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Agent {agent_name} timed out")
            return {"error": "Analysis timed out", "agent": agent_name}
        except Exception as e:
            self.logger.error(f"Agent {agent_name} failed: {e}")
            return {"error": str(e), "agent": agent_name}
    
    def _get_agent_by_type(self, agent_type: str) -> Optional[BaseAgent]:
        """Get agent by type."""
        for agent in self.agents.values():
            if hasattr(agent, 'agent_type') and agent.agent_type == agent_type:
                return agent
        return None
    
    async def coordinate_agents(self, global_context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents to achieve global objectives."""
        results = {}
        
        # Phase 1: All agents analyze the situation
        analysis_tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(agent.analyze_situation(global_context))
            analysis_tasks.append((agent.agent_id, task))
        
        # Collect analysis results
        all_goals = {}
        for agent_id, task in analysis_tasks:
            try:
                goals = await task
                all_goals[agent_id] = goals
                self.logger.info(f"Agent {agent_id} identified {len(goals)} goals")
            except Exception as e:
                self.logger.error(f"Agent {agent_id} analysis failed: {e}")
        
        # Phase 2: Collaborative planning
        await self._coordinate_planning(all_goals)
        
        # Phase 3: Coordinated execution
        execution_results = await self._coordinate_execution()
        
        # Phase 4: Collective learning
        await self._coordinate_learning()
        
        return execution_results
    
    async def _coordinate_planning(self, all_goals: Dict[str, List[AgentGoal]]) -> None:
        """Coordinate planning across agents."""
        # Identify overlapping goals and potential conflicts
        for agent_id, goals in all_goals.items():
            agent = self.agents[agent_id]
            tasks = await agent.plan_actions(goals)
            agent.tasks = tasks
            
            # Share planning context with collaborators
            collaborators = self.collaboration_graph.get(agent_id, [])
            for collab_id in collaborators:
                if collab_id in self.agents:
                    self._share_planning_context(agent_id, collab_id, tasks)
    
    def _share_planning_context(self, from_agent: str, to_agent: str, tasks: List[AgentTask]) -> None:
        """Share planning context between collaborating agents."""
        context_key = f"shared_tasks_{from_agent}_to_{to_agent}"
        self.shared_memory[context_key] = [
            {
                "task_id": task.id,
                "type": task.task_type,
                "description": task.description,
                "priority": task.priority.value
            }
            for task in tasks
        ]
    
    async def _coordinate_execution(self) -> Dict[str, Any]:
        """Coordinate execution across agents."""
        execution_tasks = []
        
        for agent in self.agents.values():
            if agent.tasks:  # Only execute if agent has tasks
                task = asyncio.create_task(agent.execute_plan())
                execution_tasks.append((agent.agent_id, task))
        
        # Wait for all agents to complete
        results = {}
        for agent_id, task in execution_tasks:
            try:
                result = await task
                results[agent_id] = result
                self.logger.info(f"Agent {agent_id} completed execution")
            except Exception as e:
                self.logger.error(f"Agent {agent_id} execution failed: {e}")
                results[agent_id] = {"error": str(e)}
        
        return results
    
    async def _coordinate_learning(self) -> None:
        """Coordinate learning across agents."""
        learning_tasks = []
        
        for agent in self.agents.values():
            task = asyncio.create_task(agent.learn_and_adapt())
            learning_tasks.append(task)
        
        # Wait for all learning to complete
        await asyncio.gather(*learning_tasks, return_exceptions=True)
        
        # Share learning insights
        self._share_learning_insights()
    
    def _share_learning_insights(self) -> None:
        """Share learning insights between agents."""
        insights = {}
        
        for agent_id, agent in self.agents.items():
            insights[agent_id] = {
                "performance_metrics": agent.memory.performance_metrics,
                "patterns": agent.memory.patterns,
                "experience_count": len(agent.memory.experiences)
            }
        
        # Store in shared memory for cross-agent learning
        self.shared_memory["learning_insights"] = insights
        self.logger.info("Shared learning insights across all agents")
