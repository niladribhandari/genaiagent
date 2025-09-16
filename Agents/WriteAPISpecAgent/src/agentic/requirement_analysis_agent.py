"""
Requirement Analysis Agent for API Specification Writing System
Analyzes user requirements to extract API needs and specifications
"""

import re
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime

from .base_agent import SpecializedAgent, Goal, AgentResult, AgentCapability, create_success_result, create_error_result


class RequirementAnalysisAgent(SpecializedAgent):
    """
    Specialized agent for analyzing user requirements and extracting API specifications.
    
    This agent processes natural language requirements and identifies:
    - API endpoints and operations
    - Data models and schemas
    - Business rules and constraints
    - Security requirements
    - Performance requirements
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Requirement Analysis Agent."""
        super().__init__(
            name="requirement_analysis_agent",
            capabilities=[
                AgentCapability.REQUIREMENT_ANALYSIS,
                AgentCapability.TEXT_PROCESSING,
                AgentCapability.ENTITY_EXTRACTION,
                AgentCapability.ENDPOINT_IDENTIFICATION,
                AgentCapability.DATA_MODEL_EXTRACTION
            ],
            description="Analyzes user requirements to extract API specifications",
            config=config or {},
            specialization="requirement_analysis"
        )
        
        # Pattern libraries for requirement analysis
        self.endpoint_patterns = [
            r"(?:create|add|insert|post)\s+(?:a\s+)?(\w+)",
            r"(?:get|retrieve|fetch|read)\s+(?:a\s+)?(\w+)",
            r"(?:update|modify|edit|change)\s+(?:a\s+)?(\w+)",
            r"(?:delete|remove)\s+(?:a\s+)?(\w+)",
            r"(?:list|show|display)\s+(?:all\s+)?(\w+)",
            r"(?:search|find|filter)\s+(\w+)",
        ]
        
        self.entity_patterns = [
            r"(\w+)\s+(?:entity|model|object|resource)",
            r"(?:manage|handle)\s+(\w+)",
            r"(\w+)\s+(?:data|information|details)",
            r"(\w+)\s+(?:table|collection|database)"
        ]
        
        self.operation_keywords = {
            "create": ["create", "add", "insert", "post", "new", "register"],
            "read": ["get", "retrieve", "fetch", "read", "show", "display", "view"],
            "update": ["update", "modify", "edit", "change", "patch"],
            "delete": ["delete", "remove", "destroy"],
            "list": ["list", "index", "all", "browse"],
            "search": ["search", "find", "filter", "query"]
        }
        
        # Common API patterns knowledge base
        self.add_knowledge("rest_patterns", {
            "create": {"method": "POST", "path_pattern": "/{resource}"},
            "read": {"method": "GET", "path_pattern": "/{resource}/{id}"},
            "update": {"method": "PUT", "path_pattern": "/{resource}/{id}"},
            "partial_update": {"method": "PATCH", "path_pattern": "/{resource}/{id}"},
            "delete": {"method": "DELETE", "path_pattern": "/{resource}/{id}"},
            "list": {"method": "GET", "path_pattern": "/{resource}"},
            "search": {"method": "GET", "path_pattern": "/{resource}/search"}
        })
    
    def _custom_goal_check(self, goal: Goal) -> bool:
        """Custom goal checking for requirement analysis objectives."""
        objective = goal.objective.lower()
        
        # Check for requirement analysis related objectives
        analysis_keywords = [
            "analyze", "requirements", "extract", "identify", 
            "determine", "parse", "process"
        ]
        
        return any(keyword in objective for keyword in analysis_keywords)
    
    async def execute_goal(self, goal: Goal) -> AgentResult:
        """Execute requirement analysis goals."""
        try:
            objective = goal.objective.lower()
            
            if "analyze_api_requirements" in objective:
                return await self._analyze_api_requirements(goal)
            elif "extract_entities" in objective:
                return await self._extract_entities(goal)
            elif "identify_endpoints" in objective:
                return await self._identify_endpoints(goal)
            elif "determine_data_models" in objective:
                return await self._determine_data_models(goal)
            elif "analyze_security_requirements" in objective:
                return await self._analyze_security_requirements(goal)
            else:
                return create_error_result(f"Unknown objective: {goal.objective}")
                
        except Exception as e:
            self.logger.error(f"Error executing goal {goal.objective}: {str(e)}")
            return create_error_result(str(e))
    
    async def _analyze_api_requirements(self, goal: Goal) -> AgentResult:
        """Main method to analyze complete API requirements."""
        requirements = goal.parameters.get("requirements", "")
        project_name = goal.parameters.get("project_name", "API")
        api_version = goal.parameters.get("api_version", "1.0.0")
        
        if not requirements:
            return create_error_result("No requirements provided for analysis")
        
        # Handle both string and structured requirements
        if isinstance(requirements, dict):
            # Extract information from structured requirements
            project_name = requirements.get("title", project_name)
            description = requirements.get("description", "")
            functional_reqs = requirements.get("functional_requirements", [])
            business_entities = requirements.get("business_entities", [])
            security_reqs = requirements.get("security_requirements", [])
            
            # Convert structured data to text for analysis
            requirements_text = f"""
            {description}
            
            Functional Requirements:
            {chr(10).join(f"- {req}" for req in functional_reqs)}
            
            Business Entities:
            {chr(10).join(f"- {entity}" for entity in business_entities)}
            
            Security Requirements:
            {chr(10).join(f"- {req}" for req in security_reqs)}
            """
        else:
            requirements_text = str(requirements)
        
        self.logger.info(f"Analyzing API requirements for project: {project_name}")
        
        # Perform comprehensive analysis
        analysis_result = {
            "project_info": {
                "name": project_name,
                "version": api_version,
                "description": self._extract_project_description(requirements_text)
            },
            "entities": await self._extract_entities_from_text(requirements_text),
            "endpoints": await self._identify_endpoints_from_text(requirements_text),
            "data_models": await self._determine_data_models_from_text(requirements_text),
            "security_requirements": await self._analyze_security_from_text(requirements_text),
            "business_rules": self._extract_business_rules(requirements_text),
            "performance_requirements": self._extract_performance_requirements(requirements_text),
            "technical_requirements": self._extract_technical_requirements(requirements_text),
            "validation_rules": self._extract_validation_rules(requirements_text)
        }
        
        # Add metadata about the analysis
        metadata = {
            "analysis_timestamp": datetime.now().isoformat(),
            "requirements_word_count": len(requirements_text.split()),
            "entities_found": len(analysis_result["entities"]),
            "endpoints_identified": len(analysis_result["endpoints"]),
            "data_models_detected": len(analysis_result["data_models"])
        }
        
        self.logger.info(
            f"Analysis complete: {metadata['entities_found']} entities, "
            f"{metadata['endpoints_identified']} endpoints, "
            f"{metadata['data_models_detected']} data models"
        )
        
        return create_success_result(analysis_result, metadata, confidence=0.9)
    
    async def _extract_entities(self, goal: Goal) -> AgentResult:
        """Extract entities from requirements text."""
        requirements = goal.parameters.get("requirements", "")
        entities = await self._extract_entities_from_text(requirements)
        
        return create_success_result(
            {"entities": entities},
            {"entity_count": len(entities)}
        )
    
    async def _identify_endpoints(self, goal: Goal) -> AgentResult:
        """Identify API endpoints from requirements text."""
        requirements = goal.parameters.get("requirements", "")
        endpoints = await self._identify_endpoints_from_text(requirements)
        
        return create_success_result(
            {"endpoints": endpoints},
            {"endpoint_count": len(endpoints)}
        )
    
    async def _determine_data_models(self, goal: Goal) -> AgentResult:
        """Determine data models from requirements text."""
        requirements = goal.parameters.get("requirements", "")
        data_models = await self._determine_data_models_from_text(requirements)
        
        return create_success_result(
            {"data_models": data_models},
            {"model_count": len(data_models)}
        )
    
    async def _analyze_security_requirements(self, goal: Goal) -> AgentResult:
        """Analyze security requirements from text."""
        requirements = goal.parameters.get("requirements", "")
        security_requirements = await self._analyze_security_from_text(requirements)
        
        return create_success_result(
            {"security_requirements": security_requirements},
            {"security_features_count": len(security_requirements.get("features", []))}
        )
    
    async def _extract_entities_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract business entities from requirements text."""
        entities = []
        text_lower = text.lower()
        
        # Use pattern matching to find entities
        for pattern in self.entity_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                entity_name = match.strip()
                if entity_name and entity_name not in [e["name"] for e in entities]:
                    entities.append({
                        "name": entity_name,
                        "type": "business_entity",
                        "source": "pattern_matching",
                        "context": self._extract_entity_context(text, entity_name)
                    })
        
        # Look for explicit mentions
        entity_keywords = ["customer", "user", "order", "product", "payment", "invoice", 
                          "address", "contact", "account", "transaction", "report"]
        
        for keyword in entity_keywords:
            if keyword in text_lower and keyword not in [e["name"] for e in entities]:
                entities.append({
                    "name": keyword,
                    "type": "business_entity",
                    "source": "keyword_matching",
                    "context": self._extract_entity_context(text, keyword)
                })
        
        # Enhance entities with attributes
        for entity in entities:
            entity["attributes"] = self._extract_entity_attributes(text, entity["name"])
            entity["relationships"] = self._extract_entity_relationships(text, entity["name"])
        
        return entities
    
    async def _identify_endpoints_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Identify API endpoints from requirements text."""
        endpoints = []
        text_lower = text.lower()
        
        # Extract operations for each entity
        entities = await self._extract_entities_from_text(text)
        
        for entity in entities:
            entity_name = entity["name"]
            
            # Check for each operation type
            for operation, keywords in self.operation_keywords.items():
                if self._text_contains_operation(text_lower, entity_name, keywords):
                    rest_pattern = self.get_knowledge("rest_patterns", {}).get(operation, {})
                    
                    endpoint = {
                        "operation": operation,
                        "entity": entity_name,
                        "method": rest_pattern.get("method", "GET"),
                        "path": rest_pattern.get("path_pattern", f"/{entity_name}").replace("{resource}", entity_name),
                        "description": f"{operation.title()} {entity_name}",
                        "parameters": self._extract_endpoint_parameters(text, entity_name, operation),
                        "response_codes": self._determine_response_codes(operation),
                        "security": self._determine_endpoint_security(text, operation)
                    }
                    
                    endpoints.append(endpoint)
        
        # Look for custom endpoints
        custom_endpoints = self._extract_custom_endpoints(text)
        endpoints.extend(custom_endpoints)
        
        return endpoints
    
    async def _determine_data_models_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Determine data models from requirements text."""
        data_models = []
        entities = await self._extract_entities_from_text(text)
        
        for entity in entities:
            model = {
                "name": entity["name"].title(),
                "type": "object",
                "description": f"Data model for {entity['name']}",
                "properties": {},
                "required": [],
                "example": {}
            }
            
            # Extract properties from attributes
            for attr in entity.get("attributes", []):
                prop_name = attr["name"]
                prop_type = self._determine_property_type(attr["context"])
                
                model["properties"][prop_name] = {
                    "type": prop_type,
                    "description": f"{prop_name.title()} of the {entity['name']}"
                }
                
                # Determine if property is required
                if self._is_required_property(text, entity["name"], prop_name):
                    model["required"].append(prop_name)
                
                # Generate example value
                model["example"][prop_name] = self._generate_example_value(prop_type, prop_name)
            
            # Add common properties if not already present
            common_props = self._get_common_properties(entity["name"])
            for prop_name, prop_def in common_props.items():
                if prop_name not in model["properties"]:
                    model["properties"][prop_name] = prop_def
                    model["example"][prop_name] = self._generate_example_value(
                        prop_def["type"], prop_name
                    )
            
            data_models.append(model)
        
        return data_models
    
    async def _analyze_security_from_text(self, text: str) -> Dict[str, Any]:
        """Analyze security requirements from text."""
        security_requirements = {
            "authentication": [],
            "authorization": [],
            "features": [],
            "schemes": []
        }
        
        text_lower = text.lower()
        
        # Authentication patterns
        auth_patterns = {
            "jwt": ["jwt", "json web token", "bearer token"],
            "oauth": ["oauth", "oauth2", "authorization code"],
            "api_key": ["api key", "apikey", "key authentication"],
            "basic": ["basic auth", "username password", "basic authentication"]
        }
        
        for auth_type, keywords in auth_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                security_requirements["authentication"].append(auth_type)
                security_requirements["schemes"].append({
                    "type": auth_type,
                    "description": f"{auth_type.upper()} authentication"
                })
        
        # Authorization patterns
        if any(word in text_lower for word in ["role", "permission", "access control", "rbac"]):
            security_requirements["authorization"].append("role_based")
        
        if any(word in text_lower for word in ["scope", "resource access"]):
            security_requirements["authorization"].append("scope_based")
        
        # Security features
        security_features = [
            ("rate_limiting", ["rate limit", "throttling", "request limit"]),
            ("input_validation", ["validation", "sanitize", "validate input"]),
            ("https_only", ["https", "ssl", "tls", "secure"]),
            ("cors", ["cors", "cross origin", "cross-origin"]),
            ("csrf_protection", ["csrf", "cross site", "token protection"])
        ]
        
        for feature, keywords in security_features:
            if any(keyword in text_lower for keyword in keywords):
                security_requirements["features"].append(feature)
        
        return security_requirements
    
    def _extract_project_description(self, text: str) -> str:
        """Extract a project description from requirements text."""
        lines = text.strip().split('\n')
        
        # Look for the first substantial sentence
        for line in lines:
            line = line.strip()
            if len(line) > 20 and not line.startswith(('1.', '2.', '3.', '-', '*')):
                return line[:200] + "..." if len(line) > 200 else line
        
        # Fallback: use first 100 words
        words = text.split()[:20]
        return " ".join(words) + "..."
    
    def _extract_entity_context(self, text: str, entity_name: str) -> str:
        """Extract context around entity mentions."""
        sentences = text.split('.')
        
        for sentence in sentences:
            if entity_name.lower() in sentence.lower():
                return sentence.strip()
        
        return ""
    
    def _extract_entity_attributes(self, text: str, entity_name: str) -> List[Dict[str, Any]]:
        """Extract attributes for an entity from text."""
        attributes = []
        
        # Common attribute patterns
        attribute_patterns = [
            rf"{entity_name}\s+(?:has|contains|includes)\s+([\w\s,]+)",
            rf"(\w+)\s+(?:of|for)\s+(?:the\s+)?{entity_name}",
            rf"{entity_name}\s+(\w+)",
        ]
        
        for pattern in attribute_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                
                # Clean and split attributes
                attrs = [attr.strip() for attr in match.split(',')]
                for attr in attrs:
                    if attr and len(attr.split()) <= 3:  # Reasonable attribute name
                        attributes.append({
                            "name": attr.lower().replace(' ', '_'),
                            "context": match,
                            "source": "pattern_extraction"
                        })
        
        # Add common attributes based on entity type
        common_attrs = self._get_common_entity_attributes(entity_name)
        for attr in common_attrs:
            if attr not in [a["name"] for a in attributes]:
                attributes.append({
                    "name": attr,
                    "context": f"Common attribute for {entity_name}",
                    "source": "knowledge_base"
                })
        
        return attributes[:10]  # Limit to reasonable number
    
    def _extract_entity_relationships(self, text: str, entity_name: str) -> List[Dict[str, Any]]:
        """Extract relationships between entities."""
        relationships = []
        
        # Relationship patterns
        relationship_patterns = [
            rf"{entity_name}\s+(?:has|contains|owns)\s+(?:many\s+)?(\w+)",
            rf"{entity_name}\s+(?:belongs\s+to|is\s+part\s+of)\s+(\w+)",
            rf"(\w+)\s+(?:has|contains)\s+(?:many\s+)?{entity_name}",
        ]
        
        for pattern in relationship_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                related_entity = match.strip()
                if related_entity != entity_name:
                    relationships.append({
                        "related_entity": related_entity,
                        "relationship_type": "association",
                        "context": f"Found in requirements text"
                    })
        
        return relationships
    
    def _text_contains_operation(self, text: str, entity: str, keywords: List[str]) -> bool:
        """Check if text contains operation keywords for an entity."""
        for keyword in keywords:
            pattern = rf"{keyword}\s+(?:a\s+)?{entity}|{entity}\s+{keyword}"
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_endpoint_parameters(self, text: str, entity: str, operation: str) -> List[Dict[str, Any]]:
        """Extract parameters for an endpoint."""
        parameters = []
        
        # Common parameters by operation
        if operation == "list":
            parameters.extend([
                {"name": "page", "type": "integer", "description": "Page number"},
                {"name": "limit", "type": "integer", "description": "Items per page"},
                {"name": "sort", "type": "string", "description": "Sort field"}
            ])
        
        if operation == "search":
            parameters.extend([
                {"name": "q", "type": "string", "description": "Search query"},
                {"name": "filter", "type": "string", "description": "Filter criteria"}
            ])
        
        if operation in ["read", "update", "delete"]:
            parameters.append({
                "name": "id",
                "type": "string",
                "description": f"{entity.title()} identifier",
                "required": True
            })
        
        return parameters
    
    def _determine_response_codes(self, operation: str) -> List[int]:
        """Determine appropriate response codes for an operation."""
        base_codes = [400, 401, 403, 500]  # Common error codes
        
        operation_codes = {
            "create": [201] + base_codes,
            "read": [200, 404] + base_codes,
            "update": [200, 404] + base_codes,
            "delete": [204, 404] + base_codes,
            "list": [200] + base_codes,
            "search": [200] + base_codes
        }
        
        return operation_codes.get(operation, [200] + base_codes)
    
    def _determine_endpoint_security(self, text: str, operation: str) -> List[str]:
        """Determine security requirements for an endpoint."""
        security = []
        
        # Operations that typically require authentication
        if operation in ["create", "update", "delete"]:
            security.append("authentication_required")
        
        # Check text for security mentions
        if any(word in text.lower() for word in ["secure", "auth", "login", "permission"]):
            security.append("authentication_required")
        
        return security
    
    def _extract_custom_endpoints(self, text: str) -> List[Dict[str, Any]]:
        """Extract custom endpoints mentioned in requirements."""
        custom_endpoints = []
        
        # Look for specific endpoint mentions
        endpoint_patterns = [
            rf"(/[\w/]+)\s+(?:endpoint|api|route)",
            rf"(?:GET|POST|PUT|DELETE|PATCH)\s+(/[\w/]+)",
        ]
        
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                path = match[0] if isinstance(match, tuple) else match
                custom_endpoints.append({
                    "operation": "custom",
                    "path": path,
                    "method": "GET",  # Default method
                    "description": f"Custom endpoint: {path}",
                    "parameters": [],
                    "response_codes": [200, 400, 500]
                })
        
        return custom_endpoints
    
    def _determine_property_type(self, context: str) -> str:
        """Determine property type from context."""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["id", "identifier", "uuid"]):
            return "string"
        elif any(word in context_lower for word in ["email", "mail"]):
            return "string"
        elif any(word in context_lower for word in ["phone", "number", "count", "age"]):
            return "integer"
        elif any(word in context_lower for word in ["price", "amount", "cost", "rate"]):
            return "number"
        elif any(word in context_lower for word in ["date", "time", "created", "updated"]):
            return "string"  # ISO date string
        elif any(word in context_lower for word in ["active", "enabled", "valid", "flag"]):
            return "boolean"
        else:
            return "string"  # Default type
    
    def _is_required_property(self, text: str, entity: str, property_name: str) -> bool:
        """Determine if a property is required."""
        required_keywords = ["required", "mandatory", "must", "necessary"]
        optional_keywords = ["optional", "may", "can be"]
        
        # Check if property is mentioned with required/optional keywords
        for keyword in required_keywords:
            if f"{property_name} {keyword}" in text.lower() or f"{keyword} {property_name}" in text.lower():
                return True
        
        for keyword in optional_keywords:
            if f"{property_name} {keyword}" in text.lower() or f"{keyword} {property_name}" in text.lower():
                return False
        
        # Default: common properties are usually required
        common_required = ["id", "name", "email", "title"]
        return property_name in common_required
    
    def _generate_example_value(self, prop_type: str, prop_name: str) -> Any:
        """Generate example values for properties."""
        examples = {
            "string": {
                "id": "12345",
                "email": "user@example.com",
                "name": "John Doe",
                "title": "Sample Title",
                "description": "Sample description",
                "default": "sample_value"
            },
            "integer": {
                "age": 25,
                "count": 10,
                "number": 100,
                "default": 1
            },
            "number": {
                "price": 99.99,
                "amount": 150.00,
                "rate": 0.05,
                "default": 0.0
            },
            "boolean": {
                "active": True,
                "enabled": True,
                "valid": True,
                "default": False
            }
        }
        
        type_examples = examples.get(prop_type, {"default": "sample"})
        return type_examples.get(prop_name, type_examples["default"])
    
    def _get_common_properties(self, entity_name: str) -> Dict[str, Dict[str, Any]]:
        """Get common properties for entity types."""
        common_props = {
            "id": {"type": "string", "description": "Unique identifier"},
            "created_at": {"type": "string", "description": "Creation timestamp"},
            "updated_at": {"type": "string", "description": "Last update timestamp"}
        }
        
        # Entity-specific properties
        entity_props = {
            "user": {
                "name": {"type": "string", "description": "User name"},
                "email": {"type": "string", "description": "User email"}
            },
            "customer": {
                "name": {"type": "string", "description": "Customer name"},
                "email": {"type": "string", "description": "Customer email"},
                "phone": {"type": "string", "description": "Customer phone"}
            },
            "order": {
                "total": {"type": "number", "description": "Order total"},
                "status": {"type": "string", "description": "Order status"}
            },
            "product": {
                "name": {"type": "string", "description": "Product name"},
                "price": {"type": "number", "description": "Product price"}
            }
        }
        
        result = common_props.copy()
        if entity_name in entity_props:
            result.update(entity_props[entity_name])
        
        return result
    
    def _get_common_entity_attributes(self, entity_name: str) -> List[str]:
        """Get common attributes for entity types."""
        common_attrs = {
            "user": ["name", "email", "password", "role"],
            "customer": ["name", "email", "phone", "address"],
            "order": ["total", "status", "date", "items"],
            "product": ["name", "description", "price", "category"],
            "address": ["street", "city", "state", "zip_code"],
            "contact": ["name", "email", "phone", "type"]
        }
        
        return common_attrs.get(entity_name, ["name", "description"])
    
    def _extract_business_rules(self, text: str) -> List[Dict[str, Any]]:
        """Extract business rules from requirements text."""
        rules = []
        
        # Rule patterns
        rule_patterns = [
            r"(?:must|should|shall)\s+([^.]+)",
            r"(?:rule|constraint|requirement):\s*([^.]+)",
            r"(?:only|cannot|not allowed)\s+([^.]+)"
        ]
        
        for pattern in rule_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                rules.append({
                    "description": match.strip(),
                    "type": "business_rule",
                    "source": "requirement_text"
                })
        
        return rules[:5]  # Limit to reasonable number
    
    def _extract_performance_requirements(self, text: str) -> Dict[str, Any]:
        """Extract performance requirements from text."""
        performance = {
            "response_time": None,
            "throughput": None,
            "availability": None,
            "scalability": []
        }
        
        # Performance patterns
        perf_patterns = {
            "response_time": [r"response time.{0,20}(\d+)\s*(ms|milliseconds|seconds)", 
                            r"within\s+(\d+)\s*(ms|milliseconds|seconds)"],
            "throughput": [r"(\d+)\s*(?:requests?|rps|transactions?)\s*per\s*(?:second|minute)"],
            "availability": [r"(\d+(?:\.\d+)?)\s*%\s*(?:uptime|availability)"]
        }
        
        for req_type, patterns in perf_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    performance[req_type] = matches[0]
                    break
        
        return performance
    
    def _extract_technical_requirements(self, text: str) -> List[str]:
        """Extract technical requirements from text."""
        tech_requirements = []
        
        # Technical keywords
        tech_keywords = [
            "rest", "restful", "json", "xml", "http", "https",
            "pagination", "filtering", "sorting", "versioning",
            "rate limiting", "caching", "compression"
        ]
        
        text_lower = text.lower()
        for keyword in tech_keywords:
            if keyword in text_lower:
                tech_requirements.append(keyword)
        
        return list(set(tech_requirements))  # Remove duplicates
    
    def _extract_validation_rules(self, text: str) -> List[Dict[str, Any]]:
        """Extract validation rules from text."""
        validation_rules = []
        
        # Validation patterns
        validation_patterns = [
            r"(?:validate|validation|check)\s+([^.]+)",
            r"(?:format|must be|should be)\s+([^.]+)",
            r"(?:minimum|maximum|min|max)\s+([^.]+)"
        ]
        
        for pattern in validation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                validation_rules.append({
                    "description": match.strip(),
                    "type": "validation_rule",
                    "source": "requirement_text"
                })
        
        return validation_rules[:3]  # Limit to reasonable number

    def _custom_goal_check(self, goal: Goal) -> bool:
        """Custom goal checking for Requirement Analysis Agent."""
        objective = goal.objective.lower()
        
        # Handle specific goal patterns that this agent can execute
        analysis_patterns = [
            "analyze_api_requirements",
            "analyze_requirements",
            "requirement_analysis",
            "extract_requirements", 
            "parse_requirements",
            "analyze_specification",
            "requirement_extraction"
        ]
        
        return any(pattern in objective for pattern in analysis_patterns)
