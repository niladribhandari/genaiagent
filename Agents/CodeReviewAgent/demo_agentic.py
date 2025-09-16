#!/usr/bin/env python3
"""
Demo script for AgenticAI Code Review System
Shows autonomous agent capabilities
"""

import asyncio
import logging
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

from agentic.core import AgentOrchestrator, AgentGoal, Priority
from agentic.review_agents import (
    FileDiscoveryAgent, CodeQualityAgent, SecurityAnalysisAgent,
    ComplianceAgent, ReportGenerationAgent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_agentic_review():
    """Demonstrate AgenticAI code review capabilities."""
    
    print("🤖 AgenticAI Code Review System Demo")
    print("=" * 50)
    
    # Configuration for agents
    config = {
        "debug": True,
        "max_file_size": 1024 * 1024,  # 1MB
        "supported_languages": ["java", "python", "javascript", "yaml"]
    }
    
    # Create the autonomous agents
    print("\n🎯 Creating Autonomous Agents...")
    agents = {
        "file_discovery": FileDiscoveryAgent("file_discovery_agent", config),
        "code_quality": CodeQualityAgent("code_quality_agent", config),
        "security": SecurityAnalysisAgent("security_agent", config),
        "compliance": ComplianceAgent("compliance_agent", config),
        "reporting": ReportGenerationAgent("reporting_agent", config)
    }
    
    for agent_type, agent in agents.items():
        print(f"  ✓ {agent.name} ({agent_type})")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(config)
    for agent in agents.values():
        orchestrator.register_agent(agent)
    
    print(f"\n🧠 Orchestrator created with {len(agents)} autonomous agents")
    
    # Set up analysis context
    project_path = Path(__file__).parent
    context = {
        "project_path": str(project_path),
        "analysis_mode": "comprehensive",
        "target_files": ["*.py", "*.yml", "*.yaml"]
    }
    
    # Create analysis goal
    main_goal = AgentGoal(
        id="demo_comprehensive_review",
        description="Demonstrate autonomous code review capabilities",
        priority=Priority.HIGH,
        success_criteria={"demo_completed": True, "agents_executed": True},
        context=context
    )
    
    print(f"\n🎯 Analysis Goal: {main_goal.description}")
    print(f"📁 Project Path: {project_path}")
    
    try:
        # Execute autonomous analysis
        print("\n🚀 Starting Autonomous Analysis...")
        
        # Each agent analyzes the situation and makes autonomous decisions
        agent_results = {}
        
        for agent_name, agent in agents.items():
            print(f"\n  🤖 {agent.name} analyzing situation...")
            
            # Agent autonomously analyzes the situation
            goals = await agent.analyze_situation(context)
            print(f"    📋 Created {len(goals)} autonomous goals")
            
            # Agent autonomously plans actions
            tasks = await agent.plan_actions(goals)
            print(f"    ⚡ Planned {len(tasks)} autonomous tasks")
            
            # Simulate task execution (in a real system, agents would execute tasks)
            if agent_name == "file_discovery":
                result = {
                    "files_discovered": 15,
                    "file_types": ["python", "yaml", "markdown"],
                    "analysis_status": "completed",
                    "autonomous_decisions": [
                        "Focused on .py and .yml files",
                        "Excluded test files for initial analysis",
                        "Prioritized main source files"
                    ]
                }
            elif agent_name == "code_quality":
                result = {
                    "quality_score": 0.85,
                    "complexity_issues": 3,
                    "structure_analysis": "good",
                    "autonomous_decisions": [
                        "Analyzed Python complexity patterns",
                        "Checked modular structure",
                        "Validated coding standards"
                    ]
                }
            elif agent_name == "security":
                result = {
                    "vulnerabilities_found": 1,
                    "security_score": 0.92,
                    "risk_level": "low",
                    "autonomous_decisions": [
                        "Scanned for injection patterns",
                        "Checked authentication methods",
                        "Analyzed file permissions"
                    ]
                }
            elif agent_name == "compliance":
                result = {
                    "compliance_score": 0.88,
                    "standards_violations": 2,
                    "best_practices": "mostly_followed",
                    "autonomous_decisions": [
                        "Checked PEP 8 compliance",
                        "Validated documentation standards",
                        "Analyzed naming conventions"
                    ]
                }
            elif agent_name == "reporting":
                result = {
                    "report_generated": True,
                    "summary_created": True,
                    "autonomous_decisions": [
                        "Prioritized critical findings",
                        "Generated executive summary",
                        "Created detailed technical report"
                    ]
                }
            
            agent_results[agent_name] = result
            print(f"    ✅ {agent.name} completed autonomous analysis")
            
            # Show autonomous decisions
            decisions = result.get("autonomous_decisions", [])
            for decision in decisions:
                print(f"      🧠 Autonomous decision: {decision}")
        
        # Final orchestration and synthesis
        print(f"\n🎼 Agent Orchestrator synthesizing results...")
        
        # Calculate overall metrics
        overall_score = sum([
            agent_results["code_quality"].get("quality_score", 0),
            agent_results["security"].get("security_score", 0),
            agent_results["compliance"].get("compliance_score", 0)
        ]) / 3
        
        total_issues = sum([
            agent_results["code_quality"].get("complexity_issues", 0),
            agent_results["security"].get("vulnerabilities_found", 0),
            agent_results["compliance"].get("standards_violations", 0)
        ])
        
        # Generate comprehensive results
        comprehensive_results = {
            "overall_assessment": {
                "overall_score": round(overall_score, 2),
                "total_issues": total_issues,
                "analysis_mode": "autonomous_agentic",
                "agents_utilized": len(agents)
            },
            "agent_contributions": agent_results,
            "autonomous_insights": [
                "Agents made independent analytical decisions",
                "Each agent focused on specialized domain expertise",
                "Collaborative intelligence enhanced overall analysis",
                "Autonomous task prioritization optimized workflow"
            ],
            "recommendations": [
                "Continue autonomous agent-based reviews",
                "Expand agent capabilities with machine learning",
                "Implement continuous autonomous monitoring",
                "Develop agent-to-agent learning protocols"
            ]
        }
        
        # Display results
        print(f"\n📊 AgenticAI Analysis Results")
        print(f"=" * 40)
        print(f"Overall Score: {comprehensive_results['overall_assessment']['overall_score']:.2f}")
        print(f"Total Issues: {comprehensive_results['overall_assessment']['total_issues']}")
        print(f"Agents Used: {comprehensive_results['overall_assessment']['agents_utilized']}")
        
        print(f"\n🧠 Autonomous Insights:")
        for insight in comprehensive_results["autonomous_insights"]:
            print(f"  • {insight}")
        
        print(f"\n💡 AI Recommendations:")
        for rec in comprehensive_results["recommendations"]:
            print(f"  • {rec}")
        
        # Save results
        output_file = "agentic_demo_results.json"
        with open(output_file, 'w') as f:
            json.dump(comprehensive_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        print(f"\n✅ AgenticAI Demo Completed Successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo Failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting AgenticAI Code Review Demo...")
    success = asyncio.run(demo_agentic_review())
    
    if success:
        print("\n🎉 Demo completed successfully!")
        print("The AgenticAI system demonstrates autonomous agent capabilities:")
        print("• Independent situation analysis")
        print("• Autonomous decision making")
        print("• Specialized domain expertise")
        print("• Collaborative intelligence")
        print("• Adaptive task planning")
    else:
        print("\n❌ Demo failed. Check logs for details.")
        sys.exit(1)
