"""Generation context and configuration models."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class ServicePattern(Enum):
    """Service implementation patterns."""
    CRUD = "crud"
    INTEGRATION = "integration"
    AGGREGATOR = "aggregator"
    ORCHESTRATOR = "orchestrator"


class IntegrationType(Enum):
    """Types of integration patterns."""
    API_CLIENT = "api_client"
    CIRCUIT_BREAKER = "circuit_breaker"
    RETRY_LOGIC = "retry_logic"
    CACHING = "caching"
    ASYNC_PROCESSING = "async_processing"
    RATE_LIMITING = "rate_limiting"


@dataclass
class IntegrationPattern:
    """Integration pattern configuration."""
    pattern_type: IntegrationType
    name: str
    description: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class BusinessRule:
    """Business rule definition."""
    name: str
    description: str
    category: str
    implementation: Optional[str] = None
    validation: Optional[str] = None
    priority: int = 1
    conditions: List[str] = field(default_factory=list)


@dataclass
class DownstreamSystem:
    """Downstream system configuration."""
    name: str
    base_url: str
    description: str
    timeout: int = 5000
    retry_config: Dict[str, Any] = field(default_factory=dict)
    circuit_breaker_config: Dict[str, Any] = field(default_factory=dict)
    authentication: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationContext:
    """Enhanced context for code generation with business logic and integration patterns."""
    file_type: str
    entity_name: str
    package_name: str
    language: str
    framework: str
    template_content: str
    spec_data: Dict[str, Any]
    instruction_data: Dict[str, Any]
    output_path: str
    
    # Enhanced fields from old version
    endpoints: Optional[List[Dict[str, Any]]] = None
    business_rules: Optional[List[BusinessRule]] = None
    integration_patterns: List[IntegrationPattern] = field(default_factory=list)
    downstream_systems: Dict[str, DownstreamSystem] = field(default_factory=dict)
    service_pattern: ServicePattern = ServicePattern.CRUD
    
    # Metadata and configuration
    metadata: Dict[str, Any] = field(default_factory=dict)
    generation_options: Dict[str, Any] = field(default_factory=dict)
    
    # Calculated fields
    complexity_score: int = 0
    requires_ai_generation: bool = False
    
    @property
    def full_package_name(self) -> str:
        """Get full package name including subpackage."""
        if self.file_type in ['controller', 'service', 'repository', 'model', 'dto', 'config']:
            return f"{self.package_name}.{self.file_type}"
        return self.package_name


@dataclass 
class ValidationConfig:
    """Configuration for code validation."""
    strict_mode: bool = False
    min_content_length: int = 10
    check_syntax: bool = False
    check_structure: bool = False
    allow_incomplete: bool = True
    require_imports: bool = False
    require_annotations: bool = False
    custom_rules: List[str] = field(default_factory=list)
