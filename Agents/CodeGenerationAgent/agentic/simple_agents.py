"""Simple specialized agents for code generation tasks."""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile

from .core import BaseAgent, AgentGoal
from .utils.pluralization import pluralize
from .utils.field_extractor import FieldExtractor
from .utils.integration_extractor import IntegrationExtractor


class SimpleConfigurationAgent(BaseAgent):
    """Agent responsible for loading and validating configuration files."""
    
    def __init__(self):
        super().__init__(
            agent_id="config_agent",
            name="Configuration Agent",
            capabilities=["load_specification", "load_instructions", "validate_compatibility"]
        )
    
    async def _execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute configuration-related goals."""
        if goal.id == "load_specification":
            return await self._load_specification(goal.context)
        elif goal.id == "load_instructions":
            return await self._load_instructions(goal.context)
        elif goal.id == "validate_compatibility":
            return await self._validate_compatibility(goal.context)
        else:
            raise ValueError(f"Unknown goal: {goal.id}")
    
    async def _load_specification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load API specification file."""
        spec_path = context.get("spec_path")
        if not spec_path or not os.path.exists(spec_path):
            raise FileNotFoundError(f"Specification file not found: {spec_path}")
        
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec_data = yaml.safe_load(f)
            
            # Extract entities - focus on main business entities, not DTOs
            entities = []
            
            # Primary approach: use the main entity if defined
            if 'entity' in spec_data:
                main_entity = spec_data['entity']['name']
                entities.append(main_entity)
                self.logger.info(f"Found main entity: {main_entity}")
            
            # Secondary approach: extract business entities from endpoints
            elif 'endpoints' in spec_data:
                # Look for main business entities from endpoint paths
                paths = set()
                for endpoint in spec_data['endpoints']:
                    path = endpoint.get('path', '')
                    if path.startswith('/'):
                        # Extract entity name from path like /policies -> Policy
                        path_parts = path.strip('/').split('/')
                        if path_parts and path_parts[0]:
                            entity_name = path_parts[0].rstrip('s').title()  # policies -> Policy
                            paths.add(entity_name)
                
                entities.extend(list(paths))
                self.logger.info(f"Extracted entities from endpoints: {entities}")
            
            # Fallback: use a default entity
            if not entities:
                entities = ["Policy"]  # Default fallback
                self.logger.info("Using default entity: Policy")
            
            # Remove duplicates and limit to reasonable number
            entities = list(set(entities))
            if len(entities) > 5:
                self.logger.warning(f"Too many entities found ({len(entities)}), limiting to main ones")
                entities = entities[:5]
            
            return {
                "success": True,
                "spec_data": spec_data,
                "entities": entities,
                "file_path": spec_path
            }
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in specification file: {e}")
    
    async def _load_instructions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load instruction template file."""
        instruction_path = context.get("instruction_path")
        if not instruction_path or not os.path.exists(instruction_path):
            raise FileNotFoundError(f"Instruction file not found: {instruction_path}")
        
        try:
            with open(instruction_path, 'r', encoding='utf-8') as f:
                instruction_data = yaml.safe_load(f)
            
            return {
                "success": True,
                "instruction_data": instruction_data,
                "framework": instruction_data.get("framework", "unknown"),
                "language": instruction_data.get("language", "unknown"),
                "file_path": instruction_path
            }
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in instruction file: {e}")
    
    async def _validate_compatibility(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compatibility between specification and instructions."""
        spec_data = context.get("spec_data", {})
        instruction_data = context.get("instruction_data", {})
        
        issues = []
        
        # Check language compatibility
        spec_language = spec_data.get("language", "").lower()
        instruction_language = instruction_data.get("language", "").lower()
        
        if spec_language and instruction_language and spec_language != instruction_language:
            issues.append(f"Language mismatch: spec={spec_language}, instruction={instruction_language}")
        
        # Check framework compatibility
        spec_framework = spec_data.get("framework", "").lower()
        instruction_framework = instruction_data.get("framework", "").lower()
        
        if spec_framework and instruction_framework and spec_framework != instruction_framework:
            issues.append(f"Framework mismatch: spec={spec_framework}, instruction={instruction_framework}")
        
        return {
            "success": len(issues) == 0,
            "compatibility_issues": issues,
            "validated": True
        }
    
    def can_handle_goal(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        return goal.id in self.capabilities


class SimpleStructureAgent(BaseAgent):
    """Agent responsible for setting up project structure."""
    
    def __init__(self):
        super().__init__(
            agent_id="structure_agent",
            name="Structure Agent", 
            capabilities=["setup_project_structure"]
        )
    
    async def _execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute structure-related goals."""
        if goal.id == "setup_project_structure":
            return await self._setup_project_structure(goal.context)
        else:
            raise ValueError(f"Unknown goal: {goal.id}")
    
    async def _setup_project_structure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create project directory structure."""
        output_path = context.get("output_path")
        instruction_data = context.get("instruction_data", {})
        
        if not output_path:
            raise ValueError("Output path not provided")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        directories_created = 0
        
        # Get project structure from instructions
        project_structure = instruction_data.get("project_structure", {})
        
        # Create standard Java/Spring Boot structure if not specified
        if not project_structure:
            project_structure = {
                "src": {
                    "main": {
                        "java": {},
                        "resources": {}
                    },
                    "test": {
                        "java": {},
                        "resources": {}
                    }
                }
            }
        
        # Create directories recursively
        def create_dirs(base_path: Path, structure: Dict[str, Any]):
            nonlocal directories_created
            for name, subdirs in structure.items():
                if name.endswith("/"):
                    name = name[:-1]
                
                dir_path = base_path / name
                dir_path.mkdir(parents=True, exist_ok=True)
                directories_created += 1
                
                if isinstance(subdirs, dict):
                    create_dirs(dir_path, subdirs)
        
        create_dirs(output_dir, project_structure)
        
        return {
            "success": True,
            "directory_count": directories_created,
            "output_path": str(output_dir),
            "structure_created": True
        }
    
    def can_handle_goal(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        return goal.id in self.capabilities


class SimpleTemplateAgent(BaseAgent):
    """Agent responsible for processing templates."""
    
    def __init__(self):
        super().__init__(
            agent_id="template_agent",
            name="Template Agent",
            capabilities=["process_all_templates"]
        )
        
        # Template definitions for code generation
        self.template_definitions = {
            # Core entity templates
            "controller": {
                "template": "Controller.java",
                "output_path": "src/main/java/{package_path}/controller/{entity}Controller.java",
                "package_suffix": ".controller"
            },
            "service": {
                "template": "Service.java", 
                "output_path": "src/main/java/{package_path}/service/{entity}Service.java",
                "package_suffix": ".service"
            },
            "service_impl": {
                "template": "ServiceImpl.java",
                "output_path": "src/main/java/{package_path}/service/impl/{entity}ServiceImpl.java", 
                "package_suffix": ".service.impl"
            },
            "repository": {
                "template": "Repository.java",
                "output_path": "src/main/java/{package_path}/repository/{entity}Repository.java",
                "package_suffix": ".repository"
            },
            "model": {
                "template": "Entity.java",
                "output_path": "src/main/java/{package_path}/model/{entity}.java",
                "package_suffix": ".model"
            },
            "dto_request": {
                "template": "RequestDto.java",
                "output_path": "src/main/java/{package_path}/dto/{entity}Request.java",
                "package_suffix": ".dto"
            },
            "dto_response": {
                "template": "ResponseDto.java", 
                "output_path": "src/main/java/{package_path}/dto/{entity}Response.java",
                "package_suffix": ".dto"
            },
            "mapper": {
                "template": "Mapper.java",
                "output_path": "src/main/java/{package_path}/mapper/{entity}Mapper.java",
                "package_suffix": ".mapper"
            },
            "exception": {
                "template": "Exception.java",
                "output_path": "src/main/java/{package_path}/exception/{entity}NotFoundException.java",
                "package_suffix": ".exception"
            }
        }
    
    async def _execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute template-related goals."""
        if goal.id == "process_all_templates":
            return await self._process_all_templates(goal.context)
        else:
            raise ValueError(f"Unknown goal: {goal.id}")
    
    async def _process_all_templates(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process templates for all entities."""
        spec_data = context.get("spec_data", {})
        instruction_data = context.get("instruction_data", {})
        output_path = context.get("output_path", "")
        
        # Get entities to process
        entities = context.get("entities", [])
        if not entities and "entity" in spec_data:
            entities = [spec_data["entity"]["name"]]
        
        if not entities:
            entities = ["Default"]  # Fallback entity name
        
        processed_templates = {}
        template_count = 0
        files_written = 0
        
        # Get base package from spec or instruction
        base_package = (spec_data.get("base_package") or 
                       spec_data.get("metadata", {}).get("base_package") or
                       instruction_data.get("base_package", "com.example.demo"))
        
        # Get project name for application class
        project_name = spec_data.get("metadata", {}).get("project", {}).get("name", "Generated")
        app_class_name = "".join(project_name.split()) + "Application"
        
        # Template definitions based on instruction file
        template_definitions = {
            # Existing entity templates (enhanced)
            "controller": {
                "template": "Controller.java",
                "output_path": "src/main/java/{package_path}/controller/{entity}Controller.java",
                "package_suffix": ".controller"
            },
            "service": {
                "template": "Service.java", 
                "output_path": "src/main/java/{package_path}/service/{entity}Service.java",
                "package_suffix": ".service"
            },
            "service_impl": {
                "template": "ServiceImpl.java",
                "output_path": "src/main/java/{package_path}/service/impl/{entity}ServiceImpl.java", 
                "package_suffix": ".service.impl"
            },
            "repository": {
                "template": "Repository.java",
                "output_path": "src/main/java/{package_path}/repository/{entity}Repository.java",
                "package_suffix": ".repository"
            },
            "model": {
                "template": "Entity.java",
                "output_path": "src/main/java/{package_path}/model/{entity}.java",
                "package_suffix": ".model"
            },
            "dto_request": {
                "template": "RequestDto.java",
                "output_path": "src/main/java/{package_path}/dto/{entity}Request.java",
                "package_suffix": ".dto"
            },
            "dto_response": {
                "template": "ResponseDto.java", 
                "output_path": "src/main/java/{package_path}/dto/{entity}Response.java",
                "package_suffix": ".dto"
            },
            "mapper": {
                "template": "Mapper.java",
                "output_path": "src/main/java/{package_path}/mapper/{entity}Mapper.java",
                "package_suffix": ".mapper"
            },
            "exception": {
                "template": "Exception.java",
                "output_path": "src/main/java/{package_path}/exception/{entity}NotFoundException.java",
                "package_suffix": ".exception"
            },
            "client": {
                "template": "Client.java",
                "output_path": "src/main/java/{package_path}/client/{entity}Client.java",
                "package_suffix": ".client"
            },
            "config": {
                "template": "Config.java",
                "output_path": "src/main/java/{package_path}/config/{entity}Config.java",
                "package_suffix": ".config"
            },
            
            # Project structure templates (new)
            "pom_xml": {
                "template": "pom.xml",
                "output_path": "pom.xml",
                "package_suffix": ""
            },
            "main_application": {
                "template": f"{app_class_name}.java", 
                "output_path": f"src/main/java/{{package_path}}/{app_class_name}.java",
                "package_suffix": ""
            },
            "application_properties": {
                "template": "application.yml",
                "output_path": "src/main/resources/application.yml", 
                "package_suffix": ""
            },
            
            # Exception templates (new)
            "resource_not_found_exception": {
                "template": "ResourceNotFoundException.java",
                "output_path": "src/main/java/{package_path}/exception/ResourceNotFoundException.java",
                "package_suffix": ".exception"
            },
            "bad_request_exception": {
                "template": "BadRequestException.java", 
                "output_path": "src/main/java/{package_path}/exception/BadRequestException.java",
                "package_suffix": ".exception"
            },
            "global_exception_handler": {
                "template": "GlobalExceptionHandler.java",
                "output_path": "src/main/java/{package_path}/exception/GlobalExceptionHandler.java", 
                "package_suffix": ".exception"
            }
        }
        
        # Process templates for each entity
        for entity_name in entities:
            entity_templates = {}
            
            for template_key, template_def in template_definitions.items():
                package_path = base_package.replace(".", "/")
                full_package = base_package + template_def["package_suffix"]
                
                relative_output_path = template_def["output_path"].format(
                    package_path=package_path,
                    entity=entity_name
                )
                
                # Create full output path
                full_output_path = Path(output_path) / relative_output_path
                
                # Create basic template content (will be enhanced later)
                template_content = self._generate_enterprise_template(
                    template_def["template"],
                    entity_name,
                    full_package,
                    base_package,
                    spec_data
                )
                
                # Write file to disk
                try:
                    full_output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_output_path, 'w', encoding='utf-8') as f:
                        f.write(template_content)
                    files_written += 1
                    self.logger.info(f"Generated: {relative_output_path}")
                except Exception as e:
                    self.logger.error(f"Failed to write {relative_output_path}: {e}")
                
                entity_templates[template_key] = {
                    "template_name": template_def["template"],
                    "content": template_content,
                    "output_path": str(full_output_path),
                    "relative_path": relative_output_path,
                    "package_name": full_package,
                    "entity_name": entity_name
                }
                
                template_count += 1
            
            processed_templates[entity_name] = entity_templates
        
        return {
            "success": True,
            "processed_templates": processed_templates,
            "template_count": template_count,
            "entities_processed": len(entities),
            "files_written": files_written,
            "generated_files": {entity: list(templates.keys()) for entity, templates in processed_templates.items()}
        }
    
    def can_handle_goal(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        return goal.id in self.capabilities
    
    def _generate_enterprise_template(self, template_name: str, entity_name: str, 
                                    full_package: str, base_package: str, spec_data: Dict[str, Any]) -> str:
        """Generate enterprise-grade template content matching old agent quality."""
        
        # Get metadata for enhanced templates
        metadata = spec_data.get("metadata", {})
        company_name = metadata.get("company_name", metadata.get("company", {}).get("name", "Example"))
        api_version = spec_data.get("api", {}).get("version", "v1")
        api_base_path = spec_data.get("api", {}).get("base_path", "/api/v1")
        
        # Create plurals and variations using proper pluralization
        entity_lower = entity_name.lower()
        entity_upper = entity_name.upper()
        entity_plural = pluralize(entity_name)
        entity_plural_lower = entity_plural.lower()
        
        if template_name == "Controller.java":
            return f"""package {full_package};

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import {base_package}.dto.{entity_name}Request;
import {base_package}.dto.{entity_name}Response;
import {base_package}.service.{entity_name}Service;

@RestController
@RequestMapping("{api_base_path}/{entity_plural_lower}")
@Tag(name = "{entity_name}", description = "{entity_name} management APIs")
@RequiredArgsConstructor
public class {entity_name}Controller {{

    private static final Logger logger = LoggerFactory.getLogger({entity_name}Controller.class);

    private final {entity_name}Service {entity_lower}Service;

    @GetMapping
    @Operation(summary = "Get all {entity_plural_lower}", description = "Retrieves a paginated list of all {entity_plural_lower}")
    public ResponseEntity<Page<{entity_name}Response>> getAll{entity_plural}(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {{
        return ResponseEntity.ok({entity_lower}Service.getAll{entity_plural}(page, size));
    }}

    @GetMapping("/{{id}}")
    @Operation(summary = "Get {entity_lower} by ID", description = "Retrieves a {entity_lower} by their ID")
    public ResponseEntity<{entity_name}Response> get{entity_name}ById(@PathVariable UUID id) {{
        return ResponseEntity.ok({entity_lower}Service.get{entity_name}ById(id));
    }}

    @PostMapping
    @Operation(summary = "Create {entity_lower}", description = "Creates a new {entity_lower}")
    public ResponseEntity<{entity_name}Response> create{entity_name}(
            @RequestBody @Valid {entity_name}Request request) {{
        {entity_name}Response response = {entity_lower}Service.create{entity_name}(request);
        return ResponseEntity
            .created(URI.create("{api_base_path}/{entity_plural_lower}/" + response.getId()))
            .body(response);
    }}

    @PutMapping("/{{id}}")
    @Operation(summary = "Update {entity_lower}", description = "Updates an existing {entity_lower}")
    public ResponseEntity<{entity_name}Response> update{entity_name}(
            @PathVariable UUID id,
            @RequestBody @Valid {entity_name}Request request) {{
        return ResponseEntity.ok({entity_lower}Service.update{entity_name}(id, request));
    }}

    @DeleteMapping("/{{id}}")
    @Operation(summary = "Delete {entity_lower}", description = "Deletes a {entity_lower}")
    public ResponseEntity<Void> delete{entity_name}(@PathVariable UUID id) {{
        {entity_lower}Service.delete{entity_name}(id);
        return ResponseEntity.noContent().build();
    }}
}}"""

        elif template_name == "ServiceImpl.java":
            return f"""package {full_package};

import {base_package}.dto.{entity_name}Request;
import {base_package}.dto.{entity_name}Response;
import {base_package}.model.{entity_name};
import {base_package}.repository.{entity_name}Repository;
import {base_package}.service.{entity_name}Service;
import {base_package}.mapper.{entity_name}Mapper;
import {base_package}.exception.ResourceNotFoundException;
import {base_package}.exception.BadRequestException;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Service implementation for {entity_name} operations
 */
@Service
@RequiredArgsConstructor
@Transactional
public class {entity_name}ServiceImpl implements {entity_name}Service {{

    private static final Logger logger = LoggerFactory.getLogger({entity_name}ServiceImpl.class);

    private final {entity_name}Repository {entity_lower}Repository;
    private final {entity_name}Mapper {entity_lower}Mapper;

    @Override
    @Transactional(readOnly = true)
    public Page<{entity_name}Response> getAll{entity_plural}(int page, int size) {{
        logger.info("Retrieving all {entity_plural_lower} - page: {{}}, size: {{}}", page, size);
        return {entity_lower}Repository.findAll(PageRequest.of(page, size))
            .map({entity_lower}Mapper::toResponse);
    }}

    @Override
    @Transactional(readOnly = true)
    public {entity_name}Response get{entity_name}ById(UUID id) {{
        logger.info("Retrieving {entity_lower} with ID: {{}}", id);
        return {entity_lower}Repository.findById(id)
            .map({entity_lower}Mapper::toResponse)
            .orElseThrow(() -> new ResourceNotFoundException("{entity_name} not found with ID: " + id));
    }}

    @Override
    public {entity_name}Response create{entity_name}({entity_name}Request request) {{
        logger.info("Creating new {entity_lower}: {{}}", request);
        
        if (request.getName() != null && {entity_lower}Repository.existsByName(request.getName())) {{
            throw new BadRequestException("{entity_name} with name '" + request.getName() + "' already exists");
        }}

        {entity_name} {entity_lower} = {entity_lower}Mapper.toEntity(request);
        {entity_name} saved{entity_name} = {entity_lower}Repository.save({entity_lower});
        
        logger.info("Successfully created {entity_lower} with ID: {{}}", saved{entity_name}.getId());
        return {entity_lower}Mapper.toResponse(saved{entity_name});
    }}

    @Override
    public {entity_name}Response update{entity_name}(UUID id, {entity_name}Request request) {{
        logger.info("Updating {entity_lower} with ID: {{}}", id);

        {entity_name} existing{entity_name} = {entity_lower}Repository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("{entity_name} not found with ID: " + id));

        // Check name uniqueness if name is being changed
        if (request.getName() != null && 
            !existing{entity_name}.getName().equals(request.getName()) &&
            {entity_lower}Repository.existsByName(request.getName())) {{
            throw new BadRequestException("{entity_name} with name '" + request.getName() + "' already exists");
        }}

        {entity_lower}Mapper.updateEntity(request, existing{entity_name});
        {entity_name} updated{entity_name} = {entity_lower}Repository.save(existing{entity_name});
        
        logger.info("Successfully updated {entity_lower} with ID: {{}}", id);
        return {entity_lower}Mapper.toResponse(updated{entity_name});
    }}

    @Override
    public void delete{entity_name}(UUID id) {{
        logger.info("Deleting {entity_lower} with ID: {{}}", id);
        
        if (!{entity_lower}Repository.existsById(id)) {{
            throw new ResourceNotFoundException("{entity_name} not found with ID: " + id);
        }}
        
        {entity_lower}Repository.deleteById(id);
        logger.info("Successfully deleted {entity_lower} with ID: {{}}", id);
    }}

    @Override
    @Transactional(readOnly = true)
    public boolean exists{entity_name}ByName(String name) {{
        logger.info("Checking if {entity_lower} exists with name: {{}}", name);
        return {entity_lower}Repository.existsByName(name);
    }}
}}"""

        elif template_name == "Entity.java":
            return self._generate_entity_template_full(entity_name, full_package, base_package, spec_data)
            
        elif template_name == "Service.java":
            return self._generate_service_interface_template_full(entity_name, full_package, base_package)
            
        elif template_name == "Repository.java":
            return self._generate_repository_template_full(entity_name, full_package, base_package)
            
        elif template_name == "RequestDto.java":
            return self._generate_request_dto_template_full(entity_name, full_package, spec_data)
            
        elif template_name == "ResponseDto.java":
            return self._generate_response_dto_template_full(entity_name, full_package, spec_data)
            
        elif template_name == "Mapper.java":
            return self._generate_mapper_template_full(entity_name, full_package, base_package)
            
        elif template_name == "Exception.java":
            return self._generate_exception_template_full(entity_name, full_package)
            
        elif template_name == "Client.java":
            return self._generate_client_template_full(entity_name, full_package, base_package, spec_data)
            
        elif template_name == "Config.java":
            return self._generate_config_template_full(entity_name, full_package, base_package)
            
        elif template_name == "pom.xml":
            return self._generate_pom_xml_template(spec_data, base_package)
            
        elif template_name.endswith("Application.java"):
            # Generate appropriate class name for the application
            metadata = spec_data.get("metadata", {})
            project_name = metadata.get("project", {}).get("name", "Generated")
            app_class_name = "".join(project_name.split()) + "Application"
            return self._generate_main_application_template(full_package, spec_data, app_class_name)
            
        elif template_name == "application.yml":
            return self._generate_application_properties_template(spec_data)
            
        elif template_name == "ResourceNotFoundException.java":
            return self._generate_resource_not_found_exception_template(full_package)
            
        elif template_name == "BadRequestException.java":
            return self._generate_bad_request_exception_template(full_package)
            
        elif template_name == "GlobalExceptionHandler.java":
            return self._generate_global_exception_handler_template(full_package)
            
        else:
            # Use the original basic template for other types
            return self._generate_basic_template(template_name, entity_name, full_package, base_package, spec_data)
    
    def _generate_basic_template(self, template_name: str, entity_name: str, 
                               full_package: str, base_package: str, spec_data: Dict[str, Any]) -> str:
        """Generate basic template content as placeholder."""
        if template_name == "Controller.java":
            return f"""package {full_package};

import {base_package}.dto.{entity_name}Request;
import {base_package}.dto.{entity_name}Response;
import {base_package}.service.{entity_name}Service;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/{entity_name.lower()}")
@RequiredArgsConstructor
public class {entity_name}Controller {{
    
    private final {entity_name}Service {entity_name.lower()}Service;
    
    @GetMapping
    public List<{entity_name}Response> getAll() {{
        return {entity_name.lower()}Service.getAll();
    }}
    
    @GetMapping("/{{id}}")
    public {entity_name}Response getById(@PathVariable UUID id) {{
        return {entity_name.lower()}Service.getById(id);
    }}
    
    @PostMapping
    public {entity_name}Response create(@RequestBody {entity_name}Request request) {{
        return {entity_name.lower()}Service.create(request);
    }}
    
    @PutMapping("/{{id}}")
    public {entity_name}Response update(@PathVariable UUID id, @RequestBody {entity_name}Request request) {{
        return {entity_name.lower()}Service.update(id, request);
    }}
    
    @DeleteMapping("/{{id}}")
    public void delete(@PathVariable UUID id) {{
        {entity_name.lower()}Service.delete(id);
    }}
}}"""
        
        elif template_name == "Service.java":
            return f"""package {full_package};

import {base_package}.dto.{entity_name}Request;
import {base_package}.dto.{entity_name}Response;
import java.util.List;
import java.util.UUID;

public interface {entity_name}Service {{
    
    List<{entity_name}Response> getAll();
    {entity_name}Response getById(UUID id);
    {entity_name}Response create({entity_name}Request request);
    {entity_name}Response update(UUID id, {entity_name}Request request);
    void delete(UUID id);
}}"""
        
        elif template_name == "ServiceImpl.java":
            return f"""package {full_package};

import {base_package}.dto.{entity_name}Request;
import {base_package}.dto.{entity_name}Response;
import {base_package}.service.{entity_name}Service;
import {base_package}.repository.{entity_name}Repository;
import {base_package}.model.{entity_name};
import org.springframework.stereotype.Service;
import lombok.RequiredArgsConstructor;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class {entity_name}ServiceImpl implements {entity_name}Service {{
    
    private final {entity_name}Repository {entity_name.lower()}Repository;
    
    @Override
    public List<{entity_name}Response> getAll() {{
        // Implementation needed
        return null;
    }}
    
    @Override
    public {entity_name}Response getById(UUID id) {{
        // Implementation needed
        return null;
    }}
    
    @Override
    public {entity_name}Response create({entity_name}Request request) {{
        // Implementation needed
        return null;
    }}
    
    @Override
    public {entity_name}Response update(UUID id, {entity_name}Request request) {{
        // Implementation needed
        return null;
    }}
    
    @Override
    public void delete(UUID id) {{
        // Implementation needed
    }}
}}"""
        
        else:
            return f"""// Generated {template_name} for {entity_name}
package {full_package};

public class {entity_name} {{
    // Basic implementation needed
}}"""

    def _generate_entity_template_full(self, entity_name: str, full_package: str, 
                                     base_package: str, spec_data: Dict[str, Any]) -> str:
        """Generate full JPA entity template with fields from API spec."""
        
        # Extract fields from API specification using field extractor
        fields = FieldExtractor.extract_entity_fields(spec_data, entity_name)
        
        # Generate imports based on extracted fields (already includes Lombok imports)
        imports = FieldExtractor.get_required_imports(fields)
        imports_str = "\n".join(imports)
        
        # Generate field declarations
        field_declarations = [field.get_field_declaration() for field in fields]
        fields_str = "\n\n".join(field_declarations)
        
        # Use proper pluralization for table name
        table_name = pluralize(entity_name.lower())
        
        return f"""package {full_package};

{imports_str}

/**
 * JPA Entity for {entity_name}
 * Generated from API specification
 */
@Entity
@Table(name = "{table_name}")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class {entity_name} {{

{fields_str}
}}"""

    def _generate_service_interface_template_full(self, entity_name: str, full_package: str, base_package: str) -> str:
        """Generate complete service interface."""
        entity_lower = entity_name.lower()
        entity_plural = pluralize(entity_name)
        
        return f"""package {full_package};

import {base_package}.dto.{entity_name}Request;
import {base_package}.dto.{entity_name}Response;
import org.springframework.data.domain.Page;
import java.util.UUID;

/**
 * Service interface for {entity_name} operations
 */
public interface {entity_name}Service {{
    
    /**
     * Get all {entity_plural.lower()} with pagination
     */
    Page<{entity_name}Response> getAll{entity_plural}(int page, int size);
    
    /**
     * Get {entity_lower} by ID
     */
    {entity_name}Response get{entity_name}ById(UUID id);
    
    /**
     * Create new {entity_lower}
     */
    {entity_name}Response create{entity_name}({entity_name}Request request);
    
    /**
     * Update existing {entity_lower}
     */
    {entity_name}Response update{entity_name}(UUID id, {entity_name}Request request);
    
    /**
     * Delete {entity_lower} by ID
     */
    void delete{entity_name}(UUID id);
    
    /**
     * Check if {entity_lower} exists by name
     */
    boolean exists{entity_name}ByName(String name);
}}"""

    def _generate_repository_template_full(self, entity_name: str, full_package: str, base_package: str) -> str:
        """Generate complete JPA repository."""
        entity_lower = entity_name.lower()
        entity_plural = pluralize(entity_name)
        
        return f"""package {full_package};

import {base_package}.model.{entity_name};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * JPA Repository for {entity_name} entity
 */
@Repository
public interface {entity_name}Repository extends JpaRepository<{entity_name}, UUID> {{
    
    /**
     * Find {entity_lower} by name
     */
    Optional<{entity_name}> findByName(String name);
    
    /**
     * Check if {entity_lower} exists by name
     */
    boolean existsByName(String name);
    
    /**
     * Find {entity_plural.lower()} by name containing (case insensitive)
     */
    @Query("SELECT p FROM {entity_name} p WHERE LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<{entity_name}> findByNameContainingIgnoreCase(@Param("name") String name);
    
    /**
     * Find active {entity_plural.lower()}
     */
    @Query("SELECT p FROM {entity_name} p WHERE p.active = true")
    List<{entity_name}> findActive{entity_plural}();
}}"""

    def _generate_request_dto_template_full(self, entity_name: str, full_package: str, spec_data: Dict[str, Any]) -> str:
        """Generate request DTO with validation."""
        
        return f"""package {full_package};

import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request DTO for {entity_name} operations
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class {entity_name}Request {{

    @NotNull(message = "Name is required")
    @Size(min = 1, max = 255, message = "Name must be between 1 and 255 characters")
    private String name;
    
    @Size(max = 1000, message = "Description cannot exceed 1000 characters")
    private String description;
    
    private Boolean active;
}}"""

    def _generate_response_dto_template_full(self, entity_name: str, full_package: str, spec_data: Dict[str, Any]) -> str:
        """Generate response DTO."""
        
        return f"""package {full_package};

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Response DTO for {entity_name} operations
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class {entity_name}Response {{

    private UUID id;
    private String name;
    private String description;
    private Boolean active;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}}"""

    def _generate_mapper_template_full(self, entity_name: str, full_package: str, base_package: str) -> str:
        """Generate mapper for entity/DTO conversions."""
        entity_lower = entity_name.lower()
        
        return f"""package {full_package};

import {base_package}.dto.{entity_name}Request;
import {base_package}.dto.{entity_name}Response;
import {base_package}.model.{entity_name};
import org.springframework.stereotype.Component;

/**
 * Mapper for {entity_name} entity and DTOs
 */
@Component
public class {entity_name}Mapper {{
    
    /**
     * Convert entity to response DTO
     */
    public {entity_name}Response toResponse({entity_name} entity) {{
        if (entity == null) {{
            return null;
        }}
        
        return {entity_name}Response.builder()
            .id(entity.getId())
            .name(entity.getName())
            .description(entity.getDescription())
            .active(entity.getActive())
            .createdAt(entity.getCreatedAt())
            .updatedAt(entity.getUpdatedAt())
            .build();
    }}
    
    /**
     * Convert request DTO to entity
     */
    public {entity_name} toEntity({entity_name}Request request) {{
        if (request == null) {{
            return null;
        }}
        
        return {entity_name}.builder()
            .name(request.getName())
            .description(request.getDescription())
            .active(request.getActive() != null ? request.getActive() : true)
            .build();
    }}
    
    /**
     * Update entity from request DTO
     */
    public void updateEntity({entity_name}Request request, {entity_name} entity) {{
        if (request == null || entity == null) {{
            return;
        }}
        
        if (request.getName() != null) {{
            entity.setName(request.getName());
        }}
        if (request.getDescription() != null) {{
            entity.setDescription(request.getDescription());
        }}
        if (request.getActive() != null) {{
            entity.setActive(request.getActive());
        }}
    }}
}}"""

    def _generate_exception_template_full(self, entity_name: str, full_package: str) -> str:
        """Generate custom exception."""
        
        return f"""package {full_package};

/**
 * Exception thrown when {entity_name} is not found
 */
public class {entity_name}NotFoundException extends RuntimeException {{
    
    public {entity_name}NotFoundException(String message) {{
        super(message);
    }}
    
    public {entity_name}NotFoundException(String message, Throwable cause) {{
        super(message, cause);
    }}
}}"""

    def _generate_client_template_full(self, entity_name: str, full_package: str, 
                                     base_package: str, spec_data: Dict[str, Any]) -> str:
        """Generate HTTP client for external service integration."""
        entity_lower = entity_name.lower()
        entity_plural_lower = pluralize(entity_name).lower()
        
        return f"""package {full_package};

import {base_package}.dto.{entity_name}Request;
import {base_package}.dto.{entity_name}Response;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.RestClientException;

import java.util.List;
import java.util.UUID;

/**
 * HTTP Client for {entity_name} external service integration
 */
@Component
public class {entity_name}Client {{
    
    private static final Logger logger = LoggerFactory.getLogger({entity_name}Client.class);
    
    private final RestTemplate restTemplate;
    private final String baseUrl;
    
    public {entity_name}Client(RestTemplate restTemplate, 
                              @Value("${{external.{entity_lower}.service.url}}") String baseUrl) {{
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }}
    
    /**
     * Fetch {entity_lower} from external service
     */
    public {entity_name}Response fetch{entity_name}(UUID externalId) {{
        try {{
            logger.info("Fetching {entity_lower} from external service: {{}}", externalId);
            
            String url = baseUrl + "/{entity_plural_lower}/" + externalId;
            ResponseEntity<{entity_name}Response> response = restTemplate.getForEntity(
                url, {entity_name}Response.class);
            
            logger.info("Successfully fetched {entity_lower}: {{}}", externalId);
            return response.getBody();
            
        }} catch (RestClientException e) {{
            logger.error("Failed to fetch {entity_lower} {{}}: {{}}", externalId, e.getMessage());
            throw new RuntimeException("External service error", e);
        }}
    }}
    
    /**
     * Sync {entity_lower} with external service
     */
    public void sync{entity_name}({entity_name}Request request, UUID externalId) {{
        try {{
            logger.info("Syncing {entity_lower} with external service: {{}}", externalId);
            
            String url = baseUrl + "/{entity_plural_lower}/" + externalId;
            restTemplate.put(url, request);
            
            logger.info("Successfully synced {entity_lower}: {{}}", externalId);
            
        }} catch (RestClientException e) {{
            logger.error("Failed to sync {entity_lower} {{}}: {{}}", externalId, e.getMessage());
            throw new RuntimeException("External service sync error", e);
        }}
    }}
}}"""

    def _generate_config_template_full(self, entity_name: str, full_package: str, base_package: str) -> str:
        """Generate configuration class."""
        
        return f"""package {full_package};

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/**
 * Configuration for {entity_name} service
 */
@Configuration
public class {entity_name}Config {{
    
    /**
     * RestTemplate bean for HTTP client operations
     */
    @Bean
    public RestTemplate restTemplate() {{
        return new RestTemplate();
    }}
}}"""

    def _generate_pom_xml_template(self, spec_data: Dict[str, Any], base_package: str) -> str:
        """Generate complete pom.xml with all required dependencies."""
        
        metadata = spec_data.get("metadata", {})
        project_name = metadata.get("project", {}).get("name", "Generated API")
        description = metadata.get("project", {}).get("description", "Generated Spring Boot API")
        version = metadata.get("version", "1.0.0")
        group_id = ".".join(base_package.split(".")[:-1]) if "." in base_package else "com.example"
        artifact_id = project_name.lower().replace(" ", "-")
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.0</version>
        <relativePath/>
    </parent>
    
    <groupId>{group_id}</groupId>
    <artifactId>{artifact_id}</artifactId>
    <version>{version}</version>
    <name>{project_name}</name>
    <description>{description}</description>
    
    <properties>
        <java.version>17</java.version>
        <spring-boot.version>3.1.0</spring-boot.version>
        <lombok.version>1.18.28</lombok.version>
        <springdoc.version>2.1.0</springdoc.version>
    </properties>
    
    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        
        <!-- Database -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>${{lombok.version}}</version>
            <scope>provided</scope>
        </dependency>
        
        <!-- OpenAPI Documentation -->
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>${{springdoc.version}}</version>
        </dependency>
        
        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                            <version>${{lombok.version}}</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>"""

    def _generate_main_application_template(self, full_package: str, spec_data: Dict[str, Any], class_name: str = None) -> str:
        """Generate Spring Boot main application class."""
        
        metadata = spec_data.get("metadata", {})
        project_name = metadata.get("project", {}).get("name", "Generated")
        
        # Use provided class_name or generate from project name
        if class_name:
            app_class_name = class_name
        else:
            app_class_name = "".join(project_name.split()) + "Application"
        
        return f"""package {full_package};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Main Spring Boot application class for {project_name}
 */
@SpringBootApplication
public class {app_class_name} {{

    public static void main(String[] args) {{
        SpringApplication.run({app_class_name}.class, args);
    }}
}}"""

    def _generate_application_properties_template(self, spec_data: Dict[str, Any]) -> str:
        """Generate application.yml with database and external service URLs."""
        
        metadata = spec_data.get("metadata", {})
        project_name = metadata.get("project", {}).get("name", "generated-api")
        
        # Extract external services for configuration
        external_services = IntegrationExtractor.extract_external_services(spec_data)
        service_configs = IntegrationExtractor.get_integration_configuration_properties(external_services)
        
        # Build external services configuration
        external_config = ""
        if service_configs:
            external_config = "\n# External Services Configuration\nexternal:\n  services:\n"
            for key, value in service_configs.items():
                clean_key = key.replace('external.services.', '').replace('.', ':\n      ')
                external_config += f"    {clean_key}: {value}\n"
        
        return f"""# Application Configuration
spring:
  application:
    name: {project_name}
  
  # Database Configuration
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password: ""
    
  h2:
    console:
      enabled: true
      path: /h2-console
      
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        
  # Jackson Configuration
  jackson:
    default-property-inclusion: non_null
    serialization:
      write-dates-as-timestamps: false

# Server Configuration  
server:
  port: 8080
  servlet:
    context-path: /api

# Management Configuration
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: always

# Logging Configuration
logging:
  level:
    root: INFO
    org.springframework.web: DEBUG
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE
{external_config}

# OpenAPI Documentation
springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
    operationsSorter: method"""

    def _generate_resource_not_found_exception_template(self, full_package: str) -> str:
        """Generate ResourceNotFoundException class."""
        
        return f"""package {full_package};

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

/**
 * Exception thrown when a requested resource is not found
 */
@ResponseStatus(HttpStatus.NOT_FOUND)
public class ResourceNotFoundException extends RuntimeException {{
    
    public ResourceNotFoundException(String message) {{
        super(message);
    }}
    
    public ResourceNotFoundException(String message, Throwable cause) {{
        super(message, cause);
    }}
    
    public ResourceNotFoundException(String resource, String field, Object value) {{
        super(String.format("%s not found with %s: '%s'", resource, field, value));
    }}
}}"""

    def _generate_bad_request_exception_template(self, full_package: str) -> str:
        """Generate BadRequestException class."""
        
        return f"""package {full_package};

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

/**
 * Exception thrown when a request is malformed or invalid
 */
@ResponseStatus(HttpStatus.BAD_REQUEST)
public class BadRequestException extends RuntimeException {{
    
    public BadRequestException(String message) {{
        super(message);
    }}
    
    public BadRequestException(String message, Throwable cause) {{
        super(message, cause);
    }}
}}"""

    def _generate_global_exception_handler_template(self, full_package: str) -> str:
        """Generate GlobalExceptionHandler class."""
        
        return f"""package {full_package};

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Global exception handler for the application
 */
@ControllerAdvice
public class GlobalExceptionHandler {{
    
    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFoundException(
            ResourceNotFoundException ex, WebRequest request) {{
        logger.error("Resource not found: {{}}", ex.getMessage());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.NOT_FOUND.value())
            .error(HttpStatus.NOT_FOUND.getReasonPhrase())
            .message(ex.getMessage())
            .path(request.getDescription(false).replace("uri=", ""))
            .build();
            
        return new ResponseEntity<>(errorResponse, HttpStatus.NOT_FOUND);
    }}
    
    @ExceptionHandler(BadRequestException.class)
    public ResponseEntity<ErrorResponse> handleBadRequestException(
            BadRequestException ex, WebRequest request) {{
        logger.error("Bad request: {{}}", ex.getMessage());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.BAD_REQUEST.value())
            .error(HttpStatus.BAD_REQUEST.getReasonPhrase())
            .message(ex.getMessage())
            .path(request.getDescription(false).replace("uri=", ""))
            .build();
            
        return new ResponseEntity<>(errorResponse, HttpStatus.BAD_REQUEST);
    }}
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ValidationErrorResponse> handleValidationExceptions(
            MethodArgumentNotValidException ex, WebRequest request) {{
        logger.error("Validation error: {{}}", ex.getMessage());
        
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach((error) -> {{
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        }});
        
        ValidationErrorResponse errorResponse = ValidationErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.BAD_REQUEST.value())
            .error("Validation Failed")
            .message("Invalid input parameters")
            .path(request.getDescription(false).replace("uri=", ""))
            .validationErrors(errors)
            .build();
            
        return new ResponseEntity<>(errorResponse, HttpStatus.BAD_REQUEST);
    }}
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGlobalException(
            Exception ex, WebRequest request) {{
        logger.error("Internal server error: {{}}", ex.getMessage(), ex);
        
        ErrorResponse errorResponse = ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
            .error(HttpStatus.INTERNAL_SERVER_ERROR.getReasonPhrase())
            .message("An unexpected error occurred")
            .path(request.getDescription(false).replace("uri=", ""))
            .build();
            
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }}
    
    /**
     * Standard error response structure
     */
    public static class ErrorResponse {{
        private LocalDateTime timestamp;
        private int status;
        private String error;
        private String message;
        private String path;
        
        // Builder pattern using Lombok would be ideal
        public static ErrorResponseBuilder builder() {{
            return new ErrorResponseBuilder();
        }}
        
        // Getters and setters
        public LocalDateTime getTimestamp() {{ return timestamp; }}
        public void setTimestamp(LocalDateTime timestamp) {{ this.timestamp = timestamp; }}
        
        public int getStatus() {{ return status; }}
        public void setStatus(int status) {{ this.status = status; }}
        
        public String getError() {{ return error; }}
        public void setError(String error) {{ this.error = error; }}
        
        public String getMessage() {{ return message; }}
        public void setMessage(String message) {{ this.message = message; }}
        
        public String getPath() {{ return path; }}
        public void setPath(String path) {{ this.path = path; }}
        
        public static class ErrorResponseBuilder {{
            private ErrorResponse errorResponse = new ErrorResponse();
            
            public ErrorResponseBuilder timestamp(LocalDateTime timestamp) {{
                errorResponse.setTimestamp(timestamp);
                return this;
            }}
            
            public ErrorResponseBuilder status(int status) {{
                errorResponse.setStatus(status);
                return this;
            }}
            
            public ErrorResponseBuilder error(String error) {{
                errorResponse.setError(error);
                return this;
            }}
            
            public ErrorResponseBuilder message(String message) {{
                errorResponse.setMessage(message);
                return this;
            }}
            
            public ErrorResponseBuilder path(String path) {{
                errorResponse.setPath(path);
                return this;
            }}
            
            public ErrorResponse build() {{
                return errorResponse;
            }}
        }}
    }}
    
    /**
     * Validation error response structure
     */
    public static class ValidationErrorResponse extends ErrorResponse {{
        private Map<String, String> validationErrors;
        
        public static ValidationErrorResponseBuilder builder() {{
            return new ValidationErrorResponseBuilder();
        }}
        
        public Map<String, String> getValidationErrors() {{ return validationErrors; }}
        public void setValidationErrors(Map<String, String> validationErrors) {{ this.validationErrors = validationErrors; }}
        
        public static class ValidationErrorResponseBuilder extends ErrorResponseBuilder {{
            private ValidationErrorResponse response = new ValidationErrorResponse();
            
            public ValidationErrorResponseBuilder validationErrors(Map<String, String> errors) {{
                response.setValidationErrors(errors);
                return this;
            }}
            
            @Override
            public ValidationErrorResponseBuilder timestamp(LocalDateTime timestamp) {{
                response.setTimestamp(timestamp);
                return this;
            }}
            
            @Override
            public ValidationErrorResponseBuilder status(int status) {{
                response.setStatus(status);
                return this;
            }}
            
            @Override
            public ValidationErrorResponseBuilder error(String error) {{
                response.setError(error);
                return this;
            }}
            
            @Override
            public ValidationErrorResponseBuilder message(String message) {{
                response.setMessage(message);
                return this;
            }}
            
            @Override
            public ValidationErrorResponseBuilder path(String path) {{
                response.setPath(path);
                return this;
            }}
            
            @Override
            public ValidationErrorResponse build() {{
                return response;
            }}
        }}
    }}
}}"""

    def _generate_external_service_client_templates(self, spec_data: Dict[str, Any], base_package: str) -> Dict[str, str]:
        """Generate external service client classes."""
        
        external_services = IntegrationExtractor.extract_external_services(spec_data)
        if not external_services:
            return {}
        
        client_templates = {}
        
        for service in external_services:
            class_name = service.client_class_name
            full_package = f"{base_package}.client"
            
            # Generate method signatures for the service
            method_signatures = IntegrationExtractor.generate_service_method_signatures(service)
            methods_code = "\n\n".join([
                f"""    public {sig['return_type']} {sig['name']}({sig['parameters']}) {{
        // {sig['description']}
        // TODO: Implement {sig['http_method']} {sig['path']}
        return null;
    }}""" for sig in method_signatures
            ])
            
            # Build authentication configuration
            auth_config = ""
            service_name_lower = service.name.lower()
            
            auth_type = service.authentication.get('type', '').lower()
            if auth_type == "bearer_token" or auth_type == "bearer":
                auth_config = f"""
    @Value("${{external.services.{service_name_lower}.token}}")
    private String authToken;
    
    private HttpHeaders createAuthHeaders() {{
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(authToken);
        return headers;
    }}"""
            elif auth_type == "api_key":
                auth_config = f"""
    @Value("${{external.services.{service_name_lower}.api-key}}")
    private String apiKey;
    
    @Value("${{external.services.{service_name_lower}.api-key-header:X-API-Key}}")
    private String apiKeyHeader;
    
    private HttpHeaders createAuthHeaders() {{
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set(apiKeyHeader, apiKey);
        return headers;
    }}"""
            else:
                auth_config = """
    private HttpHeaders createHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        return headers;
    }"""
            
            # Generate retry configuration if enabled
            retry_config = ""
            resilience_config = service.get_resilience_config()
            if resilience_config.get("retry_attempts", 0) > 0:
                retry_config = """
    @Retryable(
        value = {RestClientException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )"""
            
            # Generate circuit breaker configuration if enabled
            circuit_breaker_config = ""
            if resilience_config.get("circuit_breaker", False):
                cb_name = service.name.lower()
                circuit_breaker_config = f"""
    @CircuitBreaker(name = "{cb_name}", fallbackMethod = "fallback")"""
            
            client_code = f"""package {full_package};

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;

import java.util.List;
import java.util.Optional;

/**
 * Client service for {service.name} external API integration
 * Base URL: {service.base_url}
 * Authentication: {auth_type}
 */
@Service
public class {class_name} {{
    
    private static final Logger logger = LoggerFactory.getLogger({class_name}.class);
    
    private final RestTemplate restTemplate;
    
    @Value("${{external.services.{service_name_lower}.base-url:{service.base_url}}}")
    private String baseUrl;{auth_config}
    
    public {class_name}(RestTemplate restTemplate) {{
        this.restTemplate = restTemplate;
    }}
    
{methods_code}
    
    /**
     * Generic error handling method
     */
    private void handleRestClientException(RestClientException ex, String operation) {{
        logger.error("Error during {{}} operation: {{}}", operation, ex.getMessage());
        throw new RuntimeException("External service error: " + ex.getMessage(), ex);
    }}
    
    /**
     * Generic fallback method for circuit breaker
     */
    public Object fallback(Exception ex) {{
        logger.warn("Circuit breaker fallback triggered: {{}}", ex.getMessage());
        return null;
    }}
}}"""
            
            client_templates[f"{class_name}.java"] = client_code
        
        return client_templates

    def _write_generated_files(self, generated_files: Dict[str, str], output_path: str) -> int:
        """Write generated files to disk."""
        files_written = 0
        
        try:
            for file_path, content in generated_files.items():
                # Create full output path
                full_output_path = Path(output_path) / file_path
                
                # Create directories if they don't exist
                full_output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file to disk
                with open(full_output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_written += 1
                print(f"✓ Written: {file_path}")
                
        except Exception as e:
            print(f"❌ Error writing file {file_path}: {str(e)}")
            
        return files_written

    def generate_code(self, entity_name: str, spec_data: Dict[str, Any], instruction_data: Dict[str, Any], 
                     output_path: str = "output") -> Dict[str, str]:
        """
        Generate complete Spring Boot application code including project structure.
        Generation order: project files -> exceptions -> entities -> business logic -> external clients
        """
        generated_files = {}
        
        try:
            # Extract configuration
            base_package = instruction_data.get("base_package", "com.example.api")
            api_version = spec_data.get("metadata", {}).get("version", "v1")
            
            print(f"Generating code for entity: {entity_name}")
            print(f"Base package: {base_package}")
            print(f"API version: {api_version}")
            
            # Phase 1: Generate project structure files first
            print("Phase 1: Generating project structure...")
            
            # Generate pom.xml
            pom_content = self._generate_pom_xml_template(spec_data, base_package)
            generated_files["pom.xml"] = pom_content
            
            # Generate main application class
            app_package = base_package
            project_name = spec_data.get("metadata", {}).get("project", {}).get("name", "Generated")
            app_class_name = "".join(project_name.split()) + "Application"
            app_content = self._generate_main_application_template(app_package, spec_data, app_class_name)
            app_filename = f"src/main/java/{app_package.replace('.', '/')}/{app_class_name}.java"
            generated_files[app_filename] = app_content
            
            # Generate application.yml
            config_content = self._generate_application_properties_template(spec_data)
            generated_files["src/main/resources/application.yml"] = config_content
            
            # Phase 2: Generate exception classes
            print("Phase 2: Generating exception classes...")
            
            exception_package = f"{base_package}.exception"
            
            # ResourceNotFoundException
            resource_not_found = self._generate_resource_not_found_exception_template(exception_package)
            exception_path = f"src/main/java/{exception_package.replace('.', '/')}/ResourceNotFoundException.java"
            generated_files[exception_path] = resource_not_found
            
            # BadRequestException  
            bad_request = self._generate_bad_request_exception_template(exception_package)
            exception_path = f"src/main/java/{exception_package.replace('.', '/')}/BadRequestException.java"
            generated_files[exception_path] = bad_request
            
            # GlobalExceptionHandler
            global_handler = self._generate_global_exception_handler_template(exception_package)
            handler_path = f"src/main/java/{exception_package.replace('.', '/')}/GlobalExceptionHandler.java"
            generated_files[handler_path] = global_handler
            
            # Phase 3: Generate entity and business logic
            print("Phase 3: Generating entity and business logic...")
            
            # Generate all standard templates for the entity
            for template_name, template_info in self.template_definitions.items():
                if template_name in ['pom_xml', 'main_application', 'application_properties', 
                                   'resource_not_found_exception', 'bad_request_exception', 
                                   'global_exception_handler', 'external_service_client']:
                    continue  # Skip already generated templates
                
                print(f"Generating {template_name}...")
                
                try:
                    # Generate template content
                    if hasattr(self, template_info['method']):
                        method = getattr(self, template_info['method'])
                        
                        # Determine package based on template type
                        full_package = f"{base_package}.{template_info['package']}"
                        
                        # Call the template generation method
                        if template_name == 'config':
                            content = method(entity_name, full_package, base_package)
                        else:
                            content = method(entity_name, full_package, spec_data, instruction_data)
                        
                        # Generate filename with proper path
                        class_name = f"{entity_name}{template_info['suffix']}"
                        file_path = f"src/main/java/{full_package.replace('.', '/')}/{class_name}.java"
                        
                        generated_files[file_path] = content
                        print(f"✓ Generated {file_path}")
                        
                    else:
                        print(f"⚠ Method {template_info['method']} not found for {template_name}")
                        
                except Exception as e:
                    print(f"✗ Error generating {template_name}: {str(e)}")
                    continue
            
            # Phase 4: Generate external service clients
            print("Phase 4: Generating external service clients...")
            
            external_clients = self._generate_external_service_client_templates(spec_data, base_package)
            for client_filename, client_content in external_clients.items():
                client_path = f"src/main/java/{base_package.replace('.', '/')}/client/{client_filename}"
                generated_files[client_path] = client_content
                print(f"✓ Generated external client: {client_path}")
            
            print(f"\n✅ Successfully generated {len(generated_files)} files")
            
            # Write files to output directory
            files_written = self._write_generated_files(generated_files, output_path)
            print(f"📁 Written {files_written} files to {output_path}")
            
            return generated_files
            
        except Exception as e:
            print(f"❌ Error in code generation: {str(e)}")
            import traceback
            traceback.print_exc()
            return generated_files


class SimpleCodeGenerationAgent(BaseAgent):
    """Agent responsible for AI-enhanced code generation."""
    
    def __init__(self):
        super().__init__(
            agent_id="codegen_agent",
            name="Code Generation Agent",
            capabilities=["ai_enhanced_generation"]
        )
    
    async def _execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute code generation goals."""
        if goal.id == "ai_enhanced_generation":
            return await self._ai_enhanced_generation(goal.context)
        else:
            raise ValueError(f"Unknown goal: {goal.id}")
    
    async def _ai_enhanced_generation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance templates with AI-generated code."""
        processed_templates = context.get("processed_templates", {})
        spec_data = context.get("spec_data", {})
        
        if not processed_templates:
            return {
                "success": False,
                "error": "No processed templates available for enhancement"
            }
        
        enhanced_templates = {}
        
        # For now, provide enhanced versions based on spec data
        for entity_name, templates in processed_templates.items():
            enhanced_entity = {}
            
            for template_key, template_data in templates.items():
                enhanced_content = await self._enhance_template_content(
                    template_data, entity_name, spec_data
                )
                
                enhanced_entity[template_key] = {
                    **template_data,
                    "enhanced_content": enhanced_content
                }
            
            enhanced_templates[entity_name] = enhanced_entity
        
        return {
            "success": True,
            "enhanced_templates": enhanced_templates,
            "entities_enhanced": len(enhanced_templates)
        }
    
    async def _enhance_template_content(self, template_data: Dict[str, Any], 
                                      entity_name: str, spec_data: Dict[str, Any]) -> str:
        """Enhance template content based on spec data."""
        content = template_data.get("content", "")
        template_name = template_data.get("template_name", "")
        
        # Get entity-specific data from spec
        entity_models = spec_data.get("models", {})
        entity_endpoints = spec_data.get("endpoints", [])
        
        # Simple enhancement based on spec data
        if entity_name in entity_models:
            entity_model = entity_models[entity_name]
            # Add fields and validation based on model properties
            if "properties" in entity_model:
                content = self._add_fields_to_template(content, entity_model["properties"])
        
        # Add endpoint-specific enhancements for controllers
        if "Controller" in template_name:
            content = self._add_endpoints_to_controller(content, entity_endpoints, entity_name)
        
        return content
    
    def _add_fields_to_template(self, content: str, properties: Dict[str, Any]) -> str:
        """Add fields to template based on model properties."""
        # This is a simplified implementation
        # In a full implementation, this would parse and enhance the template properly
        return content
    
    def _add_endpoints_to_controller(self, content: str, endpoints: List[Dict[str, Any]], entity_name: str) -> str:
        """Add endpoints to controller based on spec endpoints."""
        # This is a simplified implementation  
        # In a full implementation, this would add proper endpoint methods
        return content
    
    def can_handle_goal(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        return goal.id in self.capabilities


class SimpleValidationAgent(BaseAgent):
    """Agent responsible for code validation and quality assurance."""
    
    def __init__(self):
        super().__init__(
            agent_id="validation_agent",
            name="Validation Agent",
            capabilities=["comprehensive_validation"]
        )
    
    async def _execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute validation goals."""
        if goal.id == "comprehensive_validation":
            return await self._comprehensive_validation(goal.context)
        else:
            raise ValueError(f"Unknown goal: {goal.id}")
    
    async def _comprehensive_validation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive validation of generated code."""
        enhanced_templates = context.get("enhanced_templates", {})
        
        if not enhanced_templates:
            return {
                "success": False,
                "error": "No enhanced templates available for validation"
            }
        
        validation_results = {}
        total_files = 0
        valid_files = 0
        quality_scores = []
        
        for entity_name, templates in enhanced_templates.items():
            entity_validation = {}
            
            for template_key, template_data in templates.items():
                content = template_data.get("enhanced_content", template_data.get("content", ""))
                
                # Basic validation checks
                validation_result = self._validate_code_content(content, template_key)
                entity_validation[template_key] = validation_result
                
                total_files += 1
                if validation_result["valid"]:
                    valid_files += 1
                
                quality_scores.append(validation_result["quality_score"])
            
            validation_results[entity_name] = entity_validation
        
        validation_rate = valid_files / total_files if total_files > 0 else 0
        average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "success": True,
            "code_validation": {
                "total_files": total_files,
                "valid_files": valid_files,
                "validation_rate": validation_rate
            },
            "quality_assessment": {
                "average_quality_score": average_quality,
                "quality_scores": quality_scores
            },
            "validation_results": validation_results
        }
    
    def _validate_code_content(self, content: str, template_key: str) -> Dict[str, Any]:
        """Validate individual code content."""
        issues = []
        quality_score = 100.0
        
        # Basic syntax checks
        if not content.strip():
            issues.append("Empty content")
            quality_score -= 50
        
        # Check for package declaration
        if "package " not in content:
            issues.append("Missing package declaration")
            quality_score -= 10
        
        # Check for class declaration
        if "class " not in content and "interface " not in content:
            issues.append("Missing class/interface declaration")
            quality_score -= 20
        
        # Check for proper imports
        if "import " not in content and "Controller" in template_key:
            issues.append("Missing imports in controller")
            quality_score -= 15
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "quality_score": max(0, quality_score)
        }
    
    def can_handle_goal(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        return goal.id in self.capabilities
