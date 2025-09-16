"""Event-driven architecture generator."""

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


class EventGenerator:
    """Generator for domain events and event handlers."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_event_publisher(self, context: GenerationContext) -> GeneratedCode:
        """Generate event publisher for domain events."""
        enhanced_context = self._enhance_event_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'EventGenerator'}
        )
    
    def generate_event_handler(self, context: GenerationContext) -> GeneratedCode:
        """Generate event handler for domain events."""
        enhanced_context = self._enhance_event_handler_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'EventGenerator'}
        )
    
    def _enhance_event_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context for event publisher generation."""
        entity_name = context.entity_name.replace('Event', '').replace('Publisher', '') if any(suffix in context.entity_name for suffix in ['Event', 'Publisher']) else context.entity_name
        
        # Extract event types from context
        event_types = self._extract_event_types(context)
        
        enhanced_requirements = [
            f"Domain event publisher for {entity_name}",
            "@Component annotation",
            "ApplicationEventPublisher dependency",
            "Event publication methods",
            "Event metadata enrichment",
            "Async event publishing support",
            "Event correlation ID generation",
            "Error handling for event publication failures"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}EventPublisher",
            package_name=f"{context.package_name}.events",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/events/${ENTITY_NAME}EventPublisher.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'event_types': event_types,
                'supports_async': True,
                'generates_correlation_id': True,
                'enriches_metadata': True
            }
        )
        
        return enhanced_context
    
    def _enhance_event_handler_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context for event handler generation."""
        entity_name = context.entity_name.replace('EventHandler', '').replace('Handler', '') if any(suffix in context.entity_name for suffix in ['EventHandler', 'Handler']) else context.entity_name
        
        enhanced_requirements = [
            f"Domain event handler for {entity_name}",
            "@Component annotation",
            "@EventListener annotation",
            "@Async annotation for async processing",
            "Event processing methods",
            "Event validation and filtering",
            "Error handling and retry logic",
            "Event processing metrics"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}EventHandler",
            package_name=f"{context.package_name}.events.handlers",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/events/handlers/${ENTITY_NAME}EventHandler.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'supports_async': True,
                'validates_events': True,
                'supports_retry': True,
                'collects_metrics': True
            }
        )
        
        return enhanced_context
    
    def _extract_event_types(self, context: GenerationContext) -> List[Dict[str, Any]]:
        """Extract event types from context or generate standard events."""
        # Check if event types are provided in context
        if context.additional_context and 'event_types' in context.additional_context:
            return context.additional_context['event_types']
        
        # Generate standard CRUD event types
        entity_name = context.entity_name
        standard_events = [
            {
                'name': f'{entity_name}CreatedEvent',
                'description': f'Published when {entity_name} is created',
                'fields': ['id', 'timestamp', 'correlationId', 'userId'],
                'async': True
            },
            {
                'name': f'{entity_name}UpdatedEvent',
                'description': f'Published when {entity_name} is updated',
                'fields': ['id', 'timestamp', 'correlationId', 'userId', 'previousValues', 'newValues'],
                'async': True
            },
            {
                'name': f'{entity_name}DeletedEvent',
                'description': f'Published when {entity_name} is deleted',
                'fields': ['id', 'timestamp', 'correlationId', 'userId'],
                'async': True
            },
            {
                'name': f'{entity_name}ValidationFailedEvent',
                'description': f'Published when {entity_name} validation fails',
                'fields': ['id', 'timestamp', 'correlationId', 'userId', 'validationErrors'],
                'async': False
            }
        ]
        
        return standard_events
