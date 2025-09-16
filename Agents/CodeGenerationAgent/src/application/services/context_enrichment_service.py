"""Context enrichment service for enhanced code generation."""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import asdict

# Error handling and monitoring
from datetime import datetime
from collections import defaultdict

try:
    from src.domain.models.generation_context import GenerationContext, BusinessRule, IntegrationPattern, ServicePattern
    from src.domain.services.business_logic_processor import BusinessLogicProcessor, BusinessLogicInsights
    from src.domain.services.integration_pattern_processor import IntegrationPatternProcessor, IntegrationAnalysis
    from src.infrastructure.ai_provider import EnhancedOpenAIProvider
except ImportError:
    try:
        from domain.models.generation_context import GenerationContext, BusinessRule, IntegrationPattern, ServicePattern
        from domain.services.business_logic_processor import BusinessLogicProcessor, BusinessLogicInsights
        from domain.services.integration_pattern_processor import IntegrationPatternProcessor, IntegrationAnalysis
        from infrastructure.ai_provider import EnhancedOpenAIProvider
    except ImportError:
        # Define fallback classes
        class GenerationContext: pass
        class BusinessRule: pass
        class BusinessLogicProcessor: pass
        class IntegrationPatternProcessor: pass

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from dataclasses import asdict

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from domain.models.generation_context import GenerationContext, BusinessRule, IntegrationPattern, ServicePattern
    from domain.services.business_logic_processor import BusinessLogicProcessor, BusinessLogicInsights
    from domain.services.integration_pattern_processor import IntegrationPatternProcessor, IntegrationAnalysis
    from infrastructure.ai_provider import EnhancedOpenAIProvider
except ImportError:
    # Fallback classes
    class GenerationContext:
        pass
    class BusinessRule:
        pass
    class IntegrationPattern:
        pass
    class ServicePattern:
        pass
    class BusinessLogicProcessor:
        pass
    class BusinessLogicInsights:
        pass
    class IntegrationPatternProcessor:
        pass
    class IntegrationAnalysis:
        pass
    class EnhancedOpenAIProvider:
        pass


logger = logging.getLogger(__name__)


