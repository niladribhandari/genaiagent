"""
Main Web Search System using Agentic AI principles.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .agentic import (
    AgentOrchestrator, WebSearchAgent, ContentAnalysisAgent, 
    FactCheckingAgent, SummarizationAgent, TrendMonitoringAgent,
    AgentGoal
)
from .utils import WebSearchClient
from .models import SearchResult, SearchQuery

logger = logging.getLogger(__name__)

class WebSearchSystem:
    """
    Main system for intelligent web search using multiple AI agents.
    Implements Agentic AI principles for autonomous, goal-oriented search and analysis.
    """
    
    def __init__(self):
        """Initialize the Web Search System."""
        self.orchestrator = AgentOrchestrator()
        self.search_client = WebSearchClient()
        
        # Initialize agents
        self._initialize_agents()
        
        logger.info("Initialized WebSearchSystem with Agentic AI architecture")
    
    def _initialize_agents(self):
        """Initialize and connect all agents."""
        # Create specialized agents
        self.web_search_agent = WebSearchAgent()
        self.content_analysis_agent = ContentAnalysisAgent()
        self.fact_checking_agent = FactCheckingAgent()
        self.summarization_agent = SummarizationAgent()
        self.trend_monitoring_agent = TrendMonitoringAgent()
        
        # Add agents to orchestrator
        self.orchestrator.add_agent(self.web_search_agent)
        self.orchestrator.add_agent(self.content_analysis_agent)
        self.orchestrator.add_agent(self.fact_checking_agent)
        self.orchestrator.add_agent(self.summarization_agent)
        self.orchestrator.add_agent(self.trend_monitoring_agent)
        
        logger.info("Initialized 5 specialized agents in orchestrator")
    
    async def intelligent_search(self, query: str, search_type: str = "comprehensive", **kwargs) -> Dict[str, Any]:
        """
        Perform intelligent search with AI agent collaboration.
        
        Args:
            query: Search query
            search_type: Type of search (comprehensive, quick, academic, news, trends)
            **kwargs: Additional search parameters
            
        Returns:
            Comprehensive search results and analysis
        """
        logger.info(f"Starting intelligent search: '{query}' (type: {search_type})")
        
        try:
            # Create high-level goal
            goal_description = f"Perform {search_type} search and analysis for: {query}"
            
            # Add search parameters to context
            context = {
                "query": query,
                "search_type": search_type,
                "max_results": kwargs.get("max_results", 10),
                "include_analysis": kwargs.get("include_analysis", True),
                "include_fact_check": kwargs.get("include_fact_check", False),
                "include_summary": kwargs.get("include_summary", True),
                "include_trends": kwargs.get("include_trends", False)
            }
            
            # Execute search through orchestrator
            results = await self.orchestrator.execute_goal(goal_description, context)
            
            # Enhance results with additional processing
            enhanced_results = await self._enhance_search_results(results, context)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Intelligent search failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "query": query,
                "search_type": search_type
            }
    
    async def smart_search(self, query: str, max_results: int = 10, **kwargs) -> List[SearchResult]:
        """
        Perform smart web search with result optimization.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            **kwargs: Additional search parameters
            
        Returns:
            List of optimized search results
        """
        try:
            # Use search client directly for basic search
            results = await self.search_client.search(
                query=query,
                max_results=max_results,
                **kwargs
            )
            
            # Enhance with AI analysis
            enhanced_results = []
            for result in results:
                # Add relevance scoring and content preview
                enhanced_result = await self._enhance_single_result(result, query)
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Smart search failed: {str(e)}")
            return []
    
    async def analyze_search_results(self, search_results: List[SearchResult], query: str) -> Dict[str, Any]:
        """
        Analyze search results using AI agents.
        
        Args:
            search_results: List of search results to analyze
            query: Original search query
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Prepare content for analysis
            content_list = []
            for result in search_results:
                content_list.append(f"{result.title}: {result.description}")
            
            # Create analysis goal
            analysis_goal = AgentGoal(
                id=f"analysis_{datetime.now().timestamp()}",
                description=f"Analyze search results for query: {query}",
                target_outcome="Comprehensive analysis of search results",
                context={
                    "search_results": search_results,
                    "content_list": content_list,
                    "query": query
                }
            )
            
            # Execute analysis with content analysis agent
            analysis_results = await self.content_analysis_agent.set_goal(analysis_goal)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Search results analysis failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def fact_check_results(self, search_results: List[SearchResult], claims: List[str] = None) -> Dict[str, Any]:
        """
        Fact-check search results and claims.
        
        Args:
            search_results: Search results to fact-check
            claims: Specific claims to verify
            
        Returns:
            Fact-checking results
        """
        try:
            # Extract content from search results
            sources = []
            for result in search_results:
                sources.append(f"{result.title}: {result.description}")
            
            # Auto-extract claims if not provided
            if not claims:
                claims = []
                for result in search_results:
                    # Simple claim extraction from titles and descriptions
                    if result.description:
                        sentences = result.description.split('. ')
                        claims.extend(sentences[:2])  # Take first 2 sentences as potential claims
            
            # Create fact-checking goal
            fact_check_goal = AgentGoal(
                id=f"factcheck_{datetime.now().timestamp()}",
                description="Fact-check search results and verify claims",
                target_outcome="Verified facts and credibility assessment",
                context={
                    "claims": claims[:10],  # Limit to 10 claims
                    "sources": sources,
                    "search_results": search_results
                }
            )
            
            # Execute fact-checking
            fact_check_results = await self.fact_checking_agent.set_goal(fact_check_goal)
            
            return fact_check_results
            
        except Exception as e:
            logger.error(f"Fact-checking failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def summarize_results(self, search_results: List[SearchResult], summary_type: str = "standard") -> Dict[str, Any]:
        """
        Create summaries from search results.
        
        Args:
            search_results: Search results to summarize
            summary_type: Type of summary (standard, executive, bullet_points, key_points)
            
        Returns:
            Summarization results
        """
        try:
            # Combine content from search results
            combined_content = ""
            for result in search_results:
                combined_content += f"{result.title}\n{result.description}\n\n"
            
            # Create summarization goal
            summary_goal = AgentGoal(
                id=f"summary_{datetime.now().timestamp()}",
                description=f"Create {summary_type} summary of search results",
                target_outcome="Concise and comprehensive summary",
                context={
                    "content": combined_content,
                    "search_results": search_results,
                    "summary_type": summary_type
                }
            )
            
            # Execute summarization
            summary_results = await self.summarization_agent.set_goal(summary_goal)
            
            return summary_results
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def monitor_trends(self, query: str, search_results: List[SearchResult] = None) -> Dict[str, Any]:
        """
        Monitor trends related to search query.
        
        Args:
            query: Search query to monitor trends for
            search_results: Optional search results to analyze
            
        Returns:
            Trend analysis results
        """
        try:
            # Get search results if not provided
            if not search_results:
                search_results = await self.smart_search(query, max_results=20)
            
            # Create trend monitoring goal
            trend_goal = AgentGoal(
                id=f"trends_{datetime.now().timestamp()}",
                description=f"Monitor trends for query: {query}",
                target_outcome="Trend analysis and insights",
                context={
                    "query": query,
                    "search_results": search_results,
                    "content_list": [f"{r.title}: {r.description}" for r in search_results]
                }
            )
            
            # Execute trend monitoring
            trend_results = await self.trend_monitoring_agent.set_goal(trend_goal)
            
            return trend_results
            
        except Exception as e:
            logger.error(f"Trend monitoring failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def comprehensive_search_analysis(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Perform comprehensive search with full AI analysis pipeline.
        
        Args:
            query: Search query
            **kwargs: Additional parameters
            
        Returns:
            Complete analysis including search, content analysis, fact-checking, and trends
        """
        try:
            logger.info(f"Starting comprehensive search analysis for: {query}")
            
            # Step 1: Perform search
            search_results = await self.smart_search(query, max_results=kwargs.get("max_results", 15))
            
            if not search_results:
                return {
                    "status": "failed",
                    "error": "No search results found",
                    "query": query
                }
            
            # Step 2: Run analyses in parallel
            analyses = await asyncio.gather(
                self.analyze_search_results(search_results, query),
                self.fact_check_results(search_results),
                self.summarize_results(search_results, "executive"),
                self.monitor_trends(query, search_results),
                return_exceptions=True
            )
            
            # Process results
            content_analysis = analyses[0] if not isinstance(analyses[0], Exception) else {"error": str(analyses[0])}
            fact_check = analyses[1] if not isinstance(analyses[1], Exception) else {"error": str(analyses[1])}
            summary = analyses[2] if not isinstance(analyses[2], Exception) else {"error": str(analyses[2])}
            trends = analyses[3] if not isinstance(analyses[3], Exception) else {"error": str(analyses[3])}
            
            # Compile comprehensive results
            comprehensive_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "search_results": {
                    "total_found": len(search_results),
                    "results": search_results[:10],  # Include top 10 results
                    "domains": list(set(r.domain for r in search_results if r.domain))
                },
                "content_analysis": content_analysis,
                "fact_check": fact_check,
                "summary": summary,
                "trends": trends,
                "insights": self._generate_comprehensive_insights(
                    search_results, content_analysis, fact_check, summary, trends
                ),
                "status": "completed"
            }
            
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"Comprehensive search analysis failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "query": query
            }
    
    async def _enhance_search_results(self, orchestrator_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance orchestrator results with additional processing."""
        
        enhanced = {
            "orchestrator_results": orchestrator_results,
            "search_metadata": {
                "query": context.get("query"),
                "search_type": context.get("search_type"),
                "timestamp": datetime.now().isoformat(),
                "agents_involved": orchestrator_results.get("agents_involved", []),
                "confidence": orchestrator_results.get("confidence_score", 0.0)
            }
        }
        
        # Extract search results from orchestrator results
        search_results = []
        if "results_by_agent" in orchestrator_results:
            for agent_name, agent_results in orchestrator_results["results_by_agent"].items():
                if agent_name == "WebSearchAgent":
                    for result in agent_results:
                        if isinstance(result, dict) and "search_results" in result:
                            search_results.extend(result["search_results"])
        
        enhanced["processed_results"] = search_results
        
        return enhanced
    
    async def _enhance_single_result(self, result: SearchResult, query: str) -> SearchResult:
        """Enhance a single search result with additional analysis."""
        try:
            # Calculate query relevance
            query_words = set(query.lower().split())
            title_words = set(result.title.lower().split())
            desc_words = set(result.description.lower().split())
            
            title_overlap = len(query_words.intersection(title_words))
            desc_overlap = len(query_words.intersection(desc_words))
            
            # Enhanced relevance score
            relevance = (title_overlap * 2 + desc_overlap) / max(len(query_words), 1)
            result.relevance_score = min(relevance, 1.0)
            
            # Add analysis metadata
            if not result.metadata:
                result.metadata = {}
            
            result.metadata.update({
                "enhanced": True,
                "query_relevance": relevance,
                "title_match": title_overlap > 0,
                "description_match": desc_overlap > 0
            })
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to enhance result: {str(e)}")
            return result
    
    def _generate_comprehensive_insights(self, search_results: List[SearchResult], 
                                       content_analysis: Dict[str, Any],
                                       fact_check: Dict[str, Any],
                                       summary: Dict[str, Any],
                                       trends: Dict[str, Any]) -> List[str]:
        """Generate insights from comprehensive analysis."""
        insights = []
        
        # Search insights
        if search_results:
            insights.append(f"Found {len(search_results)} relevant results")
            
            domains = [r.domain for r in search_results if r.domain]
            unique_domains = len(set(domains))
            insights.append(f"Results span {unique_domains} different domains")
        
        # Content analysis insights
        if "analyses" in content_analysis and "sentiment" in content_analysis["analyses"]:
            sentiment = content_analysis["analyses"]["sentiment"]
            if "label" in sentiment:
                insights.append(f"Overall content sentiment: {sentiment['label']}")
        
        # Fact-check insights
        if "overall_credibility" in fact_check:
            credibility = fact_check["overall_credibility"]
            insights.append(f"Information credibility score: {credibility:.1%}")
        
        # Summary insights
        if "summary" in summary and "compression_ratio" in summary:
            compression = summary["compression_ratio"]
            insights.append(f"Content summarized with {compression:.1%} compression ratio")
        
        # Trend insights
        if "trending_score" in trends:
            trending = trends["trending_score"]
            if trending > 0.7:
                insights.append("High trending activity detected")
            elif trending > 0.4:
                insights.append("Moderate trending activity detected")
        
        return insights
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "system_status": "active",
            "orchestrator": self.orchestrator.get_system_status(),
            "search_client": "connected" if self.search_client else "disconnected",
            "timestamp": datetime.now().isoformat()
        }
    
    async def close(self):
        """Close the system and cleanup resources."""
        try:
            await self.search_client.close()
            logger.info("WebSearchSystem closed successfully")
        except Exception as e:
            logger.error(f"Error closing WebSearchSystem: {str(e)}")

# Convenience function for quick usage
async def quick_search(query: str, max_results: int = 10) -> List[SearchResult]:
    """
    Quick search function for simple use cases.
    
    Args:
        query: Search query
        max_results: Maximum results to return
        
    Returns:
        List of search results
    """
    system = WebSearchSystem()
    try:
        results = await system.smart_search(query, max_results)
        return results
    finally:
        await system.close()
