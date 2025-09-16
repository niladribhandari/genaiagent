#!/usr/bin/env python3
"""
Test script for AgenticAI Code Review System
Demonstrates the autonomous agent capabilities
"""

import asyncio
import json
import logging
from pathlib import Path
import sys
import os

# Add the ReviewAgent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agentic.core import AgentOrchestrator, AgentGoal, Priority
from agentic.review_agents import (
    FileDiscoveryAgent, CodeQualityAgent, SecurityAnalysisAgent,
    ComplianceAgent, ReportGenerationAgent
)


async def test_agentic_system():
    """Test the AgenticAI review system."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("Starting AgenticAI System Test")
    
    # Configuration
    config = {
        "max_complexity": 10,
        "max_nesting_depth": 4,
        "enable_security_analysis": True,
        "enable_compliance_check": True,
        "parallel_processing": True,
        "agent_timeout": 60,  # 1 minute for testing
        "learning_enabled": True
    }
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(config)
    
    # Initialize and register agents
    agents = [
        FileDiscoveryAgent("file_discovery_agent", config),
        CodeQualityAgent("code_quality_agent", config),
        SecurityAnalysisAgent("security_analysis_agent", config),
        ComplianceAgent("compliance_agent", config),
        ReportGenerationAgent("report_generation_agent", config)
    ]
    
    for agent in agents:
        orchestrator.register_agent(agent)
    
    logger.info(f"Registered {len(agents)} agents")
    
    # Test with a sample project (use current directory if specific project not found)
    test_project_path = Path(__file__).parent / "policy-generation"
    if not test_project_path.exists():
        # Use the parent directory for testing
        test_project_path = Path(__file__).parent
    
    # Create test context
    context = {
        "project_path": str(test_project_path),
        "analysis_mode": "agentic_test",
        "timestamp": "2025-08-14T22:00:00Z"
    }
    
    logger.info(f"Analyzing project: {test_project_path}")
    
    # Create main goal
    main_goal = AgentGoal(
        id="comprehensive_review",
        description="Perform comprehensive code review",
        priority=Priority.HIGH,
        success_criteria={"review_completed": True},
        context=context
    )
    
    try:
        # Execute the goal
        results = await orchestrator.execute_goal(main_goal)
        
        # Display results
        logger.info("AgenticAI Analysis Results:")
        
        if "error" in results:
            logger.error(f"Analysis failed: {results['error']}")
            return False
        
        # Extract key metrics
        comprehensive_report = results.get("comprehensive_report", {})
        executive_summary = comprehensive_report.get("executive_summary", {})
        
        print("\n" + "="*60)
        print("AGENTICAI CODE REVIEW TEST RESULTS")
        print("="*60)
        
        if executive_summary:
            print(f"Files Analyzed: {executive_summary.get('total_files_analyzed', 0)}")
            print(f"Issues Found: {executive_summary.get('total_issues_found', 0)}")
            print(f"Quality Score: {executive_summary.get('overall_quality_score', 0.0):.2f}")
            print(f"Critical Issues: {executive_summary.get('critical_issues', 0)}")
        
        # Show agent results summary
        agent_analyses = comprehensive_report.get("agent_analyses", {})
        print(f"\nAgent Results:")
        for agent_id, result in agent_analyses.items():
            if isinstance(result, dict):
                if "error" in result:
                    print(f"  {agent_id}: FAILED - {result['error']}")
                else:
                    print(f"  {agent_id}: SUCCESS")
            else:
                print(f"  {agent_id}: COMPLETED")
        
        # Save detailed results
        output_file = Path(__file__).parent / "agentic_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {output_file}")
        
        logger.info("AgenticAI test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_simple_test():
    """Run a simple synchronous test to verify basic functionality."""
    print("Running simple AgenticAI functionality test...")
    
    try:
        # Test agent creation
        config = {"test": True}
        
        file_agent = FileDiscoveryAgent("test_file_agent", config)
        quality_agent = CodeQualityAgent("test_quality_agent", config)
        
        print(f"✓ Created FileDiscoveryAgent: {file_agent.agent_id}")
        print(f"✓ Created CodeQualityAgent: {quality_agent.agent_id}")
        
        # Test orchestrator
        orchestrator = AgentOrchestrator(config)
        orchestrator.register_agent(file_agent)
        orchestrator.register_agent(quality_agent)
        
        print(f"✓ Orchestrator created with {len(orchestrator.agents)} agents")
        
        print("\nBasic functionality test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("AgenticAI Code Review System - Test Suite")
    print("="*50)
    
    # Run simple test first
    simple_success = run_simple_test()
    
    if simple_success:
        print("\nRunning full AsyncIO test...")
        # Run the full async test
        success = asyncio.run(test_agentic_system())
        
        if success:
            print("\n🎉 All tests PASSED! AgenticAI system is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ AsyncIO test FAILED.")
            sys.exit(1)
    else:
        print("\n❌ Basic test FAILED. Cannot proceed with full test.")
        sys.exit(1)
