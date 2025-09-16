"""
Base Agent Framework for API Specification Writing System
Provides foundation for all autonomous agents with goal-oriented execution
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging


class GoalStatus(Enum):
    """Status of goal execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentCapability(Enum):
    """Standard capabilities that agents can possess."""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    API_DESIGN = "api_design"
    SPECIFICATION_WRITING = "specification_writing"
    VALIDATION = "validation"
    DOCUMENTATION = "documentation"
    SCHEMA_GENERATION = "schema_generation"
    ENDPOINT_DESIGN = "endpoint_design"
    SECURITY_DESIGN = "security_design"
    ERROR_HANDLING = "error_handling"
    TESTING = "testing"
    TEXT_PROCESSING = "text_processing"
    ENTITY_EXTRACTION = "entity_extraction"
    ENDPOINT_IDENTIFICATION = "endpoint_identification"
    DATA_MODEL_EXTRACTION = "data_model_extraction"
    ARCHITECTURE_DESIGN = "architecture_design"
    DATA_FLOW_DESIGN = "data_flow_design"
    YAML_GENERATION = "yaml_generation"
    JSON_GENERATION = "json_generation"
    FORMAT_CONVERSION = "format_conversion"
    SYNTAX_VALIDATION = "syntax_validation"
    SEMANTIC_VALIDATION = "semantic_validation"
    QUALITY_ASSESSMENT = "quality_assessment"
    MARKDOWN_GENERATION = "markdown_generation"
    EXAMPLE_GENERATION = "example_generation"


