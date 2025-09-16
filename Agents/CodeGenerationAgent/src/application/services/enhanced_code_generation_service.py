"""Enhanced code generation service with business logic intelligence."""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import asdict

try:
    from src.core.interfaces import CodeGenerator
    from src.core.exceptions import CodeGenerationError
    from src.domain.models.generation_context import GenerationContext, BusinessRule, IntegrationPattern
    from src.domain.models.code_models import GeneratedCode
    from src.domain.services.business_logic_processor import BusinessLogicProcessor, BusinessLogicInsights
    from src.domain.services.prompt_builder import AdvancedPromptBuilder
    from src.domain.services.integration_pattern_processor import IntegrationPatternProcessor, IntegrationAnalysis
    from src.infrastructure.template_engine import TemplateEngine
    from src.infrastructure.ai_provider import EnhancedOpenAIProvider
    from src.infrastructure.import_manager import ImportManager
except ImportError:
    try:
        from core.interfaces import CodeGenerator
        from core.exceptions import CodeGenerationError
        from domain.models.generation_context import GenerationContext, BusinessRule, IntegrationPattern
        from domain.models.code_models import GeneratedCode
        from domain.services.business_logic_processor import BusinessLogicProcessor, BusinessLogicInsights
        from domain.services.prompt_builder import AdvancedPromptBuilder
        from domain.services.integration_pattern_processor import IntegrationPatternProcessor, IntegrationAnalysis
        from infrastructure.template_engine import TemplateEngine
        from infrastructure.ai_provider import EnhancedOpenAIProvider
        from infrastructure.import_manager import ImportManager
    except ImportError:
        # Define fallback classes
        class CodeGenerator: pass
        class CodeGenerationError(Exception): pass


logger = logging.getLogger(__name__)


