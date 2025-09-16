"""
AgenticAI Code Review System - Autonomous Intelligent Agents

This package provides autonomous AI agents for comprehensive code review and analysis.
Each agent specializes in specific aspects of code quality, security, and compliance.
"""

from .core import (
    BaseAgent,
    AgentOrchestrator,
    AgentState,
    Priority,
    AgentGoal,
    AgentTask,
    AgentMemory,
    AgentCapability
)

from .review_agents import (
    FileDiscoveryAgent,
    CodeQualityAgent,
    SecurityAnalysisAgent,
    ComplianceAgent,
    ReportGenerationAgent
)

from .capabilities import (
    FileDiscoveryCapability,
    JavaAnalysisCapability,
    PythonAnalysisCapability,
    GenericAnalysisCapability,
    ReportGenerationCapability
)

__all__ = [
    # Core framework
    "BaseAgent",
    "AgentOrchestrator", 
    "AgentState",
    "Priority",
    "AgentGoal",
    "AgentTask",
    "AgentMemory",
    "AgentCapability",
    
    # Specialized agents
    "FileDiscoveryAgent",
    "CodeQualityAgent",
    "SecurityAnalysisAgent",
    "ComplianceAgent",
    "ReportGenerationAgent",
    
    # Agent capabilities
    "FileDiscoveryCapability",
    "JavaAnalysisCapability",
    "PythonAnalysisCapability",
    "GenericAnalysisCapability",
    "ReportGenerationCapability"
]

__version__ = "1.0.0"
__author__ = "AgenticAI Review System"
__description__ = "Autonomous AI agents for comprehensive code review and analysis"
