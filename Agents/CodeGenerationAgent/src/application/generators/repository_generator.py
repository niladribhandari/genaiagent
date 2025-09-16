"""JPA repository generator."""

import logging
from typing import List, Dict, Any

try:
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode, FieldInfo
    from application.services.code_generation_service import CodeGenerationService
except ImportError:
    # Define fallback classes
    class GenerationContext: pass
    class GeneratedCode: pass
    class CodeGenerationService: pass


class RepositoryGenerator:
    """Specialized generator for JPA Repository interfaces."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_repository(self, context: GenerationContext) -> GeneratedCode:
        """Generate JPA repository with custom finder methods."""
        enhanced_context = self._enhance_repository_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'RepositoryGenerator'}
        )
    
    def _enhance_repository_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context with repository-specific requirements."""
        entity_name = context.entity_name.replace('Repository', '') if context.entity_name.endswith('Repository') else context.entity_name
        
        # Generate custom finder methods based on entity fields
        custom_methods = self._generate_custom_methods(context.fields or [], entity_name)
        
        enhanced_requirements = [
            f"JPA Repository interface for {entity_name}",
            "@Repository annotation",
            "Extends JpaRepository for CRUD operations",
            "Custom finder methods based on entity fields",
            "Pagination and sorting support",
            "Query methods following Spring Data naming conventions"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}Repository",
            package_name=f"{context.package_name}.repository",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/repository/${ENTITY_NAME}Repository.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'primary_key_type': 'Long',  # Default, could be configured
                'custom_methods': custom_methods,
                'supports_pagination': True,
                'supports_specification': True
            }
        )
        
        return enhanced_context
    
    def _generate_custom_methods(self, fields: List[FieldInfo], entity_name: str) -> List[Dict[str, Any]]:
        """Generate custom repository methods based on entity fields."""
        methods = []
        
        for field in fields:
            field_name = field.name
            field_type = field.type
            
            # Skip ID field and audit fields
            if field_name.lower() in ['id', 'createdat', 'updatedat', 'version']:
                continue
            
            # Find by single field
            methods.append({
                'name': f'findBy{field_name.capitalize()}',
                'parameters': [f'{field_type} {field_name.lower()}'],
                'return_type': f'List<{entity_name}>',
                'description': f'Find {entity_name.lower()}s by {field_name.lower()}'
            })
            
            # Find by field (single result)
            if field_name.lower() in ['email', 'code', 'reference', 'number']:
                methods.append({
                    'name': f'findBy{field_name.capitalize()}',
                    'parameters': [f'{field_type} {field_name.lower()}'],
                    'return_type': f'Optional<{entity_name}>',
                    'description': f'Find {entity_name.lower()} by {field_name.lower()}'
                })
            
            # String fields get additional methods
            if field_type == 'String':
                methods.append({
                    'name': f'findBy{field_name.capitalize()}ContainingIgnoreCase',
                    'parameters': [f'String {field_name.lower()}'],
                    'return_type': f'List<{entity_name}>',
                    'description': f'Find {entity_name.lower()}s by {field_name.lower()} containing text (case insensitive)'
                })
                
                methods.append({
                    'name': f'findBy{field_name.capitalize()}StartingWithIgnoreCase',
                    'parameters': [f'String {field_name.lower()}'],
                    'return_type': f'List<{entity_name}>',
                    'description': f'Find {entity_name.lower()}s by {field_name.lower()} starting with text (case insensitive)'
                })
            
            # Date fields get range methods
            if field_type in ['LocalDate', 'LocalDateTime', 'Date']:
                methods.append({
                    'name': f'findBy{field_name.capitalize()}Between',
                    'parameters': [f'{field_type} start{field_name.capitalize()}', f'{field_type} end{field_name.capitalize()}'],
                    'return_type': f'List<{entity_name}>',
                    'description': f'Find {entity_name.lower()}s by {field_name.lower()} between dates'
                })
                
                methods.append({
                    'name': f'findBy{field_name.capitalize()}After',
                    'parameters': [f'{field_type} {field_name.lower()}'],
                    'return_type': f'List<{entity_name}>',
                    'description': f'Find {entity_name.lower()}s by {field_name.lower()} after date'
                })
        
        # Add common utility methods
        methods.extend([
            {
                'name': f'findBy{entity_name}sWithPagination',
                'parameters': ['Pageable pageable'],
                'return_type': f'Page<{entity_name}>',
                'description': f'Find all {entity_name.lower()}s with pagination',
                'is_pageable': True
            },
            {
                'name': 'countByActiveStatus',
                'parameters': ['boolean active'],
                'return_type': 'long',
                'description': f'Count active {entity_name.lower()}s'
            }
        ])
        
        return methods
    
    def _determine_query_complexity(self, fields: List[FieldInfo]) -> str:
        """Determine if custom queries are needed based on field complexity."""
        complex_fields = [f for f in fields if f.type in ['JSON', 'JSONB', 'ARRAY']]
        if complex_fields:
            return 'CUSTOM_QUERIES_REQUIRED'
        return 'STANDARD_QUERIES'
