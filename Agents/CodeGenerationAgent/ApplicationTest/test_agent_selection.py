#!/usr/bin/env python3
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from agentic.core import AgentGoal, Priority
from agentic.simple_agents import (
    SimpleConfigurationAgent,
    SimpleStructureAgent, 
    SimpleTemplateAgent,
    SimpleCodeGenerationAgent,
    SimpleValidationAgent
)

# Create test goals
goals = [
    AgentGoal(
        id="load_specification",
        description="Load API specification file",
        priority=Priority.HIGH,
        success_criteria={},
        context={}
    ),
    AgentGoal(
        id="load_instructions", 
        description="Load instruction template file",
        priority=Priority.HIGH,
        success_criteria={},
        context={}
    ),
    AgentGoal(
        id="validate_compatibility",
        description="Validate compatibility",
        priority=Priority.MEDIUM,
        success_criteria={},
        context={}
    )
]

# Create agents
agents = [
    ("Configuration Agent", SimpleConfigurationAgent()),
    ("Structure Agent", SimpleStructureAgent()),
    ("Template Agent", SimpleTemplateAgent()),
    ("Code Generation Agent", SimpleCodeGenerationAgent()),
    ("Validation Agent", SimpleValidationAgent())
]

print("Testing agent goal handling:")
for goal in goals:
    print(f"\nGoal: {goal.id}")
    for name, agent in agents:
        can_handle = agent.can_handle_goal(goal)
        print(f"  {name}: {'YES' if can_handle else 'NO'} (capabilities: {agent.capabilities})")
