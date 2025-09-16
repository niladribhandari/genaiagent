"""Advanced prompt builder for AI-enhanced code generation."""

from typing import Dict, Any, List, Optional
import json
import logging
from dataclasses import dataclass

# Use absolute imports to avoid relative import issues
try:
    from domain.models.generation_context import GenerationContext, BusinessRule, IntegrationPattern, ServicePattern
    from infrastructure.error_handling import (
        with_error_handling, ValidationError, BusinessLogicError, ErrorCategory, ErrorSeverity,
        safe_execute, validate_input
    )
except ImportError:
    # Fallback for testing environments
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.append(src_dir)
    
    from domain.models.generation_context import GenerationContext, BusinessRule, IntegrationPattern, ServicePattern
    from infrastructure.error_handling import (
        with_error_handling, ValidationError, BusinessLogicError, ErrorCategory, ErrorSeverity,
        safe_execute, validate_input
    )


logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """Template for generating prompts."""
    base_template: str
    context_sections: List[str]
    enhancement_rules: Dict[str, str]
    priority: int = 1


class AdvancedPromptBuilder:
    """Builds sophisticated prompts for AI code generation with business logic understanding."""

    def __init__(self):
        self.prompt_templates = self._initialize_templates()
        self.context_enhancers = {
            'business_rules': self._build_business_rules_section,
            'integration_patterns': self._build_integration_patterns_section,
            'validation_logic': self._build_validation_logic_section,
            'error_handling': self._build_validation_requirements_section,
            'security_considerations': self._build_business_constraints_section,
        }

    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize prompt templates for different contexts."""
        return {
            'controller': PromptTemplate(
                base_template="""You are an expert software architect generating a {language} {framework} controller.

CONTEXT:
- Entity: {entity_name}
- Package: {package_name}
- Service Pattern: {service_pattern}

SPECIFICATION:
{spec_summary}

REQUIREMENTS:
{requirements}

BUSINESS LOGIC:
{business_logic}

INTEGRATION PATTERNS:
{integration_patterns}

Generate a complete, production-ready controller that:
1. Implements all specified endpoints with proper HTTP methods and status codes
2. Includes comprehensive input validation based on the schema requirements
3. Implements the identified business rules and validation logic
4. Follows enterprise patterns for error handling and logging
5. Includes proper exception handling and circuit breaker patterns where needed
6. Uses dependency injection and follows SOLID principles
7. Includes comprehensive documentation and comments

The controller should be enterprise-grade with proper:
- Request/response handling
- Error handling and logging
- Input validation and sanitization
- Security considerations
- Performance optimizations
- Integration with downstream services""",
                context_sections=['spec_summary', 'requirements', 'business_logic', 'integration_patterns'],
                enhancement_rules={
                    'high_complexity': 'Add circuit breaker and retry patterns',
                    'has_validations': 'Include comprehensive validation logic',
                    'has_integrations': 'Add external service integration patterns'
                }
            ),
            
            'service': PromptTemplate(
                base_template="""You are an expert software architect generating a {language} {framework} service class.

CONTEXT:
- Entity: {entity_name}
- Package: {package_name}
- Service Pattern: {service_pattern}

SPECIFICATION:
{spec_summary}

BUSINESS RULES:
{business_rules}

INTEGRATION REQUIREMENTS:
{integration_requirements}

VALIDATION LOGIC:
{validation_logic}

Generate a complete, production-ready service that:
1. Implements all business logic and rules as specified
2. Includes comprehensive validation and error handling
3. Implements integration patterns for external services
4. Follows enterprise patterns and best practices
5. Includes proper logging, monitoring, and observability
6. Uses appropriate design patterns (Strategy, Factory, etc.)
7. Includes transaction management where needed
8. Implements caching strategies for performance

The service should be enterprise-grade with:
- Clean separation of concerns
- Comprehensive business rule implementation
- Robust error handling and recovery
- Performance optimization
- Security considerations
- Testability and maintainability""",
                context_sections=['spec_summary', 'business_rules', 'integration_requirements', 'validation_logic'],
                enhancement_rules={
                    'high_complexity': 'Add sophisticated error handling and monitoring',
                    'has_business_rules': 'Implement comprehensive business logic',
                    'has_integrations': 'Add external service integration with resilience patterns'
                }
            ),

            'model': PromptTemplate(
                base_template="""You are an expert software architect generating a {language} {framework} model/entity class.

CONTEXT:
- Entity: {entity_name}
- Package: {package_name}

