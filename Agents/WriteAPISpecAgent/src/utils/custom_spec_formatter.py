"""
Custom Specification Formatter
Converts standard OpenAPI specifications to the custom YAML format
used in the Agents/API-requirements folder
"""

import yaml
from typing import Dict, Any, List
from datetime import datetime
from collections import OrderedDict


def convert_openapi_to_custom_format(
    openapi_spec: Dict[str, Any],
    requirements: str,
    project_name: str,
    technology: str = "java_springboot"
) -> Dict[str, Any]:
    """
    Convert standard OpenAPI specification to custom API requirements format.
    
    Args:
        openapi_spec: Standard OpenAPI 3.x specification
        requirements: Original requirements text
        project_name: Name of the project
        technology: Technology stack (java_springboot, nodejs_express, etc.)
    
    Returns:
        Dictionary in the custom format matching the examples
    """
    
    # Extract basic info
    info = openapi_spec.get("info", {})
    paths = openapi_spec.get("paths", {})
    components = openapi_spec.get("components", {})
    security_schemes = components.get("securitySchemes", {})
    
    # Build the custom format
    custom_spec = {}
    
    # Metadata section
    custom_spec["metadata"] = {
        "api_name": project_name,
        "version": info.get("version", "1.0.0"),
        "description": requirements[:100] + "..." if len(requirements) > 100 else requirements,
        "team": "Development Team",
        "owner": "tech-lead@company.com",
        "generated_at": datetime.now().isoformat(),
        "generated_from": "WriteAPISpecAgent"
    }
    
    # Configuration section
    custom_spec["configuration"] = _extract_configuration(technology)
    
    # API Contract section
    custom_spec["api_contract"] = _build_api_contract(openapi_spec, paths, components)
    
    # Business Logic section
    custom_spec["business_logic"] = _extract_business_logic(paths, components)
    
    # Testing section
    custom_spec["testing"] = _build_testing_section(paths)
    
    # Monitoring section
    custom_spec["monitoring"] = _build_monitoring_section(paths)
    
    return custom_spec


def _extract_configuration(technology: str) -> Dict[str, Any]:
    """Extract configuration based on technology stack."""
    config_mapping = {
        "java_springboot": {
            "language": "Java",
            "framework": "Spring Boot",
            "database": "PostgreSQL",
            "caching": "Redis",
            "messaging": "Kafka"
        },
        "nodejs_express": {
            "language": "NodeJS",
            "framework": "Express.js",
            "database": "MongoDB",
            "caching": "Redis",
            "messaging": "RabbitMQ"
        },
        "dotnet_webapi": {
            "language": ".NET",
            "framework": "ASP.NET Core",
            "database": "SQL Server",
            "caching": "Redis",
            "messaging": "Azure Service Bus"
        }
    }
    
    return config_mapping.get(technology, config_mapping["java_springboot"])


