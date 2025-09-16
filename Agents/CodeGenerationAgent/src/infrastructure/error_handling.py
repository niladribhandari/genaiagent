"""
Phase 4.1: Production Infrastructure - Error Handling Revolution
================================================================

Critical improvement: Boost error handling coverage from 30.4% to 95%+
"""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, Union
from enum import Enum
import time

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels for production monitoring."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"

class ProductionError(Exception):
    """Base production error class with enhanced context."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.cause = cause
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to structured dictionary for logging."""
        return {
            "message": self.message,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "timestamp": self.timestamp,
            "traceback": traceback.format_exc() if self.cause else None
        }

class ValidationError(ProductionError):
    """Input validation errors."""
    
    def __init__(self, message: str, field: str = None, value: Any = None, **kwargs):
        context = kwargs.pop('context', {})
        if field:
            context['field'] = field
        if value is not None:
            context['value'] = str(value)[:100]  # Truncate for security
            
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            context=context,
            **kwargs
        )

class BusinessLogicError(ProductionError):
    """Business logic processing errors."""
    
    def __init__(self, message: str, operation: str = None, **kwargs):
        context = kwargs.pop('context', {})
        if operation:
            context['operation'] = operation
            
        super().__init__(
            message,
            error_code="BUSINESS_LOGIC_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=context,
            **kwargs
        )

class ExternalServiceError(ProductionError):
    """External service communication errors."""
    
    def __init__(self, message: str, service: str = None, status_code: int = None, **kwargs):
        context = kwargs.pop('context', {})
        if service:
            context['service'] = service
        if status_code:
            context['status_code'] = status_code
            
        super().__init__(
            message,
            error_code="EXTERNAL_SERVICE_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.EXTERNAL_SERVICE,
            context=context,
            **kwargs
        )

class ConfigurationError(ProductionError):
    """Configuration and setup errors."""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        context = kwargs.pop('context', {})
        if config_key:
            context['config_key'] = config_key
            
        super().__init__(
            message,
            error_code="CONFIGURATION_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CONFIGURATION,
            context=context,
            **kwargs
        )

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker pattern for external service resilience."""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.reset_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        else:  # HALF_OPEN
            return True
            
    def record_success(self):
        """Record successful operation."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        
    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

class ErrorHandler:
    """Production-grade error handler with comprehensive logging."""
    
    def __init__(self):
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "recent_errors": []
        }
        self.circuit_breakers = {}
        
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> ProductionError:
        """Handle any error and convert to ProductionError if needed."""
        
        # Convert to ProductionError if needed
        if isinstance(error, ProductionError):
            production_error = error
        else:
            production_error = ProductionError(
                message=str(error),
                error_code="UNHANDLED_ERROR",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.UNKNOWN,
                context=context,
                cause=error
            )
            
        # Update statistics
        self._update_stats(production_error)
        
        # Log error
        self._log_error(production_error)
        
        return production_error
        
    def _update_stats(self, error: ProductionError):
        """Update error statistics."""
        self.error_stats["total_errors"] += 1
        
        # Update category stats
        category = error.category.value
        self.error_stats["errors_by_category"][category] = \
            self.error_stats["errors_by_category"].get(category, 0) + 1
            
        # Update severity stats
        severity = error.severity.value
        self.error_stats["errors_by_severity"][severity] = \
            self.error_stats["errors_by_severity"].get(severity, 0) + 1
            
        # Keep recent errors (last 100)
        self.error_stats["recent_errors"].append(error.to_dict())
        if len(self.error_stats["recent_errors"]) > 100:
            self.error_stats["recent_errors"].pop(0)
            
    def _log_error(self, error: ProductionError):
        """Log error with appropriate level."""
        # Create clean context without reserved keys
        clean_context = {k: v for k, v in error.context.items() if k not in ['message', 'msg', 'args']}
        
        log_message = f"{error.error_code}: {error.message}"
        
        if error.severity == ErrorSeverity.LOW:
            logger.warning(f"🟡 {log_message}", extra={"error_context": clean_context, "error_code": error.error_code})
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.error(f"🟠 {log_message}", extra={"error_context": clean_context, "error_code": error.error_code})
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"🔴 {log_message}", extra={"error_context": clean_context, "error_code": error.error_code})
        else:  # CRITICAL
            logger.critical(f"💀 {log_message}", extra={"error_context": clean_context, "error_code": error.error_code})
            
    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker()
        return self.circuit_breakers[service]
        
    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return self.error_stats.copy()

# Global error handler instance
error_handler = ErrorHandler()

def with_error_handling(
    operation: str = None,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    reraise: bool = False
):
    """
    Decorator for comprehensive error handling.
    
    Args:
        operation: Name of the operation for context
        category: Error category for classification
        severity: Default error severity
        reraise: Whether to reraise the error after handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ProductionError:
                # Already a production error, just reraise
                if reraise:
                    raise
                else:
                    logger.error(f"Production error in {func.__name__}")
                    return None
            except Exception as e:
                # Convert to production error
                context = {
                    "function": func.__name__,
                    "operation": operation or func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
                
                production_error = error_handler.handle_error(e, context)
                
                if reraise:
                    raise production_error
                else:
                    logger.error(f"Handled error in {func.__name__}: {production_error.message}")
                    return None
                    
        return wrapper
    return decorator

def with_circuit_breaker(service: str, fallback_value: Any = None):
    """
    Decorator for circuit breaker pattern.
    
    Args:
        service: Service name for circuit breaker
        fallback_value: Value to return when circuit is open
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            circuit_breaker = error_handler.get_circuit_breaker(service)
            
            if not circuit_breaker.can_execute():
                logger.warning(f"Circuit breaker OPEN for {service}, returning fallback")
                return fallback_value
                
            try:
                result = func(*args, **kwargs)
                circuit_breaker.record_success()
                return result
            except Exception as e:
                circuit_breaker.record_failure()
                logger.error(f"Circuit breaker recorded failure for {service}: {e}")
                
                if circuit_breaker.state == CircuitBreakerState.OPEN:
                    logger.warning(f"Circuit breaker OPENED for {service}")
                    
                raise
                
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default_value: Any = None, **kwargs) -> Any:
    """
    Safely execute a function with comprehensive error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_value: Value to return on error
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_value on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = {
            "function": func.__name__,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys())
        }
        
        error_handler.handle_error(e, context)
        logger.warning(f"safe_execute: returning default value for {func.__name__}")
        return default_value

def validate_input(value: Any, validator: Callable, field_name: str = "input") -> Any:
    """
    Validate input with comprehensive error handling.
    
    Args:
        value: Value to validate
        validator: Validation function
        field_name: Field name for error context
        
    Returns:
        Validated value
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        if not validator(value):
            raise ValidationError(
                f"Validation failed for {field_name}",
                field=field_name,
                value=value
            )
        return value
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            f"Validation error for {field_name}: {str(e)}",
            field=field_name,
            value=value,
            cause=e
        )

# Export key components
__all__ = [
    'ProductionError',
    'ValidationError', 
    'BusinessLogicError',
    'ExternalServiceError',
    'ConfigurationError',
    'ErrorSeverity',
    'ErrorCategory',
    'CircuitBreaker',
    'ErrorHandler',
    'error_handler',
    'with_error_handling',
    'with_circuit_breaker',
    'safe_execute',
    'validate_input'
]
