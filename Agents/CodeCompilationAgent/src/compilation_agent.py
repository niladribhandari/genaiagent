"""
Enhanced Code Compilation Agent - Multi-language compilation system
Supports Java Spring Boot, .NET API, Python API, and Node.js API compilation
Enhanced with OpenAI-powered issue analysis and standardized issue format
"""

import os
import subprocess
import json
import re
import uuid
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Import enhanced models
from .models.compilation_issue import (
    CompilationIssue, IssueLocation, IssueSeverity, IssueCategory,
    CompilationIssuesSummary, convert_legacy_issue
)
from .processors.openai_processor import CompilationIssueProcessor, OpenAIConfig


class CompilationStatus(Enum):
    """Compilation status enumeration."""
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"


class ProjectType(Enum):
    """Supported project types."""
    JAVA_SPRINGBOOT = "java_springboot"
    DOTNET_API = "dotnet_api"
    PYTHON_API = "python_api"
    NODEJS_API = "nodejs_api"


@dataclass
class CompilationResult:
    """Enhanced compilation results with standardized issue format."""
    status: CompilationStatus
    project_type: ProjectType
    project_path: str
    compilation_time: float
    issues: List[CompilationIssue] = field(default_factory=list)
    output_path: str = ""
    build_logs: str = ""
    dependencies_status: Dict[str, str] = field(default_factory=dict)
    test_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced properties
    issues_summary: Optional[CompilationIssuesSummary] = None
    ai_summary: Optional[str] = None
    openai_processed: bool = False
    
    def get_errors(self) -> List[CompilationIssue]:
        """Get all error issues."""
        return [issue for issue in self.issues if issue.severity == IssueSeverity.ERROR]
    
    def get_warnings(self) -> List[CompilationIssue]:
        """Get all warning issues."""
        return [issue for issue in self.issues if issue.severity == IssueSeverity.WARNING]
    
    def has_errors(self) -> bool:
        """Check if compilation has errors."""
        return len(self.get_errors()) > 0
    
    def get_issues_by_file(self) -> Dict[str, List[CompilationIssue]]:
        """Group issues by file path."""
        issues_by_file = {}
        for issue in self.issues:
            file_path = issue.location.file_path
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        return issues_by_file
    
    def update_summary(self) -> None:
        """Update the issues summary."""
        self.issues_summary = CompilationIssuesSummary.from_issues(self.issues)
    
    def summary(self) -> Dict[str, Any]:
        """Get compilation summary."""
        if not self.issues_summary:
            self.update_summary()
            
        base_summary = {
            "status": self.status.value,
            "project_type": self.project_type.value,
            "compilation_time": self.compilation_time,
            "build_successful": self.status == CompilationStatus.SUCCESS,
            "openai_processed": self.openai_processed
        }
        
        if self.issues_summary:
            base_summary.update(self.issues_summary.to_dict())
        
        if self.ai_summary:
            base_summary["ai_summary"] = self.ai_summary
            
        return base_summary
    
    def to_simplified_format(self) -> Dict[str, Any]:
        """
        Convert to simplified format for UI and agent consumption.
        This is the main format that will be used across all components.
        """
        self.update_summary()
        
        return {
            "compilation_status": self.status.value,
            "project_info": {
                "path": self.project_path,
                "type": self.project_type.value,
                "build_tool": self.metadata.get("build_tool", "unknown"),
                "compilation_time": self.compilation_time
            },
            "summary": self.issues_summary.to_dict() if self.issues_summary else {},
            "ai_analysis": {
                "processed": self.openai_processed,
                "summary": self.ai_summary,
                "suggestions_available": sum(1 for issue in self.issues if issue.has_ai_suggestions())
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "issues_by_file": {
                file_path: [issue.to_dict() for issue in file_issues]
                for file_path, file_issues in self.get_issues_by_file().items()
            },
            "metadata": self.metadata,
            "timestamp": datetime.now().isoformat()
        }


class CodeCompilationAgent:
    """
    Enhanced multi-language code compilation agent with OpenAI integration.
    
    Supports compilation of:
    - Java Spring Boot applications
    - .NET API projects
    - Python API applications
    - Node.js API applications
    
    Features:
    - Standardized issue format
    - OpenAI-powered issue analysis
    - Intelligent categorization
    - Fix suggestions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the enhanced compilation agent."""
        self.config = config or {}
        self.default_timeout = self.config.get("timeout", 300)  # 5 minutes default
        self.verbose = self.config.get("verbose", False)
        self.cleanup_artifacts = self.config.get("cleanup_artifacts", False)
        self.enable_openai = self.config.get("enable_openai", True)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI processor if enabled
        self.openai_processor = None
        if self.enable_openai:
            try:
                openai_api_key = self.config.get("openai_api_key") or os.getenv('OPENAI_API_KEY')
                if openai_api_key:
                    openai_config = OpenAIConfig(
                        api_key=openai_api_key,
                        model=self.config.get("openai_model", "gpt-4"),
                        max_tokens=self.config.get("openai_max_tokens", 2000),
                        temperature=self.config.get("openai_temperature", 0.3)
                    )
                    self.openai_processor = CompilationIssueProcessor(openai_config)
                    self.logger.info("OpenAI processor initialized successfully")
                else:
                    self.logger.warning("OpenAI API key not found. AI features will be disabled.")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI processor: {e}")
        
        # Tool paths (can be overridden in config)
        self.tool_paths = {
            "maven": self.config.get("maven_path", "mvn"),
            "gradle": self.config.get("gradle_path", "gradle"),
            "dotnet": self.config.get("dotnet_path", "dotnet"),
            "python": self.config.get("python_path", "python3"),
            "pip": self.config.get("pip_path", "pip3"),
            "npm": self.config.get("npm_path", "npm"),
            "node": self.config.get("node_path", "node")
        }
        
        # Compilation strategies for each project type
        self.compilation_strategies = {
            ProjectType.JAVA_SPRINGBOOT: self._compile_java_springboot,
            ProjectType.DOTNET_API: self._compile_dotnet_api,
            ProjectType.PYTHON_API: self._compile_python_api,
            ProjectType.NODEJS_API: self._compile_nodejs_api
        }
    
    async def compile_project(self, 
                       project_path: str, 
                       project_type: Optional[ProjectType] = None,
                       build_options: Optional[Dict[str, Any]] = None) -> CompilationResult:
        """
        Enhanced compile project with OpenAI analysis.
        
        Args:
            project_path: Path to the project directory
            project_type: Type of project (auto-detected if not provided)
            build_options: Additional build options
            
        Returns:
            Enhanced CompilationResult with OpenAI analysis
        """
        start_time = datetime.now()
        project_path = Path(project_path).resolve()
        
        if not project_path.exists():
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=project_type or ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,
                issues=[self._create_error_issue(
                    f"Project path does not exist: {project_path}",
                    str(project_path)
                )]
            )
        
        # Auto-detect project type if not provided
        if project_type is None:
            project_type = self._detect_project_type(project_path)
        
        if self.verbose:
            print(f"🔨 Compiling {project_type.value} project at: {project_path}")
        
        try:
            # Get compilation strategy
            compile_func = self.compilation_strategies.get(project_type)
            if not compile_func:
                return CompilationResult(
                    status=CompilationStatus.FAILED,
                    project_type=project_type,
                    project_path=str(project_path),
                    compilation_time=0.0,
                    issues=[self._create_error_issue(
                        f"Unsupported project type: {project_type.value}",
                        str(project_path)
                    )]
                )
            
            # Execute compilation
            result = compile_func(project_path, build_options or {})
            
            # Calculate compilation time
            end_time = datetime.now()
            result.compilation_time = (end_time - start_time).total_seconds()
            
            # Enhance with OpenAI analysis if enabled
            if self.openai_processor and result.issues:
                try:
                    project_context = {
                        "project_type": project_type.value,
                        "build_tool": result.metadata.get("build_tool", "unknown"),
                        "project_path": str(project_path)
                    }
                    
                    # Process issues with OpenAI
                    enhanced_issues = await self.openai_processor.process_issues(
                        result.issues, project_context
                    )
                    result.issues = enhanced_issues
                    
                    # Generate AI summary
                    result.ai_summary = await self.openai_processor.generate_issue_summary(
                        result.issues
                    )
                    result.openai_processed = True
                    
                    if self.verbose:
                        print(f"🤖 Enhanced {len(result.issues)} issues with OpenAI analysis")
                        
                except Exception as e:
                    self.logger.warning(f"OpenAI enhancement failed: {e}")
            
            # Update summary
            result.update_summary()
            
            if self.verbose:
                status_emoji = "✅" if result.status == CompilationStatus.SUCCESS else "❌"
                print(f"{status_emoji} Compilation completed in {result.compilation_time:.2f}s")
                if result.issues_summary:
                    summary = result.issues_summary
                    print(f"   Issues: {summary.total_issues} ({summary.errors} errors, {summary.warnings} warnings)")
                    if result.openai_processed:
                        print(f"   AI Suggestions: {summary.ai_suggestions_available}")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            compilation_time = (end_time - start_time).total_seconds()
            
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=project_type,
                project_path=str(project_path),
                compilation_time=compilation_time,
                issues=[self._create_error_issue(
                    f"Compilation failed with exception: {str(e)}",
                    str(project_path)
                )]
            )
    
    def _create_error_issue(self, message: str, file_path: str, 
                           line_number: Optional[int] = None,
                           column_number: Optional[int] = None,
                           error_code: Optional[str] = None) -> CompilationIssue:
        """Create a standardized error issue."""
        location = IssueLocation(
            file_path=file_path,
            line_number=line_number,
            column_number=column_number
        )
        
        return CompilationIssue(
            id=str(uuid.uuid4()),
            severity=IssueSeverity.ERROR,
            message=message,
            location=location,
            category=IssueCategory.COMPILATION,
            error_code=error_code,
            tool="compilation_agent"
        )
    
    def _detect_project_type(self, project_path: Path) -> ProjectType:
        """Auto-detect project type based on files in the directory."""
        # Check for Java Spring Boot
        if (project_path / "pom.xml").exists() or (project_path / "build.gradle").exists():
            # Check for Spring Boot specific files
            if self._has_spring_boot_indicators(project_path):
                return ProjectType.JAVA_SPRINGBOOT
        
        # Check for .NET API
        if any(project_path.glob("*.csproj")) or any(project_path.glob("*.sln")):
            return ProjectType.DOTNET_API
        
        # Check for Python API
        if ((project_path / "requirements.txt").exists() or 
            (project_path / "setup.py").exists() or 
            (project_path / "pyproject.toml").exists()):
            return ProjectType.PYTHON_API
        
        # Check for Node.js API
        if (project_path / "package.json").exists():
            return ProjectType.NODEJS_API
        
        # Default to Java Spring Boot
        return ProjectType.JAVA_SPRINGBOOT
    
    def _has_spring_boot_indicators(self, project_path: Path) -> bool:
        """Check if project has Spring Boot indicators."""
        # Check pom.xml for Spring Boot
        pom_file = project_path / "pom.xml"
        if pom_file.exists():
            try:
                pom_content = pom_file.read_text()
                if "spring-boot" in pom_content.lower():
                    return True
            except:
                pass
        
        # Check build.gradle for Spring Boot
        gradle_file = project_path / "build.gradle"
        if gradle_file.exists():
            try:
                gradle_content = gradle_file.read_text()
                if "spring-boot" in gradle_content.lower():
                    return True
            except:
                pass
        
        # Check for Spring Boot application class
        src_dirs = [
            project_path / "src" / "main" / "java",
            project_path / "src" / "main" / "kotlin"
        ]
        
        for src_dir in src_dirs:
            if src_dir.exists():
                for java_file in src_dir.rglob("*.java"):
                    try:
                        content = java_file.read_text()
                        if "@SpringBootApplication" in content:
                            return True
                    except:
                        pass
        
        return False
    
    def _compile_java_springboot(self, project_path: Path, build_options: Dict[str, Any]) -> CompilationResult:
        """Compile Java Spring Boot project."""
        issues = []
        build_logs = ""
        dependencies_status = {}
        
        # Determine build tool (Maven or Gradle)
        if (project_path / "pom.xml").exists():
            return self._compile_maven_project(project_path, build_options)
        elif (project_path / "build.gradle").exists():
            return self._compile_gradle_project(project_path, build_options)
        else:
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,
                issues=[self._create_error_issue(
                    "No pom.xml or build.gradle found. Not a valid Maven or Gradle project.",
                    str(project_path)
                )]
            )
    
    def _compile_maven_project(self, project_path: Path, build_options: Dict[str, Any]) -> CompilationResult:
        """Compile Maven-based Java project."""
        issues = []
        build_logs = ""
        
        # Check if Maven is available
        if not self._check_tool_availability("maven"):
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,
                issues=[self._create_error_issue(
                    "Maven (mvn) is not available in PATH",
                    str(project_path)
                )]
            )
        
        # Prepare Maven command
        maven_goals = build_options.get("goals", ["clean", "compile"])
        maven_args = build_options.get("args", [])
        skip_tests = build_options.get("skip_tests", False)
        
        cmd = [self.tool_paths["maven"]] + maven_goals
        
        if skip_tests:
            cmd.extend(["-DskipTests"])
        
        cmd.extend(maven_args)
        
        if self.verbose:
            print(f"📦 Running Maven command: {' '.join(cmd)}")
        
        try:
            # Run Maven compilation
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=self.default_timeout
            )
            
            build_logs = result.stdout + result.stderr
            
            # Parse Maven output for issues
            issues.extend(self._parse_maven_output(result.stdout + result.stderr, project_path))
            
            # Determine compilation status
            if result.returncode == 0:
                status = CompilationStatus.SUCCESS
                output_path = str(project_path / "target")
            else:
                status = CompilationStatus.FAILED
                output_path = ""
                
                # Add general compilation failure if no specific issues found
                if not issues:
                    issues.append(self._create_error_issue(
                        "Maven compilation failed with no specific error details",
                        str(project_path)
                    ))
            
            return CompilationResult(
                status=status,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,  # Will be set by caller
                issues=issues,
                output_path=output_path,
                build_logs=build_logs,
                metadata={
                    "build_tool": "maven",
                    "goals": maven_goals,
                    "return_code": result.returncode
                }
            )
            
        except subprocess.TimeoutExpired:
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,
                issues=[self._create_error_issue(
                    f"Maven compilation timed out after {self.default_timeout} seconds",
                    str(project_path)
                )]
            )
        except Exception as e:
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,
                issues=[self._create_error_issue(
                    f"Maven compilation failed: {str(e)}",
                    str(project_path)
                )]
            )
    
    def _compile_gradle_project(self, project_path: Path, build_options: Dict[str, Any]) -> CompilationResult:
        """Compile Gradle-based Java project."""
        issues = []
        build_logs = ""
        
        # Check if Gradle is available
        gradle_wrapper = project_path / "gradlew"
        if gradle_wrapper.exists():
            gradle_cmd = str(gradle_wrapper)
        elif self._check_tool_availability("gradle"):
            gradle_cmd = self.tool_paths["gradle"]
        else:
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,
                issues=[self._create_error_issue(
                    "Gradle is not available (no gradlew wrapper or gradle in PATH)",
                    str(project_path)
                )]
            )
        
        # Prepare Gradle command
        gradle_tasks = build_options.get("tasks", ["clean", "build"])
        gradle_args = build_options.get("args", [])
        skip_tests = build_options.get("skip_tests", False)
        
        cmd = [gradle_cmd] + gradle_tasks
        
        if skip_tests:
            cmd.extend(["-x", "test"])
        
        cmd.extend(gradle_args)
        
        if self.verbose:
            print(f"🐘 Running Gradle command: {' '.join(cmd)}")
        
        try:
            # Run Gradle compilation
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=self.default_timeout
            )
            
            build_logs = result.stdout + result.stderr
            
            # Parse Gradle output for issues
            issues.extend(self._parse_gradle_output(result.stdout + result.stderr, project_path))
            
            # Determine compilation status
            if result.returncode == 0:
                status = CompilationStatus.SUCCESS
                output_path = str(project_path / "build")
            else:
                status = CompilationStatus.FAILED
                output_path = ""
                
                # Add general compilation failure if no specific issues found
                if not issues:
                    issues.append(self._create_error_issue(
                        "Gradle compilation failed with no specific error details",
                        str(project_path)
                    ))
            
            return CompilationResult(
                status=status,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,  # Will be set by caller
                issues=issues,
                output_path=output_path,
                build_logs=build_logs,
                metadata={
                    "build_tool": "gradle",
                    "tasks": gradle_tasks,
                    "return_code": result.returncode
                }
            )
            
        except subprocess.TimeoutExpired:
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,
                issues=[self._create_error_issue(
                    f"Gradle compilation timed out after {self.default_timeout} seconds",
                    str(project_path)
                )]
            )
        except Exception as e:
            return CompilationResult(
                status=CompilationStatus.FAILED,
                project_type=ProjectType.JAVA_SPRINGBOOT,
                project_path=str(project_path),
                compilation_time=0.0,
                issues=[self._create_error_issue(
                    f"Gradle compilation failed: {str(e)}",
                    str(project_path)
                )]
            )
    
    def _parse_maven_output(self, output: str, project_path: Path) -> List[CompilationIssue]:
        """Parse Maven output for compilation issues using enhanced format."""
        issues = []
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Enhanced Maven error pattern matching
            # Pattern 1: [ERROR] /path/to/file.java:[line,col] message
            error_match = re.search(r'\[ERROR\]\s*([^:]+\.java):\[(\d+),(\d+)\]\s*(.+)', line)
            if error_match:
                file_path = error_match.group(1)
                line_number = int(error_match.group(2))
                column_number = int(error_match.group(3))
                message = error_match.group(4).strip()
                
                # Get context lines
                context_lines = self._extract_context_lines(lines, i)
                
                issue = self._create_compilation_issue(
                    severity=IssueSeverity.ERROR,
                    message=message,
                    file_path=file_path,
                    line_number=line_number,
                    column_number=column_number,
                    tool="maven",
                    context_lines=context_lines
                )
                issues.append(issue)
                continue
            
            # Pattern 2: General [ERROR] messages
            error_match = re.search(r'\[ERROR\]\s*(.+)', line)
            if error_match:
                error_msg = error_match.group(1).strip()
                
                # Skip compilation summary messages
                if any(skip_phrase in error_msg.lower() for skip_phrase in [
                    "compilation failure", "failed to execute goal", 
                    "compilation error", "build failure"
                ]):
                    continue
                
                # Try to extract file and line information from message
                file_line_match = re.search(r'([^:]+\.java):(\d+)', error_msg)
                if file_line_match:
                    file_path = file_line_match.group(1)
                    line_number = int(file_line_match.group(2))
                    
                    issue = self._create_compilation_issue(
                        severity=IssueSeverity.ERROR,
                        message=error_msg,
                        file_path=file_path,
                        line_number=line_number,
                        tool="maven"
                    )
                else:
                    # General error without specific file location
                    issue = self._create_compilation_issue(
                        severity=IssueSeverity.ERROR,
                        message=error_msg,
                        file_path=str(project_path),
                        tool="maven"
                    )
                
                issues.append(issue)
                continue
            
            # Maven warning pattern
            warning_match = re.search(r'\[WARNING\]\s*(.+)', line)
            if warning_match:
                warning_msg = warning_match.group(1).strip()
                
                # Skip certain generic warnings
                if any(skip_phrase in warning_msg.lower() for skip_phrase in [
                    "using platform encoding", "default locale", "deprecated"
                ]):
                    continue
                
                issue = self._create_compilation_issue(
                    severity=IssueSeverity.WARNING,
                    message=warning_msg,
                    file_path=str(project_path),
                    tool="maven"
                )
                issues.append(issue)
                continue
            
            # Java compiler error pattern (more detailed)
            java_error_match = re.search(r'(.+\.java):\[(\d+),(\d+)\]\s*error:\s*(.+)', line)
            if java_error_match:
                file_path = java_error_match.group(1)
                line_number = int(java_error_match.group(2))
                column_number = int(java_error_match.group(3))
                message = java_error_match.group(4).strip()
                
                # Extract error code if present
                error_code = None
                code_match = re.search(r'\[([A-Z_]+)\]', message)
                if code_match:
                    error_code = code_match.group(1)
                
                context_lines = self._extract_context_lines(lines, i)
                
                issue = self._create_compilation_issue(
                    severity=IssueSeverity.ERROR,
                    message=message,
                    file_path=file_path,
                    line_number=line_number,
                    column_number=column_number,
                    error_code=error_code,
                    tool="javac",
                    context_lines=context_lines
                )
                issues.append(issue)
        
        return issues
    
    def _create_compilation_issue(self, severity: IssueSeverity, message: str,
                                file_path: str, line_number: Optional[int] = None,
                                column_number: Optional[int] = None,
                                error_code: Optional[str] = None,
                                tool: Optional[str] = None,
                                context_lines: Optional[List[str]] = None) -> CompilationIssue:
        """Create a standardized compilation issue."""
        location = IssueLocation(
            file_path=file_path,
            line_number=line_number,
            column_number=column_number
        )
        
        # Auto-categorize based on message
        category = self._categorize_message(message)
        
        return CompilationIssue(
            id=str(uuid.uuid4()),
            severity=severity,
            message=message,
            location=location,
            category=category,
            error_code=error_code,
            tool=tool,
            context_lines=context_lines or [],
            source="compilation"
        )
    
    def _categorize_message(self, message: str) -> IssueCategory:
        """Auto-categorize issue based on message content."""
        message_lower = message.lower()
        
        # Syntax errors
        if any(keyword in message_lower for keyword in [
            "illegal character", "unexpected token", "syntax error", 
            "unclosed", "missing semicolon"
        ]):
            return IssueCategory.SYNTAX
        
        # Type errors
        if any(keyword in message_lower for keyword in [
            "cannot convert", "incompatible types", "type mismatch",
            "undefined symbol", "cannot resolve symbol"
        ]):
            return IssueCategory.TYPE
        
        # Import errors
        if any(keyword in message_lower for keyword in [
            "cannot find symbol", "package", "does not exist",
            "import", "cannot be resolved"
        ]):
            return IssueCategory.IMPORT
        
        # Dependency errors
        if any(keyword in message_lower for keyword in [
            "dependency", "artifact", "repository", "version"
        ]):
            return IssueCategory.DEPENDENCY
        
        return IssueCategory.COMPILATION
    
    def _extract_context_lines(self, lines: List[str], current_index: int,
                              context_size: int = 3) -> List[str]:
        """Extract context lines around the current line."""
        start_idx = max(0, current_index - context_size)
        end_idx = min(len(lines), current_index + context_size + 1)
        return lines[start_idx:end_idx]
    
    def _parse_gradle_output(self, output: str, project_path: Path) -> List[CompilationIssue]:
        """Parse Gradle output for compilation issues using enhanced format."""
        issues = []
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Gradle compilation error pattern
            if "error:" in line.lower() or "failed" in line.lower():
                # Extract Java file compilation errors
                java_error_match = re.search(r'(.+\.java):(\d+):\s*error:\s*(.+)', line)
                if java_error_match:
                    file_path = java_error_match.group(1)
                    line_number = int(java_error_match.group(2))
                    message = java_error_match.group(3).strip()
                    
                    context_lines = self._extract_context_lines(lines, i)
                    
                    issue = self._create_compilation_issue(
                        severity=IssueSeverity.ERROR,
                        message=message,
                        file_path=file_path,
                        line_number=line_number,
                        tool="gradle",
                        context_lines=context_lines
                    )
                    issues.append(issue)
                else:
                    # General compilation error
                    issue = self._create_compilation_issue(
                        severity=IssueSeverity.ERROR,
                        message=line_stripped,
                        file_path=str(project_path),
                        tool="gradle"
                    )
                    issues.append(issue)
            
            # Gradle warning pattern
            elif "warning:" in line.lower():
                java_warning_match = re.search(r'(.+\.java):(\d+):\s*warning:\s*(.+)', line)
                if java_warning_match:
                    file_path = java_warning_match.group(1)
                    line_number = int(java_warning_match.group(2))
                    message = java_warning_match.group(3).strip()
                    
                    issue = self._create_compilation_issue(
                        severity=IssueSeverity.WARNING,
                        message=message,
                        file_path=file_path,
                        line_number=line_number,
                        tool="gradle"
                    )
                    issues.append(issue)
                else:
                    issue = self._create_compilation_issue(
                        severity=IssueSeverity.WARNING,
                        message=line_stripped,
                        file_path=str(project_path),
                        tool="gradle"
                    )
                    issues.append(issue)
        
        return issues
    
    def _compile_dotnet_api(self, project_path: Path, build_options: Dict[str, Any]) -> CompilationResult:
        """Compile .NET API project."""
        # Implementation for .NET compilation
        # This will be implemented in the next iteration
        return CompilationResult(
            status=CompilationStatus.FAILED,
            project_type=ProjectType.DOTNET_API,
            project_path=str(project_path),
            compilation_time=0.0,
            issues=[self._create_error_issue(
                ".NET compilation not yet implemented",
                str(project_path)
            )]
        )
    
    def _compile_python_api(self, project_path: Path, build_options: Dict[str, Any]) -> CompilationResult:
        """Compile Python API project."""
        # Implementation for Python compilation/validation
        # This will be implemented in the next iteration
        return CompilationResult(
            status=CompilationStatus.FAILED,
            project_type=ProjectType.PYTHON_API,
            project_path=str(project_path),
            compilation_time=0.0,
            issues=[self._create_error_issue(
                "Python compilation not yet implemented",
                str(project_path)
            )]
        )
    
    def _compile_nodejs_api(self, project_path: Path, build_options: Dict[str, Any]) -> CompilationResult:
        """Compile Node.js API project."""
        # Implementation for Node.js compilation
        # This will be implemented in the next iteration
        return CompilationResult(
            status=CompilationStatus.FAILED,
            project_type=ProjectType.NODEJS_API,
            project_path=str(project_path),
            compilation_time=0.0,
            issues=[self._create_error_issue(
                "Node.js compilation not yet implemented",
                str(project_path)
            )]
        )
    
    def _check_tool_availability(self, tool: str) -> bool:
        """Check if a tool is available in the system."""
        try:
            tool_path = self.tool_paths.get(tool, tool)
            result = subprocess.run(
                [tool_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_project_info(self, project_path: str) -> Dict[str, Any]:
        """Get information about a project."""
        project_path = Path(project_path)
        project_type = self._detect_project_type(project_path)
        
        info = {
            "project_path": str(project_path),
            "project_type": project_type.value,
            "exists": project_path.exists(),
            "build_files": [],
            "source_files_count": 0,
            "estimated_build_time": "unknown"
        }
        
        if not project_path.exists():
            return info
        
        # Detect build files
        if project_type == ProjectType.JAVA_SPRINGBOOT:
            if (project_path / "pom.xml").exists():
                info["build_files"].append("pom.xml")
            if (project_path / "build.gradle").exists():
                info["build_files"].append("build.gradle")
            
            # Count Java source files
            src_dir = project_path / "src" / "main" / "java"
            if src_dir.exists():
                info["source_files_count"] = len(list(src_dir.rglob("*.java")))
        
        elif project_type == ProjectType.DOTNET_API:
            info["build_files"].extend([f.name for f in project_path.glob("*.csproj")])
            info["build_files"].extend([f.name for f in project_path.glob("*.sln")])
            
            # Count C# source files
            info["source_files_count"] = len(list(project_path.rglob("*.cs")))
        
        elif project_type == ProjectType.PYTHON_API:
            for file in ["requirements.txt", "setup.py", "pyproject.toml"]:
                if (project_path / file).exists():
                    info["build_files"].append(file)
            
            # Count Python source files
            info["source_files_count"] = len(list(project_path.rglob("*.py")))
        
        elif project_type == ProjectType.NODEJS_API:
            if (project_path / "package.json").exists():
                info["build_files"].append("package.json")
            
            # Count JavaScript/TypeScript source files
            js_files = len(list(project_path.rglob("*.js")))
            ts_files = len(list(project_path.rglob("*.ts")))
            info["source_files_count"] = js_files + ts_files
        
        return info
    
    def generate_compilation_report(self, result: CompilationResult) -> str:
        """Generate a human-readable compilation report."""
        report = []
        
        # Header
        report.append("=" * 60)
        report.append("CODE COMPILATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Project Information
        report.append(f"Project Path: {result.project_path}")
        report.append(f"Project Type: {result.project_type.value}")
        report.append(f"Compilation Status: {result.status.value.upper()}")
        report.append(f"Compilation Time: {result.compilation_time:.2f} seconds")
        report.append("")
        
        # Summary
        summary = result.summary()
        report.append("SUMMARY:")
        report.append(f"  Total Issues: {summary['total_issues']}")
        report.append(f"  Errors: {summary['errors']}")
        report.append(f"  Warnings: {summary['warnings']}")
        report.append(f"  Build Successful: {summary['build_successful']}")
        report.append("")
        
        # Errors
        errors = result.get_errors()
        if errors:
            report.append("ERRORS:")
            report.append("-" * 40)
            for i, error in enumerate(errors, 1):
                report.append(f"{i}. {error.message}")
                if error.file_path:
                    location = f"   File: {error.file_path}"
                    if error.line_number:
                        location += f":{error.line_number}"
                        if error.column_number:
                            location += f":{error.column_number}"
                    report.append(location)
                if error.suggestion:
                    report.append(f"   Suggestion: {error.suggestion}")
                report.append("")
        
        # Warnings
        warnings = result.get_warnings()
        if warnings:
            report.append("WARNINGS:")
            report.append("-" * 40)
            for i, warning in enumerate(warnings, 1):
                report.append(f"{i}. {warning.message}")
                if warning.file_path:
                    location = f"   File: {warning.file_path}"
                    if warning.line_number:
                        location += f":{warning.line_number}"
                        if warning.column_number:
                            location += f":{warning.column_number}"
                    report.append(location)
                report.append("")
        
        # Build Information
        if result.metadata:
            report.append("BUILD INFORMATION:")
            report.append("-" * 40)
            for key, value in result.metadata.items():
                report.append(f"  {key}: {value}")
            report.append("")
        
        # Output Path
        if result.output_path:
            report.append(f"Output Path: {result.output_path}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# Utility functions for quick usage

def compile_java_springboot(project_path: str, **options) -> CompilationResult:
    """Quick function to compile Java Spring Boot project."""
    agent = CodeCompilationAgent()
    return agent.compile_project(project_path, ProjectType.JAVA_SPRINGBOOT, options)


def get_project_info(project_path: str) -> Dict[str, Any]:
    """Quick function to get project information."""
    agent = CodeCompilationAgent()
    return agent.get_project_info(project_path)


def generate_report(result: CompilationResult) -> str:
    """Quick function to generate compilation report."""
    agent = CodeCompilationAgent()
    return agent.generate_compilation_report(result)
