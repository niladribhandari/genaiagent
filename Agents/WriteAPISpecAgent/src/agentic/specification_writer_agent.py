"""
Specification Writer Agent for API Specification Writing System
Generates the actual OpenAPI specification document from API design
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import OrderedDict

from .base_agent import SpecializedAgent, Goal, AgentResult, AgentCapability, create_success_result, create_error_result


class SpecificationWriterAgent(SpecializedAgent):
    """
    Specialized agent for writing OpenAPI specifications.
    
    This agent takes API design and generates properly formatted
    OpenAPI specification documents with:
    - Correct OpenAPI structure
    - Complete documentation
    - Valid examples
    - Proper formatting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Specification Writer Agent."""
        super().__init__(
            name="specification_writer_agent",
            capabilities=[
                AgentCapability.SPECIFICATION_WRITING,
                AgentCapability.YAML_GENERATION,
                AgentCapability.JSON_GENERATION,
                AgentCapability.FORMAT_CONVERSION,
                AgentCapability.DOCUMENTATION
            ],
            description="Generates properly formatted OpenAPI specifications",
            config=config or {},
            specialization="specification_writing"
        )
        
        # OpenAPI specification templates and patterns
        self.add_knowledge("openapi_structure", {
            "required_fields": ["openapi", "info", "paths"],
            "optional_fields": ["servers", "components", "security", "tags", "externalDocs"],
            "info_required": ["title", "version"],
            "info_optional": ["description", "termsOfService", "contact", "license"]
        })
        
        self.add_knowledge("openapi_versions", {
            "3.0.0": "OpenAPI 3.0.0",
            "3.0.1": "OpenAPI 3.0.1", 
            "3.0.2": "OpenAPI 3.0.2",
            "3.0.3": "OpenAPI 3.0.3",
            "3.1.0": "OpenAPI 3.1.0"
        })
        
        self.add_knowledge("content_types", {
            "json": "application/json",
            "xml": "application/xml",
            "form": "application/x-www-form-urlencoded",
            "multipart": "multipart/form-data",
            "text": "text/plain"
        })
    
    async def execute_goal(self, goal: Goal) -> AgentResult:
        """Execute specification writing goals."""
        try:
            objective = goal.objective.lower()
            
            if "generate_api_specification" in objective or "generate_openapi_specification" in objective:
                return await self._generate_api_specification(goal)
            elif "format_specification" in objective:
                return await self._format_specification(goal)
            elif "validate_structure" in objective:
                return await self._validate_structure(goal)
            elif "add_documentation" in objective:
                return await self._add_documentation(goal)
            else:
                return create_error_result(f"Unknown objective: {goal.objective}")
                
        except Exception as e:
            self.logger.error(f"Error executing goal {goal.objective}: {str(e)}")
            return create_error_result(str(e))
    
    async def _generate_api_specification(self, goal: Goal) -> AgentResult:
        """Generate complete OpenAPI specification from API design."""
        # First check parameters, then context for api_design from previous steps
        api_design = goal.parameters.get("api_design", {})
        if not api_design:
            # Check context for API design from previous workflow steps
            for step_id, step_data in goal.context.items():
                if isinstance(step_data, dict) and "api_design" in step_data:
                    api_design = step_data["api_design"]
                    break
                # Also check if the step data itself is an API design
                elif isinstance(step_data, dict) and any(key in step_data for key in ["paths", "components", "info"]):
                    api_design = step_data
                    break
        
        output_format = goal.parameters.get("output_format", "yaml")
        openapi_version = goal.parameters.get("openapi_version", "3.0.3")
        include_examples = goal.parameters.get("include_examples", True)
        include_descriptions = goal.parameters.get("include_descriptions", True)
        
        if not api_design:
            return create_error_result("No API design provided for specification generation")
        
        self.logger.info(f"Generating OpenAPI {openapi_version} specification in {output_format} format")
        self.logger.info(f"Using API design: {type(api_design)} with keys: {list(api_design.keys()) if isinstance(api_design, dict) else 'non-dict'}")
        
        self.logger.info(f"Generating OpenAPI {openapi_version} specification in {output_format} format")
        
        # Build the OpenAPI specification
        specification = OrderedDict()
        
        # Required fields
        specification["openapi"] = openapi_version
        specification["info"] = self._build_info_section(api_design, include_descriptions)
        
        # Optional top-level fields
        if "servers" in api_design:
            specification["servers"] = api_design["servers"]
        
        # Paths (required)
        specification["paths"] = self._build_paths_section(
            api_design.get("paths", {}), 
            include_examples, 
            include_descriptions
        )
        
        # Components
        if "components" in api_design:
            specification["components"] = self._build_components_section(
                api_design["components"], 
                include_examples
            )
        
        # Security
        if "security" in api_design:
            specification["security"] = api_design["security"]
        
        # Tags
        if "tags" in api_design:
            specification["tags"] = api_design["tags"]
        
        # External docs
        if "external_docs" in api_design:
            specification["externalDocs"] = api_design["external_docs"]
        
        # Add metadata
        metadata = {
            "generation_timestamp": datetime.now().isoformat(),
            "openapi_version": openapi_version,
            "output_format": output_format,
            "total_paths": len(specification["paths"]),
            "total_operations": self._count_operations(specification["paths"]),
            "has_components": "components" in specification,
            "has_security": "security" in specification,
            "specification_size": len(str(specification))
        }
        
        self.logger.info(
            f"Specification generated: {metadata['total_paths']} paths, "
            f"{metadata['total_operations']} operations"
        )
        
        return create_success_result(specification, metadata, confidence=0.95)
    
    def _build_info_section(self, api_design: Dict[str, Any], include_descriptions: bool) -> Dict[str, Any]:
        """Build the info section of the OpenAPI specification."""
        info = api_design.get("info", {})
        
        # Required fields
        info_section = OrderedDict()
        info_section["title"] = info.get("title", "API Specification")
        info_section["version"] = info.get("version", "1.0.0")
        
        # Optional fields
        if include_descriptions and "description" in info:
            info_section["description"] = info["description"]
        
        if "termsOfService" in info:
            info_section["termsOfService"] = info["termsOfService"]
        
        if "contact" in info:
            info_section["contact"] = info["contact"]
        
        if "license" in info:
            info_section["license"] = info["license"]
        
        return info_section
    
    def _build_paths_section(
        self, 
        paths: Dict[str, Any], 
        include_examples: bool, 
        include_descriptions: bool
    ) -> Dict[str, Any]:
        """Build the paths section of the OpenAPI specification."""
        paths_section = OrderedDict()
        
        # Sort paths for consistent output
        for path in sorted(paths.keys()):
            path_item = OrderedDict()
            path_methods = paths[path]
            
            # Sort HTTP methods in a logical order
            method_order = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
            sorted_methods = sorted(
                path_methods.keys(), 
                key=lambda x: method_order.index(x) if x in method_order else 999
            )
            
            for method in sorted_methods:
                operation = path_methods[method]
                path_item[method] = self._build_operation(operation, include_examples, include_descriptions)
            
            paths_section[path] = path_item
        
        return paths_section
    
    def _build_operation(
        self, 
        operation: Dict[str, Any], 
        include_examples: bool, 
        include_descriptions: bool
    ) -> Dict[str, Any]:
        """Build an operation specification."""
        operation_spec = OrderedDict()
        
        # Basic operation fields
        if "summary" in operation:
            operation_spec["summary"] = operation["summary"]
        
        if include_descriptions and "description" in operation:
            operation_spec["description"] = operation["description"]
        
        if "operationId" in operation:
            operation_spec["operationId"] = operation["operationId"]
        
        if "tags" in operation:
            operation_spec["tags"] = operation["tags"]
        
        # Parameters
        if "parameters" in operation:
            operation_spec["parameters"] = self._build_parameters(operation["parameters"])
        
        # Request body
        if "requestBody" in operation:
            operation_spec["requestBody"] = self._build_request_body(
                operation["requestBody"], 
                include_examples
            )
        
        # Responses (required)
        operation_spec["responses"] = self._build_responses(
            operation.get("responses", {}), 
            include_examples
        )
        
        # Security
        if "security" in operation:
            operation_spec["security"] = operation["security"]
        
        # Deprecated
        if operation.get("deprecated", False):
            operation_spec["deprecated"] = True
        
        return operation_spec
    
    def _build_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build parameters specification."""
        params_spec = []
        
        for param in parameters:
            param_spec = OrderedDict()
            
            # Required fields
            param_spec["name"] = param["name"]
            param_spec["in"] = param["in"]
            
            # Optional fields
            if "description" in param:
                param_spec["description"] = param["description"]
            
            if "required" in param:
                param_spec["required"] = param["required"]
            
            if "schema" in param:
                param_spec["schema"] = param["schema"]
            
            if "example" in param:
                param_spec["example"] = param["example"]
            
            params_spec.append(param_spec)
        
        return params_spec
    
    def _build_request_body(
        self, 
        request_body: Dict[str, Any], 
        include_examples: bool
    ) -> Dict[str, Any]:
        """Build request body specification."""
        body_spec = OrderedDict()
        
        if "description" in request_body:
            body_spec["description"] = request_body["description"]
        
        if "required" in request_body:
            body_spec["required"] = request_body["required"]
        
        if "content" in request_body:
            body_spec["content"] = self._build_content(request_body["content"], include_examples)
        
        return body_spec
    
    def _build_content(self, content: Dict[str, Any], include_examples: bool) -> Dict[str, Any]:
        """Build content specification."""
        content_spec = OrderedDict()
        
        for media_type, media_spec in content.items():
            media_content = OrderedDict()
            
            if "schema" in media_spec:
                media_content["schema"] = media_spec["schema"]
            
            if include_examples and "example" in media_spec:
                media_content["example"] = media_spec["example"]
            
            if include_examples and "examples" in media_spec:
                media_content["examples"] = media_spec["examples"]
            
            content_spec[media_type] = media_content
        
        return content_spec
    
    def _build_responses(
        self, 
        responses: Dict[str, Any], 
        include_examples: bool
    ) -> Dict[str, Any]:
        """Build responses specification."""
        responses_spec = OrderedDict()
        
        # Sort response codes
        sorted_codes = sorted(responses.keys(), key=lambda x: (int(x) if x.isdigit() else 999, x))
        
        for code in sorted_codes:
            response = responses[code]
            
            if isinstance(response, dict) and "$ref" in response:
                # Reference to component
                responses_spec[code] = response
            else:
                # Full response specification
                response_spec = OrderedDict()
                
                if "description" in response:
                    response_spec["description"] = response["description"]
                
                if "headers" in response:
                    response_spec["headers"] = response["headers"]
                
                if "content" in response:
                    response_spec["content"] = self._build_content(response["content"], include_examples)
                
                responses_spec[code] = response_spec
        
        return responses_spec
    
    def _build_components_section(
        self, 
        components: Dict[str, Any], 
        include_examples: bool
    ) -> Dict[str, Any]:
        """Build the components section."""
        components_spec = OrderedDict()
        
        # Order components sections consistently
        section_order = [
            "schemas", "responses", "parameters", "examples", 
            "requestBodies", "headers", "securitySchemes", "links", "callbacks"
        ]
        
        for section in section_order:
            if section in components:
                if section == "schemas":
                    components_spec[section] = self._build_schemas(components[section])
                elif section == "examples" and include_examples:
                    components_spec[section] = components[section]
                elif section != "examples":
                    components_spec[section] = components[section]
        
        return components_spec
    
    def _build_schemas(self, schemas: Dict[str, Any]) -> Dict[str, Any]:
        """Build schemas with proper ordering."""
        schemas_spec = OrderedDict()
        
        # Sort schemas alphabetically
        for schema_name in sorted(schemas.keys()):
            schema = schemas[schema_name]
            schema_spec = OrderedDict()
            
            # Order schema fields consistently
            field_order = ["type", "description", "properties", "required", "example", "items", "additionalProperties"]
            
            for field in field_order:
                if field in schema:
                    if field == "properties":
                        # Sort properties alphabetically
                        properties = OrderedDict()
                        for prop_name in sorted(schema["properties"].keys()):
                            properties[prop_name] = schema["properties"][prop_name]
                        schema_spec[field] = properties
                    else:
                        schema_spec[field] = schema[field]
            
            # Add any remaining fields not in the order
            for field, value in schema.items():
                if field not in schema_spec:
                    schema_spec[field] = value
            
            schemas_spec[schema_name] = schema_spec
        
        return schemas_spec
    
    def _count_operations(self, paths: Dict[str, Any]) -> int:
        """Count total operations in paths."""
        count = 0
        for path_methods in paths.values():
            count += len(path_methods)
        return count
    
    async def _format_specification(self, goal: Goal) -> AgentResult:
        """Format specification in requested format."""
        specification = goal.parameters.get("specification", {})
        output_format = goal.parameters.get("format", "yaml")
        
        if not specification:
            return create_error_result("No specification provided for formatting")
        
        try:
            if output_format.lower() == "yaml":
                formatted_spec = yaml.dump(
                    specification, 
                    default_flow_style=False, 
                    indent=2,
                    sort_keys=False,
                    allow_unicode=True
                )
            elif output_format.lower() == "json":
                formatted_spec = json.dumps(
                    specification, 
                    indent=2, 
                    ensure_ascii=False
                )
            else:
                return create_error_result(f"Unsupported format: {output_format}")
            
            metadata = {
                "format": output_format,
                "size": len(formatted_spec),
                "lines": len(formatted_spec.split('\n'))
            }
            
            return create_success_result(formatted_spec, metadata)
            
        except Exception as e:
            return create_error_result(f"Error formatting specification: {str(e)}")
    
    async def _validate_structure(self, goal: Goal) -> AgentResult:
        """Validate OpenAPI specification structure."""
        specification = goal.parameters.get("specification", {})
        
        if not specification:
            return create_error_result("No specification provided for validation")
        
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check required top-level fields
        required_fields = self.get_knowledge("openapi_structure", {}).get("required_fields", [])
        for field in required_fields:
            if field not in specification:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["is_valid"] = False
        
        # Check info section
        if "info" in specification:
            info_required = self.get_knowledge("openapi_structure", {}).get("info_required", [])
            for field in info_required:
                if field not in specification["info"]:
                    validation_results["errors"].append(f"Missing required info field: {field}")
                    validation_results["is_valid"] = False
        
        # Check OpenAPI version
        if "openapi" in specification:
            version = specification["openapi"]
            supported_versions = self.get_knowledge("openapi_versions", {})
            if version not in supported_versions:
                validation_results["warnings"].append(f"Unsupported OpenAPI version: {version}")
        
        # Check paths structure
        if "paths" in specification:
            paths = specification["paths"]
            if not paths:
                validation_results["warnings"].append("No paths defined in specification")
            else:
                validation_results["info"].append(f"Found {len(paths)} paths")
                
                # Count operations
                total_operations = self._count_operations(paths)
                validation_results["info"].append(f"Found {total_operations} operations")
        
        # Check components
        if "components" in specification:
            components = specification["components"]
            if "schemas" in components:
                validation_results["info"].append(f"Found {len(components['schemas'])} schemas")
        
        metadata = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_errors": len(validation_results["errors"]),
            "total_warnings": len(validation_results["warnings"])
        }
        
        return create_success_result(validation_results, metadata)
    
    async def _add_documentation(self, goal: Goal) -> AgentResult:
        """Add comprehensive documentation to specification."""
        specification = goal.parameters.get("specification", {})
        documentation_level = goal.parameters.get("level", "standard")  # minimal, standard, comprehensive
        
        if not specification:
            return create_error_result("No specification provided for documentation")
        
        # Create a copy to avoid modifying the original
        documented_spec = specification.copy()
        
        # Add documentation based on level
        if documentation_level in ["standard", "comprehensive"]:
            # Add descriptions to operations that don't have them
            if "paths" in documented_spec:
                for path, path_item in documented_spec["paths"].items():
                    for method, operation in path_item.items():
                        if "description" not in operation:
                            operation["description"] = self._generate_operation_description(
                                method, path, operation
                            )
        
        if documentation_level == "comprehensive":
            # Add detailed descriptions and examples
            self._add_comprehensive_documentation(documented_spec)
        
        metadata = {
            "documentation_level": documentation_level,
            "documentation_timestamp": datetime.now().isoformat()
        }
        
        return create_success_result(documented_spec, metadata)
    
    def _generate_operation_description(
        self, 
        method: str, 
        path: str, 
        operation: Dict[str, Any]
    ) -> str:
        """Generate a description for an operation."""
        summary = operation.get("summary", "")
        
        if summary:
            return f"{summary}. This endpoint allows you to {method.upper()} resources at {path}."
        else:
            return f"Perform {method.upper()} operation on {path}."
    
    def _add_comprehensive_documentation(self, specification: Dict[str, Any]):
        """Add comprehensive documentation to specification."""
        # Add detailed info description
        if "info" in specification and "description" not in specification["info"]:
            specification["info"]["description"] = (
                "This API provides comprehensive access to system resources. "
                "It follows RESTful principles and uses standard HTTP methods and status codes."
            )
        
        # Add server descriptions
        if "servers" in specification:
            for server in specification["servers"]:
                if "description" not in server:
                    url = server.get("url", "")
                    if "localhost" in url:
                        server["description"] = "Development server"
                    elif "staging" in url:
                        server["description"] = "Staging server"
                    else:
                        server["description"] = "Production server"
        
        # Add parameter descriptions
        if "paths" in specification:
            for path_item in specification["paths"].values():
                for operation in path_item.values():
                    if "parameters" in operation:
                        for param in operation["parameters"]:
                            if "description" not in param:
                                param["description"] = f"The {param['name']} parameter"

    def _custom_goal_check(self, goal: Goal) -> bool:
        """Custom goal checking for Specification Writer Agent."""
        objective = goal.objective.lower()
        
        # Handle specific goal patterns that this agent can execute
        writing_patterns = [
            "generate_openapi_specification",
            "write_specification",
            "create_specification",
            "generate_spec",
            "write_openapi",
            "create_openapi",
            "specification_writing"
        ]
        
        return any(pattern in objective for pattern in writing_patterns)
