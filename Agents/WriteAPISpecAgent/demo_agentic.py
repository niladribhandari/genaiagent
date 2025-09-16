"""
Example usage of the API Specification Writing Agent System
Demonstrates how to use the agentic system for generating API specifications
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


async def example_complete_workflow():
    """Example of complete API specification generation workflow."""
    print("🚀 Starting API Specification Generation Demo")
    print("=" * 60)
    
    # 1. Define user requirements
    print("\n📋 Step 1: Defining User Requirements")
    user_requirements = UserRequirement(
        id="customer_api_req_001",
        title="Customer Management API",
        description="""
        Design a REST API for managing customer information in an e-commerce platform.
        The API should support customer registration, profile management, order tracking,
        and customer support interactions.
        """,
        functional_requirements=[
            "Create new customer accounts with email validation",
            "Update customer profile information including address and preferences",
            "Retrieve customer details and order history",
            "Delete customer accounts with data retention compliance",
            "Search customers by various criteria (name, email, phone)",
            "Manage customer addresses with multiple address support",
            "Handle customer support tickets and interactions",
            "Track customer loyalty points and rewards"
        ],
        non_functional_requirements=[
            "API must respond within 200ms for read operations",
            "Support up to 10,000 concurrent users",
            "Implement rate limiting to prevent abuse",
            "Ensure GDPR compliance for data handling",
            "Use HTTPS for all communications",
            "Implement comprehensive logging for audit trails"
        ],
        business_entities=[
            "Customer", "Address", "Order", "SupportTicket", 
            "LoyaltyProgram", "CustomerPreferences"
        ],
        security_requirements=[
            "JWT-based authentication",
            "Role-based access control (Customer, Admin, Support)",
            "API key authentication for internal services",
            "Data encryption at rest and in transit"
        ],
        priority="high"
    )
    
    print(f"✓ Created requirements for: {user_requirements.title}")
    print(f"  - {len(user_requirements.functional_requirements)} functional requirements")
    print(f"  - {len(user_requirements.business_entities)} business entities")
    print(f"  - {len(user_requirements.security_requirements)} security requirements")
    
    # 2. Initialize agents
    print("\n🤖 Step 2: Initializing Agentic AI System")
    orchestrator = AgentOrchestrator()
    
    # Register agents
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
    
    # 3. Create workflow
    print("\n🔄 Step 3: Creating API Specification Workflow")
    
    # Define workflow steps
    workflow_steps = [
        {
            "objective": "analyze_api_requirements",
            "preferred_agent": "requirement_analysis_agent",
            "parameters": {"requirements": user_requirements.__dict__},
            "dependencies": []
        },
        {
            "objective": "design_api_structure",
            "preferred_agent": "api_design_agent",
            "parameters": {"project_name": user_requirements.title},
            "dependencies": ["workflow_api_spec_generation_step_1"]
        },
        {
            "objective": "generate_openapi_specification",
            "preferred_agent": "specification_writer_agent",
            "parameters": {
                "project_name": user_requirements.title,
                "format": SpecificationFormat.OPENAPI_YAML.value
            },
            "dependencies": ["workflow_api_spec_generation_step_2"]
        },
        {
            "objective": "validate_api_specification",
            "preferred_agent": "validation_agent",
            "parameters": {},
            "dependencies": ["workflow_api_spec_generation_step_3"]
        },
        {
            "objective": "generate_api_documentation",
            "preferred_agent": "documentation_agent",
            "parameters": {
                "project_name": user_requirements.title,
                "include_examples": True,
                "include_getting_started": True
            },
            "dependencies": ["workflow_api_spec_generation_step_4"]
        }
    ]
    
    workflow_id = await orchestrator.create_workflow(
        name="api_spec_generation",
        description="Complete API specification generation workflow",
        steps=workflow_steps
    )
    
    print(f"✓ Created workflow with {len(workflow_steps)} steps")
    
    # 4. Execute workflow
    print("\n⚡ Step 4: Executing Agentic Workflow")
    print("This may take a moment as agents collaborate...")
    
    try:
        results = await orchestrator.execute_workflow(workflow_id)
        
        if results.success:
            print("✅ Workflow completed successfully!")
            
            # 5. Process results
            print("\n📊 Step 5: Processing Results")
            
            # Get step results from the workflow data
            step_results = results.data if results.data else {}
            step_keys = list(step_results.keys())
            
            # Analysis results (first step)
            if len(step_keys) > 0:
                analysis_data = step_results[step_keys[0]] if step_keys[0] in step_results else {}
                if analysis_data:
                    print("✓ Requirements Analysis:")
                    if "entities" in analysis_data:
                        print(f"  - Identified {len(analysis_data['entities'])} entities")
                    if "endpoints" in analysis_data:
                        print(f"  - Proposed {len(analysis_data['endpoints'])} endpoints")
            
            # Design results (second step)
            if len(step_keys) > 1:
                design_data = step_results[step_keys[1]] if step_keys[1] in step_results else {}
                if design_data:
                    print("✓ API Design:")
                    if "paths" in design_data:
                        print(f"  - Designed {len(design_data['paths'])} API paths")
                    if "schemas" in design_data:
                        print(f"  - Created {len(design_data['schemas'])} data schemas")
            
            # Specification results (third step)
            if len(step_keys) > 2:
                spec_data = step_results[step_keys[2]] if step_keys[2] in step_results else {}
                if spec_data and isinstance(spec_data, str):
                    spec_content = spec_data
                    print("✓ Specification Generation:")
                    print(f"  - Generated {len(spec_content.split(chr(10)))} lines of OpenAPI spec")
                    
                    # Validation results (fourth step)
                    if len(step_keys) > 3:
                        validation_data = step_results[step_keys[3]] if step_keys[3] in step_results else {}
                        if validation_data:
                            is_valid = validation_data.get("is_valid", False)
                            quality_score = validation_data.get("quality_score", 0)
                            print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}")
                            print(f"  - Quality Score: {quality_score:.2f}/1.0")
                    
                    # Documentation results (fifth step)
                    if len(step_keys) > 4:
                        doc_data = step_results[step_keys[4]] if step_keys[4] in step_results else {}
                        if doc_data and isinstance(doc_data, str):
                            doc_content = doc_data
                            print(f"✓ Documentation: Generated {len(doc_content.split(chr(10)))} lines")
                
                # 6. Save results
                print("\\n💾 Step 6: Saving Results to API-requirements folder")
                file_manager = APISpecFileManager()
                
                try:
                    from src.models.search_models import (
                        APISpecification, APIInfo, SpecificationResult
                    )
                    
                    # Create specification result
                    api_info = APIInfo(
                        title=user_requirements.title,
                        version="1.0.0",
                        description=user_requirements.description
                    )
                    
                    specification = APISpecification(info=api_info)
                    
                    spec_result_obj = SpecificationResult(
                        specification=specification,
                        format=SpecificationFormat.OPENAPI_YAML,
                        content=spec_content,
                        documentation=doc_content if doc_result and doc_result.get("success") else "",
                        validation_result=None,  # Would need to parse validation_data
                        generation_metadata={
                            "generated_by": "WriteAPISpecAgent",
                            "workflow_id": workflow_id,
                            "analysis_confidence": analysis_result.get("confidence", 0) if analysis_result else 0,
                            "design_confidence": design_result.get("confidence", 0) if design_result else 0,
                            "validation_score": quality_score if validation_result else 0
                        }
                    )
                    
                    saved_path = file_manager.save_specification(spec_result_obj)
                    print(f"✅ Specification saved to: {saved_path}")
                    
                except Exception as e:
                    print(f"⚠️  Error saving specification: {str(e)}")
                    # Fallback: save raw content
                    import os
                    os.makedirs("./API-requirements", exist_ok=True)
                    fallback_path = "./API-requirements/customer_management_api.yml"
                    with open(fallback_path, 'w') as f:
                        f.write(spec_content)
                    print(f"✅ Specification saved to: {fallback_path}")
            
        else:
            print("❌ Workflow failed!")
            error_msg = results.error or "Unknown error"
            print(f"Error: {error_msg}")
            
    except Exception as e:
        print(f"❌ Workflow execution failed: {str(e)}")
    
    print("\\n🎉 Demo completed!")
    print("=" * 60)


async def example_individual_agent_usage():
    """Example of using individual agents."""
    print("\\n🔧 Individual Agent Usage Examples")
    print("-" * 40)
    
    # Example 1: Requirement Analysis Agent
    print("\\n1. Requirement Analysis Agent:")
    analysis_agent = RequirementAnalysisAgent()
    
    from src.agentic.base_agent import Goal
    
    analysis_goal = Goal(
        objective="analyze_api_requirements",
        parameters={
            "requirements": {
                "title": "Simple User API",
                "description": "Basic user management with CRUD operations",
                "functional_requirements": [
                    "Create user accounts",
                    "Update user profiles", 
                    "Delete user accounts",
                    "List all users"
                ]
            }
        }
    )
    
    try:
        result = await analysis_agent.execute_goal(analysis_goal)
        if result.success:
            print("✓ Analysis completed successfully")
            entities = result.data.get("entities", []) if result.data else []
            endpoints = result.data.get("endpoints", []) if result.data else []
            print(f"  - Entities: {', '.join(entities[:3])}...")
            print(f"  - Endpoints: {len(endpoints)} identified")
        else:
            print(f"✗ Analysis failed: {result.error}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Example 2: API Design Agent
    print("\\n2. API Design Agent:")
    design_agent = APIDesignAgent()
    
    design_goal = Goal(
        objective="design_api_structure",
        parameters={
            "project_name": "User Management API",
            "entities": ["User", "Profile"],
            "endpoints": [
                {"path": "/users", "method": "GET", "description": "List users"},
                {"path": "/users", "method": "POST", "description": "Create user"},
                {"path": "/users/{id}", "method": "GET", "description": "Get user"},
                {"path": "/users/{id}", "method": "PUT", "description": "Update user"},
                {"path": "/users/{id}", "method": "DELETE", "description": "Delete user"}
            ]
        }
    )
    
    try:
        result = await design_agent.execute_goal(design_goal)
        if result.success:
            print("✓ Design completed successfully")
            paths = result.data.get("paths", {}) if result.data else {}
            schemas = result.data.get("schemas", {}) if result.data else {}
            print(f"  - Paths designed: {len(paths)}")
            print(f"  - Schemas created: {len(schemas)}")
        else:
            print(f"✗ Design failed: {result.error}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def example_sync_usage():
    """Example of synchronous usage patterns."""
    print("\\n⚙️  Synchronous Usage Examples")
    print("-" * 40)
    
    # Example: Quick specification formatting
    from src.utils.spec_formatter import format_specification_quick
    
    simple_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Simple API",
            "version": "1.0.0",
            "description": "A simple example API"
        },
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {
                        "200": {
                            "description": "API is healthy"
                        }
                    }
                }
            }
        }
    }
    
    try:
        formatted_yaml = format_specification_quick(simple_spec, "yaml")
        print("✓ Quick YAML formatting:")
        print("  " + formatted_yaml.replace(chr(10), chr(10) + "  ")[:100] + "...")
        
        formatted_json = format_specification_quick(simple_spec, "json")
        print(f"✓ Quick JSON formatting: {len(formatted_json)} characters")
        
    except Exception as e:
        print(f"✗ Formatting error: {str(e)}")
    
    # Example: File manager usage
    print("\\n📁 File Manager Example:")
    try:
        file_manager = APISpecFileManager("./API-requirements")
        specs = file_manager.list_specifications()
        print(f"✓ Found {len(specs)} existing specifications")
        
        if specs:
            latest = specs[0]
            print(f"  - Latest: {latest['title']} v{latest['version']}")
            print(f"  - Modified: {latest['modified'].strftime('%Y-%m-%d %H:%M')}")
        
    except Exception as e:
        print(f"✗ File manager error: {str(e)}")


async def main():
    """Main demo function."""
    print("🎯 WriteAPISpecAgent Demo - Agentic AI API Specification Generation")
    print("=" * 80)
    
    # Run complete workflow example
    await example_complete_workflow()
    
    # Run individual agent examples
    await example_individual_agent_usage()
    
    # Run synchronous examples
    example_sync_usage()
    
    print("\\n✨ All demos completed successfully!")
    print("\\nNext steps:")
    print("- Check the ./API-requirements folder for generated specifications")
    print("- Modify the user requirements to generate different APIs") 
    print("- Explore individual agent capabilities")
    print("- Integrate with your own projects")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
