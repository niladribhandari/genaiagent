"""Core interfaces for the code generation system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class GeneratedCode:
    """Represents generated code with metadata."""
    content: str
    file_path: str
    file_type: str
    imports: List[str]
    metadata: Dict[str, Any]


@dataclass  
class GenerationContext:
    """Context for code generation operations."""
    file_type: str
    entity_name: str
    package_name: str
    language: str
    framework: str
    template_content: str
    spec_data: Dict[str, Any]
    instruction_data: Dict[str, Any]
    output_path: str
    endpoints: Optional[List[Dict[str, Any]]] = None
    business_rules: Optional[List[Dict[str, Any]]] = None


class CodeGenerator(ABC):
    """Abstract interface for code generators."""
    
    @abstractmethod
    def generate(self, context: GenerationContext) -> GeneratedCode:
        """Generate code based on the provided context."""
        pass
    
    @abstractmethod
    def supports_file_type(self, file_type: str) -> bool:
        """Check if this generator supports the given file type."""
        pass


class TemplateProcessor(ABC):
    """Abstract interface for template processors."""
    
    @abstractmethod
    def process(self, template: str, variables: Dict[str, Any]) -> str:
        """Process template with provided variables."""
        pass
    
    @abstractmethod
    def supports_framework(self, framework: str) -> bool:
        """Check if this processor supports the given framework."""
        pass


class ImportDetector(ABC):
    """Abstract interface for import detection."""
    
    @abstractmethod
    def detect_imports(self, code: str, file_type: str) -> List[str]:
        """Detect required imports for the given code."""
        pass
    
    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """Check if this detector supports the given language."""
        pass


class CodeEnhancer(ABC):
    """Abstract interface for code enhancement."""
    
    @abstractmethod
    def enhance(self, code: str, context: GenerationContext) -> str:
        """Enhance code with additional features."""
        pass
    
    @abstractmethod
    def get_enhancement_type(self) -> str:
        """Get the type of enhancement this enhancer provides."""
        pass


class FileSystemProvider(ABC):
    """Abstract interface for file system operations."""
    
    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """Read file content."""
        pass
    
    @abstractmethod
    def write_file(self, file_path: str, content: str) -> None:
        """Write content to file."""
        pass
    
    @abstractmethod
    def create_directories(self, dir_path: str) -> None:
        """Create directory structure."""
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        pass


class AIProvider(ABC):
    """Abstract interface for AI services."""
    
    @abstractmethod
    def generate_code(self, prompt: str, context: GenerationContext) -> str:
        """Generate code using AI."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if AI provider is available."""
        pass
