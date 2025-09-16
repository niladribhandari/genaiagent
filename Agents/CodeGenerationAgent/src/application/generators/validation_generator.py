"""Bean validation generator."""

import logging
from typing import List, Dict, Any

try:
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode
    from application.services.code_generation_service import CodeGenerationService
except ImportError:
    # Define fallback classes
    class GenerationContext: pass
    class GeneratedCode: pass
    class CodeGenerationService: pass


class ValidationGenerator:
    """Generator for business validation logic."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_validator(self, context: GenerationContext) -> GeneratedCode:
        """Generate business validation service."""
        enhanced_context = self._enhance_validation_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'ValidationGenerator'}
        )
    
    def _enhance_validation_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context with validation-specific requirements."""
        entity_name = context.entity_name.replace('Validator', '') if context.entity_name.endswith('Validator') else context.entity_name
        
        # Parse validation rules from requirements or context
        validation_rules = self._extract_validation_rules(context)
        
        enhanced_requirements = [
            f"Business validation service for {entity_name}",
            "@Component annotation",
            "ValidationResult return type for all validations",
            "Custom business rule validation methods",
            "Integration with Bean Validation framework",
            "Detailed validation error messages"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}Validator",
            package_name=f"{context.package_name}.validation",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/validation/${ENTITY_NAME}Validator.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'validation_rules': validation_rules,
                'validation_groups': ['Create', 'Update', 'Delete'],
                'error_code_prefix': entity_name.upper()
            }
        )
        
        return enhanced_context
    
    def _extract_validation_rules(self, context: GenerationContext) -> List[Dict[str, Any]]:
        """Extract validation rules from context."""
        rules = []
        
        # Extract from fields
        for field in context.fields or []:
            if field.annotations:
                for annotation in field.annotations:
                    if any(constraint in annotation for constraint in ['@NotNull', '@NotBlank', '@Email', '@Size', '@Pattern']):
                        rules.append({
                            'field': field.name,
                            'type': 'FIELD_VALIDATION',
                            'constraint': annotation,
                            'error_message': f'{field.name} validation failed'
                        })
        
        # Extract from requirements
        if context.additional_context:
            business_rules = context.additional_context.get('business_rules', [])
            for rule in business_rules:
                rules.append({
                    'field': rule.get('field', 'entity'),
                    'type': 'BUSINESS_RULE',
                    'condition': rule.get('condition', ''),
                    'error_message': rule.get('error_message', 'Business rule validation failed'),
                    'severity': rule.get('severity', 'ERROR')
                })
        
        return rules
