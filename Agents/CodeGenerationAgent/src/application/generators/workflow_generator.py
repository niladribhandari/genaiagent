"""Business workflow generator."""

import logging
from typing import List, Dict, Any

try:
    from src.domain.models.generation_context import GenerationContext
    from src.domain.models.code_models import GeneratedCode
    from src.application.services.code_generation_service import CodeGenerationService
except ImportError:
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode
    from application.services.code_generation_service import CodeGenerationService


class WorkflowGenerator:
    """Generator for business workflow orchestration."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_workflow(self, context: GenerationContext) -> GeneratedCode:
        """Generate business workflow service."""
        enhanced_context = self._enhance_workflow_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'WorkflowGenerator'}
        )
    
    def _enhance_workflow_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context with workflow-specific requirements."""
        entity_name = context.entity_name.replace('Workflow', '') if context.entity_name.endswith('Workflow') else context.entity_name
        
        # Extract workflow steps from context
        workflow_steps = self._extract_workflow_steps(context)
        
        enhanced_requirements = [
            f"Business workflow service for {entity_name}",
            "@Service annotation",
            "@Transactional annotation for workflow execution",
            "Step-by-step workflow execution with error handling",
            "WorkflowContext for maintaining state across steps",
            "Event publishing for workflow completion/failure",
            "Rollback mechanisms for failed workflows"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}WorkflowService",
            package_name=f"{context.package_name}.workflow",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/workflow/${ENTITY_NAME}WorkflowService.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'workflow_steps': workflow_steps,
                'supports_rollback': True,
                'publishes_events': True,
                'requires_transaction': True
            }
        )
        
        return enhanced_context
    
    def _extract_workflow_steps(self, context: GenerationContext) -> List[Dict[str, Any]]:
        """Extract workflow steps from context or generate standard CRUD workflow."""
        # Check if workflow steps are provided in context
        if context.additional_context and 'workflow_steps' in context.additional_context:
            return context.additional_context['workflow_steps']
        
        # Generate standard workflow steps based on entity operations
        entity_name = context.entity_name
        standard_steps = [
            {
                'name': 'Input Validation',
                'order': 1,
                'description': f'Validate {entity_name} input data',
                'method_name': 'validateInput',
                'error_handling': 'STOP_ON_ERROR',
                'rollback_required': False
            },
            {
                'name': 'Business Rule Check',
                'order': 2,
                'description': f'Apply business rules for {entity_name}',
                'method_name': 'applyBusinessRules',
                'error_handling': 'STOP_ON_ERROR',
                'rollback_required': False
            },
            {
                'name': 'Data Processing',
                'order': 3,
                'description': f'Process and transform {entity_name} data',
                'method_name': 'processData',
                'error_handling': 'CONTINUE_ON_WARNING',
                'rollback_required': False
            },
            {
                'name': 'Persistence Operation',
                'order': 4,
                'description': f'Save {entity_name} to database',
                'method_name': 'persistEntity',
                'error_handling': 'STOP_ON_ERROR',
                'rollback_required': True
            },
            {
                'name': 'Event Publication',
                'order': 5,
                'description': f'Publish {entity_name} events',
                'method_name': 'publishEvents',
                'error_handling': 'CONTINUE_ON_ERROR',
                'rollback_required': False
            }
        ]
        
        return standard_steps
