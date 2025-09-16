"""
API Specification Writing Agent System
Main orchestrator for generating API specifications based on user requirements
"""

import asyncio
import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from pathlib import Path

from src.agentic.base_agent import BaseAgent, Goal, AgentResult
from src.agentic.agent_orchestrator import AgentOrchestrator
from src.agentic.requirement_analysis_agent import RequirementAnalysisAgent
from src.agentic.api_design_agent import APIDesignAgent
from src.agentic.specification_writer_agent import SpecificationWriterAgent
from src.agentic.validation_agent import ValidationAgent
from src.agentic.documentation_agent import DocumentationAgent
from src.models.api_models import APISpecification, UserRequirement, SpecificationResult
from src.utils.spec_formatter import SpecificationFormatter
from src.utils.file_manager import APISpecFileManager


class APISpecWriterSystem:
    """
    Main system orchestrator for API specification generation.
    Coordinates multiple specialized agents to transform user requirements
    into complete, properly formatted API specifications.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the API Spec Writer System."""
        self.config = config or self._load_default_config()
        self.orchestrator = AgentOrchestrator()
        self.file_manager = APISpecFileManager()
        self.formatter = SpecificationFormatter()
        
        # Initialize specialized agents
        self._initialize_agents()
        
        # Output directory for API requirements
        self.output_dir = Path("/Users/niladrib/WorkingFolder/genaiagent/API-requirements")
        self.output_dir.mkdir(exist_ok=True)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration for the system."""
        return {
            "output_format": "yaml",  # yaml or json
            "specification_version": "3.0.0",  # OpenAPI version
            "include_examples": True,
            "include_documentation": True,
            "validate_spec": True,
            "generate_schemas": True,
            "default_response_codes": [200, 400, 401, 403, 404, 500],
            "max_endpoints_per_spec": 50,
            "include_security_schemes": True
        }
    
    def _initialize_agents(self):
        """Initialize all specialized agents."""
        self.requirement_agent = RequirementAnalysisAgent()
        self.design_agent = APIDesignAgent()
        self.specification_agent = SpecificationWriterAgent()
        self.validation_agent = ValidationAgent()
        self.documentation_agent = DocumentationAgent()
        
        # Register agents with orchestrator
        self.orchestrator.register_agent(self.requirement_agent)
        self.orchestrator.register_agent(self.design_agent)
        self.orchestrator.register_agent(self.specification_agent)
        self.orchestrator.register_agent(self.validation_agent)
        self.orchestrator.register_agent(self.documentation_agent)
    
    async def generate_api_specification(
        self,
        user_requirements: str,
        project_name: str,
        api_version: str = "1.0.0",
        output_format: str = "yaml"
    ) -> SpecificationResult:
        """
        Generate a complete API specification from user requirements.
        
        Args:
            user_requirements: Natural language description of API requirements
            project_name: Name of the project/API
            api_version: Version of the API being specified
            output_format: Output format (yaml or json)
        
        Returns:
            SpecificationResult containing the generated specification and metadata
        """
        print(f"🚀 Starting API specification generation for: {project_name}")
        
        try:
            # Step 1: Analyze user requirements
            print("📊 Step 1: Analyzing user requirements...")
            requirement_analysis = await self._analyze_requirements(
                user_requirements, project_name, api_version
            )
            
            if not requirement_analysis.success:
                return SpecificationResult(
                    success=False,
                    error=f"Requirements analysis failed: {requirement_analysis.error}",
                    specification=None
                )
            
            # Step 2: Design API structure
            print("🏗️ Step 2: Designing API structure...")
            api_design = await self._design_api_structure(
                requirement_analysis.data, project_name
            )
            
            if not api_design.success:
                return SpecificationResult(
                    success=False,
                    error=f"API design failed: {api_design.error}",
                    specification=None
                )
            
            # Step 3: Generate specification
            print("📝 Step 3: Generating API specification...")
            specification = await self._generate_specification(
                api_design.data, output_format
            )
            
            if not specification.success:
                return SpecificationResult(
                    success=False,
                    error=f"Specification generation failed: {specification.error}",
                    specification=None
                )
            
            # Step 4: Validate specification
            print("✅ Step 4: Validating specification...")
            validation = await self._validate_specification(
                specification.data
            )
            
            # Step 5: Generate documentation
            print("📚 Step 5: Generating documentation...")
            documentation = await self._generate_documentation(
                specification.data, project_name
            )
            
            # Step 6: Save to file
            print("💾 Step 6: Saving specification to file...")
            file_path = await self._save_specification(
                specification.data,
                project_name,
                output_format,
                documentation.data if documentation.success else None
            )
            
            # Compile final result
            result = SpecificationResult(
                success=True,
                specification=specification.data,
                file_path=str(file_path),
                validation_results=validation.data if validation.success else None,
                documentation=documentation.data if documentation.success else None,
                metadata={
                    "project_name": project_name,
                    "api_version": api_version,
                    "output_format": output_format,
                    "generated_at": datetime.now().isoformat(),
                    "requirements_analysis": requirement_analysis.metadata,
                    "api_design": api_design.metadata,
                    "validation_passed": validation.success
                }
            )
            
            print(f"✅ API specification generation completed!")
            print(f"📄 Specification saved to: {file_path}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during API specification generation: {str(e)}")
            return SpecificationResult(
                success=False,
                error=str(e),
                specification=None
            )
    
    async def _analyze_requirements(
        self, 
        requirements: str, 
        project_name: str, 
        api_version: str
    ) -> AgentResult:
        """Analyze user requirements to extract API needs."""
        goal = Goal(
            objective="analyze_api_requirements",
            parameters={
                "requirements": requirements,
                "project_name": project_name,
                "api_version": api_version,
                "extract_entities": True,
                "identify_endpoints": True,
                "determine_data_models": True
            },
            priority="high"
        )
        
        return await self.requirement_agent.execute_goal(goal)
    
    async def _design_api_structure(
        self, 
        analyzed_requirements: Dict[str, Any], 
        project_name: str
    ) -> AgentResult:
        """Design the overall API structure and architecture."""
        goal = Goal(
            objective="design_api_structure",
            parameters={
                "requirements": analyzed_requirements,
                "project_name": project_name,
                "include_security": self.config.get("include_security_schemes", True),
                "max_endpoints": self.config.get("max_endpoints_per_spec", 50),
                "response_codes": self.config.get("default_response_codes", []),
                "generate_schemas": self.config.get("generate_schemas", True)
            },
            priority="high"
        )
        
        return await self.design_agent.execute_goal(goal)
    
    async def _generate_specification(
        self, 
        api_design: Dict[str, Any], 
        output_format: str
    ) -> AgentResult:
        """Generate the actual API specification document."""
        goal = Goal(
            objective="generate_api_specification",
            parameters={
                "api_design": api_design,
                "output_format": output_format,
                "openapi_version": self.config.get("specification_version", "3.0.0"),
                "include_examples": self.config.get("include_examples", True),
                "include_descriptions": True,
                "follow_standards": True
            },
            priority="high"
        )
        
        return await self.specification_agent.execute_goal(goal)
    
    async def _validate_specification(
        self, 
        specification: Dict[str, Any]
    ) -> AgentResult:
        """Validate the generated specification for correctness."""
        goal = Goal(
            objective="validate_api_specification",
            parameters={
                "specification": specification,
                "check_syntax": True,
                "check_completeness": True,
                "check_standards_compliance": True,
                "validate_schemas": True,
                "check_security": True
            },
            priority="medium"
        )
        
        return await self.validation_agent.execute_goal(goal)
    
    async def _generate_documentation(
        self, 
        specification: Dict[str, Any], 
        project_name: str
    ) -> AgentResult:
        """Generate comprehensive documentation for the API."""
        goal = Goal(
            objective="generate_api_documentation",
            parameters={
                "specification": specification,
                "project_name": project_name,
                "include_examples": True,
                "include_getting_started": True,
                "include_authentication": True,
                "include_error_handling": True,
                "format": "markdown"
            },
            priority="low"
        )
        
        return await self.documentation_agent.execute_goal(goal)
    
    async def _save_specification(
        self,
        specification: Dict[str, Any],
        project_name: str,
        output_format: str,
        documentation: Optional[str] = None
    ) -> Path:
        """Save the specification to the API-requirements folder."""
        
        # Create filename
        safe_name = project_name.lower().replace(" ", "_").replace("-", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_spec.{output_format}"
        
        file_path = self.output_dir / filename
        
        # Save specification
        if output_format.lower() == "yaml":
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(specification, f, default_flow_style=False, indent=2)
        else:  # json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(specification, f, indent=2, ensure_ascii=False)
        
        # Save documentation if provided
        if documentation:
            doc_path = self.output_dir / f"{safe_name}_documentation.md"
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(documentation)
        
        return file_path
    
    async def analyze_existing_specifications(self) -> Dict[str, Any]:
        """Analyze existing specifications in the API-requirements folder."""
        print("📊 Analyzing existing API specifications...")
        
        existing_specs = []
        spec_files = list(self.output_dir.glob("*.yml")) + list(self.output_dir.glob("*.yaml")) + list(self.output_dir.glob("*.json"))
        
        for spec_file in spec_files:
            try:
                if spec_file.suffix.lower() in ['.yml', '.yaml']:
                    with open(spec_file, 'r', encoding='utf-8') as f:
                        spec_data = yaml.safe_load(f)
                else:
                    with open(spec_file, 'r', encoding='utf-8') as f:
                        spec_data = json.load(f)
                
                # Extract metadata
                spec_info = {
                    "filename": spec_file.name,
                    "title": spec_data.get("info", {}).get("title", "Unknown"),
                    "version": spec_data.get("info", {}).get("version", "Unknown"),
                    "description": spec_data.get("info", {}).get("description", ""),
                    "endpoints": len(spec_data.get("paths", {})),
                    "schemas": len(spec_data.get("components", {}).get("schemas", {})),
                    "created": spec_file.stat().st_mtime
                }
                
                existing_specs.append(spec_info)
                
            except Exception as e:
                print(f"⚠️ Error reading {spec_file.name}: {str(e)}")
        
        return {
            "total_specifications": len(existing_specs),
            "specifications": sorted(existing_specs, key=lambda x: x["created"], reverse=True),
            "analysis_date": datetime.now().isoformat()
        }
    
    async def enhance_existing_specification(
        self,
        spec_filename: str,
        enhancement_requirements: str
    ) -> SpecificationResult:
        """Enhance an existing API specification with new requirements."""
        print(f"🔧 Enhancing existing specification: {spec_filename}")
        
        spec_path = self.output_dir / spec_filename
        
        if not spec_path.exists():
            return SpecificationResult(
                success=False,
                error=f"Specification file not found: {spec_filename}",
                specification=None
            )
        
        try:
            # Load existing specification
            if spec_path.suffix.lower() in ['.yml', '.yaml']:
                with open(spec_path, 'r', encoding='utf-8') as f:
                    existing_spec = yaml.safe_load(f)
            else:
                with open(spec_path, 'r', encoding='utf-8') as f:
                    existing_spec = json.load(f)
            
            # Analyze enhancement requirements
            enhancement_goal = Goal(
                objective="enhance_existing_specification",
                parameters={
                    "existing_specification": existing_spec,
                    "enhancement_requirements": enhancement_requirements,
                    "preserve_existing": True,
                    "add_new_endpoints": True,
                    "update_schemas": True
                },
                priority="high"
            )
            
            enhancement_result = await self.design_agent.execute_goal(enhancement_goal)
            
            if not enhancement_result.success:
                return SpecificationResult(
                    success=False,
                    error=f"Enhancement failed: {enhancement_result.error}",
                    specification=None
                )
            
            # Generate enhanced specification
            enhanced_spec = await self._generate_specification(
                enhancement_result.data,
                spec_path.suffix[1:]  # Remove the dot
            )
            
            if enhanced_spec.success:
                # Save enhanced specification
                project_name = existing_spec.get("info", {}).get("title", "Enhanced API")
                file_path = await self._save_specification(
                    enhanced_spec.data,
                    f"{project_name}_enhanced",
                    spec_path.suffix[1:]
                )
                
                return SpecificationResult(
                    success=True,
                    specification=enhanced_spec.data,
                    file_path=str(file_path),
                    metadata={
                        "original_file": spec_filename,
                        "enhanced_at": datetime.now().isoformat(),
                        "enhancement_requirements": enhancement_requirements
                    }
                )
            else:
                return SpecificationResult(
                    success=False,
                    error=f"Failed to generate enhanced specification: {enhanced_spec.error}",
                    specification=None
                )
                
        except Exception as e:
            return SpecificationResult(
                success=False,
                error=f"Error enhancing specification: {str(e)}",
                specification=None
            )
    
    async def close(self):
        """Clean up resources."""
        await self.orchestrator.shutdown()


# Convenience functions for common use cases
async def generate_api_spec_from_requirements(
    requirements: str,
    project_name: str,
    api_version: str = "1.0.0",
    output_format: str = "yaml"
) -> SpecificationResult:
    """
    Convenience function to generate API specification from requirements.
    """
    system = APISpecWriterSystem()
    try:
        result = await system.generate_api_specification(
            user_requirements=requirements,
            project_name=project_name,
            api_version=api_version,
            output_format=output_format
        )
        return result
    finally:
        await system.close()


async def analyze_existing_api_specs() -> Dict[str, Any]:
    """
    Convenience function to analyze existing API specifications.
    """
    system = APISpecWriterSystem()
    try:
        result = await system.analyze_existing_specifications()
        return result
    finally:
        await system.close()


if __name__ == "__main__":
    # Example usage
    async def main():
        system = APISpecWriterSystem()
        
        try:
            # Example requirements
            requirements = """
            I need an API for a customer management system that can:
            1. Create, read, update, and delete customers
            2. Manage customer addresses and contact information
            3. Handle customer authentication and authorization
            4. Support customer search and filtering
            5. Manage customer orders and order history
            6. Provide customer analytics and reporting
            
            The API should be RESTful, use JSON for data exchange,
            include proper error handling, and support pagination.
            """
            
            result = await system.generate_api_specification(
                user_requirements=requirements,
                project_name="Customer Management API",
                api_version="1.0.0",
                output_format="yaml"
            )
            
            if result.success:
                print(f"✅ API specification generated successfully!")
                print(f"📄 File: {result.file_path}")
                print(f"📊 Endpoints: {len(result.specification.get('paths', {}))}")
                print(f"🛡️ Validation passed: {result.metadata.get('validation_passed', False)}")
            else:
                print(f"❌ Failed to generate specification: {result.error}")
                
        finally:
            await system.close()
    
    asyncio.run(main())
