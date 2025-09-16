"""DTO generator for request/response objects."""

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


class DTOGenerator:
    """Specialized generator for Data Transfer Object classes."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
    
    def generate_request_dto(self, context: GenerationContext) -> GeneratedCode:
        """Generate request DTO with validation annotations."""
        enhanced_context = self._enhance_request_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'DTOGenerator', 'dto_type': 'request'}
        )
    
    def generate_response_dto(self, context: GenerationContext) -> GeneratedCode:
        """Generate response DTO with JSON serialization."""
        enhanced_context = self._enhance_response_context(context)
        result = self.code_service.generate_code(enhanced_context)
        
        return GeneratedCode(
            content=result.content,
            language=result.language,
            framework=result.framework,
            metadata={**result.metadata, 'generator': 'DTOGenerator', 'dto_type': 'response'}
        )
    
    def generate_dto_pair(self, context: GenerationContext) -> Dict[str, GeneratedCode]:
        """Generate both request and response DTOs."""
        return {
            'request': self.generate_request_dto(context),
            'response': self.generate_response_dto(context)
        }
    
    def _enhance_request_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context for request DTO generation."""
        enhanced_fields = self._enhance_fields_for_request(context.fields or [])
        
        enhanced_context = GenerationContext(
            entity_name=f"{context.entity_name}Request",
            package_name=f"{context.package_name}.dto",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/dto/${ENTITY_NAME}Request.java",
            fields=enhanced_fields,
            requirements=[
                "Bean Validation annotations",
                "JSON property annotations", 
                "Input validation for API requests",
                "Lombok Data annotation for getters/setters"
            ],
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'is_request_dto': True,
                'validation_groups': self._determine_validation_groups(enhanced_fields),
                'required_fields': [f for f in enhanced_fields if f.annotations and any('required' in ann.lower() for ann in f.annotations)]
            }
        )
        
        return enhanced_context
    
    def _enhance_response_context(self, context: GenerationContext) -> GenerationContext:
        """Enhance context for response DTO generation."""
        enhanced_fields = self._enhance_fields_for_response(context.fields or [])
        
        # Add standard response fields
        enhanced_fields.extend([
            FieldInfo(name="createdAt", type="LocalDateTime", annotations=["@JsonProperty(\"created_at\")"]),
            FieldInfo(name="updatedAt", type="LocalDateTime", annotations=["@JsonProperty(\"updated_at\")"])
        ])
        
        enhanced_context = GenerationContext(
            entity_name=f"{context.entity_name}Response",
            package_name=f"{context.package_name}.dto",
            target_language=context.target_language,
            framework=context.framework,
            template_path="templates/spring_boot/${BASE_PACKAGE}/dto/${ENTITY_NAME}Response.java",
            fields=enhanced_fields,
            requirements=[
                "JSON serialization annotations",
                "Response formatting for API clients",
                "Lombok Data annotation for getters/setters",
                "Timestamp fields for audit trail"
            ],
            use_ai_enhancement=context.use_ai_enhancement,
            enhancements=context.enhancements or [],
            additional_context={
                **context.additional_context,
                'is_response_dto': True,
                'json_naming_strategy': 'snake_case',
                'include_timestamps': True
            }
        )
        
        return enhanced_context
    
    def _enhance_fields_for_request(self, fields: List[FieldInfo]) -> List[FieldInfo]:
        """Enhance fields with request-specific validation annotations."""
        enhanced_fields = []
        
        for field in fields:
            enhanced_field = FieldInfo(
                name=field.name,
                type=field.type,
                annotations=field.annotations or []
            )
            
            # Add validation annotations based on field type and requirements
            if field.type == 'String':
                if field.name.lower() in ['email']:
                    enhanced_field.annotations.extend(['@Email', '@NotBlank'])
                elif field.name.lower() in ['name', 'title']:
                    enhanced_field.annotations.extend(['@NotBlank', '@Size(max = 255)'])
                else:
                    enhanced_field.annotations.append('@Size(max = 500)')
            
            elif field.type in ['Long', 'Integer', 'BigDecimal']:
                enhanced_field.annotations.append('@Positive')
            
            # Add JSON property annotation
            json_name = self._to_snake_case(field.name)
            enhanced_field.annotations.append(f'@JsonProperty("{json_name}")')
            
            enhanced_fields.append(enhanced_field)
        
        return enhanced_fields
    
    def _enhance_fields_for_response(self, fields: List[FieldInfo]) -> List[FieldInfo]:
        """Enhance fields with response-specific annotations."""
        enhanced_fields = []
        
        for field in fields:
            enhanced_field = FieldInfo(
                name=field.name,
                type=field.type,
                annotations=field.annotations or []
            )
            
            # Add JSON property annotation with snake_case naming
            json_name = self._to_snake_case(field.name)
            enhanced_field.annotations = [f'@JsonProperty("{json_name}")']
            
            # Add formatting annotations for specific types
            if field.type == 'LocalDateTime':
                enhanced_field.annotations.append('@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")')
            elif field.type == 'LocalDate':
                enhanced_field.annotations.append('@JsonFormat(pattern = "yyyy-MM-dd")')
            elif field.type == 'BigDecimal':
                enhanced_field.annotations.append('@JsonFormat(shape = JsonFormat.Shape.STRING)')
            
            enhanced_fields.append(enhanced_field)
        
        return enhanced_fields
    
    def _determine_validation_groups(self, fields: List[FieldInfo]) -> List[str]:
        """Determine validation groups based on field requirements."""
        groups = ['Default']
        
        # Add specific validation groups based on field patterns
        has_create_fields = any(f.name.lower() in ['name', 'title'] for f in fields)
        has_update_fields = any(f.name.lower() in ['status', 'description'] for f in fields)
        
        if has_create_fields:
            groups.append('Create')
        if has_update_fields:
            groups.append('Update')
        
        return groups
    
    def _to_snake_case(self, camel_case: str) -> str:
        """Convert camelCase to snake_case for JSON properties."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