@dataclass
class Goal:
    """Represents a goal that an agent should accomplish."""
    objective: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"  # high, medium, low
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    goal_id: str = field(default_factory=lambda: f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
    status: GoalStatus = GoalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def start_execution(self):
        """Mark goal as started."""
        self.status = GoalStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete_execution(self):
        """Mark goal as completed."""
        self.status = GoalStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def fail_execution(self):
        """Mark goal as failed."""
        self.status = GoalStatus.FAILED
        self.completed_at = datetime.now()


@dataclass
class AgentResult:
    """Result of agent goal execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    agent_name: Optional[str] = None
    goal_id: Optional[str] = None
    
    # Additional result information
    confidence: float = 1.0  # Confidence in the result (0.0 to 1.0)
    suggestions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """
    Base class for all autonomous agents in the API Specification Writing System.
    
    Each agent is responsible for specific capabilities and can execute goals
    autonomously while collaborating with other agents through the orchestrator.
    """
    
    def __init__(
        self,
        name: str,
        capabilities: List[Union[AgentCapability, str]],
        description: str = "",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Unique name for this agent
            capabilities: List of capabilities this agent possesses
            description: Human-readable description of agent's purpose
            config: Agent-specific configuration
        """
        self.name = name
        self.capabilities = [
            cap if isinstance(cap, AgentCapability) else AgentCapability(cap)
            for cap in capabilities
        ]
        self.description = description
        self.config = config or {}
        
        # Agent state
        self.is_active = True
        self.current_goals: List[Goal] = []
        self.completed_goals: List[Goal] = []
        self.failed_goals: List[Goal] = []
        
        # Performance tracking
        self.execution_history: List[AgentResult] = []
        self.total_executions = 0
        self.successful_executions = 0
        self.average_execution_time = 0.0
        
        # Setup logging
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    async def execute_goal(self, goal: Goal) -> AgentResult:
        """
        Execute a specific goal assigned to this agent.
        
        Args:
            goal: The goal to execute
            
        Returns:
            AgentResult containing the outcome of goal execution
        """
        pass
    
    def can_handle_goal(self, goal: Goal) -> bool:
        """
        Check if this agent can handle the given goal.
        
        Args:
            goal: The goal to check
            
        Returns:
            True if agent can handle the goal, False otherwise
        """
        # Check if goal objective matches any of our capabilities
        objective = goal.objective.lower()
        
        for capability in self.capabilities:
            if capability.value in objective:
                return True
        
        # Additional custom logic can be implemented in subclasses
        return self._custom_goal_check(goal)
    
    def _custom_goal_check(self, goal: Goal) -> bool:
        """
        Custom goal checking logic for specific agents.
        Override in subclasses for specialized checking.
        """
        return False
    
    async def _execute_with_tracking(self, goal: Goal) -> AgentResult:
        """Execute goal with performance tracking."""
        start_time = datetime.now()
        goal.start_execution()
        self.current_goals.append(goal)
        
        try:
            self.logger.info(f"Starting execution of goal: {goal.objective}")
            
            # Execute the actual goal
            result = await self.execute_goal(goal)
            
            # Update tracking
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            result.agent_name = self.name
            result.goal_id = goal.goal_id
            
            # Update agent statistics
            self.total_executions += 1
            if result.success:
                self.successful_executions += 1
                goal.complete_execution()
                self.completed_goals.append(goal)
            else:
                goal.fail_execution()
                self.failed_goals.append(goal)
            
            # Update average execution time
            self.average_execution_time = (
                (self.average_execution_time * (self.total_executions - 1) + execution_time)
                / self.total_executions
            )
            
            # Store result in history
            self.execution_history.append(result)
            
            self.logger.info(
                f"Completed goal: {goal.objective} | "
                f"Success: {result.success} | "
                f"Time: {execution_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            goal.fail_execution()
            self.failed_goals.append(goal)
            
            error_result = AgentResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                agent_name=self.name,
                goal_id=goal.goal_id
            )
            
            self.execution_history.append(error_result)
            self.logger.error(f"Goal execution failed: {goal.objective} | Error: {str(e)}")
            
            return error_result
            
        finally:
            # Remove from current goals
            if goal in self.current_goals:
                self.current_goals.remove(goal)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this agent."""
        success_rate = (
            self.successful_executions / self.total_executions
            if self.total_executions > 0 else 0.0
        )
        
        return {
            "agent_name": self.name,
            "capabilities": [cap.value for cap in self.capabilities],
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.total_executions - self.successful_executions,
            "success_rate": success_rate,
            "average_execution_time": self.average_execution_time,
            "current_goals": len(self.current_goals),
            "is_active": self.is_active
        }
    
    def get_capability_summary(self) -> Dict[str, Any]:
        """Get summary of agent capabilities."""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": [cap.value for cap in self.capabilities],
            "is_active": self.is_active,
            "performance": self.get_performance_metrics()
        }
    
    async def validate_prerequisites(self, goal: Goal) -> bool:
        """
        Validate that all prerequisites for goal execution are met.
        Override in subclasses for specific validation logic.
        """
        return True
    
    async def prepare_for_goal(self, goal: Goal) -> bool:
        """
        Prepare agent for goal execution.
        Override in subclasses for specific preparation logic.
        """
        return True
    
    async def cleanup_after_goal(self, goal: Goal, result: AgentResult):
        """
        Cleanup after goal execution.
        Override in subclasses for specific cleanup logic.
        """
        pass
    
    def add_capability(self, capability: Union[AgentCapability, str]):
        """Add a new capability to this agent."""
        if isinstance(capability, str):
            capability = AgentCapability(capability)
        
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def remove_capability(self, capability: Union[AgentCapability, str]):
        """Remove a capability from this agent."""
        if isinstance(capability, str):
            capability = AgentCapability(capability)
        
        if capability in self.capabilities:
            self.capabilities.remove(capability)
    
    def activate(self):
        """Activate the agent."""
        self.is_active = True
        self.logger.info(f"Agent {self.name} activated")
    
    def deactivate(self):
        """Deactivate the agent."""
        self.is_active = False
        self.logger.info(f"Agent {self.name} deactivated")
    
    def __str__(self) -> str:
        """String representation of the agent."""
        capabilities_str = ", ".join([cap.value for cap in self.capabilities])
        return f"{self.name} (Capabilities: {capabilities_str})"
    
    def __repr__(self) -> str:
        """Detailed representation of the agent."""
        return (
            f"BaseAgent(name='{self.name}', "
            f"capabilities={[cap.value for cap in self.capabilities]}, "
            f"active={self.is_active})"
        )


class SpecializedAgent(BaseAgent):
    """
    Extended base class for specialized agents with additional functionality.
    """
    
    def __init__(
        self,
        name: str,
        capabilities: List[Union[AgentCapability, str]],
        description: str = "",
        config: Optional[Dict[str, Any]] = None,
        specialization: str = ""
    ):
        super().__init__(name, capabilities, description, config)
        self.specialization = specialization
        self.knowledge_base: Dict[str, Any] = {}
        self.learned_patterns: List[Dict[str, Any]] = []
    
    def add_knowledge(self, key: str, value: Any):
        """Add knowledge to the agent's knowledge base."""
        self.knowledge_base[key] = value
    
    def get_knowledge(self, key: str, default: Any = None) -> Any:
        """Retrieve knowledge from the agent's knowledge base."""
        return self.knowledge_base.get(key, default)
    
    def learn_pattern(self, pattern: Dict[str, Any]):
        """Learn a new pattern for future use."""
        self.learned_patterns.append(pattern)
    
    def find_similar_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find patterns similar to the given context."""
        # Simple pattern matching - can be enhanced with ML
        similar_patterns = []
        
        for pattern in self.learned_patterns:
            similarity_score = self._calculate_pattern_similarity(pattern, context)
            if similarity_score > 0.7:  # Threshold for similarity
                similar_patterns.append(pattern)
        
        return similar_patterns
    
    def _calculate_pattern_similarity(
        self, 
        pattern: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """Calculate similarity between pattern and context."""
        # Simple key-based similarity calculation
        pattern_keys = set(pattern.keys())
        context_keys = set(context.keys())
        
        if not pattern_keys or not context_keys:
            return 0.0
        
        intersection = pattern_keys.intersection(context_keys)
        union = pattern_keys.union(context_keys)
        
        return len(intersection) / len(union)


# Utility functions for goal and result management

def create_goal(
    objective: str,
    parameters: Optional[Dict[str, Any]] = None,
    priority: str = "medium",
    context: Optional[Dict[str, Any]] = None
) -> Goal:
    """Create a new goal with proper defaults."""
    return Goal(
        objective=objective,
        parameters=parameters or {},
        priority=priority,
        context=context or {}
    )


def create_success_result(
    data: Any,
    metadata: Optional[Dict[str, Any]] = None,
    confidence: float = 1.0
) -> AgentResult:
    """Create a successful agent result."""
    return AgentResult(
        success=True,
        data=data,
        metadata=metadata or {},
        confidence=confidence
    )


def create_error_result(
    error: str,
    metadata: Optional[Dict[str, Any]] = None
) -> AgentResult:
    """Create an error agent result."""
    return AgentResult(
        success=False,
        error=error,
        metadata=metadata or {}
    )
