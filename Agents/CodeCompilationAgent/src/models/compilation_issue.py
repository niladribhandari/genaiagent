"""
Enhanced Compilation Issue Models
Standardized format for compilation issues with OpenAI integration
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json
from datetime import datetime


class IssueSeverity(Enum):
    """Standardized issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class IssueCategory(Enum):
    """Issue categorization for better grouping and handling."""
    SYNTAX = "syntax"
    TYPE = "type"
    IMPORT = "import"
    DEPENDENCY = "dependency"
    COMPILATION = "compilation"
    RUNTIME = "runtime"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_STYLE = "code_style"
    UNKNOWN = "unknown"


@dataclass
class IssueLocation:
    """Represents the location of an issue in source code."""
    file_path: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    end_line_number: Optional[int] = None
    end_column_number: Optional[int] = None
    
    def __str__(self) -> str:
        """Human-readable location string."""
        location = self.file_path
        if self.line_number:
            location += f":{self.line_number}"
            if self.column_number:
                location += f":{self.column_number}"
        return location
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "end_line_number": self.end_line_number,
            "end_column_number": self.end_column_number
        }


@dataclass
class IssueSuggestion:
    """AI-generated suggestion for fixing an issue."""
    description: str
    fix_type: str  # "quick_fix", "refactor", "manual"
    confidence: float  # 0.0 to 1.0
    code_snippet: Optional[str] = None
    explanation: Optional[str] = None
    related_links: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "description": self.description,
            "fix_type": self.fix_type,
            "confidence": self.confidence,
            "code_snippet": self.code_snippet,
            "explanation": self.explanation,
            "related_links": self.related_links
        }


