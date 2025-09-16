"""
AgenticAI Code Generation System Package
Main entry point for the autonomous code generation system.
"""

__version__ = "1.0.0"
__author__ = "AgenticAI Team"
__email__ = "team@agentic.ai"
__description__ = "Autonomous code generation using specialized AI agents"

# Import main components for easy access
from .agentic import (
    BaseAgent,
    AgentOrchestrator,
    AgentGoal,
    AgentTask,
    Priority,
    SimpleConfigurationAgent,
    SimpleStructureAgent,
    SimpleTemplateAgent,
    SimpleCodeGenerationAgent,
    SimpleValidationAgent,
)

# Main interface
from .main_agentic import AgenticCodeGenerator

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    
    # Core framework
    "BaseAgent",
    "AgentOrchestrator",
    "AgentGoal",
    "AgentTask", 
    "Priority",
    
    # Agents
    "SimpleConfigurationAgent",
    "SimpleStructureAgent",
    "SimpleTemplateAgent",
    "SimpleCodeGenerationAgent",
    "SimpleValidationAgent",
    
    # Main interface
    "AgenticCodeGenerator",
]
