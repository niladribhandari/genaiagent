"""Audit trail generator."""

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


class AuditGenerator:
    """Generator for audit trails and logging capabilities."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_audit_service(self, context: GenerationContext) -> GeneratedCode:
        """Generate audit service for tracking entity changes."""
        enhanced_context = self._enhance_audit_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'AuditGenerator'}
        )
    
    def generate_audit_entity(self, context: GenerationContext) -> GeneratedCode:
        """Generate audit entity for storing audit records."""
        enhanced_context = self._enhance_audit_entity_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'AuditGenerator'}
        )
    
    def _enhance_audit_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context for audit service generation."""
        entity_name = context.entity_name.replace('Audit', '').replace('Service', '') if any(suffix in context.entity_name for suffix in ['Audit', 'Service']) else context.entity_name
        
        # Extract audit configuration from context
        audit_config = self._extract_audit_configuration(context)
        
        enhanced_requirements = [
            f"Audit service for {entity_name}",
            "@Service annotation",
            "@Transactional annotation",
            "Audit record creation methods",
            "Change detection and tracking",
            "User context capture",
            "Timestamp management",
            "Audit query methods",
            "Audit retention policies",
            "Performance optimized audit logging"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}AuditService",
            package_name=f"{context.package_name}.audit",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/audit/${ENTITY_NAME}AuditService.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'audit_config': audit_config,
                'tracks_changes': True,
                'captures_user_context': True,
                'supports_queries': True,
                'has_retention_policy': True
            }
        )
        
        return enhanced_context
    
    def _enhance_audit_entity_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context for audit entity generation."""
        entity_name = context.entity_name.replace('Audit', '') if context.entity_name.endswith('Audit') else context.entity_name
        
        enhanced_requirements = [
            f"Audit entity for {entity_name}",
            "@Entity annotation",
            "@Table annotation with audit table name",
            "JPA entity with audit fields",
            "Primary key generation strategy",
            "Audit timestamp fields",
            "User tracking fields",
            "Operation type field (CREATE, UPDATE, DELETE)",
            "Entity ID reference field",
            "Change data fields (JSON or serialized)",
            "Indexes for query performance"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        # Define audit-specific fields
        audit_fields = [
            {'name': 'auditId', 'type': 'Long', 'annotations': ['@Id', '@GeneratedValue']},
            {'name': 'entityId', 'type': 'String', 'annotations': ['@Column(nullable = false)']},
            {'name': 'entityType', 'type': 'String', 'annotations': ['@Column(nullable = false)']},
            {'name': 'operationType', 'type': 'String', 'annotations': ['@Column(nullable = false)']},
            {'name': 'userId', 'type': 'String', 'annotations': ['@Column']},
            {'name': 'timestamp', 'type': 'LocalDateTime', 'annotations': ['@Column(nullable = false)']},
            {'name': 'oldValues', 'type': 'String', 'annotations': ['@Column(columnDefinition = "TEXT")']},
            {'name': 'newValues', 'type': 'String', 'annotations': ['@Column(columnDefinition = "TEXT")']},
            {'name': 'ipAddress', 'type': 'String', 'annotations': ['@Column']},
            {'name': 'userAgent', 'type': 'String', 'annotations': ['@Column']}
        ]
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}AuditRecord",
            package_name=f"{context.package_name}.audit.entity",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/audit/entity/${ENTITY_NAME}AuditRecord.java",
            fields=audit_fields,
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'table_name': f"{entity_name.lower()}_audit",
                'has_indexes': True,
                'stores_json_data': True
            }
        )
        
        return enhanced_context
    
    def _extract_audit_configuration(self, context: GenerationContext) -> Dict[str, Any]:
        """Extract audit configuration from context or generate default config."""
        # Check if audit config is provided in context
        if context.additional_context and 'audit_config' in context.additional_context:
            return context.additional_context['audit_config']
        
        # Generate default audit configuration
        default_config = {
            'track_creates': True,
            'track_updates': True,
            'track_deletes': True,
            'track_reads': False,
            'store_old_values': True,
            'store_new_values': True,
            'capture_ip_address': True,
            'capture_user_agent': True,
            'async_logging': True,
            'retention_days': 365,
            'batch_size': 100,
            'excluded_fields': ['password', 'token', 'secret'],
            'audit_operations': [
                {'type': 'CREATE', 'enabled': True, 'level': 'INFO'},
                {'type': 'UPDATE', 'enabled': True, 'level': 'INFO'},
                {'type': 'DELETE', 'enabled': True, 'level': 'WARN'},
                {'type': 'BULK_UPDATE', 'enabled': True, 'level': 'WARN'},
                {'type': 'BULK_DELETE', 'enabled': True, 'level': 'ERROR'}
            ]
        }
        
        return default_config
