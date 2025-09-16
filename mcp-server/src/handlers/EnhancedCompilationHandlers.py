"""
Enhanced Compilation Handler for MCP Server
Handles compilation requests with simplified, standardized output format
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add the CodeCompilationAgent to the path
sys.path.append(str(Path(__file__).parent.parent.parent / "CodeCompilationAgent"))

try:
    from src.compilation_agent import CodeCompilationAgent, ProjectType, CompilationStatus
    from src.models.compilation_issue import CompilationIssue, CompilationIssuesSummary
except ImportError as e:
    logging.error(f"Failed to import CodeCompilationAgent: {e}")
    CodeCompilationAgent = None

from .BaseToolHandler import BaseToolHandler


class EnhancedCompileCodeHandler(BaseToolHandler):
    """
    Enhanced compilation handler with simplified output format.
    
    This handler provides:
    - Standardized compilation issue format
    - OpenAI-powered issue analysis
    - Human-readable and machine-processable output
    - Consistent format for UI and agent consumption
    """
    
    def __init__(self, context):
        super().__init__(context)
        self.logger = logging.getLogger(__name__)
    
    async def handle(self, args: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Handle enhanced compilation request.
        
        Args:
            args: Request arguments containing:
                - projectPath: Path to project to compile
                - projectType: Optional project type
                - buildOptions: Optional build configuration
                - enableOpenAI: Whether to use OpenAI analysis
                - openaiApiKey: Optional OpenAI API key
                
        Returns:
            Simplified compilation result format
        """
        try:
            project_path = args.get("projectPath")
            if not project_path:
                return self._create_error_response("Project path is required")
            
            # Validate project path
            path_obj = Path(project_path)
            if not path_obj.exists():
                return self._create_error_response(f"Project path does not exist: {project_path}")
            
            self.logger.info(f"Starting enhanced compilation for: {project_path}")
            
            # Check if CodeCompilationAgent is available
            if not CodeCompilationAgent:
                return self._create_error_response("CodeCompilationAgent not available")
            
            # Configure the agent
            config = self._prepare_agent_config(args, context)
            agent = CodeCompilationAgent(config=config)
            
            # Determine project type
            project_type = self._determine_project_type(args.get("projectType"))
            
            # Prepare build options
            build_options = args.get("buildOptions", {})
            
            # Execute compilation with OpenAI enhancement
            result = await agent.compile_project(
                project_path=project_path,
                project_type=project_type,
                build_options=build_options
            )
            
            # Return simplified format
            simplified_result = result.to_simplified_format()
            
            self.logger.info(f"Compilation completed. Status: {result.status.value}, "
                           f"Issues: {len(result.issues)}, "
                           f"OpenAI processed: {result.openai_processed}")
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(simplified_result, indent=2)
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced compilation failed: {e}")
            return self._create_error_response(f"Compilation failed: {str(e)}")
    
    def _prepare_agent_config(self, args: Dict[str, Any], context) -> Dict[str, Any]:
        """Prepare configuration for the compilation agent."""
        config = {
            "verbose": args.get("verbose", False),
            "timeout": args.get("timeout", 300),
            "enable_openai": args.get("enableOpenAI", True)
        }
        
        # Get OpenAI API key from multiple sources
        openai_api_key = (
            args.get("openaiApiKey") or
            os.getenv("OPENAI_API_KEY") or
            getattr(context, 'openai', {}).get('api_key') if hasattr(context, 'openai') else None
        )
        
        if openai_api_key:
            config["openai_api_key"] = openai_api_key
        else:
            self.logger.warning("No OpenAI API key found. AI analysis will be disabled.")
            config["enable_openai"] = False
        
        return config
    
    def _determine_project_type(self, project_type_str: Optional[str]) -> Optional[ProjectType]:
        """Determine project type from string."""
        if not project_type_str:
            return None
        
        type_mapping = {
            "java": ProjectType.JAVA_SPRINGBOOT,
            "java_springboot": ProjectType.JAVA_SPRINGBOOT,
            "dotnet": ProjectType.DOTNET_API,
            "dotnet_api": ProjectType.DOTNET_API,
            "python": ProjectType.PYTHON_API,
            "python_api": ProjectType.PYTHON_API,
            "nodejs": ProjectType.NODEJS_API,
            "nodejs_api": ProjectType.NODEJS_API,
            "node": ProjectType.NODEJS_API
        }
        
        return type_mapping.get(project_type_str.lower())
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        error_result = {
            "compilation_status": "failed",
            "project_info": {},
            "summary": {
                "total_issues": 1,
                "errors": 1,
                "warnings": 0,
                "infos": 0,
                "hints": 0
            },
            "ai_analysis": {
                "processed": False,
                "summary": None,
                "suggestions_available": 0
            },
            "issues": [
                {
                    "id": "error_001",
                    "severity": "error",
                    "message": error_message,
                    "location": {
                        "file_path": "",
                        "line_number": None,
                        "column_number": None
                    },
                    "category": "compilation",
                    "tool": "mcp_handler",
                    "ai_processed": False,
                    "ai_suggestions": []
                }
            ],
            "issues_by_file": {},
            "metadata": {
                "handler": "enhanced_compile_code"
            },
            "error": error_message
        }
        
        return {
            "content": [
                {
                    "type": "text", 
                    "text": json.dumps(error_result, indent=2)
                }
            ]
        }


