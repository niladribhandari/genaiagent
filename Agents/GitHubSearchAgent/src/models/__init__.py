"""
Core data models for GitHub search agent system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum
import json


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SearchScope(Enum):
    REPOSITORIES = "repositories"
    CODE = "code"
    ISSUES = "issues"
    USERS = "users"
    COMMITS = "commits"


class AnalysisType(Enum):
    BASIC = "basic"
    DETAILED = "detailed"
    SECURITY = "security"
    TRENDS = "trends"
    DOCUMENTATION = "documentation"


@dataclass
class AgentGoal:
    """Represents a goal for an agent to achieve."""
    id: str
    description: str
    priority: Priority
    context: Dict[str, Any] = field(default_factory=dict)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None


@dataclass
class RepositoryInfo:
    """GitHub repository information."""
    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    language: Optional[str] = None
    languages: Dict[str, int] = field(default_factory=dict)
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    size: int = 0
    open_issues: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    topics: List[str] = field(default_factory=list)
    license: Optional[str] = None
    default_branch: str = "main"
    is_fork: bool = False
    is_archived: bool = False
    is_private: bool = False
    clone_url: str = ""
    html_url: str = ""
    api_url: str = ""


@dataclass
class CodeFile:
    """Represents a code file with analysis."""
    path: str
    content: str
    language: str
    size: int
    lines: int
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    quality_score: float = 0.0


@dataclass
class SecurityIssue:
    """Security vulnerability or issue."""
    severity: str
    type: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    recommendation: str = ""
    cve_ids: List[str] = field(default_factory=list)


@dataclass
class TrendAnalysis:
    """Technology trend analysis."""
    technology: str
    popularity_score: float
    growth_rate: float
    adoption_rate: float
    community_activity: float
    recent_projects: List[str] = field(default_factory=list)
    key_contributors: List[str] = field(default_factory=list)


@dataclass
class SearchQuery:
    """GitHub search query configuration."""
    query: str
    scope: SearchScope = SearchScope.REPOSITORIES
    language: Optional[str] = None
    min_stars: int = 0
    max_results: int = 100
    sort_by: str = "stars"
    order: str = "desc"
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Result of repository analysis."""
    repository: RepositoryInfo
    analysis_type: AnalysisType
    score: float
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    code_files: List[CodeFile] = field(default_factory=list)
    security_issues: List[SecurityIssue] = field(default_factory=list)
    trends: List[TrendAnalysis] = field(default_factory=list)
    documentation: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """GitHub search result with analysis."""
    query: SearchQuery
    repositories: List[RepositoryInfo] = field(default_factory=list)
    analyses: List[AnalysisResult] = field(default_factory=list)
    total_count: int = 0
    search_time: float = 0.0
    analysis_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    searched_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        """Convert to JSON string."""
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(self.__dict__, default=json_serializer, indent=2)


@dataclass
class AgentCapability:
    """Defines what an agent can do."""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    dependencies: List[str] = field(default_factory=list)
    cost_estimate: float = 0.0
    execution_time_estimate: float = 0.0


@dataclass
class AgentStatus:
    """Current status of an agent."""
    agent_id: str
    status: str  # idle, working, error, completed
    current_goal: Optional[AgentGoal] = None
    progress: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
