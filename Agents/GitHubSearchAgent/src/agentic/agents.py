"""
Specialized agents for GitHub search and analysis.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import re

from .core import BaseAgent
from ..models import (
    AgentGoal, RepositoryInfo, SearchQuery, AnalysisResult, 
    CodeFile, SecurityIssue, TrendAnalysis, SearchScope, 
    AnalysisType, Priority
)
from ..utils.github_api import GitHubAPIClient
from ..utils.code_analyzer import CodeAnalyzer


class GitHubSearchAgent(BaseAgent):
    """Agent specialized in GitHub repository search and discovery."""
    
    def __init__(self, github_client: GitHubAPIClient):
        super().__init__("search_agent", "GitHub Search Agent", 
                        "Discovers and filters GitHub repositories")
        self.github_client = github_client
        self.code_analyzer = CodeAnalyzer()
        
        # Register capabilities
        from ..models import AgentCapability
        self.register_capability(AgentCapability(
            name="repository_search",
            description="Search GitHub repositories with advanced filtering",
            input_types=["SearchQuery"],
            output_types=["List[RepositoryInfo]"],
            cost_estimate=0.1,
            execution_time_estimate=5.0
        ))
        
        self.register_capability(AgentCapability(
            name="repository_discovery",
            description="Discover related repositories based on criteria",
            input_types=["RepositoryInfo", "Dict[str, Any]"],
            output_types=["List[RepositoryInfo]"],
            cost_estimate=0.2,
            execution_time_estimate=10.0
        ))
    
    async def can_handle(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        search_keywords = ["search", "find", "discover", "repositories", "repos"]
        return any(keyword in goal.description.lower() for keyword in search_keywords)
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute search-related goals."""
        self.logger.info(f"Executing search goal: {goal.description}")
        
        start_time = datetime.now()
        
        try:
            if "search repositories" in goal.description.lower():
                return await self._search_repositories(goal)
            elif "discover related" in goal.description.lower():
                return await self._discover_related_repositories(goal)
            elif "repository details" in goal.description.lower():
                return await self._get_repository_details(goal)
            else:
                return await self._general_search(goal)
                
        except Exception as e:
            self.logger.error(f"Search goal execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _search_repositories(self, goal: AgentGoal) -> Dict[str, Any]:
        """Search for repositories based on query."""
        query_data = goal.context.get("search_query", {})
        
        if isinstance(query_data, dict):
            search_query = SearchQuery(**query_data)
        else:
            # Create default query from description
            search_query = SearchQuery(
                query=goal.context.get("query", goal.description),
                max_results=goal.context.get("max_results", 50)
            )
        
        async with self.github_client:
            repositories = await self.github_client.search_repositories(search_query)
        
        # Apply additional filtering and scoring
        scored_repositories = await self._score_repositories(repositories, goal.context)
        
        return {
            "success": True,
            "repositories": scored_repositories,
            "total_found": len(repositories),
            "query": search_query,
            "search_time": datetime.now()
        }
    
    async def _discover_related_repositories(self, goal: AgentGoal) -> Dict[str, Any]:
        """Discover repositories related to a given repository."""
        base_repo = goal.context.get("repository")
        if not base_repo:
            raise ValueError("Base repository not provided")
        
        related_repos = []
        
        # Search by similar topics
        if isinstance(base_repo, dict) and base_repo.get("topics"):
            for topic in base_repo["topics"][:3]:  # Limit to top 3 topics
                topic_query = SearchQuery(
                    query=f"topic:{topic}",
                    max_results=20,
                    min_stars=base_repo.get("stars", 0) // 2
                )
                
                async with self.github_client:
                    topic_repos = await self.github_client.search_repositories(topic_query)
                    related_repos.extend(topic_repos)
        
        # Search by language
        if isinstance(base_repo, dict) and base_repo.get("language"):
            lang_query = SearchQuery(
                query=f"language:{base_repo['language']}",
                max_results=15,
                min_stars=base_repo.get("stars", 0) // 3
            )
            
            async with self.github_client:
                lang_repos = await self.github_client.search_repositories(lang_query)
                related_repos.extend(lang_repos)
        
        # Remove duplicates and the base repository
        unique_repos = []
        seen_names = set()
        base_name = base_repo.get("full_name", "")
        
        for repo in related_repos:
            if repo.full_name != base_name and repo.full_name not in seen_names:
                unique_repos.append(repo)
                seen_names.add(repo.full_name)
        
        return {
            "success": True,
            "related_repositories": unique_repos[:25],  # Limit results
            "base_repository": base_repo,
            "discovery_methods": ["topics", "language"],
            "discovery_time": datetime.now()
        }
    
    async def _get_repository_details(self, goal: AgentGoal) -> Dict[str, Any]:
        """Get detailed information about a specific repository."""
        owner = goal.context.get("owner")
        repo = goal.context.get("repo")
        
        if not owner or not repo:
            raise ValueError("Repository owner and name must be provided")
        
        async with self.github_client:
            repo_info = await self.github_client.get_repository_details(owner, repo)
        
        return {
            "success": True,
            "repository": repo_info,
            "details_retrieved_at": datetime.now()
        }
    
    async def _general_search(self, goal: AgentGoal) -> Dict[str, Any]:
        """Handle general search requests."""
        query_text = goal.context.get("query", goal.description)
        
        search_query = SearchQuery(
            query=query_text,
            max_results=goal.context.get("max_results", 30)
        )
        
        async with self.github_client:
            repositories = await self.github_client.search_repositories(search_query)
        
        return {
            "success": True,
            "repositories": repositories,
            "query": search_query,
            "search_time": datetime.now()
        }
    
    async def _score_repositories(self, repositories: List[RepositoryInfo], 
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score and rank repositories based on relevance."""
        scored_repos = []
        
        for repo in repositories:
            score = await self._calculate_repository_score(repo, context)
            scored_repos.append({
                "repository": repo,
                "relevance_score": score,
                "score_factors": self._get_score_factors(repo, context)
            })
        
        # Sort by score
        scored_repos.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_repos
    
    async def _calculate_repository_score(self, repo: RepositoryInfo, 
                                        context: Dict[str, Any]) -> float:
        """Calculate relevance score for a repository."""
        score = 0.0
        
        # Stars weight (normalized)
        score += min(repo.stars / 1000, 10) * 0.3
        
        # Activity weight (recent updates)
        if repo.updated_at:
            days_since_update = (datetime.now() - repo.updated_at.replace(tzinfo=None)).days
            activity_score = max(0, 10 - (days_since_update / 30))
            score += activity_score * 0.2
        
        # Forks weight
        score += min(repo.forks / 100, 5) * 0.15
        
        # Description relevance
        query_terms = context.get("query", "").lower().split()
        if repo.description:
            desc_lower = repo.description.lower()
            matching_terms = sum(1 for term in query_terms if term in desc_lower)
            score += (matching_terms / max(len(query_terms), 1)) * 5 * 0.2
        
        # Language match
        preferred_language = context.get("language")
        if preferred_language and repo.language:
            if repo.language.lower() == preferred_language.lower():
                score += 3 * 0.15
        
        return min(score, 100.0)
    
    def _get_score_factors(self, repo: RepositoryInfo, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed scoring factors for transparency."""
        return {
            "stars": repo.stars,
            "forks": repo.forks,
            "last_updated": repo.updated_at.isoformat() if repo.updated_at else None,
            "language": repo.language,
            "has_description": bool(repo.description),
            "is_fork": repo.is_fork,
            "is_archived": repo.is_archived
        }


class CodeAnalysisAgent(BaseAgent):
    """Agent specialized in code analysis and quality assessment."""
    
    def __init__(self, github_client: GitHubAPIClient):
        super().__init__("analysis_agent", "Code Analysis Agent",
                        "Analyzes code quality, structure, and patterns")
        self.github_client = github_client
        self.code_analyzer = CodeAnalyzer()
        
        # Register capabilities
        from ..models import AgentCapability
        self.register_capability(AgentCapability(
            name="code_analysis",
            description="Analyze code files for quality and structure",
            input_types=["RepositoryInfo", "List[CodeFile]"],
            output_types=["AnalysisResult"],
            cost_estimate=0.5,
            execution_time_estimate=30.0
        ))
        
        self.register_capability(AgentCapability(
            name="repository_structure_analysis",
            description="Analyze overall repository structure and organization",
            input_types=["RepositoryInfo"],
            output_types=["Dict[str, Any]"],
            cost_estimate=0.3,
            execution_time_estimate=15.0
        ))
    
    async def can_handle(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        analysis_keywords = ["analyze", "analysis", "code", "quality", "structure", "patterns"]
        return any(keyword in goal.description.lower() for keyword in analysis_keywords)
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute analysis-related goals."""
        self.logger.info(f"Executing analysis goal: {goal.description}")
        
        start_time = datetime.now()
        
        try:
            if "analyze repository" in goal.description.lower():
                return await self._analyze_repository(goal)
            elif "analyze code" in goal.description.lower():
                return await self._analyze_code_files(goal)
            elif "structure analysis" in goal.description.lower():
                return await self._analyze_structure(goal)
            else:
                return await self._general_analysis(goal)
                
        except Exception as e:
            self.logger.error(f"Analysis goal execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _analyze_repository(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform comprehensive repository analysis."""
        repository = goal.context.get("repository")
        if not repository:
            raise ValueError("Repository information not provided")
        
        if isinstance(repository, dict):
            owner = repository.get("owner")
            name = repository.get("name")
        else:
            owner = repository.owner
            name = repository.name
        
        if not owner or not name:
            raise ValueError("Repository owner and name must be provided")
        
        # Get repository files
        code_files = []
        file_paths = []
        
        async with self.github_client:
            async for file_info in self.github_client.get_repository_files(
                owner, name, max_files=50
            ):
                file_path = file_info["path"]
                file_paths.append(file_path)
                
                # Only analyze code files
                language = self.code_analyzer.get_language_from_extension(file_path)
                if language and file_info["size"] < 100000:  # Skip very large files
                    content = await self.github_client.get_file_content(owner, name, file_path)
                    if content:
                        code_file = self.code_analyzer.analyze_file(file_path, content, language)
                        code_files.append(code_file)
        
        # Analyze repository structure
        structure_analysis = self.code_analyzer.analyze_repository_structure(file_paths)
        
        # Calculate overall scores
        overall_quality = sum(cf.quality_score for cf in code_files) / max(len(code_files), 1)
        overall_complexity = sum(cf.complexity_score for cf in code_files) / max(len(code_files), 1)
        
        analysis_result = AnalysisResult(
            repository=repository if isinstance(repository, RepositoryInfo) else RepositoryInfo(**repository),
            analysis_type=AnalysisType.DETAILED,
            score=overall_quality,
            summary=f"Repository analysis complete. Quality: {overall_quality:.1f}/100, "
                   f"Complexity: {overall_complexity:.1f}/100",
            details={
                "structure_analysis": structure_analysis,
                "overall_quality": overall_quality,
                "overall_complexity": overall_complexity,
                "files_analyzed": len(code_files),
                "total_files": len(file_paths)
            },
            code_files=code_files
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "analysis_time": (datetime.now() - start_time).total_seconds()
        }
    
    async def _analyze_code_files(self, goal: AgentGoal) -> Dict[str, Any]:
        """Analyze specific code files."""
        code_files = goal.context.get("code_files", [])
        
        analyzed_files = []
        for file_info in code_files:
            if isinstance(file_info, dict):
                language = self.code_analyzer.get_language_from_extension(file_info["path"])
                if language:
                    analyzed_file = self.code_analyzer.analyze_file(
                        file_info["path"], 
                        file_info["content"], 
                        language
                    )
                    analyzed_files.append(analyzed_file)
        
        return {
            "success": True,
            "analyzed_files": analyzed_files,
            "total_files": len(analyzed_files)
        }
    
    async def _analyze_structure(self, goal: AgentGoal) -> Dict[str, Any]:
        """Analyze repository structure."""
        file_paths = goal.context.get("file_paths", [])
        
        structure_analysis = self.code_analyzer.analyze_repository_structure(file_paths)
        
        return {
            "success": True,
            "structure_analysis": structure_analysis
        }
    
    async def _general_analysis(self, goal: AgentGoal) -> Dict[str, Any]:
        """Handle general analysis requests."""
        # Default to repository analysis if repository is provided
        if goal.context.get("repository"):
            return await self._analyze_repository(goal)
        else:
            return {
                "success": False,
                "error": "Insufficient context for analysis"
            }


class SecurityAnalysisAgent(BaseAgent):
    """Agent specialized in security analysis and vulnerability detection."""
    
    def __init__(self, github_client: GitHubAPIClient):
        super().__init__("security_agent", "Security Analysis Agent",
                        "Detects security vulnerabilities and issues")
        self.github_client = github_client
        self.code_analyzer = CodeAnalyzer()
        
        # Register capabilities
        from ..models import AgentCapability
        self.register_capability(AgentCapability(
            name="security_scan",
            description="Scan code for security vulnerabilities",
            input_types=["RepositoryInfo", "List[CodeFile]"],
            output_types=["List[SecurityIssue]"],
            cost_estimate=0.7,
            execution_time_estimate=45.0
        ))
    
    async def can_handle(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        security_keywords = ["security", "vulnerability", "scan", "audit", "safety"]
        return any(keyword in goal.description.lower() for keyword in security_keywords)
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute security-related goals."""
        self.logger.info(f"Executing security goal: {goal.description}")
        
        start_time = datetime.now()
        
        try:
            if "security scan" in goal.description.lower():
                return await self._security_scan(goal)
            elif "vulnerability assessment" in goal.description.lower():
                return await self._vulnerability_assessment(goal)
            else:
                return await self._general_security_analysis(goal)
                
        except Exception as e:
            self.logger.error(f"Security goal execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _security_scan(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform security scan on repository or code files."""
        repository = goal.context.get("repository")
        code_files = goal.context.get("code_files", [])
        
        security_issues = []
        
        if repository and not code_files:
            # Scan repository
            if isinstance(repository, dict):
                owner = repository.get("owner")
                name = repository.get("name")
            else:
                owner = repository.owner
                name = repository.name
            
            async with self.github_client:
                async for file_info in self.github_client.get_repository_files(
                    owner, name, max_files=100
                ):
                    file_path = file_info["path"]
                    language = self.code_analyzer.get_language_from_extension(file_path)
                    
                    if language and file_info["size"] < 50000:  # Skip very large files
                        content = await self.github_client.get_file_content(owner, name, file_path)
                        if content:
                            file_issues = self.code_analyzer.detect_security_issues(
                                file_path, content, language
                            )
                            security_issues.extend(file_issues)
        else:
            # Scan provided code files
            for code_file in code_files:
                if isinstance(code_file, CodeFile):
                    file_issues = self.code_analyzer.detect_security_issues(
                        code_file.path, code_file.content, code_file.language
                    )
                    security_issues.extend(file_issues)
        
        # Classify and prioritize issues
        critical_issues = [issue for issue in security_issues if issue.severity == "CRITICAL"]
        high_issues = [issue for issue in security_issues if issue.severity == "HIGH"]
        medium_issues = [issue for issue in security_issues if issue.severity == "MEDIUM"]
        low_issues = [issue for issue in security_issues if issue.severity == "LOW"]
        
        security_score = self._calculate_security_score(security_issues)
        
        return {
            "success": True,
            "security_issues": security_issues,
            "issue_summary": {
                "critical": len(critical_issues),
                "high": len(high_issues),
                "medium": len(medium_issues),
                "low": len(low_issues),
                "total": len(security_issues)
            },
            "security_score": security_score,
            "scan_time": (datetime.now() - start_time).total_seconds()
        }
    
    async def _vulnerability_assessment(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform detailed vulnerability assessment."""
        # This could be extended to integrate with external vulnerability databases
        scan_result = await self._security_scan(goal)
        
        if scan_result.get("success"):
            security_issues = scan_result["security_issues"]
            
            # Group issues by type
            issue_types = {}
            for issue in security_issues:
                issue_type = issue.type
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(issue)
            
            # Generate assessment report
            assessment = {
                "overall_risk": self._assess_overall_risk(security_issues),
                "vulnerability_types": issue_types,
                "recommendations": self._generate_security_recommendations(security_issues),
                "compliance_notes": self._check_compliance_issues(security_issues)
            }
            
            scan_result["vulnerability_assessment"] = assessment
        
        return scan_result
    
    async def _general_security_analysis(self, goal: AgentGoal) -> Dict[str, Any]:
        """Handle general security analysis requests."""
        return await self._security_scan(goal)
    
    def _calculate_security_score(self, security_issues: List[SecurityIssue]) -> float:
        """Calculate overall security score."""
        if not security_issues:
            return 100.0
        
        score = 100.0
        severity_weights = {
            "CRITICAL": 25,
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3
        }
        
        for issue in security_issues:
            weight = severity_weights.get(issue.severity, 5)
            score -= weight
        
        return max(score, 0.0)
    
    def _assess_overall_risk(self, security_issues: List[SecurityIssue]) -> str:
        """Assess overall security risk level."""
        critical_count = sum(1 for issue in security_issues if issue.severity == "CRITICAL")
        high_count = sum(1 for issue in security_issues if issue.severity == "HIGH")
        
        if critical_count > 0:
            return "CRITICAL"
        elif high_count > 3:
            return "HIGH"
        elif high_count > 0 or len(security_issues) > 10:
            return "MEDIUM"
        elif len(security_issues) > 0:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_security_recommendations(self, security_issues: List[SecurityIssue]) -> List[str]:
        """Generate security recommendations based on found issues."""
        recommendations = []
        issue_types = set(issue.type for issue in security_issues)
        
        if "hardcoded_secrets" in issue_types:
            recommendations.append("Implement secure configuration management for secrets")
        
        if "sql_injection" in issue_types:
            recommendations.append("Use parameterized queries throughout the application")
        
        if "xss" in issue_types:
            recommendations.append("Implement proper input validation and output encoding")
        
        if "command_injection" in issue_types:
            recommendations.append("Validate and sanitize all external inputs")
        
        if len(security_issues) > 10:
            recommendations.append("Consider implementing automated security testing in CI/CD")
        
        if not recommendations:
            recommendations.append("Maintain current security practices and regular code reviews")
        
        return recommendations
    
    def _check_compliance_issues(self, security_issues: List[SecurityIssue]) -> Dict[str, Any]:
        """Check for common compliance issues."""
        compliance_notes = {
            "data_protection": [],
            "access_control": [],
            "logging_monitoring": []
        }
        
        # This could be expanded with specific compliance framework checks
        if any(issue.type == "hardcoded_secrets" for issue in security_issues):
            compliance_notes["data_protection"].append(
                "Hardcoded secrets may violate data protection requirements"
            )
        
        return compliance_notes