SCHEMA DEFINITION:
{schema_definition}

VALIDATION REQUIREMENTS:
{validation_requirements}

BUSINESS CONSTRAINTS:
{business_constraints}

Generate a complete, production-ready model that:
1. Implements all properties with correct types and annotations
2. Includes comprehensive validation annotations and logic
3. Implements business constraints and rules
4. Includes proper serialization/deserialization support
5. Follows framework conventions and best practices
6. Includes proper documentation and comments
7. Implements equals, hashCode, and toString methods appropriately
8. Includes builder pattern if beneficial

The model should be enterprise-grade with:
- Proper data validation
- Business rule enforcement
- Framework integration
- Serialization support
- Immutability where appropriate""",
                context_sections=['schema_definition', 'validation_requirements', 'business_constraints'],
                enhancement_rules={
                    'has_validations': 'Add comprehensive validation annotations',
                    'complex_schema': 'Include advanced serialization and validation',
                    'has_business_rules': 'Implement business constraints in the model'
                }
            )
        }

    @with_error_handling(
        operation="build_enhanced_prompt",
        category=ErrorCategory.BUSINESS_LOGIC,
        severity=ErrorSeverity.HIGH
    )
    def build_prompt(self, context: GenerationContext) -> str:
        """Build an enhanced prompt for the given generation context."""
        # Validate input
        if not context:
            raise ValidationError("GenerationContext is required", field="context")
            
        if not context.file_type:
            raise ValidationError("File type is required", field="context.file_type")
            
        try:
            # Select appropriate template
            template = safe_execute(
                self._select_template,
                context,
                default_value=None
            )
            
            if not template:
                logger.warning("No template found, using fallback prompt")
                return safe_execute(
                    self._build_fallback_prompt,
                    context,
                    default_value=self._build_minimal_prompt(context)
                )

            # Build context-specific sections
            prompt_context = safe_execute(
                self._build_prompt_context,
                context,
                default_value=self._build_minimal_context(context)
            )
            
            # Apply enhancements based on context
            enhanced_template = safe_execute(
                self._apply_enhancements,
                template, context,
                default_value=template.base_template
            )
            
            # Generate final prompt
            final_prompt = enhanced_template.format(**prompt_context)
            
            logger.info(f"Generated enhanced prompt for {context.file_type} with {len(final_prompt)} characters")
            return final_prompt
            
        except Exception as e:
            raise BusinessLogicError(
                f"Failed to build enhanced prompt: {str(e)}",
                operation="build_prompt",
                cause=e
            )

    @with_error_handling(
        operation="select_template",
        category=ErrorCategory.BUSINESS_LOGIC,
        severity=ErrorSeverity.MEDIUM
    )
    def _select_template(self, context: GenerationContext) -> Optional[PromptTemplate]:
        """Select the most appropriate template based on context."""
        file_type_lower = context.file_type.lower()
        
        # Map file types to template keys
        template_mapping = {
            'controller': 'controller',
            'rest_controller': 'controller',
            'api_controller': 'controller',
            'service': 'service',
            'business_service': 'service',
            'service_impl': 'service',
            'model': 'model',
            'entity': 'model',
            'dto': 'model',
            'request': 'model',
            'response': 'model'
        }
        
        for file_pattern, template_key in template_mapping.items():
            if file_pattern in file_type_lower:
                return self.prompt_templates.get(template_key)
        
        # Default to service template for unknown types
        return self.prompt_templates.get('service')

    def _build_prompt_context(self, context: GenerationContext) -> Dict[str, str]:
        """Build context dictionary for prompt formatting."""
        prompt_context = {
            'language': context.language,
            'framework': context.framework,
            'entity_name': context.entity_name,
            'package_name': context.package_name,
            'service_pattern': context.service_pattern.value if context.service_pattern else 'crud',
        }
        
        # Add context-specific sections
        prompt_context['spec_summary'] = self._build_spec_summary(context)
        prompt_context['requirements'] = self._build_requirements_section(context)
        prompt_context['business_logic'] = self._build_business_logic_section(context)
        prompt_context['business_rules'] = self._build_business_rules_section(context)
        prompt_context['integration_patterns'] = self._build_integration_patterns_section(context)
        prompt_context['integration_requirements'] = self._build_integration_requirements_section(context)
        prompt_context['validation_logic'] = self._build_validation_logic_section(context)
        prompt_context['validation_requirements'] = self._build_validation_requirements_section(context)
        prompt_context['schema_definition'] = self._build_schema_definition_section(context)
        prompt_context['business_constraints'] = self._build_business_constraints_section(context)
        
        return prompt_context

    def _build_spec_summary(self, context: GenerationContext) -> str:
        """Build specification summary section."""
        try:
            summary_parts = []
            
            if context.spec_data:
                # Add API info
                if 'info' in context.spec_data:
                    info = context.spec_data['info']
                    summary_parts.append(f"API: {info.get('title', 'Unknown')}")
                    if 'description' in info:
                        summary_parts.append(f"Description: {info['description']}")
                
                # Add endpoints summary
                if 'paths' in context.spec_data:
                    endpoint_count = sum(len(methods) for methods in context.spec_data['paths'].values())
                    summary_parts.append(f"Endpoints: {endpoint_count} operations")
                    
                    # List key endpoints
                    key_endpoints = []
                    for path, methods in list(context.spec_data['paths'].items())[:5]:  # First 5
                        for method in methods.keys():
                            key_endpoints.append(f"{method.upper()} {path}")
                    
                    if key_endpoints:
                        summary_parts.append("Key Operations:")
                        summary_parts.extend([f"- {ep}" for ep in key_endpoints])
            
            return "\n".join(summary_parts) if summary_parts else "No specification details available"
            
        except Exception as e:
            logger.warning(f"Error building spec summary: {e}")
            return "Error processing specification"

    def _build_requirements_section(self, context: GenerationContext) -> str:
        """Build requirements section from instruction data."""
        try:
            requirements = []
            
            if context.instruction_data:
                # Extract framework-specific requirements
                framework_reqs = context.instruction_data.get('framework_requirements', [])
                if framework_reqs:
                    requirements.extend([f"- {req}" for req in framework_reqs])
                
                # Extract code style requirements
                style_reqs = context.instruction_data.get('code_style', {})
                if style_reqs:
                    requirements.append("Code Style Requirements:")
                    for key, value in style_reqs.items():
                        requirements.append(f"- {key}: {value}")
                
                # Extract performance requirements
                perf_reqs = context.instruction_data.get('performance', {})
                if perf_reqs:
                    requirements.append("Performance Requirements:")
                    for key, value in perf_reqs.items():
                        requirements.append(f"- {key}: {value}")
            
            return "\n".join(requirements) if requirements else "Standard enterprise requirements apply"
            
        except Exception as e:
            logger.warning(f"Error building requirements section: {e}")
            return "Error processing requirements"

    def _build_business_logic_section(self, context: GenerationContext) -> str:
        """Build business logic section."""
        try:
            logic_parts = []
            
            if context.business_rules:
                logic_parts.append("Business Rules to Implement:")
                for rule in context.business_rules:
                    logic_parts.append(f"- {rule.name}: {rule.description}")
                    if rule.implementation:
                        logic_parts.append(f"  Implementation: {rule.implementation}")
            
            # Add complexity considerations
            if hasattr(context, 'complexity_score') and context.complexity_score > 5:
                logic_parts.append("\nComplexity Considerations:")
                logic_parts.append("- This is a high-complexity component requiring sophisticated error handling")
                logic_parts.append("- Implement circuit breaker patterns for external integrations")
                logic_parts.append("- Add comprehensive logging and monitoring")
            
            return "\n".join(logic_parts) if logic_parts else "Standard business logic patterns apply"
            
        except Exception as e:
            logger.warning(f"Error building business logic section: {e}")
            return "Error processing business logic"

    def _build_business_rules_section(self, context: GenerationContext) -> str:
        """Build detailed business rules section."""
        try:
            if not context.business_rules:
                return "No specific business rules defined"
            
            rules_by_category = {}
            for rule in context.business_rules:
                category = rule.category
                if category not in rules_by_category:
                    rules_by_category[category] = []
                rules_by_category[category].append(rule)
            
            sections = []
            for category, rules in rules_by_category.items():
                sections.append(f"{category.upper()} Rules:")
                for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
                    sections.append(f"- {rule.name}: {rule.description}")
                    if rule.implementation:
                        sections.append(f"  → {rule.implementation}")
                    if rule.conditions:
                        sections.append(f"  Conditions: {', '.join(rule.conditions)}")
                sections.append("")  # Empty line between categories
            
            return "\n".join(sections).strip()
            
        except Exception as e:
            logger.warning(f"Error building business rules section: {e}")
            return "Error processing business rules"

    def _build_integration_patterns_section(self, context: GenerationContext) -> str:
        """Build integration patterns section."""
        try:
            if not context.integration_patterns:
                return "No specific integration patterns required"
            
            patterns = []
            for pattern in context.integration_patterns:
                patterns.append(f"- {pattern.name} ({pattern.pattern_type.value})")
                patterns.append(f"  Description: {pattern.description}")
                
                if pattern.configuration:
                    patterns.append("  Configuration:")
                    for key, value in pattern.configuration.items():
                        patterns.append(f"    {key}: {value}")
                
                if pattern.dependencies:
                    patterns.append(f"  Dependencies: {', '.join(pattern.dependencies)}")
                patterns.append("")
            
            return "\n".join(patterns).strip()
            
        except Exception as e:
            logger.warning(f"Error building integration patterns section: {e}")
            return "Error processing integration patterns"

    def _build_integration_requirements_section(self, context: GenerationContext) -> str:
        """Build integration requirements section."""
        try:
            requirements = []
            
            # From downstream systems
            if hasattr(context, 'downstream_systems') and context.downstream_systems:
                requirements.append("Downstream System Integrations:")
                for name, system in context.downstream_systems.items():
                    requirements.append(f"- {name}: {system.description}")
                    requirements.append(f"  Base URL: {system.base_url}")
                    requirements.append(f"  Timeout: {system.timeout}ms")
                    
                    if system.retry_config:
                        requirements.append(f"  Retry Config: {system.retry_config}")
                    if system.circuit_breaker_config:
                        requirements.append(f"  Circuit Breaker: {system.circuit_breaker_config}")
                requirements.append("")
            
            # From integration patterns
            if context.integration_patterns:
                requirements.append("Integration Pattern Requirements:")
                for pattern in context.integration_patterns:
                    requirements.append(f"- Implement {pattern.pattern_type.value} pattern")
                    if pattern.configuration:
                        for key, value in pattern.configuration.items():
                            requirements.append(f"  {key}: {value}")
            
            return "\n".join(requirements) if requirements else "Standard integration patterns apply"
            
        except Exception as e:
            logger.warning(f"Error building integration requirements: {e}")
            return "Error processing integration requirements"

    def _build_validation_logic_section(self, context: GenerationContext) -> str:
        """Build validation logic section."""
        try:
            validations = []
            
            if context.business_rules:
                validation_rules = [rule for rule in context.business_rules if rule.category == 'validation']
                if validation_rules:
                    validations.append("Validation Rules:")
                    for rule in validation_rules:
                        validations.append(f"- {rule.name}: {rule.description}")
                        if rule.implementation:
                            validations.append(f"  Implementation: {rule.implementation}")
            
            # Add schema-based validations
            if context.spec_data and 'components' in context.spec_data:
                schemas = context.spec_data['components'].get('schemas', {})
                if schemas:
                    validations.append("\nSchema Validation Requirements:")
                    for schema_name, schema in schemas.items():
                        if 'required' in schema:
                            validations.append(f"- {schema_name} required fields: {', '.join(schema['required'])}")
                        
                        # Property validations
                        if 'properties' in schema:
                            for prop_name, prop_schema in schema['properties'].items():
                                prop_validations = self._extract_property_validations(prop_name, prop_schema)
                                validations.extend([f"  {v}" for v in prop_validations])
            
            return "\n".join(validations) if validations else "Standard validation patterns apply"
            
        except Exception as e:
            logger.warning(f"Error building validation logic: {e}")
            return "Error processing validation logic"

    def _build_validation_requirements_section(self, context: GenerationContext) -> str:
        """Build validation requirements for models."""
        return self._build_validation_logic_section(context)  # Same logic for now

    def _build_schema_definition_section(self, context: GenerationContext) -> str:
        """Build schema definition section for models."""
        try:
            if not context.spec_data or 'components' not in context.spec_data:
                return "No schema definition available"
            
            schemas = context.spec_data['components'].get('schemas', {})
            target_schema = None
            
            # Find the relevant schema for this entity
            for schema_name, schema in schemas.items():
                if context.entity_name.lower() in schema_name.lower():
                    target_schema = schema
                    break
            
            if not target_schema and schemas:
                # Take the first schema if no match found
                target_schema = list(schemas.values())[0]
            
            if target_schema:
                return json.dumps(target_schema, indent=2)
            
            return "No relevant schema found"
            
        except Exception as e:
            logger.warning(f"Error building schema definition: {e}")
            return "Error processing schema definition"

    def _build_business_constraints_section(self, context: GenerationContext) -> str:
        """Build business constraints section for models."""
        try:
            constraints = []
            
            if context.business_rules:
                constraint_rules = [rule for rule in context.business_rules 
                                  if rule.category in ['validation', 'calculation', 'workflow']]
                if constraint_rules:
                    constraints.append("Business Constraints:")
                    for rule in constraint_rules:
                        constraints.append(f"- {rule.description}")
                        if rule.implementation:
                            constraints.append(f"  → {rule.implementation}")
            
            return "\n".join(constraints) if constraints else "Standard business constraints apply"
            
        except Exception as e:
            logger.warning(f"Error building business constraints: {e}")
            return "Error processing business constraints"

    def _extract_property_validations(self, prop_name: str, prop_schema: Dict[str, Any]) -> List[str]:
        """Extract validation requirements from property schema."""
        validations = []
        
        try:
            prop_type = prop_schema.get('type', 'unknown')
            
            if prop_type == 'string':
                if 'minLength' in prop_schema:
                    validations.append(f"{prop_name}: minimum length {prop_schema['minLength']}")
                if 'maxLength' in prop_schema:
                    validations.append(f"{prop_name}: maximum length {prop_schema['maxLength']}")
                if 'pattern' in prop_schema:
                    validations.append(f"{prop_name}: must match pattern {prop_schema['pattern']}")
            
            elif prop_type in ['integer', 'number']:
                if 'minimum' in prop_schema:
                    validations.append(f"{prop_name}: minimum value {prop_schema['minimum']}")
                if 'maximum' in prop_schema:
                    validations.append(f"{prop_name}: maximum value {prop_schema['maximum']}")
            
            if 'enum' in prop_schema:
                validations.append(f"{prop_name}: must be one of {prop_schema['enum']}")
                
        except Exception as e:
            logger.warning(f"Error extracting property validations for {prop_name}: {e}")
            
        return validations

    def _apply_enhancements(self, template: PromptTemplate, context: GenerationContext) -> str:
        """Apply context-specific enhancements to template."""
        enhanced_template = template.base_template
        
        try:
            # Apply enhancement rules based on context
            complexity_score = getattr(context, 'complexity_score', 1)
            
            if complexity_score > 5 and 'high_complexity' in template.enhancement_rules:
                enhancement = template.enhancement_rules['high_complexity']
                enhanced_template += f"\n\nIMPORTANT: {enhancement}"
            
            if context.business_rules and 'has_business_rules' in template.enhancement_rules:
                enhancement = template.enhancement_rules['has_business_rules']
                enhanced_template += f"\n\nIMPORTANT: {enhancement}"
            
            if context.integration_patterns and 'has_integrations' in template.enhancement_rules:
                enhancement = template.enhancement_rules['has_integrations']
                enhanced_template += f"\n\nIMPORTANT: {enhancement}"
            
            # Add validation enhancements
            validation_rules = [rule for rule in (context.business_rules or []) 
                              if rule.category == 'validation']
            if validation_rules and 'has_validations' in template.enhancement_rules:
                enhancement = template.enhancement_rules['has_validations']
                enhanced_template += f"\n\nIMPORTANT: {enhancement}"
                
        except Exception as e:
            logger.warning(f"Error applying enhancements: {e}")
            
        return enhanced_template

    def _build_fallback_prompt(self, context: GenerationContext) -> str:
        """Build a basic fallback prompt when template selection fails."""
        return f"""Generate a {context.language} {context.framework} {context.file_type} for {context.entity_name}.

Package: {context.package_name}

Specification Data:
{json.dumps(context.spec_data, indent=2) if context.spec_data else 'None'}

Instructions:
{json.dumps(context.instruction_data, indent=2) if context.instruction_data else 'None'}

Generate production-ready, enterprise-grade code that follows best practices and includes proper error handling, validation, and documentation."""

    def _build_minimal_prompt(self, context: GenerationContext) -> str:
        """Build minimal prompt when all else fails."""
        return f"Generate a {context.language} {context.file_type} for {context.entity_name}."
        
    def _build_minimal_context(self, context: GenerationContext) -> Dict[str, str]:
        """Build minimal context when normal context building fails."""
        return {
            'language': context.language or 'java',
            'framework': context.framework or 'spring',
            'entity_name': context.entity_name or 'Entity',
            'package_name': context.package_name or 'com.example',
            'service_pattern': 'CRUD',
            'spec_summary': 'Basic API operations',
            'requirements': 'Standard implementation',
            'business_logic': 'No specific business rules',
            'integration_patterns': 'No external integrations'
        }
