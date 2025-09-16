"""
Data models for the code review agent.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class Severity(Enum):
    """Severity levels for review issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(Enum):
    """Categories of code review issues."""
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    BEST_PRACTICES = "best_practices"


@dataclass
class CodeIssue:
    """Represents a single code review issue."""
    file_path: str
    line_number: int
    column: Optional[int] = None
    severity: Severity = Severity.MEDIUM
    category: IssueCategory = IssueCategory.CODE_QUALITY
    title: str = ""
    description: str = ""
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "rule_id": self.rule_id,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet
        }


@dataclass
class FileMetrics:
    """Metrics for a single file."""
    file_path: str
    language: str
    lines_of_code: int = 0
    lines_of_comments: int = 0
    complexity_score: float = 0.0
    maintainability_index: float = 0.0
    test_coverage: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "lines_of_code": self.lines_of_code,
            "lines_of_comments": self.lines_of_comments,
            "complexity_score": self.complexity_score,
            "maintainability_index": self.maintainability_index,
            "test_coverage": self.test_coverage
        }


@dataclass
class ReviewResult:
    """Results of reviewing a single file."""
    file_path: str
    language: str
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: Optional[FileMetrics] = None
    review_notes: List[str] = field(default_factory=list)
    
    def add_issue(self, issue: CodeIssue) -> None:
        """Add an issue to this review result."""
        self.issues.append(issue)
    
    def has_critical_issues(self) -> bool:
        """Check if this file has any critical issues."""
        return any(issue.severity == Severity.CRITICAL for issue in self.issues)
    
    def get_issues_by_severity(self, severity: Severity) -> List[CodeIssue]:
        """Get all issues of a specific severity."""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_category(self, category: IssueCategory) -> List[CodeIssue]:
        """Get all issues of a specific category."""
        return [issue for issue in self.issues if issue.category == category]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "timestamp": self.timestamp.isoformat(),
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "review_notes": self.review_notes,
            "summary": {
                "total_issues": len(self.issues),
                "critical_issues": len(self.get_issues_by_severity(Severity.CRITICAL)),
                "high_issues": len(self.get_issues_by_severity(Severity.HIGH)),
                "medium_issues": len(self.get_issues_by_severity(Severity.MEDIUM)),
                "low_issues": len(self.get_issues_by_severity(Severity.LOW))
            }
        }


@dataclass
class ReviewSummary:
    """Overall summary of the code review."""
    total_files_reviewed: int = 0
    total_issues_found: int = 0
    issues_by_severity: Dict[Severity, int] = field(default_factory=dict)
    issues_by_category: Dict[IssueCategory, int] = field(default_factory=dict)
    languages_analyzed: List[str] = field(default_factory=list)
    review_duration: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    review_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_files_reviewed": self.total_files_reviewed,
            "total_issues_found": self.total_issues_found,
            "issues_by_severity": {k.value: v for k, v in self.issues_by_severity.items()},
            "issues_by_category": {k.value: v for k, v in self.issues_by_category.items()},
            "languages_analyzed": self.languages_analyzed,
            "review_duration": self.review_duration,
            "timestamp": self.timestamp.isoformat(),
            "review_context": self.review_context
        }
