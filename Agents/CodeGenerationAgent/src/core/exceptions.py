"""Custom exceptions for the code generation system."""


class CodeGenerationError(Exception):
    """Base exception for code generation errors."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context or {}


class TemplateProcessingError(CodeGenerationError):
    """Exception raised when template processing fails."""
    pass


class ValidationError(CodeGenerationError):
    """Exception raised when validation fails."""
    pass


class ImportDetectionError(CodeGenerationError):
    """Exception raised when import detection fails."""
    pass


class ImportProcessingError(CodeGenerationError):
    """Exception raised when import processing fails."""
    pass


class CodeProcessingError(CodeGenerationError):
    """Exception raised when code processing fails."""
    pass


class FileSystemError(CodeGenerationError):
    """Exception raised for file system operations."""
    pass


class AIProviderError(CodeGenerationError):
    """Exception raised for AI provider issues."""
    pass


class ConfigurationError(CodeGenerationError):
    """Exception raised for configuration issues."""
    pass
