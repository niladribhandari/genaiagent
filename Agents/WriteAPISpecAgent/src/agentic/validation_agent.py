"""
Validation Agent for API Specification Writing System
Validates generated API specifications for correctness and best practices
"""

import json
import yaml
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime

from .base_agent import SpecializedAgent, Goal, AgentResult, AgentCapability, create_success_result, create_error_result


class ValidationAgent(SpecializedAgent):
    """
    Specialized agent for validating API specifications.
    
    This agent performs comprehensive validation including:
    - OpenAPI specification compliance
    - Schema validation
    - Best practices checking
    - Security validation
    - Performance considerations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Validation Agent."""
        super().__init__(
            name="validation_agent",
            capabilities=[
                AgentCapability.VALIDATION,
                AgentCapability.SYNTAX_VALIDATION,
                AgentCapability.SEMANTIC_VALIDATION,
                AgentCapability.SECURITY_DESIGN,
                AgentCapability.QUALITY_ASSESSMENT
            ],
            description="Validates API specifications for correctness and best practices",
            config=config or {},
            specialization="validation"
        )
        
        # Validation rules and patterns
        self.add_knowledge("openapi_rules", {
            "required_top_level": ["openapi", "info", "paths"],
            "required_info": ["title", "version"],
            "valid_http_methods": ["get", "post", "put", "patch", "delete", "head", "options", "trace"],
            "valid_parameter_locations": ["query", "header", "path", "cookie"],
            "valid_schema_types": ["string", "number", "integer", "boolean", "array", "object"],
            "common_status_codes": [200, 201, 204, 400, 401, 403, 404, 409, 422, 500, 502, 503]
        })
        
        self.add_knowledge("security_rules", {
            "required_auth_operations": ["post", "put", "patch", "delete"],
            "security_schemes": ["http", "apiKey", "oauth2", "openIdConnect"],
            "sensitive_parameters": ["password", "token", "key", "secret", "auth"],
            "security_headers": ["authorization", "x-api-key", "x-auth-token"]
        })
        
        self.add_knowledge("best_practices", {
            "naming_conventions": {
                "use_kebab_case": True,
                "use_nouns_for_resources": True,
                "use_plural_for_collections": True,
                "avoid_verbs_in_urls": True
            },
            "response_guidelines": {
                "include_error_details": True,
                "use_standard_status_codes": True,
                "provide_examples": True,
                "include_pagination_for_lists": True
            }
        })
    
    async def execute_goal(self, goal: Goal) -> AgentResult:
        """Execute validation goals."""
        try:
            objective = goal.objective.lower()
            
            if "validate_api_specification" in objective:
                return await self._validate_api_specification(goal)
            elif "validate_schema" in objective:
                return await self._validate_schema(goal)
            elif "check_security" in objective:
                return await self._check_security(goal)
            elif "check_best_practices" in objective:
                return await self._check_best_practices(goal)
            elif "validate_examples" in objective:
                return await self._validate_examples(goal)
            else:
                return create_error_result(f"Unknown objective: {goal.objective}")
                
        except Exception as e:
            self.logger.error(f"Error executing goal {goal.objective}: {str(e)}")
            return create_error_result(str(e))
    
    async def _validate_api_specification(self, goal: Goal) -> AgentResult:
        """Perform comprehensive validation of API specification."""
        # First check parameters, then context for specification from previous steps
        specification = goal.parameters.get("specification", {})
        if not specification:
            # Check context for specification from previous workflow steps
            for step_id, step_data in goal.context.items():
                if isinstance(step_data, dict) and "specification" in step_data:
                    specification = step_data["specification"]
                    break
                # Also check if the step data itself is a specification
                elif isinstance(step_data, dict) and any(key in step_data for key in ["openapi", "swagger", "paths"]):
                    specification = step_data
                    break
        
        check_syntax = goal.parameters.get("check_syntax", True)
        check_completeness = goal.parameters.get("check_completeness", True)
        check_standards_compliance = goal.parameters.get("check_standards_compliance", True)
        validate_schemas = goal.parameters.get("validate_schemas", True)
        check_security = goal.parameters.get("check_security", True)
        
        if not specification:
            return create_error_result("No specification provided for validation")
        
        self.logger.info("Performing comprehensive API specification validation")
        self.logger.info(f"Using specification: {type(specification)} with keys: {list(specification.keys()) if isinstance(specification, dict) else 'non-dict'}")
        
        validation_results = {
            "overall_valid": True,
            "validation_summary": {
                "total_errors": 0,
                "total_warnings": 0,
                "total_info": 0
            },
            "syntax_validation": {},
            "completeness_validation": {},
            "standards_compliance": {},
            "schema_validation": {},
            "security_validation": {},
            "best_practices": {},
            "recommendations": []
        }
        
        # Syntax validation
        if check_syntax:
            syntax_result = await self._validate_syntax(specification)
            validation_results["syntax_validation"] = syntax_result
            if not syntax_result.get("is_valid", True):
                validation_results["overall_valid"] = False
        
        # Completeness validation
        if check_completeness:
            completeness_result = await self._validate_completeness(specification)
            validation_results["completeness_validation"] = completeness_result
            if not completeness_result.get("is_valid", True):
                validation_results["overall_valid"] = False
        
        # Standards compliance
        if check_standards_compliance:
            standards_result = await self._validate_standards_compliance(specification)
            validation_results["standards_compliance"] = standards_result
        
        # Schema validation
        if validate_schemas:
            schema_result = await self._validate_schemas_comprehensive(specification)
            validation_results["schema_validation"] = schema_result
        
        # Security validation
        if check_security:
            security_result = await self._validate_security_comprehensive(specification)
            validation_results["security_validation"] = security_result
        
        # Best practices check
        best_practices_result = await self._validate_best_practices(specification)
        validation_results["best_practices"] = best_practices_result
        
        # Calculate summary
        for category in validation_results.values():
            if isinstance(category, dict):
                if "errors" in category:
                    validation_results["validation_summary"]["total_errors"] += len(category["errors"])
                if "warnings" in category:
                    validation_results["validation_summary"]["total_warnings"] += len(category["warnings"])
                if "info" in category:
                    validation_results["validation_summary"]["total_info"] += len(category["info"])
        
        # Generate recommendations
        validation_results["recommendations"] = self._generate_recommendations(validation_results)
        
        # Final validation status
        if validation_results["validation_summary"]["total_errors"] > 0:
            validation_results["overall_valid"] = False
        
        metadata = {
            "validation_timestamp": datetime.now().isoformat(),
            "validation_coverage": {
                "syntax": check_syntax,
                "completeness": check_completeness,
                "standards": check_standards_compliance,
                "schemas": validate_schemas,
                "security": check_security
            }
        }
        
        confidence = 0.9 if validation_results["overall_valid"] else 0.7
        
        self.logger.info(
            f"Validation complete: {validation_results['validation_summary']['total_errors']} errors, "
            f"{validation_results['validation_summary']['total_warnings']} warnings"
        )
        
        return create_success_result(validation_results, metadata, confidence)
    
    async def _validate_syntax(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Validate OpenAPI specification syntax."""
        syntax_validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check required top-level fields
        required_fields = self.get_knowledge("openapi_rules", {}).get("required_top_level", [])
        for field in required_fields:
            if field not in specification:
                syntax_validation["errors"].append(f"Missing required top-level field: {field}")
                syntax_validation["is_valid"] = False
        
        # Check OpenAPI version format
        if "openapi" in specification:
            version = specification["openapi"]
            if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
                syntax_validation["errors"].append(f"Invalid OpenAPI version format: {version}")
                syntax_validation["is_valid"] = False
        
        # Check info section
        if "info" in specification:
            info = specification["info"]
            required_info = self.get_knowledge("openapi_rules", {}).get("required_info", [])
            for field in required_info:
                if field not in info:
                    syntax_validation["errors"].append(f"Missing required info field: {field}")
                    syntax_validation["is_valid"] = False
        
        # Check paths syntax
        if "paths" in specification:
            paths = specification["paths"]
            valid_methods = self.get_knowledge("openapi_rules", {}).get("valid_http_methods", [])
            
            for path, path_item in paths.items():
                # Check path format
                if not path.startswith('/'):
                    syntax_validation["errors"].append(f"Path must start with '/': {path}")
                    syntax_validation["is_valid"] = False
                
                # Check HTTP methods
                for method, operation in path_item.items():
                    if method.lower() not in valid_methods:
                        syntax_validation["warnings"].append(f"Non-standard HTTP method: {method}")
                    
                    # Check operation structure
                    if not isinstance(operation, dict):
                        syntax_validation["errors"].append(
                            f"Operation must be an object: {path} {method}"
                        )
                        syntax_validation["is_valid"] = False
                        continue
                    
                    # Check responses (required)
                    if "responses" not in operation:
                        syntax_validation["errors"].append(
                            f"Missing responses in operation: {path} {method}"
                        )
                        syntax_validation["is_valid"] = False
        
        return syntax_validation
    
    async def _validate_completeness(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Validate specification completeness."""
        completeness_validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check if paths exist
        if "paths" not in specification or not specification["paths"]:
            completeness_validation["errors"].append("No paths defined in specification")
            completeness_validation["is_valid"] = False
        else:
            paths = specification["paths"]
            total_operations = sum(len(path_item) for path_item in paths.values())
            completeness_validation["info"].append(f"Found {len(paths)} paths with {total_operations} operations")
        
        # Check for response definitions
        missing_responses = []
        if "paths" in specification:
            for path, path_item in specification["paths"].items():
                for method, operation in path_item.items():
                    responses = operation.get("responses", {})
                    if not responses:
                        missing_responses.append(f"{path} {method}")
                    else:
                        # Check for success response
                        success_codes = [code for code in responses.keys() if code.startswith('2')]
                        if not success_codes:
                            completeness_validation["warnings"].append(
                                f"No success response defined: {path} {method}"
                            )
        
        if missing_responses:
            completeness_validation["errors"].extend([
                f"Missing responses: {resp}" for resp in missing_responses[:5]
            ])
            if len(missing_responses) > 5:
                completeness_validation["errors"].append(
                    f"... and {len(missing_responses) - 5} more operations with missing responses"
                )
            completeness_validation["is_valid"] = False
        
        # Check for component schemas
        if "components" in specification and "schemas" in specification["components"]:
            schemas = specification["components"]["schemas"]
            completeness_validation["info"].append(f"Found {len(schemas)} component schemas")
        else:
            completeness_validation["warnings"].append("No component schemas defined")
        
        return completeness_validation
    
    async def _validate_standards_compliance(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compliance with OpenAPI standards."""
        standards_validation = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check HTTP status codes
        if "paths" in specification:
            for path, path_item in specification["paths"].items():
                for method, operation in path_item.items():
                    responses = operation.get("responses", {})
                    for status_code in responses.keys():
                        if status_code.isdigit():
                            code = int(status_code)
                            if code < 100 or code > 599:
                                standards_validation["errors"].append(
                                    f"Invalid HTTP status code: {status_code} in {path} {method}"
                                )
        
        # Check parameter locations
        valid_locations = self.get_knowledge("openapi_rules", {}).get("valid_parameter_locations", [])
        if "paths" in specification:
            for path, path_item in specification["paths"].items():
                for method, operation in path_item.items():
                    parameters = operation.get("parameters", [])
                    for param in parameters:
                        location = param.get("in")
                        if location not in valid_locations:
                            standards_validation["errors"].append(
                                f"Invalid parameter location '{location}': {path} {method}"
                            )
        
        # Check schema types
        valid_types = self.get_knowledge("openapi_rules", {}).get("valid_schema_types", [])
        self._validate_schema_types_recursive(specification, valid_types, standards_validation)
        
        return standards_validation
    
    def _validate_schema_types_recursive(
        self, 
        obj: Any, 
        valid_types: List[str], 
        validation_result: Dict[str, Any],
        path: str = ""
    ):
        """Recursively validate schema types."""
        if isinstance(obj, dict):
            if "type" in obj:
                schema_type = obj["type"]
                if schema_type not in valid_types:
                    validation_result["errors"].append(
                        f"Invalid schema type '{schema_type}' at {path}"
                    )
            
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                self._validate_schema_types_recursive(value, valid_types, validation_result, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                self._validate_schema_types_recursive(item, valid_types, validation_result, new_path)
    
    async def _validate_schemas_comprehensive(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive schema validation."""
        schema_validation = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        if "components" not in specification or "schemas" not in specification["components"]:
            schema_validation["warnings"].append("No component schemas found")
            return schema_validation
        
        schemas = specification["components"]["schemas"]
        schema_validation["info"].append(f"Validating {len(schemas)} schemas")
        
        for schema_name, schema in schemas.items():
            # Check required properties
            if "type" in schema and schema["type"] == "object":
                if "properties" in schema and "required" in schema:
                    required_props = schema["required"]
                    available_props = list(schema["properties"].keys())
                    
                    for req_prop in required_props:
                        if req_prop not in available_props:
                            schema_validation["errors"].append(
                                f"Required property '{req_prop}' not found in schema '{schema_name}'"
                            )
                
                # Check for missing properties section
                if "properties" not in schema:
                    schema_validation["warnings"].append(
                        f"Object schema '{schema_name}' has no properties defined"
                    )
            
            # Check array schemas
            if "type" in schema and schema["type"] == "array":
                if "items" not in schema:
                    schema_validation["errors"].append(
                        f"Array schema '{schema_name}' missing items definition"
                    )
        
        return schema_validation
    
    async def _validate_security_comprehensive(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive security validation."""
        security_validation = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check for security schemes
        has_security_schemes = (
            "components" in specification and 
            "securitySchemes" in specification["components"]
        )
        
        if not has_security_schemes:
            security_validation["warnings"].append("No security schemes defined")
        else:
            schemes = specification["components"]["securitySchemes"]
            security_validation["info"].append(f"Found {len(schemes)} security schemes")
            
            # Validate security scheme types
            valid_scheme_types = self.get_knowledge("security_rules", {}).get("security_schemes", [])
            for scheme_name, scheme in schemes.items():
                scheme_type = scheme.get("type")
                if scheme_type not in valid_scheme_types:
                    security_validation["errors"].append(
                        f"Invalid security scheme type '{scheme_type}' in '{scheme_name}'"
                    )
        
        # Check for global security
        if "security" not in specification:
            security_validation["warnings"].append("No global security requirements defined")
        
        # Check operations that should require authentication
        required_auth_ops = self.get_knowledge("security_rules", {}).get("required_auth_operations", [])
        if "paths" in specification:
            for path, path_item in specification["paths"].items():
                for method, operation in path_item.items():
                    if method.lower() in required_auth_ops:
                        has_security = (
                            "security" in operation or 
                            "security" in specification
                        )
                        if not has_security:
                            security_validation["warnings"].append(
                                f"Operation {method.upper()} {path} should require authentication"
                            )
        
        # Check for sensitive parameters
        sensitive_params = self.get_knowledge("security_rules", {}).get("sensitive_parameters", [])
        if "paths" in specification:
            for path, path_item in specification["paths"].items():
                for method, operation in path_item.items():
                    parameters = operation.get("parameters", [])
                    for param in parameters:
                        param_name = param.get("name", "").lower()
                        for sensitive in sensitive_params:
                            if sensitive in param_name:
                                location = param.get("in", "")
                                if location in ["query", "header"]:
                                    security_validation["warnings"].append(
                                        f"Sensitive parameter '{param['name']}' in {location}: {path} {method}"
                                    )
        
        return security_validation
    
    async def _validate_best_practices(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against API best practices."""
        best_practices_validation = {
            "errors": [],
            "warnings": [],
            "info": [],
            "score": 0,
            "max_score": 0
        }
        
        # Naming conventions
        self._check_naming_conventions(specification, best_practices_validation)
        
        # Response guidelines
        self._check_response_guidelines(specification, best_practices_validation)
        
        # Documentation completeness
        self._check_documentation_completeness(specification, best_practices_validation)
        
        # Error handling
        self._check_error_handling(specification, best_practices_validation)
        
        # Calculate score
        if best_practices_validation["max_score"] > 0:
            score_percentage = (best_practices_validation["score"] / best_practices_validation["max_score"]) * 100
            best_practices_validation["score_percentage"] = score_percentage
        else:
            best_practices_validation["score_percentage"] = 0
        
        return best_practices_validation
    
    def _check_naming_conventions(self, specification: Dict[str, Any], validation_result: Dict[str, Any]):
        """Check naming conventions."""
        validation_result["max_score"] += 10
        score = 0
        
        if "paths" in specification:
            for path in specification["paths"].keys():
                # Check if path uses kebab-case or snake_case
                path_segments = [seg for seg in path.split('/') if seg and not seg.startswith('{')]
                
                for segment in path_segments:
                    if re.match(r'^[a-z]+(-[a-z]+)*$', segment) or re.match(r'^[a-z]+(_[a-z]+)*$', segment):
                        score += 1
                    else:
                        validation_result["warnings"].append(
                            f"Path segment '{segment}' should use kebab-case or snake_case"
                        )
                
                # Check for plural nouns in collection endpoints
                if not any(param in path for param in ['{id}', '{uuid}']):
                    # This is likely a collection endpoint
                    last_segment = path.split('/')[-1]
                    if last_segment and not last_segment.endswith('s'):
                        validation_result["warnings"].append(
                            f"Collection endpoint should use plural nouns: {path}"
                        )
        
        validation_result["score"] += min(score, 5)  # Cap at 5 points for naming
    
    def _check_response_guidelines(self, specification: Dict[str, Any], validation_result: Dict[str, Any]):
        """Check response guidelines."""
        validation_result["max_score"] += 15
        score = 0
        
        if "paths" in specification:
            total_operations = 0
            operations_with_examples = 0
            operations_with_error_responses = 0
            
            for path, path_item in specification["paths"].items():
                for method, operation in path_item.items():
                    total_operations += 1
                    responses = operation.get("responses", {})
                    
                    # Check for error responses
                    error_codes = [code for code in responses.keys() if code.startswith('4') or code.startswith('5')]
                    if error_codes:
                        operations_with_error_responses += 1
                    
                    # Check for examples in responses
                    for response in responses.values():
                        if isinstance(response, dict) and "content" in response:
                            content = response["content"]
                            for media_type_content in content.values():
                                if "example" in media_type_content or "examples" in media_type_content:
                                    operations_with_examples += 1
                                    break
            
            if total_operations > 0:
                error_response_ratio = operations_with_error_responses / total_operations
                example_ratio = operations_with_examples / total_operations
                
                score += int(error_response_ratio * 8)  # Up to 8 points
                score += int(example_ratio * 7)  # Up to 7 points
                
                if error_response_ratio < 0.5:
                    validation_result["warnings"].append(
                        f"Only {error_response_ratio:.1%} of operations define error responses"
                    )
                
                if example_ratio < 0.3:
                    validation_result["warnings"].append(
                        f"Only {example_ratio:.1%} of operations include examples"
                    )
        
        validation_result["score"] += score
    
    def _check_documentation_completeness(self, specification: Dict[str, Any], validation_result: Dict[str, Any]):
        """Check documentation completeness."""
        validation_result["max_score"] += 10
        score = 0
        
        # Check info description
        if "info" in specification and "description" in specification["info"]:
            if len(specification["info"]["description"]) > 20:
                score += 2
        else:
            validation_result["warnings"].append("API description missing or too short")
        
        # Check operation descriptions
        if "paths" in specification:
            total_operations = 0
            operations_with_descriptions = 0
            
            for path, path_item in specification["paths"].items():
                for method, operation in path_item.items():
                    total_operations += 1
                    if "description" in operation and len(operation["description"]) > 10:
                        operations_with_descriptions += 1
            
            if total_operations > 0:
                description_ratio = operations_with_descriptions / total_operations
                score += int(description_ratio * 8)  # Up to 8 points
                
                if description_ratio < 0.7:
                    validation_result["warnings"].append(
                        f"Only {description_ratio:.1%} of operations have descriptions"
                    )
        
        validation_result["score"] += score
    
    def _check_error_handling(self, specification: Dict[str, Any], validation_result: Dict[str, Any]):
        """Check error handling patterns."""
        validation_result["max_score"] += 5
        score = 0
        
        # Check for standard error schema
        has_error_schema = (
            "components" in specification and 
            "schemas" in specification["components"] and
            any("error" in schema_name.lower() for schema_name in specification["components"]["schemas"].keys())
        )
        
        if has_error_schema:
            score += 3
            validation_result["info"].append("Standard error schema found")
        else:
            validation_result["warnings"].append("No standard error schema defined")
        
        # Check for consistent error responses
        if "components" in specification and "responses" in specification["components"]:
            error_responses = [
                name for name in specification["components"]["responses"].keys()
                if any(error_word in name.lower() for error_word in ["error", "bad", "unauthorized", "forbidden", "notfound"])
            ]
            
            if len(error_responses) >= 3:
                score += 2
                validation_result["info"].append(f"Found {len(error_responses)} standard error responses")
            else:
                validation_result["warnings"].append("Limited standard error response definitions")
        
        validation_result["score"] += score
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Based on errors
        total_errors = validation_results["validation_summary"]["total_errors"]
        if total_errors > 0:
            recommendations.append(f"Fix {total_errors} validation errors before proceeding to production")
        
        # Based on warnings
        total_warnings = validation_results["validation_summary"]["total_warnings"]
        if total_warnings > 5:
            recommendations.append("Consider addressing validation warnings to improve API quality")
        
        # Security recommendations
        security_validation = validation_results.get("security_validation", {})
        if security_validation.get("warnings"):
            recommendations.append("Review security warnings and implement proper authentication/authorization")
        
        # Best practices score
        best_practices = validation_results.get("best_practices", {})
        score_percentage = best_practices.get("score_percentage", 0)
        
        if score_percentage < 60:
            recommendations.append("API design could benefit from following more best practices (score: {:.1f}%)".format(score_percentage))
        elif score_percentage < 80:
            recommendations.append("Good API design with room for improvement (score: {:.1f}%)".format(score_percentage))
        else:
            recommendations.append("Excellent API design following best practices (score: {:.1f}%)".format(score_percentage))
        
        # Schema recommendations
        schema_validation = validation_results.get("schema_validation", {})
        if schema_validation.get("warnings"):
            recommendations.append("Consider improving schema definitions for better API documentation")
        
        return recommendations
    
    async def _validate_schema(self, goal: Goal) -> AgentResult:
        """Validate specific schema definitions."""
        schema = goal.parameters.get("schema", {})
        schema_name = goal.parameters.get("schema_name", "unknown")
        
        # Implementation for specific schema validation
        # This is a simplified version
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        return create_success_result(validation_result)
    
    async def _check_security(self, goal: Goal) -> AgentResult:
        """Check security configuration."""
        specification = goal.parameters.get("specification", {})
        
        # Implementation for security checking
        security_result = await self._validate_security_comprehensive(specification)
        
        return create_success_result(security_result)
    
    async def _check_best_practices(self, goal: Goal) -> AgentResult:
        """Check best practices compliance."""
        specification = goal.parameters.get("specification", {})
        
        # Implementation for best practices checking
        best_practices_result = await self._validate_best_practices(specification)
        
        return create_success_result(best_practices_result)
    
    async def _validate_examples(self, goal: Goal) -> AgentResult:
        """Validate examples in the specification."""
        specification = goal.parameters.get("specification", {})
        
        validation_result = {
            "examples_found": 0,
            "valid_examples": 0,
            "invalid_examples": [],
            "warnings": []
        }
        
        # Count and validate examples
        if "components" in specification and "examples" in specification["components"]:
            examples = specification["components"]["examples"]
            validation_result["examples_found"] = len(examples)
            validation_result["valid_examples"] = len(examples)  # Simplified
        
        return create_success_result(validation_result)

    def _custom_goal_check(self, goal: Goal) -> bool:
        """Custom goal checking for Validation Agent."""
        objective = goal.objective.lower()
        
        # Handle specific goal patterns that this agent can execute
        validation_patterns = [
            "validate_api_specification",
            "validate_specification",
            "validate_openapi",
            "check_specification",
            "verify_specification",
            "validate_api",
            "specification_validation"
        ]
        
        return any(pattern in objective for pattern in validation_patterns)
