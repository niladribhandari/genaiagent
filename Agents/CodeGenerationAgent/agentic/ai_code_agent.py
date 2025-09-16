"""Enhanced AI-powered code generation agent."""

import logging
from typing import Dict, Any, List, Optional
import re

from .core import BaseAgent, AgentGoal


class GenerationContext:
    """Context for code generation."""
    
    def __init__(self, entity_name: str, package_name: str, file_type: str,
                 language: str, framework: str, template_content: str,
                 spec_data: Dict[str, Any], instruction_data: Dict[str, Any],
                 output_path: str):
        self.entity_name = entity_name
        self.package_name = package_name
        self.file_type = file_type
        self.language = language
        self.framework = framework
        self.template_content = template_content
        self.spec_data = spec_data
        self.instruction_data = instruction_data
        self.output_path = output_path


class EnhancedCodeGenerationAgent(BaseAgent):
    """Enhanced AI-powered code generation agent with smart import processing."""
    
    def __init__(self):
        super().__init__(
            agent_id="enhanced_codegen_agent", 
            name="Enhanced Code Generation Agent",
            capabilities=["smart_import_processing", "business_logic_enhancement"]
        )
    
    def _enhance_java_imports(self, content: str, context: GenerationContext) -> str:
        """Enhanced Java import processing with smart detection and organization."""
        
        # Standard Java imports
        java_imports = {
            'List': 'java.util.List',
            'Map': 'java.util.Map',
            'Set': 'java.util.Set',
            'HashMap': 'java.util.HashMap',
            'ArrayList': 'java.util.ArrayList',
            'HashSet': 'java.util.HashSet',
            'UUID': 'java.util.UUID',
            'Optional': 'java.util.Optional',
            'LocalDate': 'java.time.LocalDate',
            'LocalDateTime': 'java.time.LocalDateTime',
            'BigDecimal': 'java.math.BigDecimal'
        }
        
        # Spring imports
        spring_imports = {
            'RestController': 'org.springframework.web.bind.annotation.RestController',
            'RequestMapping': 'org.springframework.web.bind.annotation.RequestMapping',
            'GetMapping': 'org.springframework.web.bind.annotation.GetMapping',
            'PostMapping': 'org.springframework.web.bind.annotation.PostMapping',
            'PutMapping': 'org.springframework.web.bind.annotation.PutMapping',
            'DeleteMapping': 'org.springframework.web.bind.annotation.DeleteMapping',
            'RequestBody': 'org.springframework.web.bind.annotation.RequestBody',
            'PathVariable': 'org.springframework.web.bind.annotation.PathVariable',
            'RequestParam': 'org.springframework.web.bind.annotation.RequestParam',
            'ResponseEntity': 'org.springframework.http.ResponseEntity',
            'Service': 'org.springframework.stereotype.Service',
            'Repository': 'org.springframework.stereotype.Repository',
            'Component': 'org.springframework.stereotype.Component',
            'Autowired': 'org.springframework.beans.factory.annotation.Autowired',
            'Transactional': 'org.springframework.transaction.annotation.Transactional',
            'Entity': 'jakarta.persistence.Entity',
            'Id': 'jakarta.persistence.Id',
            'GeneratedValue': 'jakarta.persistence.GeneratedValue',
            'Column': 'jakarta.persistence.Column',
            'Table': 'jakarta.persistence.Table',
            'JpaRepository': 'org.springframework.data.jpa.repository.JpaRepository',
            'Page': 'org.springframework.data.domain.Page',
            'Pageable': 'org.springframework.data.domain.Pageable'
        }
        
        # Validation imports
        validation_imports = {
            'Valid': 'jakarta.validation.Valid',
            'NotNull': 'jakarta.validation.constraints.NotNull',
            'NotBlank': 'jakarta.validation.constraints.NotBlank',
            'NotEmpty': 'jakarta.validation.constraints.NotEmpty',
            'Size': 'jakarta.validation.constraints.Size',
            'Min': 'jakarta.validation.constraints.Min',
            'Max': 'jakarta.validation.constraints.Max',
            'Email': 'jakarta.validation.constraints.Email',
            'Pattern': 'jakarta.validation.constraints.Pattern'
        }
        
        # Lombok imports
        lombok_imports = {
            'RequiredArgsConstructor': 'lombok.RequiredArgsConstructor',
            'Data': 'lombok.Data',
            'Builder': 'lombok.Builder',
            'NoArgsConstructor': 'lombok.NoArgsConstructor',
            'AllArgsConstructor': 'lombok.AllArgsConstructor',
            'Getter': 'lombok.Getter',
            'Setter': 'lombok.Setter'
        }
        
        # OpenAPI/Swagger imports
        openapi_imports = {
            'Tag': 'io.swagger.v3.oas.annotations.tags.Tag',
            'Operation': 'io.swagger.v3.oas.annotations.Operation',
            'Parameter': 'io.swagger.v3.oas.annotations.Parameter',
            'Schema': 'io.swagger.v3.oas.annotations.media.Schema'
        }
        
        # Combine all import mappings
        all_imports = {**java_imports, **spring_imports, **validation_imports, 
                      **lombok_imports, **openapi_imports}
        
        # Find all annotations and classes used in the content
        used_annotations = re.findall(r'@(\w+)', content)
        used_classes = re.findall(r'\b([A-Z]\w+)(?:<[^>]*>)?\s+\w+', content)
        used_types = re.findall(r':\s*([A-Z]\w+)(?:<[^>]*>)?', content)
        
        # Combine all used symbols
        used_symbols = set(used_annotations + used_classes + used_types)
        
        # Generate required imports
        required_imports = set()
        
        for symbol in used_symbols:
            if symbol in all_imports:
                required_imports.add(all_imports[symbol])
        
        # Add package-specific imports based on file type
        base_package = context.package_name.rsplit('.', 1)[0]  # Remove the last part (.controller, .service, etc.)
        
        if context.file_type == 'controller':
            # Controllers need DTOs and services
            entity_name = context.entity_name
            required_imports.add(f'{base_package}.dto.{entity_name}Request')
            required_imports.add(f'{base_package}.dto.{entity_name}Response') 
            required_imports.add(f'{base_package}.service.{entity_name}Service')
            
        elif context.file_type == 'service':
            # Services need DTOs, models, and repositories
            entity_name = context.entity_name.replace('Service', '')
            required_imports.add(f'{base_package}.dto.{entity_name}Request')
            required_imports.add(f'{base_package}.dto.{entity_name}Response')
            required_imports.add(f'{base_package}.model.{entity_name}')
            required_imports.add(f'{base_package}.repository.{entity_name}Repository')
            
        elif context.file_type == 'repository':
            # Repositories need models
            entity_name = context.entity_name.replace('Repository', '')
            required_imports.add(f'{base_package}.model.{entity_name}')
        
        # Extract existing imports
        existing_imports = set()
        import_pattern = r'import\s+([^;]+);'
        existing_import_matches = re.findall(import_pattern, content)
        for imp in existing_import_matches:
            existing_imports.add(imp.strip())
        
        # Add missing imports
        new_imports = required_imports - existing_imports
        
        if new_imports:
            # Sort imports
            sorted_imports = sorted(new_imports)
            
            # Find package declaration
            package_match = re.search(r'^package\s+([^;]+);', content, re.MULTILINE)
            if package_match:
                package_end = package_match.end()
                
                # Insert imports after package declaration
                import_section = '\n\n' + '\n'.join(f'import {imp};' for imp in sorted_imports)
                content = content[:package_end] + import_section + content[package_end:]
        
        return content
