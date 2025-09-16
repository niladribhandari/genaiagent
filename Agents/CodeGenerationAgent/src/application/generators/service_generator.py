"""Service layer generator."""

import logging
from typing import List, Dict, Any

# Use absolute imports to avoid relative import issues
try:
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode
    from application.services.code_generation_service import CodeGenerationService
except ImportError:
    # Fallback for testing environments
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.append(src_dir)
    
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode
    from application.services.code_generation_service import CodeGenerationService


class ServiceGenerator:
    """Specialized generator for service layer classes."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_service(self, context: GenerationContext) -> GeneratedCode:
        """Generate service class with business logic."""
        # Enhance context for service-specific requirements
        enhanced_context = self._enhance_service_context(context)
        
        # Generate using the base service
        result = self.code_service.generate_code(enhanced_context)
        
        # Post-process for service-specific enhancements
        enhanced_content = self._post_process_service(result.content, context)
        
        return GeneratedCode(
            content=enhanced_content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'ServiceGenerator'}
        )
    
    def _enhance_service_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context with service-specific requirements."""
        entity_name = context.entity_name.replace('Service', '') if context.entity_name.endswith('Service') else context.entity_name
        
        enhanced_requirements = [
            f"Business service for {entity_name} entity",
            "@Service annotation",
            "@Transactional annotation for write operations",
            "@Autowired repository dependency",
            "CRUD business methods",
            "Proper exception handling",
            "Logging for important operations",
            "Input validation"
        ]
        
        # Add any existing requirements
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        # Create enhanced context
        enhanced_context = GenerationContext(
            entity_name=context.entity_name,
            package_name=context.package_name,
            target_language=context.target_language,
            framework=context.framework,
            template_path=context.template_path or "templates/spring_boot/Service.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'repository_class': f"{entity_name}Repository",
                'variable_name': entity_name.lower(),
                'business_methods': self._generate_business_method_specs(entity_name)
            }
        )
        
        return enhanced_context
    
    def _generate_business_method_specs(self, entity_name: str) -> List[Dict[str, Any]]:
        """Generate business method specifications for the service."""
        variable_name = entity_name.lower()
        
        methods = [
            {
                'name': f'getAll{entity_name}s',
                'return_type': f'List<{entity_name}>',
                'parameters': [],
                'transactional': False,
                'description': f'Get all {variable_name}s'
            },
            {
                'name': f'get{entity_name}ById',
                'return_type': f'Optional<{entity_name}>',
                'parameters': ['Long id'],
                'transactional': False,
                'description': f'Get {variable_name} by ID'
            },
            {
                'name': f'create{entity_name}',
                'return_type': entity_name,
                'parameters': [f'{entity_name} {variable_name}'],
                'transactional': True,
                'description': f'Create new {variable_name}'
            },
            {
                'name': f'update{entity_name}',
                'return_type': entity_name,
                'parameters': ['Long id', f'{entity_name} {variable_name}'],
                'transactional': True,
                'description': f'Update existing {variable_name}'
            },
            {
                'name': f'delete{entity_name}',
                'return_type': 'void',
                'parameters': ['Long id'],
                'transactional': True,
                'description': f'Delete {variable_name} by ID'
            }
        ]
        
        return methods
    
    def _post_process_service(self, content: str, context: GenerationContext) -> str:
        """Post-process generated service code."""
        # Add any service-specific post-processing here
        # For now, return content as-is
        return content
