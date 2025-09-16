"""Business logic processing service for analyzing and generating business rules."""

from typing import List, Dict, Any, Optional, Set
import re
import logging
from dataclasses import dataclass

# Use absolute imports to avoid relative import issues
try:
    from domain.models.generation_context import BusinessRule, ServicePattern, GenerationContext
    from infrastructure.error_handling import (
        with_error_handling, BusinessLogicError, ValidationError, ErrorCategory, ErrorSeverity,
        safe_execute, validate_input
    )
except ImportError:
    # Fallback for testing environments
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.append(src_dir)
    
    from domain.models.generation_context import BusinessRule, ServicePattern, GenerationContext
    from infrastructure.error_handling import (
        with_error_handling, BusinessLogicError, ValidationError, ErrorCategory, ErrorSeverity,
        safe_execute, validate_input
    )


logger = logging.getLogger(__name__)


@dataclass
class BusinessLogicInsights:
    """Insights extracted from business logic analysis."""
    complexity_score: int
    required_validations: List[str]
    integration_points: List[str]
    business_rules: List[BusinessRule]
    patterns_detected: List[str]


class BusinessLogicProcessor:
    """Processes and analyzes business logic from API specifications."""

    def __init__(self):
        self.business_rule_keywords = {
            'validation': ['validate', 'check', 'verify', 'ensure', 'must', 'should', 'required'],
            'calculation': ['calculate', 'compute', 'sum', 'total', 'aggregate', 'derive'],
            'workflow': ['process', 'workflow', 'approve', 'reject', 'submit', 'complete'],
            'security': ['authenticate', 'authorize', 'encrypt', 'decrypt', 'secure', 'permission'],
            'integration': ['integrate', 'sync', 'external', 'api', 'service', 'system']
        }
        
        self.pattern_indicators = {
            ServicePattern.CRUD: ['create', 'read', 'update', 'delete', 'get', 'post', 'put', 'patch'],
            ServicePattern.INTEGRATION: ['external', 'api', 'service', 'client', 'integrate'],
            ServicePattern.AGGREGATOR: ['aggregate', 'combine', 'merge', 'consolidate', 'collect'],
            ServicePattern.ORCHESTRATOR: ['orchestrate', 'coordinate', 'manage', 'control', 'workflow']
        }

    @with_error_handling(
        operation="analyze_business_context",
        category=ErrorCategory.BUSINESS_LOGIC,
        severity=ErrorSeverity.HIGH
    )
    def analyze_context(self, context: GenerationContext) -> BusinessLogicInsights:
        """Analyze the generation context to extract business logic insights."""
        # Validate input
        if not context:
            raise ValidationError("GenerationContext is required", field="context")
        
        if not context.spec_data:
            raise ValidationError("API specification data is required", field="context.spec_data")
        
        try:
            # Extract business rules from spec
            business_rules = safe_execute(
                self._extract_business_rules, 
                context.spec_data,
                default_value=[]
            )
            
            # Detect service patterns
            patterns = safe_execute(
                self._detect_patterns,
                context.spec_data,
                default_value=[]
            )
            
            # Calculate complexity
            complexity = safe_execute(
                self._calculate_complexity,
                context.spec_data, business_rules,
                default_value=1
            )
            
            # Identify integration points
            integration_points = safe_execute(
                self._identify_integration_points,
                context.spec_data,
                default_value=[]
            )
            
            # Extract required validations
            validations = safe_execute(
                self._extract_validations,
                context.spec_data, business_rules,
                default_value=[]
            )
            
            return BusinessLogicInsights(
                complexity_score=complexity,
                required_validations=validations,
                integration_points=integration_points,
                business_rules=business_rules,
                patterns_detected=patterns
            )
            
        except Exception as e:
            raise BusinessLogicError(
                f"Failed to analyze business logic context: {str(e)}",
                operation="analyze_context",
                cause=e
            )

    @with_error_handling(
        operation="extract_business_rules",
        category=ErrorCategory.BUSINESS_LOGIC,
        severity=ErrorSeverity.MEDIUM
    )
    def _extract_business_rules(self, spec_data: Dict[str, Any]) -> List[BusinessRule]:
        """Extract business rules from API specification."""
        rules = []
        
        try:
            # Look for business rules in various spec sections
            if 'paths' in spec_data:
                for path, methods in spec_data['paths'].items():
                    for method, details in methods.items():
                        if isinstance(details, dict):
                            rules.extend(self._extract_rules_from_operation(path, method, details))
            
            # Check components/schemas for validation rules
            if 'components' in spec_data and 'schemas' in spec_data['components']:
                for schema_name, schema in spec_data['components']['schemas'].items():
                    rules.extend(self._extract_rules_from_schema(schema_name, schema))
                    
        except Exception as e:
            logger.warning(f"Error extracting business rules: {e}")
            
        return rules

    def _extract_rules_from_operation(self, path: str, method: str, operation: Dict[str, Any]) -> List[BusinessRule]:
        """Extract business rules from API operation."""
        rules = []
        
        try:
            # Extract from description
            description = operation.get('description', '') or operation.get('summary', '')
            if description:
                extracted_rules = self._parse_description_for_rules(description, f"{method.upper()} {path}")
                rules.extend(extracted_rules)
            
            # Extract from parameters
            if 'parameters' in operation:
                for param in operation['parameters']:
                    if param.get('required', False):
                        rules.append(BusinessRule(
                            name=f"validate_{param['name']}",
                            description=f"Parameter {param['name']} is required",
                            category="validation",
                            implementation=f"validate_required_field('{param['name']}')",
                            priority=2
                        ))
            
            # Extract from request body schema
            if 'requestBody' in operation:
                request_body = operation['requestBody']
                if 'content' in request_body:
                    for content_type, content in request_body['content'].items():
                        if 'schema' in content:
                            schema_rules = self._extract_validation_rules_from_schema(
                                content['schema'], f"{method}_{path}_request"
                            )
                            rules.extend(schema_rules)
                            
        except Exception as e:
            logger.warning(f"Error extracting rules from operation {method} {path}: {e}")
            
        return rules

    def _extract_rules_from_schema(self, schema_name: str, schema: Dict[str, Any]) -> List[BusinessRule]:
        """Extract business rules from schema definition."""
        rules = []
        
        try:
            # Required fields validation
            if 'required' in schema and isinstance(schema['required'], list):
                for field in schema['required']:
                    rules.append(BusinessRule(
                        name=f"validate_{schema_name}_{field}",
                        description=f"Field {field} is required in {schema_name}",
                        category="validation",
                        implementation=f"validate_required_field('{field}')",
                        priority=2
                    ))
            
            # Property-level validations
            if 'properties' in schema:
                for prop_name, prop_schema in schema['properties'].items():
                    prop_rules = self._extract_property_validation_rules(
                        schema_name, prop_name, prop_schema
                    )
                    rules.extend(prop_rules)
                    
        except Exception as e:
            logger.warning(f"Error extracting rules from schema {schema_name}: {e}")
            
        return rules

    def _extract_property_validation_rules(self, schema_name: str, prop_name: str, prop_schema: Dict[str, Any]) -> List[BusinessRule]:
        """Extract validation rules from property schema."""
        rules = []
        
        try:
            # String length validation
            if prop_schema.get('type') == 'string':
                if 'minLength' in prop_schema:
                    rules.append(BusinessRule(
                        name=f"validate_{schema_name}_{prop_name}_min_length",
                        description=f"{prop_name} must be at least {prop_schema['minLength']} characters",
                        category="validation",
                        implementation=f"validate_min_length('{prop_name}', {prop_schema['minLength']})",
                        priority=2
                    ))
                
                if 'maxLength' in prop_schema:
                    rules.append(BusinessRule(
                        name=f"validate_{schema_name}_{prop_name}_max_length",
                        description=f"{prop_name} must be at most {prop_schema['maxLength']} characters",
                        category="validation",
                        implementation=f"validate_max_length('{prop_name}', {prop_schema['maxLength']})",
                        priority=2
                    ))
                
                if 'pattern' in prop_schema:
                    rules.append(BusinessRule(
                        name=f"validate_{schema_name}_{prop_name}_pattern",
                        description=f"{prop_name} must match pattern: {prop_schema['pattern']}",
                        category="validation",
                        implementation=f"validate_pattern('{prop_name}', r'{prop_schema['pattern']}')",
                        priority=2
                    ))
            
            # Numeric validation
            elif prop_schema.get('type') in ['integer', 'number']:
                if 'minimum' in prop_schema:
                    rules.append(BusinessRule(
                        name=f"validate_{schema_name}_{prop_name}_minimum",
                        description=f"{prop_name} must be at least {prop_schema['minimum']}",
                        category="validation",
                        implementation=f"validate_minimum('{prop_name}', {prop_schema['minimum']})",
                        priority=2
                    ))
                
                if 'maximum' in prop_schema:
                    rules.append(BusinessRule(
                        name=f"validate_{schema_name}_{prop_name}_maximum",
                        description=f"{prop_name} must be at most {prop_schema['maximum']}",
                        category="validation",
                        implementation=f"validate_maximum('{prop_name}', {prop_schema['maximum']})",
                        priority=2
                    ))
            
            # Enum validation
            if 'enum' in prop_schema:
                enum_values = ', '.join([f"'{v}'" for v in prop_schema['enum']])
                rules.append(BusinessRule(
                    name=f"validate_{schema_name}_{prop_name}_enum",
                    description=f"{prop_name} must be one of: {enum_values}",
                    category="validation",
                    implementation=f"validate_enum('{prop_name}', {prop_schema['enum']})",
                    priority=2
                ))
                
        except Exception as e:
            logger.warning(f"Error extracting property validation rules: {e}")
            
        return rules

    def _parse_description_for_rules(self, description: str, context: str) -> List[BusinessRule]:
        """Parse natural language description for business rules."""
        rules = []
        
        try:
            # Look for validation keywords
            for category, keywords in self.business_rule_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in description.lower():
                        # Extract sentence containing the keyword
                        sentences = re.split(r'[.!?]', description)
                        for sentence in sentences:
                            if keyword.lower() in sentence.lower():
                                rules.append(BusinessRule(
                                    name=f"{category}_{context.replace(' ', '_').replace('/', '_')}",
                                    description=sentence.strip(),
                                    category=category,
                                    priority=1
                                ))
                                break
                                
        except Exception as e:
            logger.warning(f"Error parsing description for rules: {e}")
            
        return rules

    def _detect_patterns(self, spec_data: Dict[str, Any]) -> List[str]:
        """Detect service patterns from specification."""
        patterns = []
        
        try:
            if 'paths' in spec_data:
                operation_words = []
                for path, methods in spec_data['paths'].items():
                    for method, details in methods.items():
                        if isinstance(details, dict):
                            # Collect words from path, method, summary, description
                            words = [method.lower()]
                            words.extend(path.lower().split('/'))
                            
                            summary = details.get('summary', '')
                            description = details.get('description', '')
                            words.extend((summary + ' ' + description).lower().split())
                            
                            operation_words.extend(words)
                
                # Check for pattern indicators
                for pattern, indicators in self.pattern_indicators.items():
                    for indicator in indicators:
                        if indicator in operation_words:
                            patterns.append(pattern.value)
                            break
                            
        except Exception as e:
            logger.warning(f"Error detecting patterns: {e}")
            
        return patterns

    def _calculate_complexity(self, spec_data: Dict[str, Any], business_rules: List[BusinessRule]) -> int:
        """Calculate complexity score based on various factors."""
        complexity = 1
        
        try:
            # Base complexity from number of endpoints
            if 'paths' in spec_data:
                endpoint_count = sum(len(methods) for methods in spec_data['paths'].values())
                complexity += min(endpoint_count // 2, 5)  # Cap at 5 points
            
            # Complexity from business rules
            complexity += min(len(business_rules) // 3, 3)  # Cap at 3 points
            
            # Complexity from schema depth
            if 'components' in spec_data and 'schemas' in spec_data['components']:
                schema_complexity = 0
                for schema in spec_data['components']['schemas'].values():
                    if isinstance(schema, dict):
                        schema_complexity += self._calculate_schema_complexity(schema)
                complexity += min(schema_complexity // 10, 2)  # Cap at 2 points
                
        except Exception as e:
            logger.warning(f"Error calculating complexity: {e}")
            
        return min(complexity, 10)  # Cap total complexity at 10

    def _calculate_schema_complexity(self, schema: Dict[str, Any]) -> int:
        """Calculate complexity score for a single schema."""
        complexity = 0
        
        try:
            if 'properties' in schema:
                complexity += len(schema['properties'])
                
                # Add complexity for nested objects
                for prop in schema['properties'].values():
                    if isinstance(prop, dict):
                        if prop.get('type') == 'object' and 'properties' in prop:
                            complexity += self._calculate_schema_complexity(prop)
                        elif prop.get('type') == 'array' and 'items' in prop:
                            if isinstance(prop['items'], dict) and 'properties' in prop['items']:
                                complexity += self._calculate_schema_complexity(prop['items'])
                                
        except Exception as e:
            logger.warning(f"Error calculating schema complexity: {e}")
            
        return complexity

    def _identify_integration_points(self, spec_data: Dict[str, Any]) -> List[str]:
        """Identify potential integration points from the specification."""
        integration_points = []
        
        try:
            if 'paths' in spec_data:
                for path, methods in spec_data['paths'].items():
                    for method, details in methods.items():
                        if isinstance(details, dict):
                            # Look for external service references
                            description = (details.get('description', '') + ' ' + 
                                         details.get('summary', '')).lower()
                            
                            if any(keyword in description for keyword in 
                                  ['external', 'third-party', 'integrate', 'api', 'service']):
                                integration_points.append(f"{method.upper()} {path}")
                                
        except Exception as e:
            logger.warning(f"Error identifying integration points: {e}")
            
        return integration_points

    def _extract_validations(self, spec_data: Dict[str, Any], business_rules: List[BusinessRule]) -> List[str]:
        """Extract required validations from spec and business rules."""
        validations = []
        
        try:
            # Extract from business rules
            validation_rules = [rule for rule in business_rules if rule.category == 'validation']
            validations.extend([rule.name for rule in validation_rules])
            
            # Extract from schema required fields
            if 'components' in spec_data and 'schemas' in spec_data['components']:
                for schema_name, schema in spec_data['components']['schemas'].items():
                    if isinstance(schema, dict) and 'required' in schema:
                        for field in schema['required']:
                            validations.append(f"validate_{schema_name}_{field}_required")
                            
        except Exception as e:
            logger.warning(f"Error extracting validations: {e}")
            
        return validations

    def _extract_validation_rules_from_schema(self, schema: Dict[str, Any], context: str) -> List[BusinessRule]:
        """Extract validation rules from a schema definition."""
        rules = []
        
        try:
            if isinstance(schema, dict):
                # Required fields
                if 'required' in schema:
                    for field in schema['required']:
                        rules.append(BusinessRule(
                            name=f"validate_{context}_{field}_required",
                            description=f"Field {field} is required",
                            category="validation",
                            implementation=f"validate_required_field('{field}')",
                            priority=2
                        ))
                
                # Property validations
                if 'properties' in schema:
                    for prop_name, prop_schema in schema['properties'].items():
                        prop_rules = self._extract_property_validation_rules(
                            context, prop_name, prop_schema
                        )
                        rules.extend(prop_rules)
                        
        except Exception as e:
            logger.warning(f"Error extracting validation rules from schema: {e}")
            
        return rules
