"""
API Design Agent for API Specification Writing System
Designs the overall API structure and architecture based on analyzed requirements
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import json

from .base_agent import SpecializedAgent, Goal, AgentResult, AgentCapability, create_success_result, create_error_result


class APIDesignAgent(SpecializedAgent):
    """
    Specialized agent for designing API structure and architecture.
    
    This agent takes analyzed requirements and creates:
    - Complete API architecture
    - Endpoint structure and organization
    - Data flow design
    - Security architecture
    - Error handling strategy
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the API Design Agent."""
        super().__init__(
            name="api_design_agent",
            capabilities=[
                AgentCapability.API_DESIGN,
                AgentCapability.ENDPOINT_DESIGN,
                AgentCapability.SECURITY_DESIGN,
                AgentCapability.SCHEMA_GENERATION,
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.DATA_FLOW_DESIGN
            ],
            description="Designs comprehensive API structure and architecture",
            config=config or {},
            specialization="api_design"
        )
        
        # API design patterns and best practices
        self.add_knowledge("rest_conventions", {
            "resource_naming": {
                "use_nouns": True,
                "use_plural": True,
                "lowercase": True,
                "hyphen_separated": True
            },
            "http_methods": {
                "GET": "retrieve resource(s)",
                "POST": "create new resource",
                "PUT": "update entire resource",
                "PATCH": "partial update",
                "DELETE": "remove resource"
            },
            "status_codes": {
                "2xx": "success",
                "3xx": "redirection", 
                "4xx": "client error",
                "5xx": "server error"
            }
        })
        
        self.add_knowledge("security_patterns", {
            "authentication": {
                "jwt": {"type": "bearer", "format": "JWT"},
                "oauth2": {"type": "oauth2", "flows": ["authorization_code", "client_credentials"]},
                "api_key": {"type": "apiKey", "in": "header"}
            },
            "common_security_headers": [
                "Authorization",
                "X-API-Key",
                "X-Client-ID"
            ]
        })
        
        self.add_knowledge("error_handling", {
            "standard_errors": {
                "400": "Bad Request - Invalid input",
                "401": "Unauthorized - Authentication required",
                "403": "Forbidden - Insufficient permissions",
                "404": "Not Found - Resource not found",
                "409": "Conflict - Resource conflict",
                "422": "Unprocessable Entity - Validation error",
                "500": "Internal Server Error - Server error"
            },
            "error_response_format": {
                "error": {
                    "code": "string",
                    "message": "string",
                    "details": "object"
                }
            }
        })
    
    async def execute_goal(self, goal: Goal) -> AgentResult:
        """Execute API design goals."""
        try:
            objective = goal.objective.lower()
            
            if "design_api_structure" in objective:
                return await self._design_api_structure(goal)
            elif "enhance_existing_specification" in objective:
                return await self._enhance_existing_specification(goal)
            elif "design_endpoints" in objective:
                return await self._design_endpoints(goal)
            elif "design_security" in objective:
                return await self._design_security(goal)
            elif "design_data_models" in objective:
                return await self._design_data_models(goal)
            else:
                return create_error_result(f"Unknown objective: {goal.objective}")
                
        except Exception as e:
            self.logger.error(f"Error executing goal {goal.objective}: {str(e)}")
            return create_error_result(str(e))
    
    async def _design_api_structure(self, goal: Goal) -> AgentResult:
        """Design the complete API structure."""
        # First check parameters, then context for requirements from previous steps
        requirements = goal.parameters.get("requirements", {})
        if not requirements:
            # Check context for requirements from previous workflow steps
            for step_id, step_data in goal.context.items():
                if isinstance(step_data, dict) and "requirements" in step_data:
                    requirements = step_data["requirements"]
                    break
                # Also check if the step data itself is requirements
                elif isinstance(step_data, dict) and any(key in step_data for key in ["entities", "endpoints", "functional_requirements"]):
                    requirements = step_data
                    break
        
        project_name = goal.parameters.get("project_name", "API")
        include_security = goal.parameters.get("include_security", True)
        max_endpoints = goal.parameters.get("max_endpoints", 50)
        
        if not requirements:
            return create_error_result("No requirements provided for API design")
        
        self.logger.info(f"Designing API structure for: {project_name}")
        self.logger.info(f"Using requirements: {type(requirements)} with keys: {list(requirements.keys()) if isinstance(requirements, dict) else 'non-dict'}")
        
        # Extract components from requirements
        entities = requirements.get("entities", [])
        endpoints = requirements.get("endpoints", [])
        data_models = requirements.get("data_models", [])
        security_requirements = requirements.get("security_requirements", {})
        
        # Design comprehensive API structure
        api_design = {
            "info": self._design_api_info(requirements, project_name),
            "servers": self._design_servers(),
            "paths": await self._design_paths(entities, endpoints, max_endpoints),
            "components": {
                "schemas": await self._design_schemas(entities, data_models),
                "responses": self._design_standard_responses(),
                "parameters": self._design_common_parameters(),
                "examples": self._design_examples(entities),
                "headers": self._design_headers()
            },
            "tags": self._design_tags(entities),
            "external_docs": self._design_external_docs(project_name)
        }
        
        # Add security if required
        if include_security:
            security_design = await self._design_security_comprehensive(security_requirements)
            api_design["components"]["securitySchemes"] = security_design["schemes"]
            api_design["security"] = security_design["global_security"]
            
            # Apply security to endpoints
            for path, methods in api_design["paths"].items():
                for method, endpoint in methods.items():
                    endpoint["security"] = self._determine_endpoint_security(endpoint, security_design)
        
        # Add metadata
        metadata = {
            "design_timestamp": datetime.now().isoformat(),
            "total_paths": len(api_design["paths"]),
            "total_schemas": len(api_design["components"]["schemas"]),
            "security_enabled": include_security,
            "entities_designed": len(entities),
            "design_patterns": self._identify_design_patterns(api_design)
        }
        
        self.logger.info(
            f"API design complete: {metadata['total_paths']} paths, "
            f"{metadata['total_schemas']} schemas"
        )
        
        return create_success_result(api_design, metadata, confidence=0.95)
    
    async def _enhance_existing_specification(self, goal: Goal) -> AgentResult:
        """Enhance an existing API specification."""
        existing_spec = goal.parameters.get("existing_specification", {})
        enhancement_requirements = goal.parameters.get("enhancement_requirements", "")
        preserve_existing = goal.parameters.get("preserve_existing", True)
        
        if not existing_spec:
            return create_error_result("No existing specification provided")
        
        self.logger.info("Enhancing existing API specification")
        
        # Analyze enhancement requirements
        # This would typically use the RequirementAnalysisAgent
        # For now, we'll do basic enhancement
        
        enhanced_spec = existing_spec.copy() if preserve_existing else {}
        
        # Enhance info section
        if "info" not in enhanced_spec:
            enhanced_spec["info"] = {}
        
        enhanced_spec["info"]["version"] = self._increment_version(
            existing_spec.get("info", {}).get("version", "1.0.0")
        )
        enhanced_spec["info"]["description"] = (
            existing_spec.get("info", {}).get("description", "") + 
            f"\nEnhanced with: {enhancement_requirements}"
        )
        
        # Add enhancement metadata
        metadata = {
            "enhancement_timestamp": datetime.now().isoformat(),
            "original_version": existing_spec.get("info", {}).get("version", "unknown"),
            "new_version": enhanced_spec["info"]["version"],
            "enhancement_requirements": enhancement_requirements
        }
        
        return create_success_result(enhanced_spec, metadata, confidence=0.8)
    
    def _design_api_info(self, requirements: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        """Design the API info section."""
        project_info = requirements.get("project_info", {})
        
        return {
            "title": project_info.get("name", project_name),
            "description": project_info.get("description", f"API for {project_name}"),
            "version": project_info.get("version", "1.0.0"),
            "termsOfService": "https://example.com/terms",
            "contact": {
                "name": "API Support",
                "email": "api-support@example.com",
                "url": "https://example.com/support"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        }
    
    def _design_servers(self) -> List[Dict[str, Any]]:
        """Design server configurations."""
        return [
            {
                "url": "https://api.example.com/v1",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.example.com/v1",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:3000/v1",
                "description": "Development server"
            }
        ]
    
    async def _design_paths(
        self, 
        entities: List[Dict[str, Any]], 
        identified_endpoints: List[Dict[str, Any]], 
        max_endpoints: int
    ) -> Dict[str, Any]:
        """Design API paths based on entities and identified endpoints."""
        paths = {}
        endpoint_count = 0
        
        # Group endpoints by entity
        entity_endpoints = {}
        for endpoint in identified_endpoints:
            entity = endpoint.get("entity", "unknown")
            if entity not in entity_endpoints:
                entity_endpoints[entity] = []
            entity_endpoints[entity].append(endpoint)
        
        # Design paths for each entity
        for entity in entities:
            if endpoint_count >= max_endpoints:
                break
                
            entity_name = entity["name"]
            entity_endpoints_list = entity_endpoints.get(entity_name, [])
            
            # Create resource paths
            resource_path = f"/{entity_name}"
            item_path = f"/{entity_name}/{{id}}"
            
            # Collection endpoints
            collection_methods = {}
            item_methods = {}
            
            # Determine available operations
            operations = [ep["operation"] for ep in entity_endpoints_list]
            
            # GET /resources (list)
            if "list" in operations or not operations:
                collection_methods["get"] = self._create_endpoint_spec(
                    operation="list",
                    entity=entity_name,
                    description=f"List all {entity_name}",
                    parameters=[
                        {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 10}},
                        {"name": "sort", "in": "query", "schema": {"type": "string"}}
                    ]
                )
                endpoint_count += 1
            
            # POST /resources (create)
            if "create" in operations or not operations:
                collection_methods["post"] = self._create_endpoint_spec(
                    operation="create",
                    entity=entity_name,
                    description=f"Create a new {entity_name}",
                    request_body=self._create_request_body_spec(entity_name)
                )
                endpoint_count += 1
            
            # GET /resources/{id} (read)
            if "read" in operations or not operations:
                item_methods["get"] = self._create_endpoint_spec(
                    operation="read",
                    entity=entity_name,
                    description=f"Get a specific {entity_name}",
                    parameters=[{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]
                )
                endpoint_count += 1
            
            # PUT /resources/{id} (update)
            if "update" in operations or not operations:
                item_methods["put"] = self._create_endpoint_spec(
                    operation="update",
                    entity=entity_name,
                    description=f"Update a specific {entity_name}",
                    parameters=[{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    request_body=self._create_request_body_spec(entity_name)
                )
                endpoint_count += 1
            
            # DELETE /resources/{id} (delete)
            if "delete" in operations or not operations:
                item_methods["delete"] = self._create_endpoint_spec(
                    operation="delete",
                    entity=entity_name,
                    description=f"Delete a specific {entity_name}",
                    parameters=[{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]
                )
                endpoint_count += 1
            
            # Add paths
            if collection_methods:
                paths[resource_path] = collection_methods
            if item_methods:
                paths[item_path] = item_methods
            
            # Add search endpoint if needed
            if "search" in operations:
                search_path = f"/{entity_name}/search"
                paths[search_path] = {
                    "get": self._create_endpoint_spec(
                        operation="search",
                        entity=entity_name,
                        description=f"Search {entity_name}",
                        parameters=[
                            {"name": "q", "in": "query", "schema": {"type": "string"}},
                            {"name": "filter", "in": "query", "schema": {"type": "string"}}
                        ]
                    )
                }
                endpoint_count += 1
        
        return paths
    
    def _create_endpoint_spec(
        self, 
        operation: str, 
        entity: str, 
        description: str, 
        parameters: Optional[List[Dict[str, Any]]] = None,
        request_body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a complete endpoint specification."""
        spec = {
            "summary": f"{operation.title()} {entity}",
            "description": description,
            "operationId": f"{operation}{entity.title()}",
            "tags": [entity],
            "responses": self._create_responses_spec(operation, entity)
        }
        
        if parameters:
            spec["parameters"] = parameters
        
        if request_body:
            spec["requestBody"] = request_body
        
        return spec
    
    def _create_request_body_spec(self, entity: str) -> Dict[str, Any]:
        """Create request body specification."""
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": f"#/components/schemas/{entity.title()}"
                    },
                    "example": {
                        "$ref": f"#/components/examples/{entity.title()}Example"
                    }
                }
            }
        }
    
    def _create_responses_spec(self, operation: str, entity: str) -> Dict[str, Any]:
        """Create responses specification for an operation."""
        responses = {}
        
        # Success responses
        if operation == "create":
            responses["201"] = {
                "description": f"{entity.title()} created successfully",
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{entity.title()}"}
                    }
                }
            }
        elif operation == "delete":
            responses["204"] = {
                "description": f"{entity.title()} deleted successfully"
            }
        elif operation == "list":
            responses["200"] = {
                "description": f"List of {entity}",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "data": {
                                    "type": "array",
                                    "items": {"$ref": f"#/components/schemas/{entity.title()}"}
                                },
                                "pagination": {
                                    "$ref": "#/components/schemas/Pagination"
                                }
                            }
                        }
                    }
                }
            }
        else:  # read, update, search
            responses["200"] = {
                "description": f"{entity.title()} retrieved successfully",
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{entity.title()}"}
                    }
                }
            }
        
        # Error responses
        error_responses = {
            "400": {"$ref": "#/components/responses/BadRequest"},
            "401": {"$ref": "#/components/responses/Unauthorized"},
            "403": {"$ref": "#/components/responses/Forbidden"},
            "500": {"$ref": "#/components/responses/InternalServerError"}
        }
        
        if operation in ["read", "update", "delete"]:
            error_responses["404"] = {"$ref": "#/components/responses/NotFound"}
        
        responses.update(error_responses)
        return responses
    
    async def _design_schemas(
        self, 
        entities: List[Dict[str, Any]], 
        data_models: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Design data schemas for the API."""
        schemas = {}
        
        # Create schemas from data models
        for model in data_models:
            schema_name = model["name"]
            schemas[schema_name] = {
                "type": model.get("type", "object"),
                "description": model.get("description", f"Schema for {schema_name}"),
                "properties": model.get("properties", {}),
                "required": model.get("required", [])
            }
        
        # Add common schemas
        schemas.update(self._get_common_schemas())
        
        return schemas
    
    def _get_common_schemas(self) -> Dict[str, Any]:
        """Get common reusable schemas."""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Error code"},
                            "message": {"type": "string", "description": "Error message"},
                            "details": {"type": "object", "description": "Additional error details"}
                        },
                        "required": ["code", "message"]
                    }
                },
                "required": ["error"]
            },
            "Pagination": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Current page number"},
                    "limit": {"type": "integer", "description": "Items per page"},
                    "total": {"type": "integer", "description": "Total number of items"},
                    "pages": {"type": "integer", "description": "Total number of pages"}
                },
                "required": ["page", "limit", "total", "pages"]
            },
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "description": "Operation success status"},
                    "message": {"type": "string", "description": "Success message"},
                    "data": {"type": "object", "description": "Response data"}
                },
                "required": ["success"]
            }
        }
    
    def _design_standard_responses(self) -> Dict[str, Any]:
        """Design standard response definitions."""
        return {
            "BadRequest": {
                "description": "Bad Request - Invalid input",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "Unauthorized": {
                "description": "Unauthorized - Authentication required",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "Forbidden": {
                "description": "Forbidden - Insufficient permissions",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "NotFound": {
                "description": "Not Found - Resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "InternalServerError": {
                "description": "Internal Server Error - Server error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            }
        }
    
    def _design_common_parameters(self) -> Dict[str, Any]:
        """Design common reusable parameters."""
        return {
            "PageParam": {
                "name": "page",
                "in": "query",
                "description": "Page number for pagination",
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1
                }
            },
            "LimitParam": {
                "name": "limit",
                "in": "query",
                "description": "Number of items per page",
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10
                }
            },
            "SortParam": {
                "name": "sort",
                "in": "query",
                "description": "Sort field and direction (e.g., 'name:asc', 'created_at:desc')",
                "schema": {
                    "type": "string",
                    "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*:(asc|desc)$"
                }
            },
            "SearchParam": {
                "name": "q",
                "in": "query",
                "description": "Search query string",
                "schema": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100
                }
            }
        }
    
    def _design_examples(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Design example values for entities."""
        examples = {}
        
        for entity in entities:
            entity_name = entity["name"]
            example_name = f"{entity_name.title()}Example"
            
            # Create example based on entity attributes
            example_value = {"id": "12345"}
            
            for attr in entity.get("attributes", []):
                attr_name = attr["name"]
                # Generate example value based on attribute name
                if "email" in attr_name:
                    example_value[attr_name] = "user@example.com"
                elif "name" in attr_name:
                    example_value[attr_name] = f"Sample {entity_name.title()}"
                elif "date" in attr_name or "time" in attr_name:
                    example_value[attr_name] = "2024-01-15T10:30:00Z"
                elif "price" in attr_name or "amount" in attr_name:
                    example_value[attr_name] = 99.99
                elif "count" in attr_name or "number" in attr_name:
                    example_value[attr_name] = 10
                else:
                    example_value[attr_name] = f"sample_{attr_name}"
            
            examples[example_name] = {
                "summary": f"Example {entity_name}",
                "description": f"A sample {entity_name} object",
                "value": example_value
            }
        
        return examples
    
    def _design_headers(self) -> Dict[str, Any]:
        """Design common headers."""
        return {
            "X-Rate-Limit-Limit": {
                "description": "The number of allowed requests in the current period",
                "schema": {"type": "integer"}
            },
            "X-Rate-Limit-Remaining": {
                "description": "The number of remaining requests in the current period",
                "schema": {"type": "integer"}
            },
            "X-Rate-Limit-Reset": {
                "description": "The time at which the current rate limit window resets",
                "schema": {"type": "integer"}
            }
        }
    
    def _design_tags(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Design API tags for grouping endpoints."""
        tags = []
        
        for entity in entities:
            tags.append({
                "name": entity["name"],
                "description": f"Operations related to {entity['name']}"
            })
        
        # Add common tags
        tags.extend([
            {"name": "health", "description": "Health check operations"},
            {"name": "auth", "description": "Authentication operations"}
        ])
        
        return tags
    
    def _design_external_docs(self, project_name: str) -> Dict[str, Any]:
        """Design external documentation links."""
        return {
            "description": f"Find more info about {project_name} API",
            "url": "https://example.com/docs"
        }
    
    async def _design_security_comprehensive(
        self, 
        security_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Design comprehensive security for the API."""
        security_design = {
            "schemes": {},
            "global_security": []
        }
        
        # Design security schemes based on requirements
        auth_methods = security_requirements.get("authentication", [])
        
        if "jwt" in auth_methods:
            security_design["schemes"]["BearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Bearer token authentication"
            }
            security_design["global_security"].append({"BearerAuth": []})
        
        if "oauth" in auth_methods:
            security_design["schemes"]["OAuth2"] = {
                "type": "oauth2",
                "description": "OAuth2 authentication",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://example.com/oauth/authorize",
                        "tokenUrl": "https://example.com/oauth/token",
                        "scopes": {
                            "read": "Read access to resources",
                            "write": "Write access to resources",
                            "admin": "Administrative access"
                        }
                    }
                }
            }
            security_design["global_security"].append({"OAuth2": ["read", "write"]})
        
        if "api_key" in auth_methods:
            security_design["schemes"]["ApiKeyAuth"] = {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key authentication"
            }
            security_design["global_security"].append({"ApiKeyAuth": []})
        
        # Default to Bearer auth if no specific auth mentioned
        if not auth_methods:
            security_design["schemes"]["BearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "description": "Bearer token authentication"
            }
            security_design["global_security"].append({"BearerAuth": []})
        
        return security_design
    
    def _determine_endpoint_security(
        self, 
        endpoint: Dict[str, Any], 
        security_design: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Determine security requirements for a specific endpoint."""
        # Use global security by default
        return security_design.get("global_security", [])
    
    def _identify_design_patterns(self, api_design: Dict[str, Any]) -> List[str]:
        """Identify design patterns used in the API."""
        patterns = []
        
        # Check for RESTful patterns
        paths = api_design.get("paths", {})
        if paths:
            patterns.append("RESTful")
        
        # Check for CRUD patterns
        methods_found = set()
        for path_methods in paths.values():
            methods_found.update(path_methods.keys())
        
        if {"get", "post", "put", "delete"}.issubset(methods_found):
            patterns.append("CRUD")
        
        # Check for pagination
        if any("page" in str(path_methods) for path_methods in paths.values()):
            patterns.append("Pagination")
        
        # Check for search
        if any("/search" in path for path in paths.keys()):
            patterns.append("Search")
        
        # Check for security
        if "security" in api_design:
            patterns.append("Security")
        
        return patterns
    
    def _increment_version(self, current_version: str) -> str:
        """Increment API version."""
        try:
            parts = current_version.split('.')
            if len(parts) >= 3:
                parts[2] = str(int(parts[2]) + 1)
            elif len(parts) == 2:
                parts.append("1")
            else:
                return "1.0.1"
            return '.'.join(parts)
        except (ValueError, IndexError):
            return "1.0.1"

    def _custom_goal_check(self, goal: Goal) -> bool:
        """Custom goal checking for API Design Agent."""
        objective = goal.objective.lower()
        
        # Handle specific goal patterns that this agent can execute
        design_patterns = [
            "design_api_structure",
            "design_api",
            "api_structure",
            "create_api_design",
            "generate_api_design",
            "structure_api",
            "architect_api"
        ]
        
        return any(pattern in objective for pattern in design_patterns)
