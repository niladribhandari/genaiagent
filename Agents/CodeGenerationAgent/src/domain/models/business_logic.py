"""Business logic models for code generation."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class WorkflowStepType(Enum):
    """Types of workflow steps."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    BUSINESS_RULE = "business_rule"
    PERSISTENCE = "persistence"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"


class ErrorHandlingStrategy(Enum):
    """Error handling strategies for workflow steps."""
    STOP_ON_ERROR = "stop_on_error"
    CONTINUE_ON_ERROR = "continue_on_error"
    CONTINUE_ON_WARNING = "continue_on_warning"
    RETRY_ON_ERROR = "retry_on_error"


@dataclass
class WorkflowStepInfo:
    """Information about a workflow step."""
    name: str
    step_type: WorkflowStepType
    order: int
    description: str
    method_name: str
    error_handling: ErrorHandlingStrategy
    rollback_required: bool = False
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    conditions: Optional[Dict[str, Any]] = None
    parameters: Optional[List[str]] = None


@dataclass
class WorkflowInfo:
    """Information about business workflow."""
    name: str
    description: str
    steps: List[WorkflowStepInfo]
    supports_rollback: bool = True
    is_transactional: bool = True
    publishes_events: bool = True
    requires_authentication: bool = True
    timeout_seconds: Optional[int] = None
    
    def get_step_by_name(self, step_name: str) -> Optional[WorkflowStepInfo]:
        """Get workflow step by name."""
        return next((step for step in self.steps if step.name == step_name), None)
    
    def get_ordered_steps(self) -> List[WorkflowStepInfo]:
        """Get steps ordered by execution order."""
        return sorted(self.steps, key=lambda x: x.order)


@dataclass
class CalculationRuleInfo:
    """Information about a calculation rule."""
    name: str
    description: str
    method_name: str
    formula: str
    parameters: List[str]
    return_type: str = "BigDecimal"
    validation_required: bool = True
    cacheable: bool = False
    precision: int = 2
    rounding_mode: str = "HALF_UP"
    conditions: Optional[Dict[str, Any]] = None


@dataclass
class CalculationInfo:
    """Information about business calculations."""
    name: str
    description: str
    rules: List[CalculationRuleInfo]
    uses_big_decimal: bool = True
    supports_caching: bool = True
    audit_enabled: bool = True
    configurable_formulas: bool = True
    
    def get_rule_by_name(self, rule_name: str) -> Optional[CalculationRuleInfo]:
        """Get calculation rule by name."""
        return next((rule for rule in self.rules if rule.name == rule_name), None)


@dataclass
class EventInfo:
    """Information about domain events."""
    name: str
    description: str
    event_type: str
    fields: List[str]
    async_processing: bool = True
    persistent: bool = False
    retry_policy: Optional[Dict[str, Any]] = None
    routing_key: Optional[str] = None


@dataclass
class ValidationRuleInfo:
    """Information about validation rules."""
    name: str
    description: str
    rule_type: str  # FIELD, CROSS_FIELD, BUSINESS_RULE, EXTERNAL
    target_field: Optional[str] = None
    validation_logic: str = ""
    error_message: str = ""
    error_code: Optional[str] = None
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    conditions: Optional[Dict[str, Any]] = None


@dataclass
class ValidationInfo:
    """Information about business validation."""
    entity_name: str
    rules: List[ValidationRuleInfo]
    supports_groups: bool = True
    supports_conditional: bool = True
    generates_custom_validators: bool = True
    
    def get_rules_by_type(self, rule_type: str) -> List[ValidationRuleInfo]:
        """Get validation rules by type."""
        return [rule for rule in self.rules if rule.rule_type == rule_type]
    
    def get_field_rules(self, field_name: str) -> List[ValidationRuleInfo]:
        """Get validation rules for a specific field."""
        return [rule for rule in self.rules if rule.target_field == field_name]


@dataclass
class AuditConfigInfo:
    """Information about audit configuration."""
    track_creates: bool = True
    track_updates: bool = True
    track_deletes: bool = True
    track_reads: bool = False
    store_old_values: bool = True
    store_new_values: bool = True
    capture_ip_address: bool = True
    capture_user_agent: bool = True
    async_logging: bool = True
    retention_days: int = 365
    batch_size: int = 100
    excluded_fields: List[str] = None
    
    def __post_init__(self):
        if self.excluded_fields is None:
            self.excluded_fields = ['password', 'token', 'secret']


@dataclass
class BusinessLogicInfo:
    """Comprehensive business logic information."""
    workflows: List[WorkflowInfo] = None
    calculations: List[CalculationInfo] = None
    events: List[EventInfo] = None
    validations: List[ValidationInfo] = None
    audit_config: Optional[AuditConfigInfo] = None
    
    def __post_init__(self):
        if self.workflows is None:
            self.workflows = []
        if self.calculations is None:
            self.calculations = []
        if self.events is None:
            self.events = []
        if self.validations is None:
            self.validations = []
        if self.audit_config is None:
            self.audit_config = AuditConfigInfo()
    
    def has_workflows(self) -> bool:
        """Check if business logic includes workflows."""
        return bool(self.workflows)
    
    def has_calculations(self) -> bool:
        """Check if business logic includes calculations."""
        return bool(self.calculations)
    
    def has_events(self) -> bool:
        """Check if business logic includes events."""
        return bool(self.events)
    
    def has_validations(self) -> bool:
        """Check if business logic includes validations."""
        return bool(self.validations)
    
    def requires_audit(self) -> bool:
        """Check if business logic requires audit capabilities."""
        return self.audit_config is not None
