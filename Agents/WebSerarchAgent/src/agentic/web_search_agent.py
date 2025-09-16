"""
Web Search Agent for intelligent information retrieval.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentGoal, AgentCapability
from ..utils.web_search_client import WebSearchClient
from ..models.search_models import SearchResult, SearchQuery

logger = logging.getLogger(__name__)

class WebSearchAgent(BaseAgent):
    """
    Specialized agent for web search and information retrieval.
    Implements intelligent search strategies and result filtering.
    """
    
    def __init__(self, name: str = "WebSearchAgent"):
        """Initialize the Web Search Agent."""
        capabilities = [
            AgentCapability(
                name="web_search",
                description="Search the web for information using multiple search engines",
                input_types=["search_query", "keywords", "topic"],
                output_types=["search_results", "web_content", "urls"]
            ),
            AgentCapability(
                name="advanced_search",
                description="Perform advanced search with filters and operators",
                input_types=["complex_query", "search_parameters"],
                output_types=["filtered_results", "targeted_content"]
            ),
            AgentCapability(
                name="content_retrieval",
                description="Retrieve and extract content from web pages",
                input_types=["urls", "web_links"],
                output_types=["page_content", "extracted_text", "metadata"]
            ),
            AgentCapability(
                name="search_optimization",
                description="Optimize search queries for better results",
                input_types=["raw_query", "search_intent"],
                output_types=["optimized_query", "search_strategy"]
            )
        ]
        
        super().__init__(name, capabilities)
        self.search_client = WebSearchClient()
        self.search_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized {name} with web search capabilities")
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """
        Execute a web search goal.
        
        Args:
            goal: The search goal to achieve
            
        Returns:
            Dictionary containing search results and analysis
        """
        goal_desc = goal.description.lower()
        context = goal.context or {}
        
        logger.info(f"WebSearchAgent executing goal: {goal.description}")
        
        # Determine search strategy based on goal
        if "comprehensive" in goal_desc or "detailed" in goal_desc:
            return await self._comprehensive_search(goal)
        elif "quick" in goal_desc or "brief" in goal_desc:
            return await self._quick_search(goal)
        elif "academic" in goal_desc or "research" in goal_desc:
            return await self._academic_search(goal)
        elif "news" in goal_desc or "current" in goal_desc or "latest" in goal_desc:
            return await self._news_search(goal)
        else:
            return await self._standard_search(goal)
    
    async def _comprehensive_search(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform comprehensive search with multiple sources and deep analysis."""
        query = self._extract_query_from_goal(goal)
        
        logger.info(f"Performing comprehensive search for: {query}")
        
        # Multi-stage search approach
        results = {
            "search_type": "comprehensive",
            "original_query": query,
            "timestamp": datetime.now(),
            "stages": {}
        }
        
        try:
            # Stage 1: General web search
            general_results = await self.search_client.search(
                query=query,
                search_type="web",
                max_results=20
            )
            results["stages"]["general_web"] = general_results
            
            # Stage 2: Academic sources
            academic_results = await self.search_client.search(
                query=f"{query} site:scholar.google.com OR site:arxiv.org OR site:researchgate.net",
                search_type="web",
                max_results=10
            )
            results["stages"]["academic"] = academic_results
            
            # Stage 3: News sources
            news_results = await self.search_client.search(
                query=query,
                search_type="news",
                max_results=10
            )
            results["stages"]["news"] = news_results
            
            # Stage 4: Image search for visual content
            image_results = await self.search_client.search(
                query=query,
                search_type="images",
                max_results=5
            )
            results["stages"]["images"] = image_results
            
            # Combine and rank results
            all_results = self._combine_search_results([
                general_results, academic_results, news_results
            ])
            
            results["combined_results"] = all_results
            results["total_results"] = len(all_results)
            results["quality_score"] = self._calculate_quality_score(all_results)
            
            # Extract content from top results
            top_results = all_results[:10]
            content_extracts = []
            
            for result in top_results:
                try:
                    content = await self.search_client.extract_content(result.url)
                    content_extracts.append({
                        "url": result.url,
                        "title": result.title,
                        "content": content,
                        "relevance_score": result.relevance_score
                    })
                except Exception as e:
                    logger.warning(f"Failed to extract content from {result.url}: {str(e)}")
            
            results["content_extracts"] = content_extracts
            results["status"] = "completed"
            
            # Update search history
            self.search_history.append({
                "goal_id": goal.id,
                "query": query,
                "search_type": "comprehensive",
                "results_count": len(all_results),
                "timestamp": datetime.now()
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive search failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            return results
    
    async def _quick_search(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform quick search for immediate answers."""
        query = self._extract_query_from_goal(goal)
        
        logger.info(f"Performing quick search for: {query}")
        
        try:
            # Single search with limited results
            search_results = await self.search_client.search(
                query=query,
                search_type="web",
                max_results=5
            )
            
            # Extract key information from top result
            top_result = search_results[0] if search_results else None
            quick_answer = None
            
            if top_result:
                content = await self.search_client.extract_content(top_result.url)
                quick_answer = self._extract_quick_answer(content, query)
            
            results = {
                "search_type": "quick",
                "original_query": query,
                "timestamp": datetime.now(),
                "quick_answer": quick_answer,
                "top_results": search_results[:3],
                "total_results": len(search_results),
                "status": "completed"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Quick search failed: {str(e)}")
            return {
                "search_type": "quick",
                "original_query": query,
                "status": "failed",
                "error": str(e)
            }
    
    async def _academic_search(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform academic and research-focused search."""
        query = self._extract_query_from_goal(goal)
        
        logger.info(f"Performing academic search for: {query}")
        
        try:
            # Academic sources search
            academic_query = f"{query} site:scholar.google.com OR site:arxiv.org OR site:jstor.org OR site:pubmed.ncbi.nlm.nih.gov"
            
            search_results = await self.search_client.search(
                query=academic_query,
                search_type="web",
                max_results=15
            )
            
            # Filter for academic sources
            academic_results = [
                result for result in search_results
                if any(domain in result.url for domain in [
                    "scholar.google.com", "arxiv.org", "jstor.org", 
                    "pubmed.ncbi.nlm.nih.gov", "researchgate.net", ".edu"
                ])
            ]
            
            results = {
                "search_type": "academic",
                "original_query": query,
                "timestamp": datetime.now(),
                "academic_results": academic_results,
                "total_results": len(academic_results),
                "credibility_score": self._calculate_credibility_score(academic_results),
                "status": "completed"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Academic search failed: {str(e)}")
            return {
                "search_type": "academic",
                "original_query": query,
                "status": "failed",
                "error": str(e)
            }
    
    async def _news_search(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform news and current events search."""
        query = self._extract_query_from_goal(goal)
        
        logger.info(f"Performing news search for: {query}")
        
        try:
            # News search
            news_results = await self.search_client.search(
                query=query,
                search_type="news",
                max_results=15
            )
            
            # Sort by recency
            news_results.sort(key=lambda x: x.published_date or datetime.min, reverse=True)
            
            results = {
                "search_type": "news",
                "original_query": query,
                "timestamp": datetime.now(),
                "news_results": news_results,
                "recent_articles": news_results[:5],
                "total_results": len(news_results),
                "latest_update": news_results[0].published_date if news_results else None,
                "status": "completed"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"News search failed: {str(e)}")
            return {
                "search_type": "news",
                "original_query": query,
                "status": "failed",
                "error": str(e)
            }
    
    async def _standard_search(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform standard web search."""
        query = self._extract_query_from_goal(goal)
        
        logger.info(f"Performing standard search for: {query}")
        
        try:
            search_results = await self.search_client.search(
                query=query,
                search_type="web",
                max_results=10
            )
            
            results = {
                "search_type": "standard",
                "original_query": query,
                "timestamp": datetime.now(),
                "search_results": search_results,
                "total_results": len(search_results),
                "status": "completed"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Standard search failed: {str(e)}")
            return {
                "search_type": "standard",
                "original_query": query,
                "status": "failed",
                "error": str(e)
            }
    
    def _extract_query_from_goal(self, goal: AgentGoal) -> str:
        """Extract search query from goal description."""
        # Simple extraction - can be enhanced with NLP
        query = goal.context.get("query", "")
        
        if not query:
            # Extract from description
            desc = goal.description.lower()
            
            # Remove common goal phrases
            for phrase in ["search for", "find", "lookup", "get information about", "information on"]:
                desc = desc.replace(phrase, "").strip()
            
            query = desc
        
        return query or goal.description
    
    def _combine_search_results(self, result_lists: List[List[SearchResult]]) -> List[SearchResult]:
        """Combine and deduplicate search results from multiple sources."""
        combined = []
        seen_urls = set()
        
        for result_list in result_lists:
            for result in result_list:
                if result.url not in seen_urls:
                    combined.append(result)
                    seen_urls.add(result.url)
        
        # Sort by relevance score
        combined.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        
        return combined
    
    def _calculate_quality_score(self, results: List[SearchResult]) -> float:
        """Calculate quality score for search results."""
        if not results:
            return 0.0
        
        # Simple quality scoring based on relevance and source diversity
        total_relevance = sum(result.relevance_score or 0 for result in results)
        avg_relevance = total_relevance / len(results)
        
        # Bonus for source diversity
        unique_domains = len(set(result.domain for result in results if result.domain))
        diversity_bonus = min(unique_domains / 10, 0.2)  # Max 20% bonus
        
        return min(avg_relevance + diversity_bonus, 1.0)
    
    def _calculate_credibility_score(self, results: List[SearchResult]) -> float:
        """Calculate credibility score for academic results."""
        if not results:
            return 0.0
        
        credible_domains = [
            "scholar.google.com", "arxiv.org", "jstor.org", 
            "pubmed.ncbi.nlm.nih.gov", "researchgate.net", ".edu", ".gov"
        ]
        
        credible_count = sum(
            1 for result in results
            if any(domain in result.url for domain in credible_domains)
        )
        
        return credible_count / len(results)
    
    def _extract_quick_answer(self, content: str, query: str) -> Optional[str]:
        """Extract a quick answer from content."""
        if not content or len(content) < 50:
            return None
        
        # Simple answer extraction - first 200 characters
        sentences = content.split('. ')
        
        # Find sentence containing query keywords
        query_words = query.lower().split()
        
        for sentence in sentences[:5]:  # Check first 5 sentences
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in query_words):
                return sentence.strip()[:200] + "..." if len(sentence) > 200 else sentence.strip()
        
        # Fallback to first sentence
        return sentences[0][:200] + "..." if len(sentences[0]) > 200 else sentences[0]
    
    async def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions for partial query."""
        try:
            suggestions = await self.search_client.get_suggestions(partial_query)
            return suggestions
        except Exception as e:
            logger.error(f"Failed to get search suggestions: {str(e)}")
            return []
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history for this agent."""
        return self.search_history.copy()
    
    async def optimize_query(self, query: str, intent: str = None) -> str:
        """Optimize search query for better results."""
        optimized = query.strip()
        
        # Basic query optimization
        if intent == "academic":
            optimized += " research paper OR study OR analysis"
        elif intent == "news":
            optimized += f" {datetime.now().year}"
        elif intent == "how-to":
            if not optimized.startswith("how to"):
                optimized = f"how to {optimized}"
        
        logger.info(f"Optimized query: '{query}' -> '{optimized}'")
        return optimized