def _build_api_contract(openapi_spec: Dict[str, Any], paths: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    """Build the API contract section in custom format."""
    info = openapi_spec.get("info", {})
    servers = openapi_spec.get("servers", [])
    security = openapi_spec.get("security", [])
    
    api_contract = {}
    api_contract["format"] = "OpenAPI"
    api_contract["version"] = openapi_spec.get("openapi", "3.0.3")
    
    # Extract base path from servers
    base_path = "/api/v1"
    if servers:
        first_server = servers[0].get("url", "")
        if "/v1" in first_server:
            base_path = "/api/v1"
        elif "/api" in first_server:
            base_path = first_server.split("/api")[1] or "/api/v1"
    
    api_contract["base_path"] = base_path
    
    # Security
    if security or components.get("securitySchemes"):
        api_contract["security"] = _extract_security_info(security, components.get("securitySchemes", {}))
    
    # Endpoints
    api_contract["endpoints"] = _convert_paths_to_endpoints(paths)
    
    return api_contract


def _extract_security_info(security: List[Dict[str, Any]], security_schemes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract security information in custom format."""
    security_info = []
    
    for scheme_name, scheme_def in security_schemes.items():
        security_item = {
            "type": scheme_def.get("type", "").upper(),
            "scopes": ["read", "write"]
        }
        
        if scheme_def.get("type") == "http" and scheme_def.get("scheme") == "bearer":
            security_item["type"] = "JWT"
        elif scheme_def.get("type") == "apiKey":
            security_item["type"] = "API_KEY"
            security_item["header"] = scheme_def.get("name", "X-API-Key")
        
        security_info.append(security_item)
    
    return security_info


def _convert_paths_to_endpoints(paths: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert OpenAPI paths to custom endpoint format."""
    endpoints = []
    
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            endpoint = {}
            endpoint["path"] = path
            endpoint["method"] = method.upper()
            endpoint["summary"] = operation.get("summary", f"{method.upper()} {path}")
            endpoint["description"] = operation.get("description", endpoint["summary"])
            
            # Tags
            if "tags" in operation:
                endpoint["tags"] = operation["tags"]
            
            # Security
            if "security" in operation:
                endpoint["security"] = operation["security"]
            
            # Request
            request_info = {}
            request_info["content_type"] = "application/json"
            
            # Headers
            if "parameters" in operation:
                headers = [p["name"] for p in operation["parameters"] if p.get("in") == "header"]
                if headers:
                    request_info["required_headers"] = headers
            
            # Path parameters
            path_params = {}
            if "parameters" in operation:
                for param in operation["parameters"]:
                    if param.get("in") == "path":
                        path_params[param["name"]] = param.get("schema", {}).get("type", "string")
            
            if path_params:
                request_info["path_parameters"] = path_params
            
            # Request body schema
            if "requestBody" in operation:
                request_body = operation["requestBody"]
                content = request_body.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    request_info["schema"] = _simplify_schema(schema)
            
            if len(request_info) > 1:  # More than just content_type
                endpoint["request"] = request_info
            
            # Response
            responses = operation.get("responses", {})
            endpoint["response"] = _convert_responses(responses)
            
            endpoints.append(endpoint)
    
    return endpoints


def _convert_responses(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Convert OpenAPI responses to custom format."""
    response_info = {}
    
    # Success response
    for status_code in ["200", "201", "202", "204"]:
        if status_code in responses:
            response = responses[status_code]
            response_info["success"] = {
                "status": int(status_code),
                "content_type": "application/json"
            }
            
            if "description" in response:
                response_info["success"]["description"] = response["description"]
            
            # Extract schema from content
            content = response.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                response_info["success"]["schema"] = _simplify_schema(schema)
            
            break
    
    # Error responses
    error_responses = []
    for status_code, response in responses.items():
        if status_code.startswith("4") or status_code.startswith("5"):
            error_resp = {
                "status": int(status_code),
                "description": response.get("description", f"Error {status_code}")
            }
            
            content = response.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                error_resp["schema"] = _simplify_schema(schema)
            
            error_responses.append(error_resp)
    
    if error_responses:
        response_info["errors"] = error_responses
    
    return response_info


def _simplify_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Simplify OpenAPI schema to custom format."""
    if not schema:
        return {}
    
    simplified = {}
    
    if "type" in schema:
        simplified["type"] = schema["type"]
    
    if "properties" in schema:
        props = {}
        for prop_name, prop_def in schema["properties"].items():
            if isinstance(prop_def, dict):
                prop_simple = {
                    "type": prop_def.get("type", "string")
                }
                if "description" in prop_def:
                    prop_simple["description"] = prop_def["description"]
                if "format" in prop_def:
                    prop_simple["format"] = prop_def["format"]
                if "minLength" in prop_def:
                    prop_simple["minLength"] = prop_def["minLength"]
                if "maxLength" in prop_def:
                    prop_simple["maxLength"] = prop_def["maxLength"]
                
                props[prop_name] = prop_simple
        
        simplified["properties"] = props
    
    if "required" in schema:
        simplified["required"] = schema["required"]
    
    return simplified


def _extract_business_logic(paths: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    """Extract business logic patterns from the API specification."""
    business_logic = {}
    
    # Validation rules
    validation_rules = []
    schemas = components.get("schemas", {})
    
    for schema_name, schema_def in schemas.items():
        if "properties" in schema_def:
            for prop_name, prop_def in schema_def["properties"].items():
                if "format" in prop_def and prop_def["format"] == "email":
                    validation_rules.append({
                        "name": f"{prop_name}_format",
                        "description": f"{prop_name.capitalize()} must be in valid format",
                        "pattern": "^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\\.[A-Za-z]{2,})$"
                    })
    
    if validation_rules:
        business_logic["validation_rules"] = validation_rules
    
    # Workflows
    workflows = []
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method.upper() in ["POST", "PUT", "PATCH"]:
                workflow = {
                    "endpoint": f"{method.upper()} {path}",
                    "steps": [
                        {
                            "name": "Input Validation",
                            "description": "Validate input data"
                        },
                        {
                            "name": "Business Logic",
                            "description": "Apply business rules"
                        },
                        {
                            "name": "Data Persistence",
                            "description": "Save to database"
                        },
                        {
                            "name": "Response Generation",
                            "description": "Generate response"
                        }
                    ]
                }
                workflows.append(workflow)
    
    if workflows:
        business_logic["workflows"] = workflows
    
    return business_logic


def _build_testing_section(paths: Dict[str, Any]) -> Dict[str, Any]:
    """Build testing section with sample test scenarios."""
    testing = {}
    
    # Unit tests
    unit_tests = {
        "services": [
            {
                "test": "api_service_tests",
                "scenarios": [
                    {
                        "name": "successful_operation",
                        "given": {"valid_input": True},
                        "when": {"call_api": "with_valid_data"},
                        "then": {"success": True}
                    }
                ]
            }
        ]
    }
    
    # Integration tests
    integration_tests = {
        "api_endpoints": []
    }
    
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            test_scenario = {
                "test": f"{method.upper()} {path}",
                "scenarios": [
                    {
                        "name": "valid_request",
                        "request": {
                            "headers": {"Content-Type": "application/json"}
                        },
                        "response": {
                            "status": 200,
                            "body": {"success": True}
                        }
                    }
                ]
            }
            integration_tests["api_endpoints"].append(test_scenario)
    
    testing["unit_tests"] = unit_tests
    testing["integration_tests"] = integration_tests
    
    # Performance tests
    testing["performance_tests"] = {
        "scenarios": [
            {
                "name": "api_load_test",
                "type": "load_test",
                "duration": "5m",
                "target_rps": 50,
                "success_criteria": {
                    "p95_latency_ms": 200,
                    "error_rate": "0.1%"
                }
            }
        ]
    }
    
    return testing


def _build_monitoring_section(paths: Dict[str, Any]) -> Dict[str, Any]:
    """Build monitoring section with metrics and alerts."""
    monitoring = {}
    
    # Metrics
    monitoring["metrics"] = [
        {
            "name": "api_requests_total",
            "type": "counter",
            "labels": ["method", "path", "status"]
        },
        {
            "name": "api_request_duration",
            "type": "histogram",
            "buckets": [10, 50, 100, 200, 500]
        }
    ]
    
    # Alerts
    monitoring["alerts"] = [
        {
            "name": "high_error_rate",
            "condition": "error_rate > 5% for 5m",
            "severity": "critical",
            "notification": "slack#incidents"
        }
    ]
    
    # Logging
    monitoring["logging"] = {
        "required_fields": [
            "correlation_id",
            "request_path",
            "status_code",
            "duration_ms"
        ]
    }
    
    return monitoring


def format_as_yaml(custom_spec: Dict[str, Any]) -> str:
    """Format the custom specification as YAML string."""
    
    # Convert OrderedDict to regular dict to avoid Python object serialization
    def convert_ordered_dict(obj):
        if isinstance(obj, OrderedDict):
            return dict(obj)
        elif isinstance(obj, dict):
            return {k: convert_ordered_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_ordered_dict(item) for item in obj]
        else:
            return obj
    
    clean_spec = convert_ordered_dict(custom_spec)
    
    return yaml.dump(
        clean_spec,
        default_flow_style=False,
        indent=2,
        sort_keys=False,
        allow_unicode=True,
        width=120
    )
