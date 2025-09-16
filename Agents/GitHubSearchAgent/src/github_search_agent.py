"""
Main GitHub Search Agent System based on Agentic AI principles.
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

from .agentic.core import AgentOrchestrator
from .agentic.agents import GitHubSearchAgent, CodeAnalysisAgent, SecurityAnalysisAgent
from .agentic.trend_docs_agents import TrendAnalysisAgent, DocumentationAgent
from .models import (
    AgentGoal, SearchQuery, RepositoryInfo, AnalysisResult, 
    SearchResult, Priority, AnalysisType, SearchScope
)
from .utils.github_api import GitHubAPIClient

# Load environment variables
load_dotenv()


class GitHubSearchSystem:
    """
    Main GitHub Search System orchestrating multiple specialized agents.
    
    This system implements Agentic AI principles with autonomous agents
    that can collaborate to perform complex GitHub search and analysis tasks.
    """
    
    def __init__(self, github_token: Optional[str] = None, 
                 openai_api_key: Optional[str] = None):
        """
        Initialize the GitHub Search System.
        
        Args:
            github_token: GitHub API token (optional, will try to load from env)
            openai_api_key: OpenAI API key for enhanced analysis (optional)
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("github_search_system")
        
        # Get API keys
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.github_token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass github_token parameter.")
        
        # Initialize GitHub API client
        self.github_client = GitHubAPIClient(self.github_token)
        
        # Initialize orchestrator and agents
        self.orchestrator = AgentOrchestrator()
        self._initialize_agents()
        
        self.logger.info("GitHub Search System initialized with 5 specialized agents")
    
    def _initialize_agents(self):
        """Initialize and register all specialized agents."""
        # Create agents
        self.search_agent = GitHubSearchAgent(self.github_client)
        self.analysis_agent = CodeAnalysisAgent(self.github_client)
        self.security_agent = SecurityAnalysisAgent(self.github_client)
        self.trend_agent = TrendAnalysisAgent(self.github_client)
        self.documentation_agent = DocumentationAgent(self.github_client)
        
        # Register with orchestrator
        self.orchestrator.register_agent(self.search_agent)
        self.orchestrator.register_agent(self.analysis_agent)
        self.orchestrator.register_agent(self.security_agent)
        self.orchestrator.register_agent(self.trend_agent)
        self.orchestrator.register_agent(self.documentation_agent)
        
        self.logger.info(f"Registered {len(self.orchestrator.agents)} agents with orchestrator")
    
    async def search_repositories(self, query: str, max_results: int = 50, 
                                language: Optional[str] = None,
                                min_stars: int = 0,
                                include_analysis: bool = False,
                                include_security_scan: bool = False) -> SearchResult:
        """
        Search for repositories with optional analysis.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            language: Filter by programming language
            min_stars: Minimum star count
            include_analysis: Whether to include code analysis
            include_security_scan: Whether to include security scanning
            
        Returns:
            SearchResult object containing repositories and analyses
        """
        self.logger.info(f"Starting repository search: '{query}'")
        start_time = datetime.now()
        
        try:
            # Create search query
            search_query = SearchQuery(
                query=query,
                max_results=max_results,
                language=language,
                min_stars=min_stars
            )
            
            # Create search goal
            search_goal = AgentGoal(
                id=f"search_{datetime.now().timestamp()}",
                description="search repositories",
                priority=Priority.HIGH,
                context={
                    "search_query": search_query.__dict__,
                    "query": query,
                    "max_results": max_results
                }
            )
            
            # Execute search
            search_result = await self.orchestrator.execute_goal(search_goal)
            
            if not search_result["success"]:
                raise Exception(f"Search failed: {search_result.get('error', 'Unknown error')}")
            
            repositories = search_result["result"]["repositories"]
            
            # Perform additional analysis if requested
            analyses = []
            if include_analysis or include_security_scan:
                for repo_data in repositories[:min(10, len(repositories))]:  # Limit analysis
                    repo_analyses = await self._analyze_repository(
                        repo_data, include_analysis, include_security_scan
                    )
                    analyses.extend(repo_analyses)
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            return SearchResult(
                query=search_query,
                repositories=[r["repository"] if isinstance(r, dict) else r for r in repositories],
                analyses=analyses,
                total_count=len(repositories),
                search_time=search_time,
                analysis_time=sum(getattr(a, 'analyzed_at', datetime.now()).timestamp() - start_time.timestamp() 
                                for a in analyses) if analyses else 0.0,
                success=True,
                searched_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Repository search failed: {str(e)}")
            return SearchResult(
                query=SearchQuery(query=query),
                success=False,
                error_message=str(e),
                search_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def analyze_repository(self, owner: str, repo: str, 
                               include_security: bool = True,
                               include_trends: bool = True) -> AnalysisResult:
        """
        Perform comprehensive analysis of a specific repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            include_security: Include security analysis
            include_trends: Include trend analysis
            
        Returns:
            AnalysisResult object with comprehensive analysis
        """
        self.logger.info(f"Starting repository analysis: {owner}/{repo}")
        
        try:
            # Get repository details first
            details_goal = AgentGoal(
                id=f"details_{datetime.now().timestamp()}",
                description="repository details",
                priority=Priority.HIGH,
                context={"owner": owner, "repo": repo}
            )
            
            details_result = await self.orchestrator.execute_goal(details_goal)
            if not details_result["success"]:
                raise Exception(f"Failed to get repository details: {details_result.get('error')}")
            
            repository = details_result["result"]["repository"]
            
            # Create analysis goals
            goals = []
            
            # Code analysis goal
            analysis_goal = AgentGoal(
                id=f"analysis_{datetime.now().timestamp()}",
                description="analyze repository",
                priority=Priority.HIGH,
                context={"repository": repository.__dict__ if hasattr(repository, '__dict__') else repository}
            )
            goals.append(analysis_goal)
            
            # Security analysis goal
            if include_security:
                security_goal = AgentGoal(
                    id=f"security_{datetime.now().timestamp()}",
                    description="security scan",
                    priority=Priority.MEDIUM,
                    context={"repository": repository.__dict__ if hasattr(repository, '__dict__') else repository}
                )
                goals.append(security_goal)
            
            # Execute analysis goals
            results = await self.orchestrator.execute_multi_goal_workflow(goals)
            
            # Process results
            analysis_data = None
            security_issues = []
            
            for result in results:
                if result["success"]:
                    if "analysis" in result["result"]:
                        analysis_data = result["result"]["analysis"]
                    elif "security_issues" in result["result"]:
                        security_issues = result["result"]["security_issues"]
            
            if analysis_data:
                if security_issues:
                    analysis_data.security_issues = security_issues
                return analysis_data
            else:
                # Create basic analysis result
                return AnalysisResult(
                    repository=repository,
                    analysis_type=AnalysisType.BASIC,
                    score=50.0,
                    summary="Basic repository information retrieved",
                    security_issues=security_issues
                )
                
        except Exception as e:
            self.logger.error(f"Repository analysis failed: {str(e)}")
            raise
    
    async def discover_trending_technologies(self, time_period: str = "6months",
                                           max_technologies: int = 10) -> List[Dict[str, Any]]:
        """
        Discover trending technologies and frameworks.
        
        Args:
            time_period: Analysis time period ("3months", "6months", "1year")
            max_technologies: Maximum number of technologies to analyze
            
        Returns:
            List of trend analysis results
        """
        self.logger.info(f"Discovering trending technologies for {time_period}")
        
        try:
            trend_goal = AgentGoal(
                id=f"trends_{datetime.now().timestamp()}",
                description="analyze trends",
                priority=Priority.MEDIUM,
                context={
                    "time_period": time_period,
                    "max_technologies": max_technologies
                }
            )
            
            result = await self.orchestrator.execute_goal(trend_goal)
            
            if result["success"]:
                return result["result"]["trend_analyses"]
            else:
                raise Exception(f"Trend analysis failed: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Trend discovery failed: {str(e)}")
            raise
    
    async def compare_repositories(self, repositories: List[str]) -> Dict[str, Any]:
        """
        Compare multiple repositories across various metrics.
        
        Args:
            repositories: List of repository names in "owner/repo" format
            
        Returns:
            Comparison results with metrics and insights
        """
        self.logger.info(f"Comparing {len(repositories)} repositories")
        
        try:
            comparison_data = {}
            
            for repo_spec in repositories:
                if "/" in repo_spec:
                    owner, repo = repo_spec.split("/", 1)
                    analysis = await self.analyze_repository(owner, repo, 
                                                           include_security=True, 
                                                           include_trends=False)
                    comparison_data[repo_spec] = {
                        "repository": analysis.repository,
                        "quality_score": analysis.score,
                        "security_issues": len(analysis.security_issues),
                        "summary": analysis.summary,
                        "details": analysis.details
                    }
            
            # Generate comparison insights
            insights = self._generate_comparison_insights(comparison_data)
            
            return {
                "comparison_data": comparison_data,
                "insights": insights,
                "compared_repositories": repositories,
                "comparison_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Repository comparison failed: {str(e)}")
            raise
    
    async def generate_documentation(self, owner: str, repo: str) -> Dict[str, str]:
        """
        Generate comprehensive documentation for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary containing generated documentation sections
        """
        self.logger.info(f"Generating documentation for {owner}/{repo}")
        
        try:
            # First analyze the repository
            analysis = await self.analyze_repository(owner, repo, 
                                                   include_security=False, 
                                                   include_trends=False)
            
            # Create documentation goal
            doc_goal = AgentGoal(
                id=f"docs_{datetime.now().timestamp()}",
                description="generate documentation",
                priority=Priority.MEDIUM,
                context={
                    "repository": analysis.repository.__dict__,
                    "analysis_result": analysis.__dict__
                }
            )
            
            result = await self.orchestrator.execute_goal(doc_goal)
            
            if result["success"]:
                return result["result"]["documentation"]
            else:
                raise Exception(f"Documentation generation failed: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Documentation generation failed: {str(e)}")
            raise
    
    async def create_analysis_report(self, search_results: SearchResult,
                                   include_trends: bool = True) -> str:
        """
        Create a comprehensive analysis report.
        
        Args:
            search_results: SearchResult object from previous search
            include_trends: Whether to include trend analysis
            
        Returns:
            Formatted report string
        """
        self.logger.info("Creating comprehensive analysis report")
        
        try:
            context = {
                "search_results": search_results.repositories,
                "analyses": search_results.analyses,
                "trends": []
            }
            
            if include_trends:
                trends = await self.discover_trending_technologies()
                context["trends"] = trends
            
            report_goal = AgentGoal(
                id=f"report_{datetime.now().timestamp()}",
                description="generate report",
                priority=Priority.LOW,
                context=context
            )
            
            result = await self.orchestrator.execute_goal(report_goal)
            
            if result["success"]:
                return result["result"]["report"]
            else:
                raise Exception(f"Report generation failed: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise
    
    async def _analyze_repository(self, repo_data: Dict[str, Any], 
                                include_analysis: bool, 
                                include_security: bool) -> List[AnalysisResult]:
        """Helper method to analyze a repository."""
        analyses = []
        
        if include_analysis:
            try:
                analysis_goal = AgentGoal(
                    id=f"analysis_{datetime.now().timestamp()}",
                    description="analyze repository",
                    priority=Priority.MEDIUM,
                    context={"repository": repo_data}
                )
                
                result = await self.orchestrator.execute_goal(analysis_goal)
                if result["success"] and "analysis" in result["result"]:
                    analyses.append(result["result"]["analysis"])
                    
            except Exception as e:
                self.logger.warning(f"Analysis failed for repository: {str(e)}")
        
        if include_security:
            try:
                security_goal = AgentGoal(
                    id=f"security_{datetime.now().timestamp()}",
                    description="security scan",
                    priority=Priority.MEDIUM,
                    context={"repository": repo_data}
                )
                
                result = await self.orchestrator.execute_goal(security_goal)
                if result["success"] and "security_issues" in result["result"]:
                    # Create security analysis result
                    security_analysis = AnalysisResult(
                        repository=repo_data,
                        analysis_type=AnalysisType.SECURITY,
                        score=result["result"].get("security_score", 0),
                        summary=f"Security scan found {len(result['result']['security_issues'])} issues",
                        security_issues=result["result"]["security_issues"]
                    )
                    analyses.append(security_analysis)
                    
            except Exception as e:
                self.logger.warning(f"Security scan failed for repository: {str(e)}")
        
        return analyses
    
    def _generate_comparison_insights(self, comparison_data: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate insights from repository comparison."""
        insights = []
        
        if len(comparison_data) < 2:
            return ["Not enough repositories for meaningful comparison"]
        
        # Find highest quality repository
        best_quality = max(comparison_data.items(), key=lambda x: x[1]["quality_score"])
        insights.append(f"{best_quality[0]} has the highest quality score ({best_quality[1]['quality_score']:.1f})")
        
        # Find most secure repository
        security_scores = {repo: data["security_issues"] for repo, data in comparison_data.items()}
        most_secure = min(security_scores.items(), key=lambda x: x[1])
        insights.append(f"{most_secure[0]} has the fewest security issues ({most_secure[1]} issues)")
        
        return insights
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics."""
        return self.orchestrator.get_system_status()
    
    async def close(self):
        """Clean up resources."""
        # Close GitHub API client if needed
        self.github_client.clear_cache()
        self.logger.info("GitHub Search System closed")


# Convenience functions for quick access
async def search_repositories(query: str, github_token: Optional[str] = None, 
                            max_results: int = 20) -> SearchResult:
    """
    Quick repository search function.
    
    Args:
        query: Search query
        github_token: GitHub API token (optional)
        max_results: Maximum results to return
        
    Returns:
        SearchResult object
    """
    system = GitHubSearchSystem(github_token)
    try:
        return await system.search_repositories(query, max_results=max_results)
    finally:
        await system.close()


async def analyze_repository(owner: str, repo: str, 
                           github_token: Optional[str] = None) -> AnalysisResult:
    """
    Quick repository analysis function.
    
    Args:
        owner: Repository owner
        repo: Repository name
        github_token: GitHub API token (optional)
        
    Returns:
        AnalysisResult object
    """
    system = GitHubSearchSystem(github_token)
    try:
        return await system.analyze_repository(owner, repo)
    finally:
        await system.close()


if __name__ == "__main__":
    # Example usage
    async def main():
        system = GitHubSearchSystem()
        
        try:
            # Search for machine learning repositories
            results = await system.search_repositories(
                "machine learning python",
                max_results=10,
                include_analysis=True
            )
            
            print(f"Found {results.total_count} repositories")
            for repo in results.repositories[:3]:
                print(f"- {repo.full_name}: {repo.stars} stars")
            
            # Analyze a specific repository
            if results.repositories:
                top_repo = results.repositories[0]
                analysis = await system.analyze_repository(
                    top_repo.owner, top_repo.name
                )
                print(f"\nAnalysis of {top_repo.full_name}:")
                print(f"Quality Score: {analysis.score:.1f}")
                print(f"Security Issues: {len(analysis.security_issues)}")
            
        finally:
            await system.close()
    
    # Run example
    asyncio.run(main())
