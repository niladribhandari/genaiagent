"""
Field extraction utility for parsing API specification models and extracting entity fields.
"""

from typing import Dict, List, Any, Optional, Tuple
import re


class Field:
    """Represents a field extracted from API specification."""
    
    def __init__(self, name: str, field_type: str, required: bool = False, 
                 validation: Dict[str, Any] = None, description: str = ""):
        self.name = name
        self.field_type = field_type
        self.java_type = self._map_to_java_type(field_type)
        self.required = required
        self.validation = validation or {}
        self.description = description
        self.jpa_annotations = self._generate_jpa_annotations()
        self.validation_annotations = self._generate_validation_annotations()
    
    def _map_to_java_type(self, api_type: str) -> str:
        """Map API specification type to Java type."""
        type_mapping = {
            'string': 'String',
            'integer': 'Integer',
            'int': 'Integer',
            'long': 'Long',
            'number': 'BigDecimal',
            'decimal': 'BigDecimal',
            'float': 'Double',
            'double': 'Double',
            'boolean': 'Boolean',
            'date': 'LocalDate',
            'datetime': 'LocalDateTime',
            'timestamp': 'LocalDateTime',
            'time': 'LocalTime',
            'uuid': 'UUID',
            'email': 'String',
            'url': 'String',
            'json': 'String',
            'text': 'String'
        }
        
        # Handle List types
        if api_type.startswith('List<') or api_type.startswith('list<'):
            inner_type = api_type[api_type.index('<')+1:api_type.rindex('>')]
            inner_java_type = type_mapping.get(inner_type.lower(), inner_type)
            return f'List<{inner_java_type}>'
        
        # Handle Set types
        if api_type.startswith('Set<') or api_type.startswith('set<'):
            inner_type = api_type[api_type.index('<')+1:api_type.rindex('>')]
            inner_java_type = type_mapping.get(inner_type.lower(), inner_type)
            return f'Set<{inner_java_type}>'
        
        return type_mapping.get(api_type.lower(), api_type)
    
    def _generate_jpa_annotations(self) -> List[str]:
        """Generate JPA annotations for this field."""
        annotations = []
        
        # ID field
        if self.name.lower() == 'id':
            annotations.extend(['@Id', '@GeneratedValue(strategy = GenerationType.AUTO)'])
        else:
            # Regular column
            column_def = f'@Column(name = "{self.name.lower()}"'
            
            # Add nullable constraint
            if self.required:
                column_def += ', nullable = false'
            
            # Add length constraint for strings
            if self.java_type == 'String' and 'max_length' in self.validation:
                column_def += f', length = {self.validation["max_length"]}'
            
            # Add unique constraint
            if self.validation.get('unique', False):
                column_def += ', unique = true'
            
            column_def += ')'
            annotations.append(column_def)
        
        # Timestamp fields
        if self.name.lower() in ['created_at', 'createdat']:
            annotations.append('@CreationTimestamp')
            if '@Column' not in str(annotations):
                annotations.append('@Column(name = "created_at", updatable = false)')
        elif self.name.lower() in ['updated_at', 'updatedat']:
            annotations.append('@UpdateTimestamp')
            if '@Column' not in str(annotations):
                annotations.append('@Column(name = "updated_at")')
        
        return annotations
    
    def _generate_validation_annotations(self) -> List[str]:
        """Generate validation annotations for this field."""
        annotations = []
        
        # Required validation
        if self.required:
            annotations.append('@NotNull')
        
        # String validations
        if self.java_type == 'String':
            size_constraints = []
            if 'min_length' in self.validation:
                size_constraints.append(f'min = {self.validation["min_length"]}')
            if 'max_length' in self.validation:
                size_constraints.append(f'max = {self.validation["max_length"]}')
            
            if size_constraints:
                annotations.append(f'@Size({", ".join(size_constraints)})')
            
            # Email validation
            if 'email' in self.validation and self.validation['email']:
                annotations.append('@Email')
            
            # Pattern validation
            if 'pattern' in self.validation:
                pattern = self.validation['pattern'].replace('"', '\\"')
                annotations.append(f'@Pattern(regexp = "{pattern}")')
        
        # Numeric validations
        if self.java_type in ['Integer', 'Long', 'BigDecimal', 'Double']:
            if 'min' in self.validation:
                if self.java_type == 'BigDecimal':
                    annotations.append(f'@DecimalMin(value = "{self.validation["min"]}")')
                else:
                    annotations.append(f'@Min({self.validation["min"]})')
            
            if 'max' in self.validation:
                if self.java_type == 'BigDecimal':
                    annotations.append(f'@DecimalMax(value = "{self.validation["max"]}")')
                else:
                    annotations.append(f'@Max({self.validation["max"]})')
        
        return annotations
    
    def get_field_declaration(self) -> str:
        """Get the complete field declaration with annotations."""
        lines = []
        
        # Add validation annotations
        for annotation in self.validation_annotations:
            lines.append(f'    {annotation}')
        
        # Add JPA annotations
        for annotation in self.jpa_annotations:
            lines.append(f'    {annotation}')
        
        # Add field declaration
        lines.append(f'    private {self.java_type} {self.name};')
        
        return '\n'.join(lines)