@dataclass
class CompilationIssue:
    """
    Enhanced compilation issue with standardized format.
    
    This model serves as the universal format for compilation issues
    across all agents and UI components.
    """
    
    # Core issue information
    id: str  # Unique identifier for the issue
    severity: IssueSeverity
    message: str
    location: IssueLocation
    
    # Classification and metadata
    category: IssueCategory = IssueCategory.UNKNOWN
    error_code: Optional[str] = None
    tool: Optional[str] = None  # "maven", "gradle", "javac", etc.
    
    # AI-enhanced information
    ai_processed: bool = False
    ai_suggestions: List[IssueSuggestion] = field(default_factory=list)
    ai_summary: Optional[str] = None
    
    # Context and debugging
    context_lines: List[str] = field(default_factory=list)
    stack_trace: Optional[str] = None
    related_issues: List[str] = field(default_factory=list)  # IDs of related issues
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "compilation"  # "compilation", "linting", "testing", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.severity, str):
            self.severity = IssueSeverity(self.severity)
        if isinstance(self.category, str):
            self.category = IssueCategory(self.category)
    
    def get_display_severity(self) -> str:
        """Get human-readable severity with emoji."""
        severity_map = {
            IssueSeverity.ERROR: "🔴 Error",
            IssueSeverity.WARNING: "🟡 Warning",
            IssueSeverity.INFO: "🔵 Info",
            IssueSeverity.HINT: "💡 Hint"
        }
        return severity_map.get(self.severity, "❓ Unknown")
    
    def get_short_location(self) -> str:
        """Get shortened file path for display."""
        parts = self.location.file_path.split('/')
        if len(parts) > 3:
            return f".../{'/'.join(parts[-2:])}"
        return self.location.file_path
    
    def has_ai_suggestions(self) -> bool:
        """Check if AI suggestions are available."""
        return self.ai_processed and len(self.ai_suggestions) > 0
    
    def get_best_suggestion(self) -> Optional[IssueSuggestion]:
        """Get the highest confidence AI suggestion."""
        if not self.ai_suggestions:
            return None
        return max(self.ai_suggestions, key=lambda s: s.confidence)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "severity": self.severity.value,
            "message": self.message,
            "location": self.location.to_dict(),
            "category": self.category.value,
            "error_code": self.error_code,
            "tool": self.tool,
            "ai_processed": self.ai_processed,
            "ai_suggestions": [s.to_dict() for s in self.ai_suggestions],
            "ai_summary": self.ai_summary,
            "context_lines": self.context_lines,
            "stack_trace": self.stack_trace,
            "related_issues": self.related_issues,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompilationIssue':
        """Create instance from dictionary."""
        location_data = data.get("location", {})
        location = IssueLocation(**location_data)
        
        suggestions_data = data.get("ai_suggestions", [])
        suggestions = [IssueSuggestion(**s) for s in suggestions_data]
        
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
        
        return cls(
            id=data.get("id", ""),
            severity=IssueSeverity(data.get("severity", "error")),
            message=data.get("message", ""),
            location=location,
            category=IssueCategory(data.get("category", "unknown")),
            error_code=data.get("error_code"),
            tool=data.get("tool"),
            ai_processed=data.get("ai_processed", False),
            ai_suggestions=suggestions,
            ai_summary=data.get("ai_summary"),
            context_lines=data.get("context_lines", []),
            stack_trace=data.get("stack_trace"),
            related_issues=data.get("related_issues", []),
            timestamp=timestamp,
            source=data.get("source", "compilation"),
            metadata=data.get("metadata", {})
        )
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CompilationIssue':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class CompilationIssuesSummary:
    """Summary of compilation issues for display and processing."""
    
    total_issues: int
    errors: int
    warnings: int
    infos: int
    hints: int
    
    files_with_issues: int
    most_common_category: Optional[IssueCategory] = None
    ai_suggestions_available: int = 0
    
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    issues_by_category: Dict[str, int] = field(default_factory=dict)
    issues_by_file: Dict[str, int] = field(default_factory=dict)
    
    @classmethod
    def from_issues(cls, issues: List[CompilationIssue]) -> 'CompilationIssuesSummary':
        """Create summary from list of issues."""
        total_issues = len(issues)
        
        # Count by severity
        errors = sum(1 for i in issues if i.severity == IssueSeverity.ERROR)
        warnings = sum(1 for i in issues if i.severity == IssueSeverity.WARNING)
        infos = sum(1 for i in issues if i.severity == IssueSeverity.INFO)
        hints = sum(1 for i in issues if i.severity == IssueSeverity.HINT)
        
        # Count AI suggestions
        ai_suggestions_available = sum(1 for i in issues if i.has_ai_suggestions())
        
        # Count by category
        issues_by_category = {}
        for issue in issues:
            category = issue.category.value
            issues_by_category[category] = issues_by_category.get(category, 0) + 1
        
        # Count by severity
        issues_by_severity = {}
        for issue in issues:
            severity = issue.severity.value
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
        
        # Count by file
        issues_by_file = {}
        for issue in issues:
            file_path = issue.location.file_path
            issues_by_file[file_path] = issues_by_file.get(file_path, 0) + 1
        
        files_with_issues = len(issues_by_file)
        
        # Find most common category
        most_common_category = None
        if issues_by_category:
            most_common_cat_str = max(issues_by_category, key=issues_by_category.get)
            most_common_category = IssueCategory(most_common_cat_str)
        
        return cls(
            total_issues=total_issues,
            errors=errors,
            warnings=warnings,
            infos=infos,
            hints=hints,
            files_with_issues=files_with_issues,
            most_common_category=most_common_category,
            ai_suggestions_available=ai_suggestions_available,
            issues_by_severity=issues_by_severity,
            issues_by_category=issues_by_category,
            issues_by_file=issues_by_file
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_issues": self.total_issues,
            "errors": self.errors,
            "warnings": self.warnings,
            "infos": self.infos,
            "hints": self.hints,
            "files_with_issues": self.files_with_issues,
            "most_common_category": self.most_common_category.value if self.most_common_category else None,
            "ai_suggestions_available": self.ai_suggestions_available,
            "issues_by_severity": self.issues_by_severity,
            "issues_by_category": self.issues_by_category,
            "issues_by_file": self.issues_by_file
        }


# Legacy compatibility functions
def convert_legacy_issue(legacy_issue) -> CompilationIssue:
    """Convert legacy CompilationIssue to new format."""
    import uuid
    
    # Create location
    location = IssueLocation(
        file_path=getattr(legacy_issue, 'file_path', ''),
        line_number=getattr(legacy_issue, 'line_number', None),
        column_number=getattr(legacy_issue, 'column_number', None)
    )
    
    # Map severity
    severity_str = getattr(legacy_issue, 'severity', 'error')
    try:
        severity = IssueSeverity(severity_str)
    except ValueError:
        severity = IssueSeverity.ERROR
    
    # Create new issue
    return CompilationIssue(
        id=str(uuid.uuid4()),
        severity=severity,
        message=getattr(legacy_issue, 'message', ''),
        location=location,
        error_code=getattr(legacy_issue, 'error_code', None),
        metadata={
            "suggestion": getattr(legacy_issue, 'suggestion', None),
            "legacy_converted": True
        }
    )