class ContextEnrichmentService:
    """Service for enriching generation context with business intelligence."""
    
    def __init__(self, ai_provider: Optional[EnhancedOpenAIProvider] = None):
        self.business_logic_processor = BusinessLogicProcessor()
        self.integration_processor = IntegrationPatternProcessor()
        self.ai_provider = ai_provider
        self.logger = logging.getLogger(__name__)
    
    def enrich_context(self, context: GenerationContext) -> GenerationContext:
        """Enrich context with comprehensive business intelligence."""
        try:
            self.logger.info(f"Enriching context for {context.entity_name}")
            
            # Step 1: Analyze business logic
            business_insights = self._analyze_business_logic(context)
            
            # Step 2: Analyze integration patterns
            integration_analysis = self._analyze_integration_patterns(context)
            
            # Step 3: AI-powered requirement analysis
            ai_analysis = self._analyze_with_ai(context)
            
            # Step 4: Synthesize all analyses
            enriched_context = self._synthesize_analyses(
                context, business_insights, integration_analysis, ai_analysis
            )
            
            self._log_enrichment_results(enriched_context)
            
            return enriched_context
            
        except Exception as e:
            self.logger.error(f"Context enrichment failed: {e}")
            # Return original context with minimal enrichment
            return self._minimal_enrichment(context)
    
    def _analyze_business_logic(self, context: GenerationContext) -> BusinessLogicInsights:
        """Analyze business logic using domain processor."""
        try:
            return self.business_logic_processor.analyze_context(context)
        except Exception as e:
            self.logger.warning(f"Business logic analysis failed: {e}")
            return BusinessLogicInsights(
                complexity_score=1,
                required_validations=[],
                integration_points=[],
                business_rules=[],
                patterns_detected=[]
            )
    
    def _analyze_integration_patterns(self, context: GenerationContext) -> IntegrationAnalysis:
        """Analyze integration patterns using domain processor."""
        try:
            return self.integration_processor.analyze_integration_patterns(context)
        except Exception as e:
            self.logger.warning(f"Integration pattern analysis failed: {e}")
            return IntegrationAnalysis(
                patterns=[],
                downstream_systems={},
                complexity_factors=[],
                recommendations=[]
            )
    
    def _analyze_with_ai(self, context: GenerationContext) -> Dict[str, Any]:
        """Analyze requirements using AI if available."""
        if not self.ai_provider:
            return {}
        
        try:
            if context.spec_data:
                return self.ai_provider.analyze_business_requirements(
                    context.spec_data,
                    context.instruction_data or {}
                )
        except Exception as e:
            self.logger.warning(f"AI analysis failed: {e}")
        
        return {}
    
    def _synthesize_analyses(self, 
                           original_context: GenerationContext,
                           business_insights: BusinessLogicInsights,
                           integration_analysis: IntegrationAnalysis,
                           ai_analysis: Dict[str, Any]) -> GenerationContext:
        """Synthesize all analyses into enriched context."""
        
        # Merge business rules from all sources
        merged_business_rules = self._merge_business_rules(
            business_insights.business_rules,
            ai_analysis.get('business_rules', [])
        )
        
        # Determine service pattern
        service_pattern = self._determine_service_pattern(
            business_insights.patterns_detected,
            ai_analysis.get('enterprise_patterns', [])
        )
        
        # Calculate final complexity score
        complexity_score = max(
            business_insights.complexity_score,
            ai_analysis.get('complexity_score', 1),
            self._calculate_integration_complexity(integration_analysis)
        )
        
        # Determine if AI generation is required
        requires_ai = self._determine_ai_requirement(
            business_insights, integration_analysis, ai_analysis, complexity_score
        )
        
        # Extract endpoints if not already present
        endpoints = original_context.endpoints or self._extract_endpoints_from_spec(
            original_context.spec_data
        )
        
        # Build enriched metadata
        enriched_metadata = {
            **original_context.metadata,
            'enrichment_timestamp': self._get_timestamp(),
            'business_insights': asdict(business_insights),
            'integration_analysis': asdict(integration_analysis),
            'ai_analysis': ai_analysis,
            'enrichment_sources': ['business_logic_processor', 'integration_processor'] + 
                                (['ai_analysis'] if ai_analysis else [])
        }
        
        # Create enriched context
        return GenerationContext(
            # Original fields
            file_type=original_context.file_type,
            entity_name=original_context.entity_name,
            package_name=original_context.package_name,
            language=original_context.language,
            framework=original_context.framework,
            template_content=original_context.template_content,
            spec_data=original_context.spec_data,
            instruction_data=original_context.instruction_data,
            output_path=original_context.output_path,
            
            # Enriched fields
            endpoints=endpoints,
            business_rules=merged_business_rules,
            integration_patterns=integration_analysis.patterns,
            downstream_systems=integration_analysis.downstream_systems,
            service_pattern=service_pattern,
            
            # Configuration
            metadata=enriched_metadata,
            generation_options=original_context.generation_options,
            complexity_score=complexity_score,
            requires_ai_generation=requires_ai
        )
    
    def _merge_business_rules(self, processor_rules: List[BusinessRule], 
                            ai_rules: List[Dict[str, Any]]) -> List[BusinessRule]:
        """Merge business rules from different sources."""
        merged_rules = list(processor_rules)
        
        # Convert AI rules to BusinessRule objects
        for ai_rule in ai_rules:
            try:
                if isinstance(ai_rule, dict) and 'name' in ai_rule:
                    # Check for duplicates
                    rule_name = ai_rule['name']
                    if not any(rule.name == rule_name for rule in merged_rules):
                        merged_rules.append(BusinessRule(
                            name=rule_name,
                            description=ai_rule.get('description', ''),
                            category=ai_rule.get('category', 'validation'),
                            implementation=ai_rule.get('implementation'),
                            validation=ai_rule.get('validation'),
                            priority=ai_rule.get('priority', 1),
                            conditions=ai_rule.get('conditions', [])
                        ))
            except Exception as e:
                self.logger.warning(f"Error merging AI rule {ai_rule}: {e}")
        
        # Sort by priority (higher priority first)
        merged_rules.sort(key=lambda r: r.priority, reverse=True)
        
        return merged_rules
    
    def _determine_service_pattern(self, detected_patterns: List[str], 
                                 ai_patterns: List[str]) -> ServicePattern:
        """Determine the most appropriate service pattern."""
        all_patterns = detected_patterns + ai_patterns
        
        # Priority-based pattern selection
        pattern_priority = {
            'orchestrator': ServicePattern.ORCHESTRATOR,
            'aggregator': ServicePattern.AGGREGATOR,
            'integration': ServicePattern.INTEGRATION,
            'crud': ServicePattern.CRUD
        }
        
        for pattern_name in pattern_priority.keys():
            if any(pattern_name in p.lower() for p in all_patterns):
                return pattern_priority[pattern_name]
        
        # Default based on complexity
        if len(all_patterns) > 3:
            return ServicePattern.ORCHESTRATOR
        elif len(all_patterns) > 1:
            return ServicePattern.INTEGRATION
        else:
            return ServicePattern.CRUD
    
    def _calculate_integration_complexity(self, integration_analysis: IntegrationAnalysis) -> int:
        """Calculate complexity based on integration analysis."""
        complexity = 1
        
        # Add complexity for patterns
        pattern_complexity = {
            'circuit_breaker': 3,
            'async_processing': 2,
            'retry_logic': 1,
            'caching': 1,
            'rate_limiting': 2,
            'api_client': 1
        }
        
        for pattern in integration_analysis.patterns:
            complexity += pattern_complexity.get(pattern.pattern_type.value, 1)
        
        # Add complexity for downstream systems
        complexity += len(integration_analysis.downstream_systems) * 2
        
        # Add complexity for complexity factors
        complexity += len(integration_analysis.complexity_factors)
        
        return min(complexity, 10)  # Cap at 10
    
    def _determine_ai_requirement(self, 
                                business_insights: BusinessLogicInsights,
                                integration_analysis: IntegrationAnalysis,
                                ai_analysis: Dict[str, Any],
                                complexity_score: int) -> bool:
        """Determine if AI generation is required."""
        
        # High complexity always requires AI
        if complexity_score >= 7:
            return True
        
        # Significant business logic requires AI
        if len(business_insights.business_rules) >= 5:
            return True
        
        # Complex integration patterns require AI
        complex_patterns = ['circuit_breaker', 'async_processing', 'orchestrator']
        has_complex_patterns = any(
            pattern.pattern_type.value in complex_patterns 
            for pattern in integration_analysis.patterns
        )
        if has_complex_patterns:
            return True
        
        # Multiple downstream systems require AI
        if len(integration_analysis.downstream_systems) >= 2:
            return True
        
        # AI analysis suggests high complexity
        if ai_analysis.get('complexity_score', 0) >= 6:
            return True
        
        # Many AI-detected patterns
        if len(ai_analysis.get('enterprise_patterns', [])) >= 3:
            return True
        
        return False
    
    def _extract_endpoints_from_spec(self, spec_data: Optional[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Extract endpoint information from API specification."""
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
                            'operation_id': details.get('operationId'),
                            'parameters': details.get('parameters', []),
                            'request_body': details.get('requestBody'),
                            'responses': details.get('responses', {}),
                            'tags': details.get('tags', [])
                        })
        except Exception as e:
            self.logger.warning(f"Error extracting endpoints: {e}")
            return None
        
        return endpoints if endpoints else None
    
    def _minimal_enrichment(self, context: GenerationContext) -> GenerationContext:
        """Provide minimal enrichment when full analysis fails."""
        return GenerationContext(
            # Copy all original fields
            file_type=context.file_type,
            entity_name=context.entity_name,
            package_name=context.package_name,
            language=context.language,
            framework=context.framework,
            template_content=context.template_content,
            spec_data=context.spec_data,
            instruction_data=context.instruction_data,
            output_path=context.output_path,
            endpoints=context.endpoints,
            business_rules=context.business_rules or [],
            integration_patterns=context.integration_patterns,
            downstream_systems=context.downstream_systems,
            service_pattern=context.service_pattern or ServicePattern.CRUD,
            metadata={
                **context.metadata,
                'enrichment_status': 'minimal_fallback',
                'enrichment_timestamp': self._get_timestamp()
            },
            generation_options=context.generation_options,
            complexity_score=max(context.complexity_score, 2),  # Slightly higher for safety
            requires_ai_generation=context.requires_ai_generation
        )
    
    def _log_enrichment_results(self, context: GenerationContext):
        """Log the results of context enrichment."""
        self.logger.info(f"Context enrichment completed for {context.entity_name}:")
        self.logger.info(f"  - Complexity Score: {context.complexity_score}")
        self.logger.info(f"  - Business Rules: {len(context.business_rules or [])}")
        self.logger.info(f"  - Integration Patterns: {len(context.integration_patterns)}")
        self.logger.info(f"  - Downstream Systems: {len(context.downstream_systems or {})}")
        self.logger.info(f"  - Service Pattern: {context.service_pattern.value if context.service_pattern else 'None'}")
        self.logger.info(f"  - Requires AI: {context.requires_ai_generation}")
        
        if context.business_rules:
            rule_categories = {}
            for rule in context.business_rules:
                category = rule.category
                rule_categories[category] = rule_categories.get(category, 0) + 1
            
            self.logger.info(f"  - Rule Categories: {dict(rule_categories)}")
        
        if context.integration_patterns:
            pattern_types = [pattern.pattern_type.value for pattern in context.integration_patterns]
            self.logger.info(f"  - Integration Pattern Types: {pattern_types}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
