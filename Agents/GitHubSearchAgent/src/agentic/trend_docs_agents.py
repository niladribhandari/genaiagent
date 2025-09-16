"""
Additional specialized agents for trend analysis and documentation.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import json

from .core import BaseAgent
from ..models import (
    AgentGoal, RepositoryInfo, SearchQuery, TrendAnalysis, 
    AnalysisType, Priority, SearchScope
)
from ..utils.github_api import GitHubAPIClient
from ..utils.code_analyzer import CodeAnalyzer


class TrendAnalysisAgent(BaseAgent):
    """Agent specialized in analyzing technology trends and patterns."""
    
    def __init__(self, github_client: GitHubAPIClient):
        super().__init__("trend_agent", "Trend Analysis Agent",
                        "Analyzes technology trends and popularity patterns")
        self.github_client = github_client
        
        # Register capabilities
        from ..models import AgentCapability
        self.register_capability(AgentCapability(
            name="trend_analysis",
            description="Analyze technology trends and adoption patterns",
            input_types=["List[RepositoryInfo]", "Dict[str, Any]"],
            output_types=["List[TrendAnalysis]"],
            cost_estimate=0.4,
            execution_time_estimate=25.0
        ))
        
        self.register_capability(AgentCapability(
            name="technology_comparison",
            description="Compare technologies and frameworks",
            input_types=["List[str]"],
            output_types=["Dict[str, Any]"],
            cost_estimate=0.6,
            execution_time_estimate=40.0
        ))
    
    async def can_handle(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        trend_keywords = ["trend", "popular", "adoption", "growth", "comparison", "analytics"]
        return any(keyword in goal.description.lower() for keyword in trend_keywords)
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute trend analysis goals."""
        self.logger.info(f"Executing trend goal: {goal.description}")
        
        start_time = datetime.now()
        
        try:
            if "analyze trends" in goal.description.lower():
                return await self._analyze_trends(goal)
            elif "compare technologies" in goal.description.lower():
                return await self._compare_technologies(goal)
            elif "language trends" in goal.description.lower():
                return await self._analyze_language_trends(goal)
            elif "framework trends" in goal.description.lower():
                return await self._analyze_framework_trends(goal)
            else:
                return await self._general_trend_analysis(goal)
                
        except Exception as e:
            self.logger.error(f"Trend goal execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _analyze_trends(self, goal: AgentGoal) -> Dict[str, Any]:
        """Analyze general technology trends."""
        technologies = goal.context.get("technologies", [])
        time_period = goal.context.get("time_period", "6months")
        
        if not technologies:
            # Auto-detect popular technologies
            technologies = await self._discover_trending_technologies()
        
        trend_analyses = []
        
        for tech in technologies:
            trend_analysis = await self._analyze_technology_trend(tech, time_period)
            trend_analyses.append(trend_analysis)
        
        # Sort by popularity score
        trend_analyses.sort(key=lambda x: x.popularity_score, reverse=True)
        
        return {
            "success": True,
            "trend_analyses": trend_analyses,
            "analysis_period": time_period,
            "analyzed_technologies": len(trend_analyses),
            "analysis_time": (datetime.now() - start_time).total_seconds()
        }
    
    async def _compare_technologies(self, goal: AgentGoal) -> Dict[str, Any]:
        """Compare multiple technologies."""
        technologies = goal.context.get("technologies", [])
        
        if len(technologies) < 2:
            raise ValueError("At least 2 technologies required for comparison")
        
        comparison_data = {}
        
        for tech in technologies:
            tech_data = await self._get_technology_metrics(tech)
            comparison_data[tech] = tech_data
        
        # Generate comparison insights
        insights = self._generate_comparison_insights(comparison_data)
        
        return {
            "success": True,
            "technology_comparison": comparison_data,
            "insights": insights,
            "compared_technologies": technologies
        }
    
    async def _analyze_language_trends(self, goal: AgentGoal) -> Dict[str, Any]:
        """Analyze programming language trends."""
        languages = goal.context.get("languages", [
            "python", "javascript", "java", "typescript", "go", "rust", "kotlin", "swift"
        ])
        
        language_trends = {}
        
        for language in languages:
            # Search for repositories in this language
            query = SearchQuery(
                query=f"language:{language}",
                max_results=100,
                created_after=datetime.now() - timedelta(days=365)
            )
            
            async with self.github_client:
                repos = await self.github_client.search_repositories(query)
            
            # Calculate metrics
            total_stars = sum(repo.stars for repo in repos)
            avg_stars = total_stars / max(len(repos), 1)
            recent_activity = sum(1 for repo in repos 
                                if repo.updated_at and 
                                (datetime.now() - repo.updated_at.replace(tzinfo=None)).days < 30)
            
            language_trends[language] = {
                "total_repositories": len(repos),
                "total_stars": total_stars,
                "average_stars": avg_stars,
                "recent_activity": recent_activity,
                "activity_rate": recent_activity / max(len(repos), 1),
                "sample_repositories": [repo.full_name for repo in repos[:5]]
            }
        
        # Rank languages
        ranked_languages = sorted(language_trends.items(), 
                                key=lambda x: x[1]["total_stars"], reverse=True)
        
        return {
            "success": True,
            "language_trends": language_trends,
            "ranked_languages": ranked_languages,
            "analysis_period": "last_12_months"
        }
    
    async def _analyze_framework_trends(self, goal: AgentGoal) -> Dict[str, Any]:
        """Analyze framework and library trends."""
        frameworks = goal.context.get("frameworks", [
            "react", "vue", "angular", "django", "flask", "express", "spring", "rails"
        ])
        
        framework_trends = {}
        
        for framework in frameworks:
            # Search for repositories using this framework
            query = SearchQuery(
                query=f"{framework} framework",
                max_results=50
            )
            
            async with self.github_client:
                repos = await self.github_client.search_repositories(query)
            
            # Filter repositories that actually use the framework
            relevant_repos = []
            for repo in repos:
                if framework.lower() in repo.description.lower() if repo.description else False:
                    relevant_repos.append(repo)
                elif framework.lower() in " ".join(repo.topics).lower():
                    relevant_repos.append(repo)
            
            framework_trends[framework] = await self._calculate_framework_metrics(
                framework, relevant_repos
            )
        
        return {
            "success": True,
            "framework_trends": framework_trends,
            "analyzed_frameworks": len(frameworks)
        }
    
    async def _general_trend_analysis(self, goal: AgentGoal) -> Dict[str, Any]:
        """Handle general trend analysis requests."""
        # Default to discovering trending technologies
        trending_technologies = await self._discover_trending_technologies()
        
        trend_analyses = []
        for tech in trending_technologies[:10]:  # Limit to top 10
            trend_analysis = await self._analyze_technology_trend(tech)
            trend_analyses.append(trend_analysis)
        
        return {
            "success": True,
            "trending_technologies": trend_analyses,
            "discovery_method": "automatic"
        }
    
    async def _discover_trending_technologies(self) -> List[str]:
        """Discover currently trending technologies."""
        # Search for repositories with high recent activity
        query = SearchQuery(
            query="",
            max_results=100,
            sort_by="updated",
            created_after=datetime.now() - timedelta(days=30)
        )
        
        async with self.github_client:
            recent_repos = await self.github_client.search_repositories(query)
        
        # Extract technologies from topics and descriptions
        technology_mentions = Counter()
        
        for repo in recent_repos:
            # Count topics
            for topic in repo.topics:
                technology_mentions[topic] += 1
            
            # Extract from description
            if repo.description:
                desc_words = re.findall(r'\b\w+\b', repo.description.lower())
                for word in desc_words:
                    if len(word) > 2:  # Filter short words
                        technology_mentions[word] += 1
        
        # Filter and return most common technologies
        common_tech_terms = [
            "python", "javascript", "react", "node", "api", "web", "mobile", 
            "machine-learning", "ai", "docker", "kubernetes", "cloud", "aws",
            "tensorflow", "pytorch", "django", "flask", "express", "vue", "angular"
        ]
        
        trending = []
        for tech, count in technology_mentions.most_common(20):
            if tech in common_tech_terms and count > 2:
                trending.append(tech)
        
        return trending[:15]
    
    async def _analyze_technology_trend(self, technology: str, 
                                      time_period: str = "6months") -> TrendAnalysis:
        """Analyze trend for a specific technology."""
        # Calculate date range
        if time_period == "3months":
            start_date = datetime.now() - timedelta(days=90)
        elif time_period == "6months":
            start_date = datetime.now() - timedelta(days=180)
        elif time_period == "1year":
            start_date = datetime.now() - timedelta(days=365)
        else:
            start_date = datetime.now() - timedelta(days=180)
        
        # Search for repositories
        query = SearchQuery(
            query=technology,
            max_results=100,
            created_after=start_date
        )
        
        async with self.github_client:
            repos = await self.github_client.search_repositories(query)
        
        # Calculate metrics
        total_stars = sum(repo.stars for repo in repos)
        total_forks = sum(repo.forks for repo in repos)
        
        # Calculate growth rate (simplified)
        recent_repos = [repo for repo in repos 
                       if repo.created_at and 
                       (datetime.now() - repo.created_at.replace(tzinfo=None)).days < 30]
        growth_rate = len(recent_repos) / max(len(repos), 1) * 100
        
        # Calculate community activity
        active_repos = [repo for repo in repos 
                       if repo.updated_at and 
                       (datetime.now() - repo.updated_at.replace(tzinfo=None)).days < 7]
        activity_rate = len(active_repos) / max(len(repos), 1) * 100
        
        # Get top contributors/repositories
        top_repos = sorted(repos, key=lambda x: x.stars, reverse=True)[:5]
        
        return TrendAnalysis(
            technology=technology,
            popularity_score=min(total_stars / 100, 100),  # Normalized
            growth_rate=growth_rate,
            adoption_rate=len(repos),  # Simple adoption metric
            community_activity=activity_rate,
            recent_projects=[repo.full_name for repo in recent_repos[:5]],
            key_contributors=[repo.owner for repo in top_repos]
        )
    
    async def _get_technology_metrics(self, technology: str) -> Dict[str, Any]:
        """Get comprehensive metrics for a technology."""
        query = SearchQuery(query=technology, max_results=50)
        
        async with self.github_client:
            repos = await self.github_client.search_repositories(query)
        
        return {
            "total_repositories": len(repos),
            "total_stars": sum(repo.stars for repo in repos),
            "total_forks": sum(repo.forks for repo in repos),
            "average_stars": sum(repo.stars for repo in repos) / max(len(repos), 1),
            "languages": Counter(repo.language for repo in repos if repo.language),
            "recent_activity": len([repo for repo in repos 
                                  if repo.updated_at and 
                                  (datetime.now() - repo.updated_at.replace(tzinfo=None)).days < 30]),
            "top_repositories": [
                {"name": repo.full_name, "stars": repo.stars, "description": repo.description}
                for repo in sorted(repos, key=lambda x: x.stars, reverse=True)[:3]
            ]
        }
    
    async def _calculate_framework_metrics(self, framework: str, 
                                         repositories: List[RepositoryInfo]) -> Dict[str, Any]:
        """Calculate metrics specific to frameworks."""
        return {
            "framework_name": framework,
            "repository_count": len(repositories),
            "total_stars": sum(repo.stars for repo in repositories),
            "average_stars": sum(repo.stars for repo in repositories) / max(len(repositories), 1),
            "languages_used": Counter(repo.language for repo in repositories if repo.language),
            "last_updated": max((repo.updated_at for repo in repositories 
                               if repo.updated_at), default=None),
            "maturity_score": self._calculate_maturity_score(repositories),
            "example_projects": [repo.full_name for repo in repositories[:3]]
        }
    
    def _calculate_maturity_score(self, repositories: List[RepositoryInfo]) -> float:
        """Calculate framework maturity score."""
        if not repositories:
            return 0.0
        
        score = 0.0
        
        # Age factor
        oldest_repo = min((repo.created_at for repo in repositories 
                          if repo.created_at), default=datetime.now())
        age_years = (datetime.now() - oldest_repo.replace(tzinfo=None)).days / 365
        score += min(age_years * 10, 30)  # Max 30 points for age
        
        # Popularity factor
        avg_stars = sum(repo.stars for repo in repositories) / len(repositories)
        score += min(avg_stars / 100, 40)  # Max 40 points for popularity
        
        # Activity factor
        recent_updates = sum(1 for repo in repositories 
                           if repo.updated_at and 
                           (datetime.now() - repo.updated_at.replace(tzinfo=None)).days < 90)
        activity_ratio = recent_updates / len(repositories)
        score += activity_ratio * 30  # Max 30 points for activity
        
        return min(score, 100.0)
    
    def _generate_comparison_insights(self, comparison_data: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate insights from technology comparison."""
        insights = []
        
        # Find most popular
        most_popular = max(comparison_data.items(), key=lambda x: x[1]["total_stars"])
        insights.append(f"{most_popular[0]} has the highest total stars ({most_popular[1]['total_stars']:,})")
        
        # Find fastest growing
        growth_rates = {tech: data.get("recent_activity", 0) 
                       for tech, data in comparison_data.items()}
        fastest_growing = max(growth_rates.items(), key=lambda x: x[1])
        insights.append(f"{fastest_growing[0]} shows the highest recent activity ({fastest_growing[1]} active repos)")
        
        # Find most diverse
        language_counts = {tech: len(data.get("languages", {})) 
                         for tech, data in comparison_data.items()}
        most_diverse = max(language_counts.items(), key=lambda x: x[1])
        insights.append(f"{most_diverse[0]} is used across the most languages ({most_diverse[1]} different languages)")
        
        return insights


class DocumentationAgent(BaseAgent):
    """Agent specialized in generating documentation and summaries."""
    
    def __init__(self, github_client: GitHubAPIClient):
        super().__init__("documentation_agent", "Documentation Agent",
                        "Generates documentation and summaries")
        self.github_client = github_client
        self.code_analyzer = CodeAnalyzer()
        
        # Register capabilities
        from ..models import AgentCapability
        self.register_capability(AgentCapability(
            name="documentation_generation",
            description="Generate documentation for repositories and code",
            input_types=["RepositoryInfo", "List[CodeFile]"],
            output_types=["Dict[str, str]"],
            cost_estimate=0.3,
            execution_time_estimate=20.0
        ))
        
        self.register_capability(AgentCapability(
            name="summary_generation",
            description="Generate summaries and reports",
            input_types=["Dict[str, Any]"],
            output_types=["str"],
            cost_estimate=0.2,
            execution_time_estimate=10.0
        ))
    
    async def can_handle(self, goal: AgentGoal) -> bool:
        """Check if this agent can handle the goal."""
        doc_keywords = ["document", "documentation", "summary", "report", "generate", "readme"]
        return any(keyword in goal.description.lower() for keyword in doc_keywords)
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """Execute documentation-related goals."""
        self.logger.info(f"Executing documentation goal: {goal.description}")
        
        start_time = datetime.now()
        
        try:
            if "generate documentation" in goal.description.lower():
                return await self._generate_documentation(goal)
            elif "create summary" in goal.description.lower():
                return await self._create_summary(goal)
            elif "generate report" in goal.description.lower():
                return await self._generate_report(goal)
            else:
                return await self._general_documentation(goal)
                
        except Exception as e:
            self.logger.error(f"Documentation goal execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _generate_documentation(self, goal: AgentGoal) -> Dict[str, Any]:
        """Generate documentation for a repository."""
        repository = goal.context.get("repository")
        analysis_result = goal.context.get("analysis_result")
        
        if not repository:
            raise ValueError("Repository information required for documentation")
        
        documentation = {
            "readme": await self._generate_readme(repository, analysis_result),
            "api_docs": await self._generate_api_docs(repository, analysis_result),
            "architecture": await self._generate_architecture_docs(repository, analysis_result),
            "contributing": await self._generate_contributing_guide(repository),
            "changelog": await self._generate_changelog_template(repository)
        }
        
        return {
            "success": True,
            "documentation": documentation,
            "repository": repository
        }
    
    async def _create_summary(self, goal: AgentGoal) -> Dict[str, Any]:
        """Create summary of analysis results."""
        data = goal.context.get("data", {})
        summary_type = goal.context.get("type", "general")
        
        if summary_type == "security":
            summary = self._create_security_summary(data)
        elif summary_type == "trend":
            summary = self._create_trend_summary(data)
        elif summary_type == "analysis":
            summary = self._create_analysis_summary(data)
        else:
            summary = self._create_general_summary(data)
        
        return {
            "success": True,
            "summary": summary,
            "summary_type": summary_type
        }
    
    async def _generate_report(self, goal: AgentGoal) -> Dict[str, Any]:
        """Generate comprehensive report."""
        search_results = goal.context.get("search_results", [])
        analyses = goal.context.get("analyses", [])
        trends = goal.context.get("trends", [])
        
        report = self._create_comprehensive_report(search_results, analyses, trends)
        
        return {
            "success": True,
            "report": report,
            "report_sections": ["executive_summary", "findings", "recommendations", "appendix"]
        }
    
    async def _general_documentation(self, goal: AgentGoal) -> Dict[str, Any]:
        """Handle general documentation requests."""
        return await self._generate_documentation(goal)
    
    async def _generate_readme(self, repository: Dict[str, Any], 
                             analysis_result: Optional[Dict[str, Any]] = None) -> str:
        """Generate README.md content."""
        repo_name = repository.get("name", "Repository")
        description = repository.get("description", "No description provided")
        language = repository.get("language", "Unknown")
        
        readme_content = f"""# {repo_name}

{description}

## Overview

This is a {language} project with the following characteristics:

"""
        
        if analysis_result:
            details = analysis_result.get("details", {})
            structure = details.get("structure_analysis", {})
            
            readme_content += f"""### Project Statistics

- **Primary Language**: {language}
- **Total Files**: {structure.get('total_files', 'Unknown')}
- **Quality Score**: {details.get('overall_quality', 0):.1f}/100
- **Languages Used**: {', '.join(structure.get('languages', {}).keys())}

"""
        
        readme_content += f"""## Installation

```bash
# Clone the repository
git clone {repository.get('clone_url', '')}
cd {repo_name.lower()}

# Install dependencies
# Add specific installation instructions based on the language
```

## Usage

```{language.lower() if language else 'bash'}
# Add usage examples here
```

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

{repository.get('license', 'No license specified')}

## Contact

Repository: [{repository.get('full_name', '')}]({repository.get('html_url', '')})
"""
        
        return readme_content
    
    async def _generate_api_docs(self, repository: Dict[str, Any], 
                                analysis_result: Optional[Dict[str, Any]] = None) -> str:
        """Generate API documentation."""
        if not analysis_result:
            return "# API Documentation\n\n*API documentation will be generated after code analysis.*"
        
        code_files = analysis_result.get("code_files", [])
        api_functions = []
        
        for file_info in code_files:
            if hasattr(file_info, 'functions'):
                api_functions.extend(file_info.functions)
        
        api_docs = "# API Documentation\n\n"
        
        if api_functions:
            api_docs += "## Available Functions\n\n"
            for func in api_functions[:10]:  # Limit to first 10
                api_docs += f"### `{func}`\n\n*Documentation pending*\n\n"
        else:
            api_docs += "*No API functions detected in the analyzed code.*\n"
        
        return api_docs
    
    async def _generate_architecture_docs(self, repository: Dict[str, Any], 
                                        analysis_result: Optional[Dict[str, Any]] = None) -> str:
        """Generate architecture documentation."""
        arch_docs = "# Architecture Documentation\n\n"
        
        if analysis_result:
            details = analysis_result.get("details", {})
            structure = details.get("structure_analysis", {})
            
            arch_docs += f"""## Project Structure

- **Project Type**: {structure.get('project_type', 'Unknown')}
- **Frameworks**: {', '.join(structure.get('frameworks', []))}
- **Structure Score**: {structure.get('structure_score', 0):.1f}/100

## File Organization

"""
            
            languages = structure.get("languages", {})
            for lang, count in languages.items():
                arch_docs += f"- **{lang}**: {count} files\n"
        else:
            arch_docs += "*Architecture analysis pending.*"
        
        return arch_docs
    
    async def _generate_contributing_guide(self, repository: Dict[str, Any]) -> str:
        """Generate contributing guidelines."""
        return """# Contributing Guidelines

## Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Code Style

Please follow the established code style and conventions.

## Testing

Ensure all tests pass before submitting your changes.

## Issue Reporting

Please use the issue tracker to report bugs or request features.
"""
    
    async def _generate_changelog_template(self, repository: Dict[str, Any]) -> str:
        """Generate changelog template."""
        return f"""# Changelog

All notable changes to {repository.get('name', 'this project')} will be documented in this file.

## [Unreleased]

### Added
- 

### Changed
- 

### Fixed
- 

## [1.0.0] - {datetime.now().strftime('%Y-%m-%d')}

### Added
- Initial release
"""
    
    def _create_security_summary(self, data: Dict[str, Any]) -> str:
        """Create security analysis summary."""
        security_issues = data.get("security_issues", [])
        issue_summary = data.get("issue_summary", {})
        security_score = data.get("security_score", 0)
        
        summary = f"""# Security Analysis Summary

**Overall Security Score**: {security_score:.1f}/100

## Issue Summary
- **Critical**: {issue_summary.get('critical', 0)}
- **High**: {issue_summary.get('high', 0)}
- **Medium**: {issue_summary.get('medium', 0)}
- **Low**: {issue_summary.get('low', 0)}

## Key Findings
"""
        
        if security_issues:
            critical_issues = [issue for issue in security_issues if hasattr(issue, 'severity') and issue.severity == "CRITICAL"]
            if critical_issues:
                summary += "\n### Critical Issues\n"
                for issue in critical_issues[:3]:
                    summary += f"- {issue.type}: {issue.description}\n"
        else:
            summary += "\nNo significant security issues detected."
        
        return summary
    
    def _create_trend_summary(self, data: Dict[str, Any]) -> str:
        """Create trend analysis summary."""
        trend_analyses = data.get("trend_analyses", [])
        
        summary = "# Technology Trend Analysis\n\n"
        
        if trend_analyses:
            summary += "## Top Trending Technologies\n\n"
            for i, trend in enumerate(trend_analyses[:5], 1):
                if hasattr(trend, 'technology'):
                    summary += f"{i}. **{trend.technology}** - Popularity Score: {trend.popularity_score:.1f}\n"
        
        return summary
    
    def _create_analysis_summary(self, data: Dict[str, Any]) -> str:
        """Create code analysis summary."""
        analysis = data.get("analysis", {})
        
        if hasattr(analysis, 'score'):
            score = analysis.score
            summary_text = analysis.summary
        else:
            score = data.get("score", 0)
            summary_text = data.get("summary", "Analysis completed")
        
        return f"""# Code Analysis Summary

**Overall Score**: {score:.1f}/100

## Summary
{summary_text}

## Details
{json.dumps(data.get("details", {}), indent=2) if data.get("details") else "No additional details available"}
"""
    
    def _create_general_summary(self, data: Dict[str, Any]) -> str:
        """Create general summary."""
        return f"""# Analysis Summary

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
{json.dumps(data, indent=2)}
"""
    
    def _create_comprehensive_report(self, search_results: List[Any], 
                                   analyses: List[Any], trends: List[Any]) -> str:
        """Create comprehensive analysis report."""
        report = f"""# GitHub Search and Analysis Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report provides a comprehensive analysis of GitHub repositories, including search results, code quality assessments, and technology trend analysis.

## Search Results Summary

- **Total Repositories Analyzed**: {len(search_results)}
- **Analysis Results**: {len(analyses)}
- **Trend Analyses**: {len(trends)}

## Key Findings

### Repository Quality
"""
        
        if analyses:
            avg_quality = sum(getattr(a, 'score', 0) for a in analyses) / len(analyses)
            report += f"- Average Quality Score: {avg_quality:.1f}/100\n"
        
        report += """
### Technology Trends
"""
        
        if trends:
            top_trend = max(trends, key=lambda x: getattr(x, 'popularity_score', 0))
            if hasattr(top_trend, 'technology'):
                report += f"- Most Popular Technology: {top_trend.technology}\n"
        
        report += """
## Recommendations

1. Focus on repositories with high quality scores for reliable solutions
2. Consider trending technologies for future projects
3. Review security findings before implementation

## Appendix

### Methodology
- Repository search using GitHub API
- Code analysis using static analysis tools
- Trend analysis based on repository metrics and activity

### Limitations
- Analysis limited to publicly available repositories
- Code quality assessment based on static analysis only
- Trend analysis reflects GitHub activity patterns
"""
        
        return report
