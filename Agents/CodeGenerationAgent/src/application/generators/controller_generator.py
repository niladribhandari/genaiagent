"""REST controller generator."""

import logging
from typing import List, Dict, Any

# Use absolute imports to avoid relative import issues
try:
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode, FieldInfo
    from application.services.code_generation_service import CodeGenerationService
except ImportError:
    # Fallback for testing environments
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.append(src_dir)
    
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode, FieldInfo
    from application.services.code_generation_service import CodeGenerationService


class ControllerGenerator:
    """Specialized generator for REST controller classes."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_controller(self, context: GenerationContext) -> GeneratedCode:
        """Generate REST controller with CRUD endpoints."""
        # Enhance context for controller-specific requirements
        enhanced_context = self._enhance_controller_context(context)
        
        # Generate using the base service
        result = self.code_service.generate_code(enhanced_context)
        
        # Post-process for controller-specific enhancements
        enhanced_content = self._post_process_controller(result.content, context)
        
        return GeneratedCode(
            content=enhanced_content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'ControllerGenerator'}
        )
    
    def _enhance_controller_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context with controller-specific requirements."""
        entity_name = context.entity_name.replace('Controller', '') if context.entity_name.endswith('Controller') else context.entity_name
        
        enhanced_requirements = [
            f"REST controller for {entity_name} entity",
            "@RestController annotation",
            f"@RequestMapping(\"/{entity_name.lower()}s\")",
            "CRUD endpoints: GET (all), GET (by ID), POST, PUT, DELETE",
            "Proper HTTP status codes",
            "Input validation with @Valid",
            "Exception handling",
            "@Autowired service dependency"
        ]
        
        # Add any existing requirements
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        # Determine endpoint paths
        endpoint_base = f"/{entity_name.lower()}s"
        
        # Create enhanced context
        enhanced_context = GenerationContext(
            entity_name=context.entity_name,
            package_name=context.package_name,
            target_language=context.target_language,
            framework=context.framework,
            template_path=context.template_path or "templates/spring_boot/Controller.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'service_class': f"{entity_name}Service",
                'endpoint_base': endpoint_base,
                'variable_name': entity_name.lower(),
                'endpoints': self._generate_endpoint_specs(entity_name)
            }
        )
        
        return enhanced_context
    
    def _generate_endpoint_specs(self, entity_name: str) -> List[Dict[str, Any]]:
        """Generate endpoint specifications for the controller."""
        variable_name = entity_name.lower()
        endpoint_base = f"/{variable_name}s"
        
        endpoints = [
            {
                'method': 'GET',
                'path': '',
                'handler_name': f'getAll{entity_name}s',
                'description': f'Get all {variable_name}s',
                'return_type': f'List<{entity_name}>',
                'parameters': []
            },
            {
                'method': 'GET',
                'path': '/{id}',
                'handler_name': f'get{entity_name}ById',
                'description': f'Get {variable_name} by ID',
                'return_type': f'ResponseEntity<{entity_name}>',
                'parameters': ['@PathVariable Long id']
            },
            {
                'method': 'POST',
                'path': '',
                'handler_name': f'create{entity_name}',
                'description': f'Create new {variable_name}',
                'return_type': f'ResponseEntity<{entity_name}>',
                'parameters': [f'@Valid @RequestBody {entity_name} {variable_name}']
            },
            {
                'method': 'PUT',
                'path': '/{id}',
                'handler_name': f'update{entity_name}',
                'description': f'Update existing {variable_name}',
                'return_type': f'ResponseEntity<{entity_name}>',
                'parameters': ['@PathVariable Long id', f'@Valid @RequestBody {entity_name} {variable_name}']
            },
            {
                'method': 'DELETE',
                'path': '/{id}',
                'handler_name': f'delete{entity_name}',
                'description': f'Delete {variable_name} by ID',
                'return_type': 'ResponseEntity<Void>',
                'parameters': ['@PathVariable Long id']
            }
        ]
        
        return endpoints
    
    def _post_process_controller(self, content: str, context: GenerationContext) -> str:
        """Post-process generated controller code."""
        # Add any controller-specific post-processing here
        # For now, return content as-is
        return content