class EnhancedCodeGenerationService(CodeGenerator):
    """Enhanced code generation service with business intelligence and AI integration."""
    
    def __init__(self, 
                 template_engine: TemplateEngine,
                 ai_provider: EnhancedOpenAIProvider,
                 import_manager: ImportManager):
        self.template_engine = template_engine
        self.ai_provider = ai_provider
        self.import_manager = import_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize domain services
        self.business_logic_processor = BusinessLogicProcessor()
        self.prompt_builder = AdvancedPromptBuilder()
        self.integration_processor = IntegrationPatternProcessor()
        
    def generate(self, context: GenerationContext) -> GeneratedCode:
        """Generate intelligent code using business logic analysis and AI enhancement."""
        try:
            self.logger.info(f"Starting enhanced code generation for {context.entity_name}")
            
            # Step 1: Enhance context with business intelligence
            enhanced_context = self._analyze_and_enhance_context(context)
            
            # Step 2: Determine generation strategy
            generation_strategy = self._determine_generation_strategy(enhanced_context)
            
            # Step 3: Generate code using appropriate strategy
            if generation_strategy == 'ai_enhanced':
                generated_code = self._generate_with_ai_intelligence(enhanced_context)
            elif generation_strategy == 'ai_basic':
                generated_code = self._generate_with_basic_ai(enhanced_context)
            else:
                generated_code = self._generate_from_template(enhanced_context)
            
            # Step 4: Post-process the generated code
            final_code = self._post_process_code(generated_code, enhanced_context)
            
            # Step 5: Create comprehensive result
            result = self._create_generation_result(final_code, enhanced_context, generation_strategy)
            
            self.logger.info(f"Enhanced code generation completed for {context.entity_name} using {generation_strategy}")
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced code generation failed: {str(e)}")
            # Fallback to basic generation
            return self._fallback_generation(context)
    
    def _analyze_and_enhance_context(self, context: GenerationContext) -> GenerationContext:
        """Analyze context and enhance with business intelligence."""
        try:
            self.logger.info("Analyzing context for business intelligence")
            
            # Analyze business logic
            business_insights = self.business_logic_processor.analyze_context(context)
            
            # Analyze integration patterns
            integration_analysis = self.integration_processor.analyze_integration_patterns(context)
            
            # Use AI to analyze business requirements if spec data is available
            ai_analysis = {}
            if context.spec_data:
                try:
                    ai_analysis = self.ai_provider.analyze_business_requirements(
                        context.spec_data, 
                        context.instruction_data or {}
                    )
                except Exception as e:
                    self.logger.warning(f"AI business analysis failed: {e}")
            
            # Create enhanced context
            enhanced_context = GenerationContext(
                file_type=context.file_type,
                entity_name=context.entity_name,
                package_name=context.package_name,
                language=context.language,
                framework=context.framework,
                template_content=context.template_content,
                spec_data=context.spec_data,
                instruction_data=context.instruction_data,
                output_path=context.output_path,
                
                # Enhanced fields from business analysis
                endpoints=context.endpoints or self._extract_endpoints_from_spec(context.spec_data),
                business_rules=self._merge_business_rules(
                    business_insights.business_rules,
                    ai_analysis.get('business_rules', [])
                ),
                integration_patterns=integration_analysis.patterns,
                downstream_systems=integration_analysis.downstream_systems,
                service_pattern=self._determine_service_pattern(business_insights.patterns_detected),
                
                # Metadata
                metadata={
                    **context.metadata,
                    'business_insights': asdict(business_insights),
                    'integration_analysis': asdict(integration_analysis),
                    'ai_analysis': ai_analysis
                },
                
                # Configuration
                generation_options=context.generation_options,
                complexity_score=max(business_insights.complexity_score, ai_analysis.get('complexity_score', 1)),
                requires_ai_generation=self._should_use_ai_generation(business_insights, integration_analysis, ai_analysis)
            )
            
            self.logger.info(f"Context enhanced - Complexity: {enhanced_context.complexity_score}, "
                           f"Business Rules: {len(enhanced_context.business_rules or [])}, "
                           f"Integration Patterns: {len(enhanced_context.integration_patterns)}")
            
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"Context analysis failed: {e}")
            # Return original context if analysis fails
            return context
    
    def _determine_generation_strategy(self, context: GenerationContext) -> str:
        """Determine the best generation strategy based on context analysis."""
        try:
            # Check if AI generation is explicitly required
            if context.requires_ai_generation:
                return 'ai_enhanced'
            
            # High complexity suggests AI enhancement
            if context.complexity_score >= 7:
                return 'ai_enhanced'
            
            # Significant business rules or integration patterns suggest AI
            business_rule_count = len(context.business_rules or [])
            integration_pattern_count = len(context.integration_patterns)
            
            if business_rule_count >= 5 or integration_pattern_count >= 3:
                return 'ai_enhanced'
            
            # Some business logic suggests basic AI
            if business_rule_count > 0 or integration_pattern_count > 0:
                return 'ai_basic'
            
            # Otherwise use template
            return 'template_only'
            
        except Exception as e:
            self.logger.warning(f"Strategy determination failed: {e}")
            return 'template_only'
    
    def _generate_with_ai_intelligence(self, context: GenerationContext) -> str:
        """Generate code using full AI intelligence with sophisticated prompting."""
        try:
            self.logger.info("Generating code with full AI intelligence")
            
            # Generate sophisticated code using AI
            result = self.ai_provider.generate_code(context)
            
            if not result.content:
                raise CodeGenerationError("AI generated empty content")
            
            return result.content
            
        except Exception as e:
            self.logger.warning(f"AI intelligence generation failed: {e}, falling back to basic AI")
            return self._generate_with_basic_ai(context)
    
    def _generate_with_basic_ai(self, context: GenerationContext) -> str:
        """Generate code using basic AI enhancement of template."""
        try:
            self.logger.info("Generating code with basic AI enhancement")
            
            # Start with template if available
            if context.template_content:
                base_code = self._generate_from_template(context)
                
                # Enhance with AI
                enhanced_code = self.ai_provider.enhance_code(
                    base_code, 
                    'business_logic',
                    {
                        'business_rules': [asdict(rule) for rule in (context.business_rules or [])],
                        'integration_patterns': [asdict(pattern) for pattern in context.integration_patterns],
                        'language': context.language,
                        'framework': context.framework
                    }
                )
                
                return enhanced_code if enhanced_code else base_code
            else:
                # Generate directly with AI
                result = self.ai_provider.generate_code(context)
                return result.content if result.content else self._generate_fallback_content(context)
                
        except Exception as e:
            self.logger.warning(f"Basic AI generation failed: {e}, falling back to template")
            return self._generate_from_template(context)
    
    def _generate_from_template(self, context: GenerationContext) -> str:
        """Generate code from template with enhanced context."""
        try:
            if not context.template_content:
                return self._generate_fallback_content(context)
            
            # Build enhanced template context
            template_context = self._build_enhanced_template_context(context)
            
            # Process template
            return self.template_engine.process_template(context.template_content, template_context)
            
        except Exception as e:
            self.logger.warning(f"Template generation failed: {e}")
            return self._generate_fallback_content(context)
    
    def _post_process_code(self, code: str, context: GenerationContext) -> str:
        """Post-process generated code with imports and final enhancements."""
        try:
            # Process imports
            processed_code = self._process_imports(code, context)
            
            # Apply additional enhancements if needed
            if context.complexity_score >= 5:
                # Add logging enhancement for complex code
                try:
                    enhanced_code = self.ai_provider.enhance_code(
                        processed_code, 
                        'error_handling',
                        {'language': context.language, 'framework': context.framework}
                    )
                    processed_code = enhanced_code if enhanced_code else processed_code
                except Exception as e:
                    self.logger.warning(f"Post-processing enhancement failed: {e}")
            
            return processed_code
            
        except Exception as e:
            self.logger.warning(f"Post-processing failed: {e}")
            return code
    
    def _create_generation_result(self, code: str, context: GenerationContext, strategy: str) -> GeneratedCode:
        """Create comprehensive generation result with metadata."""
        return GeneratedCode(
            content=code,
            language=context.language,
            framework=context.framework,
            metadata={
                'entity_name': context.entity_name,
                'package_name': context.package_name,
                'file_type': context.file_type,
                'generation_strategy': strategy,
                'complexity_score': context.complexity_score,
                'business_rules_count': len(context.business_rules or []),
                'integration_patterns_count': len(context.integration_patterns),
                'requires_ai_generation': context.requires_ai_generation,
                'service_pattern': context.service_pattern.value if context.service_pattern else None,
                'downstream_systems_count': len(context.downstream_systems) if context.downstream_systems else 0,
                'analysis_metadata': context.metadata.get('business_insights', {}),
                'generation_timestamp': self._get_timestamp(),
                'code_quality_indicators': {
                    'has_business_logic': len(context.business_rules or []) > 0,
                    'has_integration_patterns': len(context.integration_patterns) > 0,
                    'complexity_level': 'high' if context.complexity_score >= 7 else 'medium' if context.complexity_score >= 4 else 'low',
                    'ai_enhanced': strategy in ['ai_enhanced', 'ai_basic']
                }
            }
        )
    
    def _fallback_generation(self, context: GenerationContext) -> GeneratedCode:
        """Fallback generation when enhanced generation fails."""
        try:
            self.logger.info("Using fallback generation")
            fallback_code = self._generate_fallback_content(context)
            
            return GeneratedCode(
                content=fallback_code,
                language=context.language,
                framework=context.framework,
                metadata={
                    'entity_name': context.entity_name,
                    'package_name': context.package_name,
                    'generation_strategy': 'fallback',
                    'generation_timestamp': self._get_timestamp()
                }
            )
        except Exception as e:
            raise CodeGenerationError(f"Even fallback generation failed: {str(e)}")
    
    # Helper methods
    
    def _extract_endpoints_from_spec(self, spec_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Extract endpoints from API specification."""
        if not spec_data or 'paths' not in spec_data:
            return None
        
        endpoints = []
        try:
            for path, methods in spec_data['paths'].items():
                for method, details in methods.items():
                    if isinstance(details, dict):
                        endpoints.append({
                            'path': path,
                            'method': method.upper(),
                            'summary': details.get('summary', ''),
                            'description': details.get('description', ''),
                            'parameters': details.get('parameters', []),
                            'responses': details.get('responses', {})
                        })
        except Exception as e:
            self.logger.warning(f"Error extracting endpoints: {e}")
            return None
        
        return endpoints if endpoints else None
    
    def _merge_business_rules(self, processor_rules: List[BusinessRule], ai_rules: List[Dict[str, Any]]) -> List[BusinessRule]:
        """Merge business rules from different sources."""
        merged_rules = list(processor_rules)
        
        # Convert AI rules to BusinessRule objects
        for ai_rule in ai_rules:
            try:
                if isinstance(ai_rule, dict):
                    merged_rules.append(BusinessRule(
                        name=ai_rule.get('name', 'ai_rule'),
                        description=ai_rule.get('description', ''),
                        category=ai_rule.get('category', 'validation'),
                        implementation=ai_rule.get('implementation'),
                        priority=ai_rule.get('priority', 1)
                    ))
            except Exception as e:
                self.logger.warning(f"Error merging AI rule: {e}")
        
        return merged_rules
    
    def _determine_service_pattern(self, detected_patterns: List[str]) -> Optional[Any]:
        """Determine service pattern from detected patterns."""
        try:
            from domain.models.generation_context import ServicePattern
        except ImportError:
            # Define fallback if import fails
            class ServicePattern:
                CRUD = "crud"
                INTEGRATION = "integration"
                AGGREGATOR = "aggregator"
        
        if not detected_patterns:
            return ServicePattern.CRUD
        
        pattern_mapping = {
            'integration': ServicePattern.INTEGRATION,
            'aggregator': ServicePattern.AGGREGATOR,
            'orchestrator': ServicePattern.ORCHESTRATOR,
            'crud': ServicePattern.CRUD
        }
        
        for pattern in detected_patterns:
            if pattern in pattern_mapping:
                return pattern_mapping[pattern]
        
        return ServicePattern.CRUD
    
    def _should_use_ai_generation(self, business_insights: BusinessLogicInsights, 
                                integration_analysis: IntegrationAnalysis, 
                                ai_analysis: Dict[str, Any]) -> bool:
        """Determine if AI generation should be used."""
        # High complexity always uses AI
        if business_insights.complexity_score >= 7 or ai_analysis.get('complexity_score', 0) >= 7:
            return True
        
        # Significant business logic uses AI
        if len(business_insights.business_rules) >= 5:
            return True
        
        # Multiple integration patterns use AI
        if len(integration_analysis.patterns) >= 3:
            return True
        
        # Complex integration scenarios use AI
        if len(integration_analysis.downstream_systems) >= 2:
            return True
        
        return False
    
    def _build_enhanced_template_context(self, context: GenerationContext) -> Dict[str, Any]:
        """Build enhanced context for template processing."""
        base_context = {
            'entity_name': context.entity_name,
            'package_name': context.package_name,
            'class_name': self._to_class_name(context.entity_name),
            'variable_name': self._to_variable_name(context.entity_name),
            'framework': context.framework,
            'language': context.language,
            'complexity_score': context.complexity_score,
            'service_pattern': context.service_pattern.value if context.service_pattern else 'crud'
        }
        
        # Add business rules context
        if context.business_rules:
            base_context['business_rules'] = [
                {
                    'name': rule.name,
                    'description': rule.description,
                    'category': rule.category,
                    'implementation': rule.implementation,
                    'priority': rule.priority
                }
                for rule in context.business_rules
            ]
            base_context['has_business_rules'] = True
        else:
            base_context['business_rules'] = []
            base_context['has_business_rules'] = False
        
        # Add integration patterns context
        if context.integration_patterns:
            base_context['integration_patterns'] = [
                {
                    'name': pattern.name,
                    'type': pattern.pattern_type.value,
                    'description': pattern.description,
                    'configuration': pattern.configuration
                }
                for pattern in context.integration_patterns
            ]
            base_context['has_integration_patterns'] = True
        else:
            base_context['integration_patterns'] = []
            base_context['has_integration_patterns'] = False
        
        # Add endpoints context
        if context.endpoints:
            base_context['endpoints'] = context.endpoints
            base_context['has_endpoints'] = True
        else:
            base_context['endpoints'] = []
            base_context['has_endpoints'] = False
        
        return base_context
    
    def _process_imports(self, code: str, context: GenerationContext) -> str:
        """Enhanced import processing."""
        try:
            required_imports = self.import_manager.detect_imports(code, context.language)
            
            # Add framework-specific imports based on patterns
            if context.integration_patterns:
                for pattern in context.integration_patterns:
                    pattern_imports = self._get_pattern_imports(pattern, context)
                    required_imports.extend(pattern_imports)
            
            return self.import_manager.add_missing_imports(code, required_imports)
        except Exception as e:
            self.logger.warning(f"Enhanced import processing failed: {e}")
            return code
    
    def _get_pattern_imports(self, pattern: IntegrationPattern, context: GenerationContext) -> List[str]:
        """Get imports needed for integration patterns."""
        imports = []
        
        try:
            if context.language.lower() == 'java' and context.framework.lower() == 'springboot':
                pattern_import_map = {
                    'circuit_breaker': ['io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker'],
                    'retry_logic': ['org.springframework.retry.annotation.Retryable'],
                    'caching': ['org.springframework.cache.annotation.Cacheable'],
                    'async_processing': ['org.springframework.scheduling.annotation.Async']
                }
                
                pattern_imports = pattern_import_map.get(pattern.pattern_type.value, [])
                imports.extend(pattern_imports)
        except Exception as e:
            self.logger.warning(f"Error getting pattern imports: {e}")
        
        return imports
    
    def _generate_fallback_content(self, context: GenerationContext) -> str:
        """Generate basic fallback content when all else fails."""
        if context.language.lower() == 'java':
            return f"""package {context.package_name};

/**
 * {context.entity_name} - Generated class
 * Generation failed, this is a basic fallback implementation.
 */
public class {self._to_class_name(context.entity_name)} {{
    
    // TODO: Implement business logic
    // This is a fallback implementation
    
}}
"""
        else:
            return f"# {context.entity_name} - Generated class\n# This is a fallback implementation\n"
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to ClassName format."""
        return ''.join(word.capitalize() for word in name.replace('_', ' ').split())
    
    def _to_variable_name(self, name: str) -> str:
        """Convert name to variableName format."""
        words = name.replace('_', ' ').split()
        if not words:
            return name
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