class CompilationIssueAnalyzer(BaseToolHandler):
    """
    Handler for analyzing compilation issues with OpenAI.
    
    This handler can take raw compilation output and convert it to
    the standardized format with AI analysis.
    """
    
    def __init__(self, context):
        super().__init__(context)
        self.logger = logging.getLogger(__name__)
    
    async def handle(self, args: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Analyze compilation issues and provide standardized output.
        
        Args:
            args: Request arguments containing:
                - issues: List of compilation issues (legacy or simplified format)
                - projectPath: Optional project path for context
                - enableOpenAI: Whether to use OpenAI analysis
                
        Returns:
            Analyzed and standardized compilation issues
        """
        try:
            issues_data = args.get("issues", [])
            project_path = args.get("projectPath", "")
            enable_openai = args.get("enableOpenAI", True)
            
            if not issues_data:
                return self._create_empty_response()
            
            self.logger.info(f"Analyzing {len(issues_data)} compilation issues")
            
            # Convert issues to standardized format
            standardized_issues = self._convert_to_standardized_format(issues_data, project_path)
            
            # Enhance with OpenAI if enabled
            if enable_openai and hasattr(context, 'openai') and context.openai:
                try:
                    from src.processors.openai_processor import CompilationIssueProcessor
                    
                    processor = CompilationIssueProcessor()
                    enhanced_issues = await processor.process_issues(
                        standardized_issues,
                        {"project_path": project_path}
                    )
                    standardized_issues = enhanced_issues
                    
                    self.logger.info("Issues enhanced with OpenAI analysis")
                    
                except Exception as e:
                    self.logger.warning(f"OpenAI enhancement failed: {e}")
            
            # Create summary
            summary = CompilationIssuesSummary.from_issues(standardized_issues)
            
            # Format response
            result = {
                "total_issues": len(standardized_issues),
                "summary": summary.to_dict(),
                "issues": [issue.to_dict() for issue in standardized_issues],
                "issues_by_file": self._group_issues_by_file(standardized_issues),
                "ai_processed": any(issue.ai_processed for issue in standardized_issues)
            }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Issue analysis failed: {e}")
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _convert_to_standardized_format(self, issues_data: List[Dict[str, Any]], 
                                      project_path: str) -> List[CompilationIssue]:
        """Convert various issue formats to standardized CompilationIssue format."""
        standardized_issues = []
        
        for i, issue_data in enumerate(issues_data):
            try:
                # Check if already in new format
                if "location" in issue_data and isinstance(issue_data["location"], dict):
                    issue = CompilationIssue.from_dict(issue_data)
                else:
                    # Convert from legacy format
                    issue = self._convert_legacy_issue(issue_data, project_path, i)
                
                standardized_issues.append(issue)
                
            except Exception as e:
                self.logger.warning(f"Failed to convert issue {i}: {e}")
                # Create a fallback issue
                issue = self._create_fallback_issue(issue_data, project_path, i)
                standardized_issues.append(issue)
        
        return standardized_issues
    
    def _convert_legacy_issue(self, issue_data: Dict[str, Any], 
                            project_path: str, index: int) -> CompilationIssue:
        """Convert legacy issue format to standardized format."""
        from src.models.compilation_issue import IssueLocation, IssueSeverity, IssueCategory
        import uuid
        
        # Extract basic information
        severity_str = issue_data.get("severity", "error")
        message = issue_data.get("message", "Unknown error")
        file_path = issue_data.get("file_path", project_path)
        line_number = issue_data.get("line_number")
        column_number = issue_data.get("column_number")
        
        # Create location
        location = IssueLocation(
            file_path=file_path,
            line_number=line_number,
            column_number=column_number
        )
        
        # Map severity
        try:
            severity = IssueSeverity(severity_str)
        except ValueError:
            severity = IssueSeverity.ERROR
        
        # Create issue
        return CompilationIssue(
            id=issue_data.get("id", f"issue_{index}_{uuid.uuid4().hex[:8]}"),
            severity=severity,
            message=message,
            location=location,
            category=IssueCategory.COMPILATION,
            error_code=issue_data.get("error_code"),
            tool=issue_data.get("tool", "unknown"),
            metadata={
                "converted_from_legacy": True,
                "original_suggestion": issue_data.get("suggestion")
            }
        )
    
    def _create_fallback_issue(self, issue_data: Dict[str, Any], 
                             project_path: str, index: int) -> CompilationIssue:
        """Create a fallback issue when conversion fails."""
        from src.models.compilation_issue import IssueLocation, IssueSeverity, IssueCategory
        import uuid
        
        location = IssueLocation(file_path=project_path)
        
        return CompilationIssue(
            id=f"fallback_{index}_{uuid.uuid4().hex[:8]}",
            severity=IssueSeverity.ERROR,
            message=str(issue_data.get("message", f"Conversion failed for issue {index}")),
            location=location,
            category=IssueCategory.UNKNOWN,
            tool="fallback",
            metadata={
                "conversion_failed": True,
                "original_data": issue_data
            }
        )
    
    def _group_issues_by_file(self, issues: List[CompilationIssue]) -> Dict[str, List[Dict[str, Any]]]:
        """Group issues by file path."""
        issues_by_file = {}
        
        for issue in issues:
            file_path = issue.location.file_path
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue.to_dict())
        
        return issues_by_file
    
    def _create_empty_response(self) -> Dict[str, Any]:
        """Create response for empty issues list."""
        result = {
            "total_issues": 0,
            "summary": {
                "total_issues": 0,
                "errors": 0,
                "warnings": 0,
                "infos": 0,
                "hints": 0
            },
            "issues": [],
            "issues_by_file": {},
            "ai_processed": False
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": error_message}, indent=2)
                }
            ]
        }
