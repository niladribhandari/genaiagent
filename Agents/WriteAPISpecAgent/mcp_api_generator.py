#!/usr/bin/env python3
"""
MCP API Generator - Bridge between MCP server and WriteAPISpecAgent
This script provides a command-line interface that works with the MCP server
while using the fixed workflow system.
"""

import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Import the working components
from src.agentic.agent_orchestrator import AgentOrchestrator
from src.agentic.requirement_analysis_agent import RequirementAnalysisAgent
from src.agentic.api_design_agent import APIDesignAgent
from src.agentic.specification_writer_agent import SpecificationWriterAgent
from src.agentic.validation_agent import ValidationAgent
from src.agentic.documentation_agent import DocumentationAgent
from src.models.search_models import SpecificationFormat
from src.utils.file_manager import APISpecFileManager


async def generate_api_specification(requirements: str, project_name: str, technology: str = "openapi", output_format: str = "yaml"):
    """Generate API specification using the working agentic workflow."""
    
    try:
        # 1. Create orchestrator and register agents
        orchestrator = AgentOrchestrator()
        
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
        
        # 2. Define workflow steps with proper dependencies
        workflow_steps = [
            {
                "objective": "analyze_api_requirements",
                "preferred_agent": "requirement_analysis_agent",
                "parameters": {
                    "requirements": requirements
                },
                "dependencies": []  # No dependencies for first step
            },
            {
                "objective": "design_api_structure",
                "preferred_agent": "api_design_agent",
                "parameters": {"project_name": project_name},
                "dependencies": [0]  # Depends on step 0
            },
            {
                "objective": "generate_openapi_specification",
                "preferred_agent": "specification_writer_agent",
                "parameters": {
                    "project_name": project_name,
                    "format": SpecificationFormat.OPENAPI_YAML.value,
                    "output_format": output_format
                },
                "dependencies": ["prev"]  # Depends on previous step
            },
            {
                "objective": "validate_api_specification",
                "preferred_agent": "validation_agent",
                "parameters": {},
                "dependencies": ["prev"]  # Depends on previous step
            },
            {
                "objective": "generate_documentation",
                "preferred_agent": "documentation_agent",
                "parameters": {"doc_format": "markdown"},
                "dependencies": ["prev"]  # Depends on previous step
            }
        ]
        
        # 3. Create and execute workflow
        workflow_id = await orchestrator.create_workflow(
            name=f"API Spec Generation - {project_name}",
            description=f"Generate API specification for {project_name}",
            steps=workflow_steps
        )
        
        # 4. Execute workflow
        result = await orchestrator.execute_workflow(workflow_id)
        
        if result.success:
            # Extract the results from each step
            step_results = result.data
            
            # Get the final specification from step 3
            specification = None
            documentation = None
            validation_report = None
            
            for step_id, step_data in step_results.items():
                if "step_3" in step_id:  # Specification step
                    specification = step_data
                elif "step_4" in step_id:  # Validation step
                    validation_report = step_data
                elif "step_5" in step_id:  # Documentation step
                    documentation = step_data
            
            # Save the specification to file
            if specification:
                from src.utils.file_manager import save_specification_quick
                from src.utils.custom_spec_formatter import convert_openapi_to_custom_format, format_as_yaml
                
                # Convert OpenAPI specification to custom format
                technology_mapping = {
                    "java_springboot": "java_springboot",
                    "nodejs_express": "nodejs_express", 
                    "dotnet_webapi": "dotnet_webapi",
                    "spring boot": "java_springboot",
                    "express": "nodejs_express",
                    "asp.net": "dotnet_webapi"
                }
                
                tech_key = technology_mapping.get(technology.lower(), "java_springboot")
                
                # Convert to custom format
                custom_spec = convert_openapi_to_custom_format(
                    openapi_spec=specification,
                    requirements=requirements,
                    project_name=project_name,
                    technology=tech_key
                )
                
                # Format as YAML
                spec_content = format_as_yaml(custom_spec)
                
                # Generate safe filename
                safe_name = "".join(c for c in project_name.lower().replace(" ", "_") if c.isalnum() or c == "_")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{safe_name}_{timestamp}.yml"
                
                spec_path = save_specification_quick(
                    content=spec_content,
                    filename=filename,
                    directory="../API-requirements"
                )
                
                # Return structured result
                return {
                    "success": True,
                    "data": {
                        "specification": custom_spec,  # Return custom format instead of OpenAPI
                        "openapi_specification": specification,  # Keep original OpenAPI for reference
                        "specification_file": str(spec_path),
                        "documentation": documentation,
                        "validation_report": validation_report,
                        "workflow_id": workflow_id,
                        "project_name": project_name,
                        "requirements": requirements,
                        "technology": tech_key,
                        "generated_at": datetime.now().isoformat()
                    },
                    "metadata": {
                        "generator": "WriteAPISpecAgent_MCP",
                        "version": "1.0.0",
                        "workflow_steps": len(workflow_steps),
                        "output_format": "custom_yaml"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No specification generated in workflow",
                    "data": step_results
                }
        else:
            return {
                "success": False,
                "error": f"Workflow failed: {result.error}",
                "metadata": {
                    "workflow_id": workflow_id
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"API generation failed: {str(e)}",
            "metadata": {
                "generator": "WriteAPISpecAgent_MCP",
                "version": "1.0.0"
            }
        }


def main():
    """Main entry point for MCP integration."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "No arguments provided. Expected JSON argument."
        }))
        sys.exit(1)
    
    try:
        # Parse JSON arguments
        args = json.loads(sys.argv[1])
        
        requirements = args.get("requirements", "Simple API")
        project_name = args.get("project_name", "Generated API")
        technology = args.get("technology", "openapi")
        output_format = args.get("output_format", "yaml")
        
        # Run the async workflow
        result = asyncio.run(generate_api_specification(
            requirements=requirements,
            project_name=project_name,
            technology=technology,
            output_format=output_format
        ))
        
        # Output JSON result
        print(json.dumps(result, indent=2, default=str))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON arguments: {str(e)}"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
