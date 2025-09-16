"""
Documentation Agent for API Specification Writing System
Generates comprehensive documentation for API specifications
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from .base_agent import SpecializedAgent, Goal, AgentResult, AgentCapability, create_success_result, create_error_result


class DocumentationAgent(SpecializedAgent):
    """
    Specialized agent for generating API documentation.
    
    This agent creates comprehensive documentation including:
    - Getting started guides
    - Authentication documentation
    - Error handling guides
    - Code examples
    - API reference documentation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Documentation Agent."""
        super().__init__(
            name="documentation_agent",
            capabilities=[
                AgentCapability.DOCUMENTATION,
                AgentCapability.MARKDOWN_GENERATION,
                AgentCapability.EXAMPLE_GENERATION,
                AgentCapability.TEXT_PROCESSING,
                AgentCapability.FORMAT_CONVERSION
            ],
            description="Generates comprehensive API documentation",
            config=config or {},
            specialization="documentation"
        )
        
        # Documentation templates and patterns
        self.add_knowledge("doc_templates", {
            "getting_started": {
                "sections": ["introduction", "authentication", "first_request", "response_format"],
                "include_examples": True,
                "include_troubleshooting": True
            },
            "authentication": {
                "cover_all_schemes": True,
                "include_examples": True,
                "include_error_scenarios": True
            },
            "error_handling": {
                "list_all_codes": True,
                "include_examples": True,
                "provide_solutions": True
            }
        })
        
        self.add_knowledge("code_examples", {
            "languages": ["curl", "javascript", "python", "java"],
            "include_headers": True,
            "include_error_handling": True,
            "show_response_examples": True
        })
    
    async def execute_goal(self, goal: Goal) -> AgentResult:
        """Execute documentation generation goals."""
        try:
            objective = goal.objective.lower()
            
            if "generate_api_documentation" in objective or "generate_documentation" in objective:
                return await self._generate_api_documentation(goal)
            elif "generate_getting_started" in objective:
                return await self._generate_getting_started(goal)
            elif "generate_authentication_docs" in objective:
                return await self._generate_authentication_docs(goal)
            elif "generate_error_handling_docs" in objective:
                return await self._generate_error_handling_docs(goal)
            elif "generate_code_examples" in objective:
                return await self._generate_code_examples(goal)
            else:
                return create_error_result(f"Unknown objective: {goal.objective}")
                
        except Exception as e:
            self.logger.error(f"Error executing goal {goal.objective}: {str(e)}")
            return create_error_result(str(e))
    
    async def _generate_api_documentation(self, goal: Goal) -> AgentResult:
        """Generate comprehensive API documentation."""
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
        
        project_name = goal.parameters.get("project_name", "API")
        include_examples = goal.parameters.get("include_examples", True)
        include_getting_started = goal.parameters.get("include_getting_started", True)
        include_authentication = goal.parameters.get("include_authentication", True)
        include_error_handling = goal.parameters.get("include_error_handling", True)
        doc_format = goal.parameters.get("format", "markdown")
        
        if not specification:
            return create_error_result("No specification provided for documentation generation")
        
        self.logger.info(f"Generating comprehensive documentation for {project_name}")
        self.logger.info(f"Using specification: {type(specification)} with keys: {list(specification.keys()) if isinstance(specification, dict) else 'non-dict'}")
        
        # Build documentation sections
        documentation_sections = []
        
        # Title and introduction
        api_info = specification.get("info", {})
        title = api_info.get("title", project_name)
        version = api_info.get("version", "1.0.0")
        description = api_info.get("description", f"API documentation for {project_name}")
        
        documentation_sections.append(f"# {title}")
        documentation_sections.append(f"**Version:** {version}")
        documentation_sections.append("")
        documentation_sections.append(description)
        documentation_sections.append("")
        
        # Table of contents
        toc_sections = ["## Table of Contents"]
        section_count = 1
        
        if include_getting_started:
            toc_sections.append(f"{section_count}. [Getting Started](#getting-started)")
            section_count += 1
        
        if include_authentication:
            toc_sections.append(f"{section_count}. [Authentication](#authentication)")
            section_count += 1
        
        toc_sections.append(f"{section_count}. [API Reference](#api-reference)")
        section_count += 1
        
        if include_error_handling:
            toc_sections.append(f"{section_count}. [Error Handling](#error-handling)")
            section_count += 1
        
        toc_sections.append(f"{section_count}. [Response Formats](#response-formats)")
        
        documentation_sections.extend(toc_sections)
        documentation_sections.append("")
        
        # Getting started section
        if include_getting_started:
            getting_started = await self._build_getting_started_section(specification, include_examples)
            documentation_sections.extend(getting_started)
        
        # Authentication section
        if include_authentication:
            auth_docs = await self._build_authentication_section(specification, include_examples)
            documentation_sections.extend(auth_docs)
        
        # API Reference section
        api_reference = await self._build_api_reference_section(specification, include_examples)
        documentation_sections.extend(api_reference)
        
        # Error handling section
        if include_error_handling:
            error_docs = await self._build_error_handling_section(specification, include_examples)
            documentation_sections.extend(error_docs)
        
        # Response formats section
        response_formats = await self._build_response_formats_section(specification)
        documentation_sections.extend(response_formats)
        
        # Combine all sections
        full_documentation = "\n".join(documentation_sections)
        
        # Add metadata
        metadata = {
            "generation_timestamp": datetime.now().isoformat(),
            "project_name": project_name,
            "format": doc_format,
            "sections_included": {
                "getting_started": include_getting_started,
                "authentication": include_authentication,
                "error_handling": include_error_handling,
                "examples": include_examples
            },
            "total_length": len(full_documentation),
            "total_lines": len(full_documentation.split('\n'))
        }
        
        self.logger.info(f"Documentation generated: {metadata['total_lines']} lines")
        
        return create_success_result(full_documentation, metadata, confidence=0.9)
    
    async def _build_getting_started_section(
        self, 
        specification: Dict[str, Any], 
        include_examples: bool
    ) -> List[str]:
        """Build getting started section."""
        section = ["## Getting Started", ""]
        
        # Introduction
        section.extend([
            "This guide will help you get started with the API quickly.",
            ""
        ])
        
        # Base URL
        servers = specification.get("servers", [])
        if servers:
            base_url = servers[0].get("url", "https://api.example.com")
            section.extend([
                "### Base URL",
                "",
                f"```",
                f"{base_url}",
                f"```",
                ""
            ])
        
        # Prerequisites
        section.extend([
            "### Prerequisites",
            "",
            "- API key or authentication credentials",
            "- HTTP client (curl, Postman, or programming language HTTP library)",
            "- Basic understanding of REST APIs and JSON",
            ""
        ])
        
        # First request example
        if include_examples:
            section.extend(await self._build_first_request_example(specification))
        
        return section
    
    async def _build_first_request_example(self, specification: Dict[str, Any]) -> List[str]:
        """Build first request example."""
        section = ["### Your First Request", ""]
        
        # Find a simple GET endpoint
        paths = specification.get("paths", {})
        simple_endpoint = None
        
        for path, path_item in paths.items():
            if "get" in path_item:
                simple_endpoint = (path, path_item["get"])
                break
        
        if simple_endpoint:
            path, operation = simple_endpoint
            
            section.extend([
                f"Let's start with a simple request to `{path}`:",
                "",
                "#### Using curl:",
                "",
                "```bash",
                f"curl -X GET \\",
                f"  https://api.example.com{path} \\",
                f"  -H 'Authorization: Bearer YOUR_API_KEY' \\",
                f"  -H 'Content-Type: application/json'",
                "```",
                ""
            ])
            
            # Add response example
            responses = operation.get("responses", {})
            if "200" in responses:
                section.extend([
                    "#### Response:",
                    "",
                    "```json",
                    "{",
                    '  "status": "success",',
                    '  "data": {',
                    '    "message": "Hello, World!"',
                    "  }",
                    "}",
                    "```",
                    ""
                ])
        
        return section
    
    async def _build_authentication_section(
        self, 
        specification: Dict[str, Any], 
        include_examples: bool
    ) -> List[str]:
        """Build authentication section."""
        section = ["## Authentication", ""]
        
        # Check for security schemes
        security_schemes = specification.get("components", {}).get("securitySchemes", {})
        
        if not security_schemes:
            section.extend([
                "This API does not require authentication.",
                ""
            ])
            return section
        
        section.extend([
            "This API uses the following authentication methods:",
            ""
        ])
        
        for scheme_name, scheme in security_schemes.items():
            section.extend(await self._build_auth_scheme_docs(scheme_name, scheme, include_examples))
        
        return section
    
    async def _build_auth_scheme_docs(
        self, 
        scheme_name: str, 
        scheme: Dict[str, Any], 
        include_examples: bool
    ) -> List[str]:
        """Build documentation for a specific auth scheme."""
        section = [f"### {scheme_name}", ""]
        
        scheme_type = scheme.get("type", "")
        description = scheme.get("description", "")
        
        if description:
            section.extend([description, ""])
        
        if scheme_type == "http":
            if scheme.get("scheme") == "bearer":
                section.extend([
                    "**Type:** Bearer Token",
                    "",
                    "Include your token in the Authorization header:",
                    ""
                ])
                
                if include_examples:
                    section.extend([
                        "```bash",
                        "curl -H 'Authorization: Bearer YOUR_TOKEN' \\",
                        "  https://api.example.com/endpoint",
                        "```",
                        ""
                    ])
        
        elif scheme_type == "apiKey":
            header_name = scheme.get("name", "X-API-Key")
            section.extend([
                "**Type:** API Key",
                "",
                f"Include your API key in the `{header_name}` header:",
                ""
            ])
            
            if include_examples:
                section.extend([
                    "```bash",
                    f"curl -H '{header_name}: YOUR_API_KEY' \\",
                    "  https://api.example.com/endpoint",
                    "```",
                    ""
                ])
        
        elif scheme_type == "oauth2":
            section.extend([
                "**Type:** OAuth 2.0",
                "",
                "This API supports OAuth 2.0 authentication.",
                ""
            ])
            
            flows = scheme.get("flows", {})
            if flows:
                section.extend(["**Supported flows:**", ""])
                for flow_name, flow in flows.items():
                    section.append(f"- {flow_name.replace('_', ' ').title()}")
                section.append("")
        
        return section
    
    async def _build_api_reference_section(
        self, 
        specification: Dict[str, Any], 
        include_examples: bool
    ) -> List[str]:
        """Build API reference section."""
        section = ["## API Reference", ""]
        
        paths = specification.get("paths", {})
        if not paths:
            section.extend(["No endpoints documented.", ""])
            return section
        
        # Group endpoints by tags
        tagged_endpoints = {}
        untagged_endpoints = []
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                tags = operation.get("tags", [])
                if tags:
                    tag = tags[0]  # Use first tag
                    if tag not in tagged_endpoints:
                        tagged_endpoints[tag] = []
                    tagged_endpoints[tag].append((path, method, operation))
                else:
                    untagged_endpoints.append((path, method, operation))
        
        # Document tagged endpoints
        for tag in sorted(tagged_endpoints.keys()):
            section.extend([f"### {tag.title()}", ""])
            
            for path, method, operation in tagged_endpoints[tag]:
                section.extend(await self._build_endpoint_docs(path, method, operation, include_examples))
        
        # Document untagged endpoints
        if untagged_endpoints:
            section.extend(["### Other Endpoints", ""])
            for path, method, operation in untagged_endpoints:
                section.extend(await self._build_endpoint_docs(path, method, operation, include_examples))
        
        return section
    
    async def _build_endpoint_docs(
        self, 
        path: str, 
        method: str, 
        operation: Dict[str, Any], 
        include_examples: bool
    ) -> List[str]:
        """Build documentation for a single endpoint."""
        section = [f"#### {method.upper()} {path}", ""]
        
        # Summary and description
        summary = operation.get("summary", "")
        description = operation.get("description", "")
        
        if summary:
            section.extend([summary, ""])
        
        if description and description != summary:
            section.extend([description, ""])
        
        # Parameters
        parameters = operation.get("parameters", [])
        if parameters:
            section.extend(["**Parameters:**", ""])
            
            for param in parameters:
                param_name = param.get("name", "")
                param_type = param.get("schema", {}).get("type", "string")
                param_desc = param.get("description", "")
                param_required = param.get("required", False)
                param_location = param.get("in", "")
                
                required_text = " (required)" if param_required else " (optional)"
                section.append(f"- `{param_name}` ({param_location}, {param_type}){required_text}: {param_desc}")
            
            section.append("")
        
        # Request body
        request_body = operation.get("requestBody", {})
        if request_body:
            section.extend(["**Request Body:**", ""])
            
            content = request_body.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                section.extend(await self._build_schema_docs(schema))
        
        # Responses
        responses = operation.get("responses", {})
        if responses:
            section.extend(["**Responses:**", ""])
            
            for status_code, response in responses.items():
                if isinstance(response, dict) and "description" in response:
                    desc = response["description"]
                    section.append(f"- `{status_code}`: {desc}")
            
            section.append("")
        
        # Examples
        if include_examples:
            section.extend(await self._build_endpoint_examples(path, method, operation))
        
        section.append("---")
        section.append("")
        
        return section
    
    async def _build_schema_docs(self, schema: Dict[str, Any]) -> List[str]:
        """Build documentation for a schema."""
        section = []
        
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            if properties:
                section.extend(["```json", "{"])
                
                for prop_name, prop_schema in properties.items():
                    prop_type = prop_schema.get("type", "string")
                    prop_desc = prop_schema.get("description", "")
                    is_required = prop_name in required
                    
                    comment = f"  // {prop_desc}" if prop_desc else ""
                    required_marker = " (required)" if is_required else ""
                    
                    if prop_type == "string":
                        section.append(f'  "{prop_name}": "string_value"{required_marker}{comment}')
                    elif prop_type == "integer":
                        section.append(f'  "{prop_name}": 123{required_marker}{comment}')
                    elif prop_type == "boolean":
                        section.append(f'  "{prop_name}": true{required_marker}{comment}')
                    else:
                        section.append(f'  "{prop_name}": "value"{required_marker}{comment}')
                
                section.extend(["}", "```", ""])
        
        return section
    
    async def _build_endpoint_examples(
        self, 
        path: str, 
        method: str, 
        operation: Dict[str, Any]
    ) -> List[str]:
        """Build examples for an endpoint."""
        section = ["**Example:**", ""]
        
        # Build curl example
        section.extend([
            "```bash",
            f"curl -X {method.upper()} \\",
            f"  https://api.example.com{path} \\",
            "  -H 'Authorization: Bearer YOUR_TOKEN' \\",
            "  -H 'Content-Type: application/json'"
        ])
        
        # Add request body if needed
        if method.upper() in ["POST", "PUT", "PATCH"]:
            section.extend([
                "  -d '{",
                '    "example": "data"',
                "  }'"
            ])
        
        section.extend(["```", ""])
        
        return section
    
    async def _build_error_handling_section(
        self, 
        specification: Dict[str, Any], 
        include_examples: bool
    ) -> List[str]:
        """Build error handling section."""
        section = ["## Error Handling", ""]
        
        section.extend([
            "The API uses standard HTTP response codes to indicate success or failure.",
            ""
        ])
        
        # Common error codes
        error_codes = {
            "400": "Bad Request - The request was invalid or cannot be served",
            "401": "Unauthorized - Authentication is required",
            "403": "Forbidden - The request is valid but not allowed",
            "404": "Not Found - The requested resource was not found",
            "422": "Unprocessable Entity - Validation errors",
            "500": "Internal Server Error - Something went wrong on our end"
        }
        
        section.extend(["### HTTP Status Codes", ""])
        
        for code, description in error_codes.items():
            section.append(f"- `{code}`: {description}")
        
        section.append("")
        
        # Error response format
        if include_examples:
            section.extend([
                "### Error Response Format",
                "",
                "```json",
                "{",
                '  "error": {',
                '    "code": "VALIDATION_ERROR",',
                '    "message": "Invalid input provided",',
                '    "details": {',
                '      "field": "email",',
                '      "issue": "Invalid email format"',
                "    }",
                "  }",
                "}",
                "```",
                ""
            ])
        
        return section
    
    async def _build_response_formats_section(self, specification: Dict[str, Any]) -> List[str]:
        """Build response formats section."""
        section = ["## Response Formats", ""]
        
        section.extend([
            "All responses are returned in JSON format with appropriate HTTP status codes.",
            "",
            "### Success Response Format",
            "",
            "```json",
            "{",
            '  "status": "success",',
            '  "data": {',
            '    // Response data here',
            "  }",
            "}",
            "```",
            ""
        ])
        
        return section
    
    async def _generate_getting_started(self, goal: Goal) -> AgentResult:
        """Generate getting started guide."""
        specification = goal.parameters.get("specification", {})
        
        getting_started = await self._build_getting_started_section(specification, True)
        documentation = "\n".join(getting_started)
        
        return create_success_result(documentation)
    
    async def _generate_authentication_docs(self, goal: Goal) -> AgentResult:
        """Generate authentication documentation."""
        specification = goal.parameters.get("specification", {})
        
        auth_docs = await self._build_authentication_section(specification, True)
        documentation = "\n".join(auth_docs)
        
        return create_success_result(documentation)
    
    async def _generate_error_handling_docs(self, goal: Goal) -> AgentResult:
        """Generate error handling documentation."""
        specification = goal.parameters.get("specification", {})
        
        error_docs = await self._build_error_handling_section(specification, True)
        documentation = "\n".join(error_docs)
        
        return create_success_result(documentation)
    
    async def _generate_code_examples(self, goal: Goal) -> AgentResult:
        """Generate code examples."""
        specification = goal.parameters.get("specification", {})
        languages = goal.parameters.get("languages", ["curl", "javascript", "python"])
        
        examples = {}
        
        # Generate examples for each language
        for language in languages:
            examples[language] = await self._build_language_examples(specification, language)
        
        return create_success_result(examples)
    
    async def _build_language_examples(self, specification: Dict[str, Any], language: str) -> str:
        """Build code examples for a specific language."""
        if language == "curl":
            return self._build_curl_examples(specification)
        elif language == "javascript":
            return self._build_javascript_examples(specification)
        elif language == "python":
            return self._build_python_examples(specification)
        else:
            return f"# {language.title()} examples not implemented yet"
    
    def _build_curl_examples(self, specification: Dict[str, Any]) -> str:
        """Build curl examples."""
        examples = ["# curl Examples", ""]
        
        paths = specification.get("paths", {})
        for path, path_item in list(paths.items())[:3]:  # Limit to first 3 endpoints
            for method, operation in path_item.items():
                summary = operation.get("summary", f"{method.upper()} {path}")
                examples.extend([
                    f"## {summary}",
                    "",
                    "```bash",
                    f"curl -X {method.upper()} \\",
                    f"  https://api.example.com{path} \\",
                    "  -H 'Authorization: Bearer YOUR_TOKEN' \\",
                    "  -H 'Content-Type: application/json'",
                    "```",
                    ""
                ])
        
        return "\n".join(examples)
    
    def _build_javascript_examples(self, specification: Dict[str, Any]) -> str:
        """Build JavaScript examples."""
        examples = ["// JavaScript Examples", ""]
        
        examples.extend([
            "const apiClient = {",
            "  baseURL: 'https://api.example.com',",
            "  token: 'YOUR_TOKEN',",
            "",
            "  async request(method, path, data = null) {",
            "    const response = await fetch(`${this.baseURL}${path}`, {",
            "      method,",
            "      headers: {",
            "        'Authorization': `Bearer ${this.token}`,",
            "        'Content-Type': 'application/json'",
            "      },",
            "      body: data ? JSON.stringify(data) : null",
            "    });",
            "    return response.json();",
            "  }",
            "};",
            ""
        ])
        
        return "\n".join(examples)
    
    def _build_python_examples(self, specification: Dict[str, Any]) -> str:
        """Build Python examples."""
        examples = ["# Python Examples", ""]
        
        examples.extend([
            "import requests",
            "",
            "class APIClient:",
            "    def __init__(self, base_url, token):",
            "        self.base_url = base_url",
            "        self.token = token",
            "        self.session = requests.Session()",
            "        self.session.headers.update({",
            "            'Authorization': f'Bearer {token}',",
            "            'Content-Type': 'application/json'",
            "        })",
            "",
            "    def request(self, method, path, data=None):",
            "        url = f'{self.base_url}{path}'",
            "        response = self.session.request(method, url, json=data)",
            "        return response.json()",
            "",
            "# Usage",
            "client = APIClient('https://api.example.com', 'YOUR_TOKEN')",
            ""
        ])
        
        return "\n".join(examples)

    def _custom_goal_check(self, goal: Goal) -> bool:
        """Custom goal checking for Documentation Agent."""
        objective = goal.objective.lower()
        
        # Handle specific goal patterns that this agent can execute
        documentation_patterns = [
            "generate_documentation",
            "create_documentation", 
            "write_documentation",
            "document_api",
            "generate_docs",
            "create_docs",
            "api_documentation"
        ]
        
        return any(pattern in objective for pattern in documentation_patterns)
