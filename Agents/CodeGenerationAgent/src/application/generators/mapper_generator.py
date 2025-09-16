"""MapStruct mapper generator for entity-DTO conversion."""

import logging
from typing import List, Dict, Any

try:
    from src.domain.models.generation_context import GenerationContext
    from src.domain.models.code_models import GeneratedCode, FieldInfo
    from src.application.services.code_generation_service import CodeGenerationService
except ImportError:
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode, FieldInfo
    from application.services.code_generation_service import CodeGenerationService


class MapperGenerator:
    """Specialized generator for MapStruct mapper interfaces."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_mapper(self, context: GenerationContext) -> GeneratedCode:
        """Generate MapStruct mapper for entity-DTO conversion."""
        enhanced_context = self._enhance_mapper_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'MapperGenerator'}
        )
    
    def _enhance_mapper_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context with mapper-specific requirements."""
        entity_name = context.entity_name.replace('Mapper', '') if context.entity_name.endswith('Mapper') else context.entity_name
        
        # Generate mapping configurations
        mapping_configs = self._generate_mapping_configs(context.fields or [], entity_name)
        
        enhanced_requirements = [
            f"MapStruct mapper for {entity_name}",
            "@Mapper(componentModel = \"spring\")",
            "Entity to DTO bidirectional mapping",
            "Request DTO to Entity mapping with ignored audit fields",
            "Entity to Response DTO mapping with all fields",
            "Update method with null value property mapping strategy",
            "Collection mapping support"
        ]
        
        if context.requirements:
            enhanced_requirements.extend(context.requirements)
        
        enhanced_context = GenerationContext(
            entity_name=f"{entity_name}Mapper",
            package_name=f"{context.package_name}.mapper",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/mapper/${ENTITY_NAME}Mapper.java",
            fields=context.fields or [],
            requirements=enhanced_requirements,
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'entity_class': entity_name,
                'request_dto_class': f"{entity_name}Request",
                'response_dto_class': f"{entity_name}Response",
                'mapping_configs': mapping_configs,
                'ignored_fields_for_create': ['id', 'createdAt', 'updatedAt', 'version'],
                'ignored_fields_for_update': ['id', 'createdAt'],
                'uses_collections': self._has_collection_fields(context.fields or [])
            }
        )
        
        return enhanced_context
    
    def _generate_mapping_configs(self, fields: List[FieldInfo], entity_name: str) -> List[Dict[str, Any]]:
        """Generate mapping configurations for complex field mappings."""
        configs = []
        
        for field in fields:
            # Handle special field mappings
            if field.name.lower() == 'status' and field.type == 'String':
                configs.append({
                    'source_field': field.name,
                    'target_field': field.name,
                    'mapping_expression': 'java(mapStatus(source.getStatus()))',
                    'requires_custom_method': True,
                    'custom_method_name': 'mapStatus'
                })
            
            # Handle date formatting
            elif field.type in ['LocalDateTime', 'LocalDate']:
                configs.append({
                    'source_field': field.name,
                    'target_field': field.name,
                    'date_format': 'yyyy-MM-dd HH:mm:ss' if field.type == 'LocalDateTime' else 'yyyy-MM-dd',
                    'requires_formatting': True
                })
            
            # Handle nested objects
            elif self._is_complex_type(field.type):
                configs.append({
                    'source_field': field.name,
                    'target_field': field.name,
                    'mapping_type': 'NESTED_OBJECT',
                    'nested_mapper': f"{field.type}Mapper"
                })
            
            # Handle collections
            elif self._is_collection_type(field.type):
                element_type = self._extract_collection_element_type(field.type)
                configs.append({
                    'source_field': field.name,
                    'target_field': field.name,
                    'mapping_type': 'COLLECTION',
                    'element_type': element_type,
                    'element_mapper': f"{element_type}Mapper" if self._is_complex_type(element_type) else None
                })
        
        return configs
    
    def _has_collection_fields(self, fields: List[FieldInfo]) -> bool:
        """Check if entity has collection fields that need special mapping."""
        return any(self._is_collection_type(field.type) for field in fields)
    
    def _is_complex_type(self, field_type: str) -> bool:
        """Check if field type is a complex object requiring nested mapping."""
        # Simple heuristic: if it's not a primitive or common Java type
        simple_types = {
            'String', 'Integer', 'Long', 'Double', 'Float', 'Boolean', 
            'BigDecimal', 'LocalDate', 'LocalDateTime', 'Date', 'UUID'
        }
        return field_type not in simple_types and not field_type.startswith('List<') and not field_type.startswith('Set<')
    
    def _is_collection_type(self, field_type: str) -> bool:
        """Check if field type is a collection."""
        return field_type.startswith('List<') or field_type.startswith('Set<') or field_type.startswith('Collection<')
    
    def _extract_collection_element_type(self, collection_type: str) -> str:
        """Extract element type from collection type."""
        # Extract type from List<Type>, Set<Type>, etc.
        import re
        match = re.search(r'<([^>]+)>', collection_type)
        return match.group(1) if match else 'Object'
    
    def _generate_custom_mapping_methods(self, configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate custom mapping methods for complex field conversions."""
        custom_methods = []
        
        for config in configs:
            if config.get('requires_custom_method'):
                custom_methods.append({
                    'method_name': config['custom_method_name'],
                    'parameters': [f"String {config['source_field']}"],
                    'return_type': 'String',
                    'implementation': f'// Custom mapping logic for {config["source_field"]}'
                })
        
        return custom_methods
