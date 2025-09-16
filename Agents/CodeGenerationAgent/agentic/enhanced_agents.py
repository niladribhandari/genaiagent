"""Enhanced intelligent agents with business logic awareness and AI integration."""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile

import sys
import os

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.append(src_dir)

from .core import BaseAgent, AgentGoal
from application.services.enhanced_code_generation_service import EnhancedCodeGenerationService
from application.services.context_enrichment_service import ContextEnrichmentService
from infrastructure.ai_provider import EnhancedOpenAIProvider
from infrastructure.template_engine import TemplateEngine
from infrastructure.import_manager import ImportManager
from domain.models.generation_context import GenerationContext


logger = logging.getLogger(__name__)


class EnhancedConfigurationAgent(BaseAgent):
    """Enhanced configuration agent with business intelligence."""
    
    def __init__(self):
        super().__init__(
            agent_id="enhanced_config_agent",
            name="Enhanced Configuration Agent",
            capabilities=["load_specification", "load_instructions", "validate_compatibility", "analyze_business_requirements"]
        )
    
    async def _execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute configuration-related goals with enhancement."""
        if goal.id == "load_specification":
            return await self._load_specification(goal.context)
        elif goal.id == "load_instructions":
            return await self._load_instructions(goal.context)
        elif goal.id == "validate_compatibility":
            return await self._validate_compatibility(goal.context)
        elif goal.id == "analyze_business_requirements":
            return await self._analyze_business_requirements(goal.context)
        else:
            raise ValueError(f"Unknown goal: {goal.id}")
    
    async def _load_specification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load and analyze API specification file."""
        spec_path = context.get("spec_path")
        if not spec_path or not os.path.exists(spec_path):
            raise FileNotFoundError(f"Specification file not found: {spec_path}")
        
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec_data = yaml.safe_load(f)
            
            # Enhanced entity extraction
            entities = self._extract_entities_from_spec(spec_data)
            
            # Extract additional metadata for business analysis
            business_metadata = self._extract_business_metadata(spec_data)
            
            return {
                "success": True,
                "spec_data": spec_data,
                "entities": entities,
                "business_metadata": business_metadata,
                "file_path": spec_path,
                "complexity_indicators": self._assess_spec_complexity(spec_data)
            }
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in specification file: {e}")
    
    async def _analyze_business_requirements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business requirements from specification."""
        spec_data = context.get("spec_data", {})
        instruction_data = context.get("instruction_data", {})
        
        try:
            # Initialize AI provider for analysis
            ai_provider = EnhancedOpenAIProvider()
            
            # Analyze business requirements using AI
            business_analysis = ai_provider.analyze_business_requirements(spec_data, instruction_data)
            
            return {
                "success": True,
                "business_analysis": business_analysis,
                "requires_ai_generation": business_analysis.get('complexity_score', 1) >= 5
            }
            
        except Exception as e:
            logger.warning(f"Business analysis failed: {e}")
            return {
                "success": True,
                "business_analysis": {},
                "requires_ai_generation": False
            }
    
    def _extract_entities_from_spec(self, spec_data: Dict[str, Any]) -> List[str]:
        """Extract entities with enhanced logic."""
        entities = []
        
        # Check multiple sources for entities
        if 'models' in spec_data:
            entities.extend(spec_data['models'].keys())
        
        if 'entity' in spec_data:
            entities.append(spec_data['entity']['name'])
        
        # Extract from OpenAPI components/schemas
        if 'components' in spec_data and 'schemas' in spec_data['components']:
            entities.extend(spec_data['components']['schemas'].keys())
        
        # Extract from paths
        if 'paths' in spec_data:
            path_entities = self._extract_entities_from_paths(spec_data['paths'])
            entities.extend(path_entities)
        
        # Remove duplicates and filter
        entities = list(set([entity for entity in entities if entity and len(entity) > 1]))
        
        return entities if entities else ["Default"]
    
    def _extract_entities_from_paths(self, paths: Dict[str, Any]) -> List[str]:
        """Extract entity names from API paths."""
        entities = []
        
        for path in paths.keys():
            # Extract from path patterns like /api/v1/users, /policies, etc.
            path_parts = path.strip('/').split('/')
            for part in path_parts:
                # Skip common API prefixes
                if part not in ['api', 'v1', 'v2', 'rest']:
                    # Convert plural to singular and capitalize
                    if part.endswith('s') and len(part) > 3:
                        entity = part[:-1].capitalize()
                        if entity not in entities:
                            entities.append(entity)
                    elif len(part) > 2:
                        entity = part.capitalize()
                        if entity not in entities:
                            entities.append(entity)
        
        return entities
    
    def _extract_business_metadata(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business-relevant metadata from specification."""
        metadata = {}
        
        # API info
        if 'info' in spec_data:
            info = spec_data['info']
            metadata['api_title'] = info.get('title', '')
            metadata['api_description'] = info.get('description', '')
            metadata['api_version'] = info.get('version', '')
        
        # Business domain indicators
        metadata['has_authentication'] = self._has_security_requirements(spec_data)
        metadata['has_validation'] = self._has_validation_requirements(spec_data)
        metadata['has_business_rules'] = self._has_business_rules(spec_data)
        
        return metadata
    
    def _assess_spec_complexity(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the complexity of the specification."""
        complexity = {
            'endpoint_count': 0,
            'schema_count': 0,
            'business_rule_indicators': 0,
            'integration_indicators': 0
        }
        
        # Count endpoints
        if 'paths' in spec_data:
            for path_data in spec_data['paths'].values():
                complexity['endpoint_count'] += len(path_data)
        
        # Count schemas
        if 'components' in spec_data and 'schemas' in spec_data['components']:
            complexity['schema_count'] = len(spec_data['components']['schemas'])
        
        # Look for business rule indicators
        spec_text = json.dumps(spec_data).lower()
        business_keywords = ['validate', 'business', 'rule', 'constraint', 'policy', 'approve', 'workflow']
        complexity['business_rule_indicators'] = sum(1 for keyword in business_keywords if keyword in spec_text)
        
        # Look for integration indicators
        integration_keywords = ['external', 'integrate', 'api', 'service', 'third-party']
        complexity['integration_indicators'] = sum(1 for keyword in integration_keywords if keyword in spec_text)
        
        return complexity
    
    def _has_security_requirements(self, spec_data: Dict[str, Any]) -> bool:
        """Check if specification has security requirements."""
        return ('security' in spec_data or 
                'securityDefinitions' in spec_data or
                'securitySchemes' in spec_data.get('components', {}))
    
    def _has_validation_requirements(self, spec_data: Dict[str, Any]) -> bool:
        """Check if specification has validation requirements."""
        # Check for validation keywords in schema properties
        if 'components' in spec_data and 'schemas' in spec_data['components']:
            for schema in spec_data['components']['schemas'].values():
                if isinstance(schema, dict):
                    if 'required' in schema or 'properties' in schema:
                        return True
                    for prop in schema.get('properties', {}).values():
                        if isinstance(prop, dict) and any(key in prop for key in ['pattern', 'minLength', 'maxLength', 'minimum', 'maximum']):
                            return True
        return False
    
    def _has_business_rules(self, spec_data: Dict[str, Any]) -> bool:
        """Check if specification contains business rule indicators."""
        spec_text = json.dumps(spec_data).lower()
        business_rule_keywords = ['business', 'rule', 'policy', 'workflow', 'approve', 'validate', 'constraint']
        return any(keyword in spec_text for keyword in business_rule_keywords)


class IntelligentCodeGenerationAgent(BaseAgent):
    """Intelligent code generation agent with business logic awareness."""
    
    def __init__(self):
        super().__init__(
            agent_id="intelligent_codegen_agent",
            name="Intelligent Code Generation Agent",
            capabilities=["intelligent_generation", "business_aware_generation", "pattern_based_generation"]
        )
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all required services."""
        try:
            # Initialize AI provider
            self.ai_provider = EnhancedOpenAIProvider()
            
            # Initialize other infrastructure services
            self.template_engine = TemplateEngine()
            self.import_manager = ImportManager()
            
            # Initialize application services
            self.code_generation_service = EnhancedCodeGenerationService(
                template_engine=self.template_engine,
                ai_provider=self.ai_provider,
                import_manager=self.import_manager
            )
            
            self.context_enrichment_service = ContextEnrichmentService(
                ai_provider=self.ai_provider
            )
            
            logger.info("Intelligent code generation services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            # Initialize fallback basic services
            self._initialize_fallback_services()
    
    def _initialize_fallback_services(self):
        """Initialize basic fallback services when enhanced services fail."""
        try:
            self.ai_provider = EnhancedOpenAIProvider(use_langchain=False)
            self.template_engine = TemplateEngine()
            self.import_manager = ImportManager()
            
            # Use basic services as fallback
            from ..src.application.services.code_generation_service import CodeGenerationService
            self.code_generation_service = CodeGenerationService(
                template_engine=self.template_engine,
                ai_provider=self.ai_provider,
                import_manager=self.import_manager
            )
            
            self.context_enrichment_service = None
            
            logger.info("Fallback code generation services initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize even fallback services: {e}")
            raise RuntimeError("Could not initialize code generation services")
    
    async def _execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute intelligent code generation goals."""
        if goal.id == "intelligent_generation":
            return await self._intelligent_generation(goal.context)
        elif goal.id == "business_aware_generation":
            return await self._business_aware_generation(goal.context)
        elif goal.id == "pattern_based_generation":
            return await self._pattern_based_generation(goal.context)
        else:
            raise ValueError(f"Unknown goal: {goal.id}")
    
    async def _intelligent_generation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using full business intelligence."""
        try:
            logger.info("Starting intelligent code generation")
            
            # Extract context data
            spec_data = context.get("spec_data", {})
            instruction_data = context.get("instruction_data", {})
            entities = context.get("entities", [])
            output_path = context.get("output_path", "")
            
            generated_files = {}
            generation_stats = {
                'total_files': 0,
                'ai_enhanced_files': 0,
                'business_rules_applied': 0,
                'integration_patterns_applied': 0
            }
            
            # Generate code for each entity
            for entity_name in entities:
                entity_files = await self._generate_entity_files(
                    entity_name, spec_data, instruction_data, output_path
                )
                generated_files[entity_name] = entity_files
                
                # Update statistics
                for file_info in entity_files.values():
                    generation_stats['total_files'] += 1
                    if file_info.get('ai_enhanced', False):
                        generation_stats['ai_enhanced_files'] += 1
                    generation_stats['business_rules_applied'] += file_info.get('business_rules_count', 0)
                    generation_stats['integration_patterns_applied'] += file_info.get('integration_patterns_count', 0)
            
            return {
                "success": True,
                "generated_files": generated_files,
                "generation_stats": generation_stats,
                "approach": "intelligent_ai_enhanced"
            }
            
        except Exception as e:
            logger.error(f"Intelligent generation failed: {e}")
            # Fallback to basic generation
            return await self._fallback_generation(context)
    
    async def _generate_entity_files(self, entity_name: str, spec_data: Dict[str, Any], 
                                   instruction_data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Generate all files for a single entity using intelligent services."""
        
        # File type definitions
        file_types = [
            ("controller", "Controller.java", "src/main/java/{package_path}/controller/{entity}Controller.java"),
            ("service", "Service.java", "src/main/java/{package_path}/service/{entity}Service.java"),
            ("service_impl", "ServiceImpl.java", "src/main/java/{package_path}/service/impl/{entity}ServiceImpl.java"),
            ("repository", "Repository.java", "src/main/java/{package_path}/repository/{entity}Repository.java"),
            ("model", "Entity.java", "src/main/java/{package_path}/model/{entity}.java"),
            ("dto_request", "RequestDto.java", "src/main/java/{package_path}/dto/{entity}Request.java"),
            ("dto_response", "ResponseDto.java", "src/main/java/{package_path}/dto/{entity}Response.java")
        ]
        
        entity_files = {}
        
        for file_key, template_name, output_pattern in file_types:
            try:
                # Create generation context
                generation_context = self._create_generation_context(
                    entity_name, file_key, spec_data, instruction_data, output_path, output_pattern
                )
                
                # Enrich context with business intelligence
                if self.context_enrichment_service:
                    enriched_context = self.context_enrichment_service.enrich_context(generation_context)
                else:
                    enriched_context = generation_context
                
                # Generate code using enhanced service
                generated_code = self.code_generation_service.generate(enriched_context)
                
                # Determine output file path
                base_package = self._get_base_package(spec_data, instruction_data)
                package_path = base_package.replace(".", "/")
                output_file_path = output_pattern.format(
                    package_path=package_path,
                    entity=entity_name
                )
                
                # Write file to disk
                full_output_path = Path(output_path) / output_file_path
                full_output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_output_path, 'w', encoding='utf-8') as f:
                    f.write(generated_code.content)
                
                # Collect file information
                entity_files[file_key] = {
                    'file_path': str(full_output_path),
                    'relative_path': output_file_path,
                    'template_name': template_name,
                    'ai_enhanced': generated_code.metadata.get('generation_strategy') in ['ai_enhanced', 'ai_basic'],
                    'complexity_score': generated_code.metadata.get('complexity_score', 0),
                    'business_rules_count': generated_code.metadata.get('business_rules_count', 0),
                    'integration_patterns_count': generated_code.metadata.get('integration_patterns_count', 0),
                    'generation_strategy': generated_code.metadata.get('generation_strategy', 'unknown'),
                    'code_quality_indicators': generated_code.metadata.get('code_quality_indicators', {}),
                    'lines_of_code': len(generated_code.content.split('\n'))
                }
                
                logger.info(f"Generated {file_key} for {entity_name} using {generated_code.metadata.get('generation_strategy', 'unknown')}")
                
            except Exception as e:
                logger.error(f"Failed to generate {file_key} for {entity_name}: {e}")
                # Add error information
                entity_files[file_key] = {
                    'error': str(e),
                    'generation_failed': True
                }
        
        return entity_files
    
    def _create_generation_context(self, entity_name: str, file_type: str, 
                                 spec_data: Dict[str, Any], instruction_data: Dict[str, Any],
                                 output_path: str, output_pattern: str) -> GenerationContext:
        """Create generation context for intelligent code generation."""
        
        # Get configuration
        base_package = self._get_base_package(spec_data, instruction_data)
        language = instruction_data.get('language', 'java')
        framework = instruction_data.get('framework', 'springboot')
        
        # Create package name based on file type
        package_suffixes = {
            'controller': '.controller',
            'service': '.service', 
            'service_impl': '.service.impl',
            'repository': '.repository',
            'model': '.model',
            'dto_request': '.dto',
            'dto_response': '.dto'
        }
        
        package_name = base_package + package_suffixes.get(file_type, '')
        
        # Determine output path
        output_file_path = output_pattern.format(
            package_path=base_package.replace(".", "/"),
            entity=entity_name
        )
        full_output_path = str(Path(output_path) / output_file_path)
        
        # Create context
        return GenerationContext(
            file_type=file_type,
            entity_name=entity_name,
            package_name=package_name,
            language=language,
            framework=framework,
            template_content=self._get_basic_template_content(file_type, entity_name, package_name),
            spec_data=spec_data,
            instruction_data=instruction_data,
            output_path=full_output_path,
            
            # Initial values - will be enriched
            endpoints=None,
            business_rules=None,
            integration_patterns=[],
            downstream_systems={},
            service_pattern=None,
            
            # Metadata
            metadata={
                'creation_timestamp': self._get_timestamp(),
                'file_pattern': output_pattern
            },
            generation_options={
                'use_ai_enhancement': True,
                'include_business_logic': True,
                'apply_patterns': True
            },
            complexity_score=1,  # Will be calculated during enrichment
            requires_ai_generation=False  # Will be determined during enrichment
        )
    
    def _get_basic_template_content(self, file_type: str, entity_name: str, package_name: str) -> str:
        """Get basic template content as starting point."""
        templates = {
            'controller': f'''package {package_name};

import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/v1/{entity_name.lower()}")
@RequiredArgsConstructor
public class {entity_name}Controller {{
    
    // TODO: Implement controller logic
    
}}''',
            'service': f'''package {package_name};

public interface {entity_name}Service {{
    
    // TODO: Define service interface
    
}}''',
            'service_impl': f'''package {package_name};

import org.springframework.stereotype.Service;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class {entity_name}ServiceImpl implements {entity_name}Service {{
    
    // TODO: Implement service logic
    
}}''',
            'model': f'''package {package_name};

import lombok.Data;

@Data
public class {entity_name} {{
    
    // TODO: Add entity fields
    
}}'''
        }
        
        return templates.get(file_type, f'''package {package_name};

public class {entity_name} {{
    
    // TODO: Implement class
    
}}''')
    
    def _get_base_package(self, spec_data: Dict[str, Any], instruction_data: Dict[str, Any]) -> str:
        """Get base package name from configuration."""
        return (spec_data.get("base_package") or 
                spec_data.get("metadata", {}).get("base_package") or
                instruction_data.get("base_package", "com.example.demo"))
    
    async def _fallback_generation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to basic generation when intelligent generation fails."""
        logger.warning("Falling back to basic code generation")
        
        # Use the original simple agent logic as fallback
        from .simple_agents import SimpleTemplateAgent
        simple_agent = SimpleTemplateAgent()
        
        return await simple_agent._execute_goal(
            type('Goal', (), {'id': 'process_all_templates', 'context': context})()
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def can_handle_goal(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        return goal.id in self.capabilities
