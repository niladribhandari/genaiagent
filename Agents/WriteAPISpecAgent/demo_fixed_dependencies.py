"""
Fixed Demo: API Specification Generation with Improved Dependency Resolution
This demo shows how the flexible dependency resolution prevents deadlocks
"""

import asyncio
import json
from typing import Dict, Any

from src.agentic.agent_orchestrator import AgentOrchestrator
from src.agentic.requirement_analysis_agent import RequirementAnalysisAgent
from src.agentic.api_design_agent import APIDesignAgent
from src.agentic.specification_writer_agent import SpecificationWriterAgent
from src.agentic.validation_agent import ValidationAgent
from src.agentic.documentation_agent import DocumentationAgent
from src.models.search_models import UserRequirement, SpecificationFormat
from src.utils.file_manager import APISpecFileManager


async def example_fixed_workflow():
    """Example with improved dependency resolution that prevents deadlocks."""
    print("🚀 Fixed API Specification Generation Demo")
    print("=" * 60)
    
    # 1. Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # 2. Register agents
    analysis_agent = RequirementAnalysisAgent()
    design_agent = APIDesignAgent()
    writer_agent = SpecificationWriterAgent()
    validation_agent = ValidationAgent()
    documentation_agent = DocumentationAgent()
    
    orchestrator.register_agent(analysis_agent)
    orchestrator.register_agent(design_agent)
    orchestrator.register_agent(writer_agent)
    orchestrator.register_agent(validation_agent)
    orchestrator.register_agent(documentation_agent)
    
    print(f"✓ Registered {len(orchestrator.registered_agents)} specialized agents")
    
    # 3. Create workflow with flexible dependencies
    print("\n🔄 Step 3: Creating Fixed API Specification Workflow")
    
    # Define workflow steps with FLEXIBLE dependencies
    workflow_steps = [
        {
            "objective": "analyze_api_requirements",
            "preferred_agent": "requirement_analysis_agent",
            "parameters": {
                "requirements": "User Management API for e-commerce platform"
            },
            "dependencies": []  # No dependencies for first step
        },
        {
            "objective": "design_api_structure",
            "preferred_agent": "api_design_agent",
            "parameters": {"project_name": "User Management API"},
            "dependencies": [0]  # ✅ Depends on step 0 (numeric index)
        },
        {
            "objective": "generate_openapi_specification",
            "preferred_agent": "specification_writer_agent",
            "parameters": {
                "project_name": "User Management API",
                "format": SpecificationFormat.OPENAPI_YAML.value
            },
            "dependencies": ["prev"]  # ✅ Depends on previous step (relative)
        },
        {
            "objective": "validate_api_specification",
            "preferred_agent": "validation_agent",
            "parameters": {},
            "dependencies": ["prev"]  # ✅ Depends on previous step
        },
        {
            "objective": "generate_documentation",
            "preferred_agent": "documentation_agent",
            "parameters": {"doc_format": "markdown"},
            "dependencies": ["prev"]  # ✅ Depends on previous step
        }
    ]
    
    workflow_id = await orchestrator.create_workflow(
        name="API Spec Generation - Fixed",
        description="Fixed workflow with flexible dependency resolution",
        steps=workflow_steps
    )
    
    print(f"✓ Created workflow with {len(workflow_steps)} steps")
    
    # 4. Execute workflow
    print("\n⚡ Step 4: Executing Fixed Workflow")
    print("This should now work without deadlocks...")
    
    try:
        result = await orchestrator.execute_workflow(workflow_id)
        
        if result.success:
            print("✅ Workflow executed successfully!")
            print(f"Result: {result.data}")
            
            # Save the generated specification
            if isinstance(result.data, dict) and 'specification' in result.data:
                file_manager = APISpecFileManager("./API-requirements")
                spec_path = file_manager.save_specification_content(
                    content=result.data['specification'],
                    filename="user_management_api_fixed.yml",
                    metadata={
                        "generated_by": "WriteAPISpecAgent_Fixed",
                        "workflow_id": workflow_id,
                        "dependency_resolution": "flexible"
                    }
                )
                print(f"✅ Specification saved to: {spec_path}")
        else:
            print(f"❌ Workflow failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Workflow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("🎉 Fixed Demo completed!")


async def demonstrate_dependency_patterns():
    """Demonstrate different dependency resolution patterns."""
    print("\n📋 Dependency Resolution Patterns Demo")
    print("-" * 40)
    
    patterns = [
        {
            "name": "Numeric Index",
            "dependencies": [0, 1],
            "description": "Depends on steps 0 and 1"
        },
        {
            "name": "String Numeric",
            "dependencies": ["0", "1"],
            "description": "Same as numeric but as strings"
        },
        {
            "name": "Relative Previous",
            "dependencies": ["prev"],
            "description": "Depends on the immediately previous step"
        },
        {
            "name": "Named Steps",
            "dependencies": ["step_1", "step_2"],
            "description": "Depends on named steps"
        },
        {
            "name": "Mixed Pattern",
            "dependencies": [0, "prev", "step_1"],
            "description": "Mix of different dependency types"
        }
    ]
    
    for pattern in patterns:
        print(f"✓ {pattern['name']}: {pattern['dependencies']}")
        print(f"  → {pattern['description']}")


if __name__ == "__main__":
    print("🎯 WriteAPISpecAgent - Fixed Dependency Resolution Demo")
    print("=" * 80)
    
    asyncio.run(example_fixed_workflow())
    asyncio.run(demonstrate_dependency_patterns())
    
    print("\n✨ Key Improvements:")
    print("1. ✅ Flexible dependency resolution prevents deadlocks")
    print("2. ✅ Multiple dependency patterns supported")
    print("3. ✅ Backward compatibility with legacy dependencies") 
    print("4. ✅ Better error handling and validation")
    print("5. ✅ More maintainable and scalable workflows")