class FieldExtractor:
    """Extract fields from API specification models."""
    
    @staticmethod
    def extract_entity_fields(spec_data: Dict[str, Any], entity_name: str) -> List[Field]:
        """
        Extract fields for an entity from API specification.
        
        Args:
            spec_data: The complete API specification data
            entity_name: Name of the entity to extract fields for
            
        Returns:
            List of Field objects representing the entity's fields
        """
        fields = []
        
        # Get models section
        models = spec_data.get('models', {})
        if not models:
            return FieldExtractor._get_default_fields(entity_name)
        
        # Look for the entity model
        entity_model = None
        
        # Try exact match first
        if entity_name in models:
            entity_model = models[entity_name]
        else:
            # Try case-insensitive match
            for model_name, model_data in models.items():
                if model_name.lower() == entity_name.lower():
                    entity_model = model_data
                    break
        
        if not entity_model:
            return FieldExtractor._get_default_fields(entity_name)
        
        # Extract properties/fields
        properties = entity_model.get('properties', {})
        if not properties:
            # Try alternative field names
            properties = entity_model.get('fields', {})
        
        if not properties:
            return FieldExtractor._get_default_fields(entity_name)
        
        # Process each property
        for field_name, field_def in properties.items():
            if isinstance(field_def, dict):
                field_type = field_def.get('type', 'string')
                required = field_def.get('required', False)
                description = field_def.get('description', '')
                validation = field_def.get('validation', {})
                
                # Extract validation rules from field definition
                if 'min_length' in field_def:
                    validation['min_length'] = field_def['min_length']
                if 'max_length' in field_def:
                    validation['max_length'] = field_def['max_length']
                if 'pattern' in field_def:
                    validation['pattern'] = field_def['pattern']
                if 'email' in field_def:
                    validation['email'] = field_def['email']
                if 'min' in field_def:
                    validation['min'] = field_def['min']
                if 'max' in field_def:
                    validation['max'] = field_def['max']
                if 'unique' in field_def:
                    validation['unique'] = field_def['unique']
                
                field = Field(
                    name=field_name,
                    field_type=field_type,
                    required=required,
                    validation=validation,
                    description=description
                )
                fields.append(field)
            else:
                # Simple field definition (just type)
                field = Field(
                    name=field_name,
                    field_type=str(field_def),
                    required=False
                )
                fields.append(field)
        
        # Ensure we have essential fields
        return FieldExtractor._ensure_essential_fields(fields, entity_name)
    
    @staticmethod
    def _get_default_fields(entity_name: str) -> List[Field]:
        """Get default fields when no model definition is found."""
        return [
            Field('id', 'uuid', required=True, description='Unique identifier'),
            Field('name', 'string', required=True, validation={'min_length': 1, 'max_length': 255}, description='Name'),
            Field('description', 'string', required=False, validation={'max_length': 1000}, description='Description'),
            Field('active', 'boolean', required=False, description='Active status'),
            Field('createdAt', 'datetime', required=False, description='Creation timestamp'),
            Field('updatedAt', 'datetime', required=False, description='Last update timestamp')
        ]
    
    @staticmethod
    def _ensure_essential_fields(fields: List[Field], entity_name: str) -> List[Field]:
        """Ensure essential fields are present."""
        field_names = {f.name.lower() for f in fields}
        
        # Add ID if not present
        if 'id' not in field_names:
            id_field = Field('id', 'uuid', required=True, description='Unique identifier')
            fields.insert(0, id_field)
        
        # Add timestamps if not present
        if 'createdat' not in field_names and 'created_at' not in field_names:
            created_field = Field('createdAt', 'datetime', required=False, description='Creation timestamp')
            fields.append(created_field)
        
        if 'updatedat' not in field_names and 'updated_at' not in field_names:
            updated_field = Field('updatedAt', 'datetime', required=False, description='Last update timestamp')
            fields.append(updated_field)
        
        return fields
    
    @staticmethod
    def get_required_imports(fields: List[Field]) -> List[str]:
        """Get required imports for the given fields."""
        imports = set()
        
        # Basic imports always needed
        imports.update([
            'import jakarta.persistence.*;',
            'import lombok.AllArgsConstructor;',
            'import lombok.Builder;',
            'import lombok.Data;',
            'import lombok.NoArgsConstructor;'
        ])
        
        # Check field types for additional imports
        for field in fields:
            if field.java_type == 'UUID':
                imports.add('import java.util.UUID;')
            elif field.java_type == 'BigDecimal':
                imports.add('import java.math.BigDecimal;')
            elif field.java_type in ['LocalDate', 'LocalDateTime', 'LocalTime']:
                imports.add('import java.time.*;')
            elif field.java_type.startswith('List'):
                imports.add('import java.util.List;')
            elif field.java_type.startswith('Set'):
                imports.add('import java.util.Set;')
            
            # Validation annotations
            if field.validation_annotations:
                imports.add('import jakarta.validation.constraints.*;')
            
            # Timestamp annotations
            if any('Timestamp' in ann for ann in field.jpa_annotations):
                imports.add('import org.hibernate.annotations.CreationTimestamp;')
                imports.add('import org.hibernate.annotations.UpdateTimestamp;')
        
        return sorted(list(imports))


# Export main classes and functions
__all__ = ['Field', 'FieldExtractor']
