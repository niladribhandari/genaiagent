"""Integration pattern analyzer and generator."""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass

try:
    from src.domain.models.generation_context import IntegrationPattern, IntegrationType, DownstreamSystem, GenerationContext
except ImportError:
    from domain.models.generation_context import IntegrationPattern, IntegrationType, DownstreamSystem, GenerationContext


logger = logging.getLogger(__name__)


@dataclass
class IntegrationAnalysis:
    """Result of integration pattern analysis."""
    patterns: List[IntegrationPattern]
    downstream_systems: Dict[str, DownstreamSystem]
    complexity_factors: List[str]
    recommendations: List[str]


class IntegrationPatternProcessor:
    """Processes and analyzes integration patterns from specifications."""

    def __init__(self):
        self.pattern_detectors = {
            IntegrationType.API_CLIENT: self._detect_api_client_pattern,
            IntegrationType.CIRCUIT_BREAKER: self._detect_circuit_breaker_pattern,
            IntegrationType.RETRY_LOGIC: self._detect_retry_pattern,
            IntegrationType.CACHING: self._detect_caching_pattern,
            IntegrationType.ASYNC_PROCESSING: self._detect_async_pattern,
            IntegrationType.RATE_LIMITING: self._detect_rate_limiting_pattern,
        }

    def analyze_integration_patterns(self, context: GenerationContext) -> IntegrationAnalysis:
        """Analyze the context to identify integration patterns."""
        try:
            patterns = []
            downstream_systems = {}
            complexity_factors = []
            recommendations = []

            # Analyze API specification for integration patterns
            if context.spec_data:
                spec_patterns = self._analyze_spec_for_patterns(context.spec_data)
                patterns.extend(spec_patterns)

                # Identify downstream systems
                downstream = self._identify_downstream_systems(context.spec_data)
                downstream_systems.update(downstream)

            # Analyze instruction data for integration requirements
            if context.instruction_data:
                instruction_patterns = self._analyze_instructions_for_patterns(context.instruction_data)
                patterns.extend(instruction_patterns)

            # Generate recommendations based on patterns
            recommendations = self._generate_recommendations(patterns, downstream_systems)

            # Calculate complexity factors
            complexity_factors = self._identify_complexity_factors(patterns, downstream_systems)

            return IntegrationAnalysis(
                patterns=patterns,
                downstream_systems=downstream_systems,
                complexity_factors=complexity_factors,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error analyzing integration patterns: {e}")
            return IntegrationAnalysis(
                patterns=[],
                downstream_systems={},
                complexity_factors=[],
                recommendations=[]
            )

    def _analyze_spec_for_patterns(self, spec_data: Dict[str, Any]) -> List[IntegrationPattern]:
        """Analyze API specification for integration patterns."""
        patterns = []

        try:
            if 'paths' in spec_data:
                for path, methods in spec_data['paths'].items():
                    for method, operation in methods.items():
                        if isinstance(operation, dict):
                            # Check for external service references
                            operation_patterns = self._detect_patterns_in_operation(
                                path, method, operation
                            )
                            patterns.extend(operation_patterns)

            # Check for OpenAPI extensions that might indicate patterns
            if 'x-integration-patterns' in spec_data:
                custom_patterns = self._parse_custom_integration_patterns(
                    spec_data['x-integration-patterns']
                )
                patterns.extend(custom_patterns)

        except Exception as e:
            logger.warning(f"Error analyzing spec for patterns: {e}")

        return patterns

    def _detect_patterns_in_operation(self, path: str, method: str, operation: Dict[str, Any]) -> List[IntegrationPattern]:
        """Detect integration patterns in a single operation."""
        patterns = []

        try:
            description = (operation.get('description', '') + ' ' + 
                         operation.get('summary', '')).lower()

            # API Client pattern detection
            if any(keyword in description for keyword in ['external', 'third-party', 'api', 'client']):
                patterns.append(IntegrationPattern(
                    pattern_type=IntegrationType.API_CLIENT,
                    name=f"{method}_{path}_api_client".replace('/', '_').replace('-', '_'),
                    description=f"API client integration for {method.upper()} {path}",
                    configuration={
                        'endpoint': path,
                        'method': method.upper(),
                        'timeout': 5000,
                        'retries': 3
                    }
                ))

            # Circuit breaker pattern detection
            if any(keyword in description for keyword in ['resilient', 'fault-tolerant', 'circuit', 'fallback']):
                patterns.append(IntegrationPattern(
                    pattern_type=IntegrationType.CIRCUIT_BREAKER,
                    name=f"{method}_{path}_circuit_breaker".replace('/', '_').replace('-', '_'),
                    description=f"Circuit breaker for {method.upper()} {path}",
                    configuration={
                        'failure_threshold': 5,
                        'recovery_timeout': 30000,
                        'half_open_max_calls': 3
                    }
                ))

            # Caching pattern detection
            if any(keyword in description for keyword in ['cache', 'cached', 'caching']) or method.lower() == 'get':
                patterns.append(IntegrationPattern(
                    pattern_type=IntegrationType.CACHING,
                    name=f"{method}_{path}_caching".replace('/', '_').replace('-', '_'),
                    description=f"Caching for {method.upper()} {path}",
                    configuration={
                        'ttl': 300,  # 5 minutes
                        'max_size': 1000,
                        'cache_key_strategy': 'path_params'
                    }
                ))

            # Async processing pattern detection
            if any(keyword in description for keyword in ['async', 'asynchronous', 'background', 'queue']):
                patterns.append(IntegrationPattern(
                    pattern_type=IntegrationType.ASYNC_PROCESSING,
                    name=f"{method}_{path}_async".replace('/', '_').replace('-', '_'),
                    description=f"Async processing for {method.upper()} {path}",
                    configuration={
                        'queue_name': f"{method}_{path}_queue".replace('/', '_'),
                        'retry_attempts': 3,
                        'delay_between_retries': 1000
                    }
                ))

            # Rate limiting detection
            if any(keyword in description for keyword in ['rate', 'limit', 'throttle', 'quota']):
                patterns.append(IntegrationPattern(
                    pattern_type=IntegrationType.RATE_LIMITING,
                    name=f"{method}_{path}_rate_limit".replace('/', '_').replace('-', '_'),
                    description=f"Rate limiting for {method.upper()} {path}",
                    configuration={
                        'requests_per_minute': 100,
                        'burst_capacity': 20,
                        'key_strategy': 'user_id'
                    }
                ))

        except Exception as e:
            logger.warning(f"Error detecting patterns in operation {method} {path}: {e}")

        return patterns

    def _analyze_instructions_for_patterns(self, instruction_data: Dict[str, Any]) -> List[IntegrationPattern]:
        """Analyze instruction data for integration pattern requirements."""
        patterns = []

        try:
            # Check for explicit integration pattern requirements
            if 'integration_patterns' in instruction_data:
                for pattern_config in instruction_data['integration_patterns']:
                    if isinstance(pattern_config, dict):
                        pattern_type = pattern_config.get('type')
                        if pattern_type:
                            try:
                                integration_type = IntegrationType(pattern_type)
                                patterns.append(IntegrationPattern(
                                    pattern_type=integration_type,
                                    name=pattern_config.get('name', f"custom_{pattern_type}"),
                                    description=pattern_config.get('description', f"Custom {pattern_type} pattern"),
                                    configuration=pattern_config.get('configuration', {})
                                ))
                            except ValueError:
                                logger.warning(f"Unknown integration pattern type: {pattern_type}")

            # Check for performance requirements that might need patterns
            if 'performance' in instruction_data:
                perf_config = instruction_data['performance']
                
                # High availability requirements suggest circuit breaker
                if perf_config.get('high_availability', False):
                    patterns.append(IntegrationPattern(
                        pattern_type=IntegrationType.CIRCUIT_BREAKER,
                        name="high_availability_circuit_breaker",
                        description="Circuit breaker for high availability requirements",
                        configuration={
                            'failure_threshold': 3,
                            'recovery_timeout': 10000
                        }
                    ))

                # Caching for performance
                if perf_config.get('enable_caching', False):
                    patterns.append(IntegrationPattern(
                        pattern_type=IntegrationType.CACHING,
                        name="performance_caching",
                        description="Caching for performance optimization",
                        configuration={
                            'ttl': perf_config.get('cache_ttl', 300),
                            'max_size': perf_config.get('cache_size', 1000)
                        }
                    ))

        except Exception as e:
            logger.warning(f"Error analyzing instructions for patterns: {e}")

        return patterns

    def _identify_downstream_systems(self, spec_data: Dict[str, Any]) -> Dict[str, DownstreamSystem]:
        """Identify downstream systems from API specification."""
        systems = {}

        try:
            # Check for external service references in operation descriptions
            if 'paths' in spec_data:
                for path, methods in spec_data['paths'].items():
                    for method, operation in methods.items():
                        if isinstance(operation, dict):
                            description = (operation.get('description', '') + ' ' + 
                                         operation.get('summary', '')).lower()
                            
                            # Look for external service mentions
                            if any(keyword in description for keyword in ['external', 'third-party', 'downstream']):
                                system_name = self._extract_system_name(description, path)
                                if system_name and system_name not in systems:
                                    systems[system_name] = DownstreamSystem(
                                        name=system_name,
                                        base_url=f"https://{system_name.lower()}.api.com",  # Placeholder
                                        description=f"External system integration for {system_name}",
                                        timeout=5000,
                                        retry_config={
                                            'max_attempts': 3,
                                            'delay': 1000,
                                            'backoff_multiplier': 2
                                        },
                                        circuit_breaker_config={
                                            'failure_threshold': 5,
                                            'recovery_timeout': 30000
                                        }
                                    )

            # Check for explicit external systems configuration
            if 'x-external-systems' in spec_data:
                for system_config in spec_data['x-external-systems']:
                    if isinstance(system_config, dict):
                        name = system_config.get('name')
                        if name:
                            systems[name] = DownstreamSystem(
                                name=name,
                                base_url=system_config.get('base_url', ''),
                                description=system_config.get('description', ''),
                                timeout=system_config.get('timeout', 5000),
                                retry_config=system_config.get('retry_config', {}),
                                circuit_breaker_config=system_config.get('circuit_breaker_config', {}),
                                authentication=system_config.get('authentication', {})
                            )

        except Exception as e:
            logger.warning(f"Error identifying downstream systems: {e}")

        return systems

    def _extract_system_name(self, description: str, path: str) -> Optional[str]:
        """Extract system name from description or path."""
        # Simple heuristic - look for capitalized words that might be system names
        import re
        
        # Try to extract from description
        words = description.split()
        for word in words:
            if word.istitle() and len(word) > 3:
                return word
        
        # Try to extract from path
        path_parts = path.strip('/').split('/')
        for part in path_parts:
            if part.istitle() and len(part) > 3:
                return part
        
        return None

    def _parse_custom_integration_patterns(self, patterns_config: List[Dict[str, Any]]) -> List[IntegrationPattern]:
        """Parse custom integration patterns from OpenAPI extensions."""
        patterns = []

        try:
            for pattern_config in patterns_config:
                if isinstance(pattern_config, dict):
                    pattern_type_str = pattern_config.get('type')
                    if pattern_type_str:
                        try:
                            pattern_type = IntegrationType(pattern_type_str)
                            patterns.append(IntegrationPattern(
                                pattern_type=pattern_type,
                                name=pattern_config.get('name', f"custom_{pattern_type_str}"),
                                description=pattern_config.get('description', ''),
                                configuration=pattern_config.get('configuration', {}),
                                dependencies=pattern_config.get('dependencies', [])
                            ))
                        except ValueError:
                            logger.warning(f"Unknown pattern type in custom config: {pattern_type_str}")

        except Exception as e:
            logger.warning(f"Error parsing custom integration patterns: {e}")

        return patterns

    def _generate_recommendations(self, patterns: List[IntegrationPattern], 
                                downstream_systems: Dict[str, DownstreamSystem]) -> List[str]:
        """Generate recommendations based on identified patterns."""
        recommendations = []

        try:
            # Recommend circuit breaker if we have external integrations but no circuit breaker
            has_api_clients = any(p.pattern_type == IntegrationType.API_CLIENT for p in patterns)
            has_circuit_breaker = any(p.pattern_type == IntegrationType.CIRCUIT_BREAKER for p in patterns)
            
            if has_api_clients and not has_circuit_breaker:
                recommendations.append("Consider adding circuit breaker pattern for external API integrations")

            # Recommend retry logic if we have integrations but no retry
            has_retry = any(p.pattern_type == IntegrationType.RETRY_LOGIC for p in patterns)
            if has_api_clients and not has_retry:
                recommendations.append("Consider adding retry logic for external API calls")

            # Recommend caching for read-heavy operations
            api_client_patterns = [p for p in patterns if p.pattern_type == IntegrationType.API_CLIENT]
            get_operations = [p for p in api_client_patterns if p.configuration.get('method') == 'GET']
            has_caching = any(p.pattern_type == IntegrationType.CACHING for p in patterns)
            
            if get_operations and not has_caching:
                recommendations.append("Consider adding caching for GET operations to improve performance")

            # Recommend rate limiting for public APIs
            if len(patterns) > 3 and not any(p.pattern_type == IntegrationType.RATE_LIMITING for p in patterns):
                recommendations.append("Consider adding rate limiting to protect against abuse")

            # Recommend monitoring and observability
            if len(downstream_systems) > 1:
                recommendations.append("Implement comprehensive monitoring and observability for multiple downstream integrations")

        except Exception as e:
            logger.warning(f"Error generating recommendations: {e}")

        return recommendations

    def _identify_complexity_factors(self, patterns: List[IntegrationPattern], 
                                   downstream_systems: Dict[str, DownstreamSystem]) -> List[str]:
        """Identify factors that contribute to integration complexity."""
        factors = []

        try:
            if len(downstream_systems) > 2:
                factors.append(f"Multiple downstream systems ({len(downstream_systems)})")

            if len(patterns) > 5:
                factors.append(f"High number of integration patterns ({len(patterns)})")

            # Check for complex patterns
            complex_patterns = [IntegrationType.CIRCUIT_BREAKER, IntegrationType.ASYNC_PROCESSING]
            complex_count = sum(1 for p in patterns if p.pattern_type in complex_patterns)
            if complex_count > 0:
                factors.append(f"Complex integration patterns ({complex_count})")

            # Check for authentication complexity
            auth_systems = [s for s in downstream_systems.values() if s.authentication]
            if auth_systems:
                factors.append(f"Systems requiring authentication ({len(auth_systems)})")

        except Exception as e:
            logger.warning(f"Error identifying complexity factors: {e}")

        return factors

    # Individual pattern detection methods
    def _detect_api_client_pattern(self, context: Dict[str, Any]) -> bool:
        """Detect if API client pattern is needed."""
        return 'external' in str(context).lower() or 'api' in str(context).lower()

    def _detect_circuit_breaker_pattern(self, context: Dict[str, Any]) -> bool:
        """Detect if circuit breaker pattern is needed."""
        keywords = ['resilient', 'fault-tolerant', 'circuit', 'fallback']
        return any(keyword in str(context).lower() for keyword in keywords)

    def _detect_retry_pattern(self, context: Dict[str, Any]) -> bool:
        """Detect if retry pattern is needed."""
        keywords = ['retry', 'resilient', 'fault-tolerant']
        return any(keyword in str(context).lower() for keyword in keywords)

    def _detect_caching_pattern(self, context: Dict[str, Any]) -> bool:
        """Detect if caching pattern is needed."""
        keywords = ['cache', 'performance', 'fast']
        return any(keyword in str(context).lower() for keyword in keywords)

    def _detect_async_pattern(self, context: Dict[str, Any]) -> bool:
        """Detect if async processing pattern is needed."""
        keywords = ['async', 'asynchronous', 'background', 'queue']
        return any(keyword in str(context).lower() for keyword in keywords)

    def _detect_rate_limiting_pattern(self, context: Dict[str, Any]) -> bool:
        """Detect if rate limiting pattern is needed."""
        keywords = ['rate', 'limit', 'throttle', 'quota']
        return any(keyword in str(context).lower() for keyword in keywords)
