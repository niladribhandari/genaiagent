"""Business calculation engine generator."""

import logging
from typing import List, Dict, Any, Optional

try:
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode
    from application.services.code_generation_service import CodeGenerationService
except ImportError:
    # Define fallback classes
    class GenerationContext: pass
    class GeneratedCode: pass
    class CodeGenerationService: pass


class CalculationGenerator:
    """Generator for business calculation engines."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_calculation_engine(self, context: GenerationContext) -> GeneratedCode:
        """Generate business calculation engine."""
        enhanced_context = self._enhance_calculation_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'CalculationGenerator'}
        )
    
    def _enhance_calculation_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context with calculation-specific requirements."""
        entity_name = context.entity_name.replace('Calculator', '').replace('Engine', '') if any(suffix in context.entity_name for suffix in ['Calculator', 'Engine']) else context.entity_name
        
        # Extract calculation rules from context
        calculation_rules = self._extract_calculation_rules(context)
        
        enhanced_requirements = [
            f"Business calculation engine for {entity_name}",
            "@Service annotation",
            "Mathematical calculation methods",
            "BigDecimal for financial calculations",
            "Input validation for calculation parameters",
            "Formula-based calculations with configurable rules",
            "Calculation result caching for performance",
            "Error handling for calculation failures",
            "Calculation audit trail logging"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}CalculationEngine",
            package_name=f"{context.package_name}.calculation",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/calculation/${ENTITY_NAME}CalculationEngine.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'calculation_rules': calculation_rules,
                'uses_big_decimal': True,
                'supports_caching': True,
                'audit_enabled': True,
                'configurable_formulas': True
            }
        )
        
        return enhanced_context
    
    def _extract_calculation_rules(self, context: GenerationContext) -> List[Dict[str, Any]]:
        """Extract calculation rules from context or generate standard calculations."""
        # Check if calculation rules are provided in context
        if context.additional_context and 'calculation_rules' in context.additional_context:
            return context.additional_context['calculation_rules']
        
        # Generate standard calculation rules based on entity fields
        entity_name = context.entity_name
        fields = context.fields or []
        
        # Find numeric fields that could be used in calculations
        numeric_fields = [f for f in fields if self._is_numeric_field(f)]
        
        standard_rules = [
            {
                'name': 'Total Calculation',
                'description': f'Calculate total for {entity_name}',
                'method_name': 'calculateTotal',
                'formula': 'SUM(numeric_fields)',
                'parameters': [f.name for f in numeric_fields] if numeric_fields else ['amount', 'quantity'],
                'return_type': 'BigDecimal',
                'validation_required': True
            },
            {
                'name': 'Average Calculation',
                'description': f'Calculate average for {entity_name}',
                'method_name': 'calculateAverage',
                'formula': 'SUM(values) / COUNT(values)',
                'parameters': ['values'],
                'return_type': 'BigDecimal',
                'validation_required': True
            },
            {
                'name': 'Percentage Calculation',
                'description': f'Calculate percentage for {entity_name}',
                'method_name': 'calculatePercentage',
                'formula': '(part / total) * 100',
                'parameters': ['part', 'total'],
                'return_type': 'BigDecimal',
                'validation_required': True
            },
            {
                'name': 'Tax Calculation',
                'description': f'Calculate tax for {entity_name}',
                'method_name': 'calculateTax',
                'formula': 'amount * (taxRate / 100)',
                'parameters': ['amount', 'taxRate'],
                'return_type': 'BigDecimal',
                'validation_required': True
            }
        ]
        
        return standard_rules
    
    def _is_numeric_field(self, field) -> bool:
        """Check if field is numeric type."""
        if hasattr(field, 'type'):
            numeric_types = ['Integer', 'Long', 'Double', 'Float', 'BigDecimal', 'int', 'long', 'double', 'float']
            return field.type in numeric_types
        return False
