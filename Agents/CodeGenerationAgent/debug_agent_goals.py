#!/usr/bin/env python3
"""
Debug script to test agent goal handling
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic.core import AgentOrchestrator, AgentGoal, Priority
from agentic.simple_agents import SimpleConfigurationAgent

def test_agent_goals():
    """Test agent goal handling directly."""
    
    print("🔍 Testing Agent Goal Handling")
    print("=" * 40)
    
    # Create agent and orchestrator
    orchestrator_config = {"max_concurrent_goals": 5}
    orchestrator = AgentOrchestrator(orchestrator_config)
    config_agent = SimpleConfigurationAgent()
    
    print(f"✅ Created ConfigurationAgent with capabilities: {config_agent.capabilities}")
    
    # Register agent
    orchestrator.register_agent(config_agent)
    print(f"✅ Registered agent. Orchestrator now has {len(orchestrator.agents)} agents")
    
    # Test goals
    test_goals = [
        "load_specification", 
        "load_instructions",
        "validate_compatibility"
    ]
    
    for goal_id in test_goals:
        goal = AgentGoal(
            id=goal_id,
            description=f"Test {goal_id}",
            priority=Priority.HIGH,
            success_criteria={},
            context={}
        )
        
        # Test can_handle_goal
        can_handle = config_agent.can_handle_goal(goal)
        print(f"📋 Goal '{goal_id}': can_handle = {can_handle}")
        
        # Test agent selection
        selected_agent = orchestrator._select_agent_for_goal(goal)
        print(f"🎯 Goal '{goal_id}': selected_agent = {selected_agent.name if selected_agent else 'None'}")
        
        print()

if __name__ == "__main__":
    test_agent_goals()
