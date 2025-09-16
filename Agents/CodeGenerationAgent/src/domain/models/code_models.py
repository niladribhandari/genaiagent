"""Code-related domain models."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class CodeQualityLevel(Enum):
    """Code quality levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"


@dataclass
class ImportInfo:
    """Information about code imports."""
    import_statement: str
    import_type: str  # 'standard', 'framework', 'custom'
    is_wildcard: bool = False
    source_package: Optional[str] = None


@dataclass
class FieldInfo:
    """Information about entity fields."""
    name: str
    field_type: str
    is_required: bool = False
    default_value: Optional[str] = None
    validation_rules: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class GeneratedCode:
    """Represents generated code with metadata."""
    content: str
    file_path: str
    file_type: str
    imports: List[ImportInfo] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    
    def add_import(self, import_statement: str, import_type: str = 'custom'):
        """Add an import to the code."""
        import_info = ImportInfo(
            import_statement=import_statement,
            import_type=import_type,
            is_wildcard='*' in import_statement
        )
        if import_info not in self.imports:
            self.imports.append(import_info)


@dataclass
class CodeQuality:
    """Code quality metrics."""
    has_package: bool = False
    has_imports: bool = False
    has_class_definition: bool = False
    has_proper_formatting: bool = False
    has_documentation: bool = False
    has_logging: bool = False
    lines_of_code: int = 0
    complexity_score: float = 0.0
    
    @property
    def overall_score(self) -> float:
        """Calculate overall quality score."""
        checks = [
            self.has_package,
            self.has_imports, 
            self.has_class_definition,
            self.has_proper_formatting,
            self.has_documentation,
            self.has_logging
        ]
        return sum(checks) / len(checks)
    
    @property
    def quality_level(self) -> CodeQualityLevel:
        """Get quality level based on score."""
        score = self.overall_score
        if score >= 0.9:
            return CodeQualityLevel.EXCELLENT
        elif score >= 0.7:
            return CodeQualityLevel.HIGH
        elif score >= 0.5:
            return CodeQualityLevel.MEDIUM
        else:
            return CodeQualityLevel.LOW
