"""Specialized entity generator."""

import logging
from typing import List, Dict, Any

# Use absolute imports to avoid relative import issues
try:
    from core.interfaces import CodeGenerator
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
    
    from core.interfaces import CodeGenerator
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode, FieldInfo
    from application.services.code_generation_service import CodeGenerationService


class EntityGenerator:
    """Specialized generator for JPA entity classes."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_entity(self, context: GenerationContext) -> GeneratedCode:
        """Generate JPA entity with enhanced field processing."""
        # Enhance context for entity-specific requirements
        enhanced_context = self._enhance_entity_context(context)
        
        # Generate using the base service
        result = self.code_service.generate_code(enhanced_context)
        
        # Post-process for entity-specific enhancements
        enhanced_content = self._post_process_entity(result.content, context)
        
        return GeneratedCode(
            content=enhanced_content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'EntityGenerator'}
        )
    
    def _enhance_entity_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context with entity-specific requirements."""
        enhanced_requirements = list(context.requirements or [])
        
        # Add standard entity requirements
        enhanced_requirements.extend([
            "JPA @Entity annotation",
            "Primary key with @Id and @GeneratedValue",
            "Proper column annotations",
            "Default and parameterized constructors",
            "Getters and setters for all fields",
            "toString(), equals(), and hashCode() methods"
        ])
        
        # Process fields to ensure proper JPA annotations
        enhanced_fields = self._enhance_fields_for_jpa(context.fields or [])
        
        # Create enhanced context
        enhanced_context = GenerationContext(
            entity_name=context.entity_name,
            package_name=context.package_name,
            target_language=context.target_language,
            framework=context.framework,
            template_path=context.template_path or "templates/spring_boot/Entity.java",
            fields=enhanced_fields,
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'table_name': context.entity_name.lower() + 's',
                'has_relationships': self._has_relationships(enhanced_fields)
            }
        )
        
        return enhanced_context
    
    def _enhance_fields_for_jpa(self, fields: List[FieldInfo]) -> List[FieldInfo]:
        """Enhance fields with JPA-specific metadata."""
        enhanced_fields = []
        
        for field in fields:
            enhanced_field = FieldInfo(
                name=field.name,
                type=field.type,
                annotations=field.annotations or []
            )
            
            # Add JPA annotations based on field type and name
            if field.name.lower() == 'id':
                enhanced_field.annotations.extend(['@Id', '@GeneratedValue(strategy = GenerationType.IDENTITY)'])
            
            # Add column annotation if not present
            if not any('@Column' in ann for ann in enhanced_field.annotations):
                column_annotation = self._generate_column_annotation(field)
                if column_annotation:
                    enhanced_field.annotations.append(column_annotation)
            
            # Add validation annotations
            if field.type == 'String' and not any('@NotNull' in ann or '@NotEmpty' in ann for ann in enhanced_field.annotations):
                enhanced_field.annotations.append('@NotEmpty')
            
            enhanced_fields.append(enhanced_field)
        
        return enhanced_fields
    
    def _generate_column_annotation(self, field: FieldInfo) -> str:
        """Generate appropriate @Column annotation for field."""
        column_parts = ['@Column']
        params = []
        
        # Set column name (snake_case)
        column_name = self._to_snake_case(field.name)
        params.append(f'name = "{column_name}"')
        
        # Set constraints based on type
        if field.type == 'String':
            params.append('length = 255')
        elif field.name.lower() == 'id':
            return ''  # ID fields don't need @Column
        
        if params:
            return f"@Column({', '.join(params)})"
        else:
            return '@Column'
    
    def _has_relationships(self, fields: List[FieldInfo]) -> bool:
        """Check if entity has relationship fields."""
        relationship_types = ['OneToMany', 'ManyToOne', 'OneToOne', 'ManyToMany']
        for field in fields:
            for annotation in field.annotations:
                if any(rel in annotation for rel in relationship_types):
                    return True
        return False
    
    def _to_snake_case(self, camel_case: str) -> str:
        """Convert camelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _post_process_entity(self, content: str, context: GenerationContext) -> str:
        """Post-process generated entity code."""
        # Add any entity-specific post-processing here
        # For now, return content as-is
        return content
