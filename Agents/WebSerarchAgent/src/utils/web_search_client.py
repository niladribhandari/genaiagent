"""
Web Search Client for interacting with search engines.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json
from ..models import SearchResult, SearchQuery, WebContent, SearchSuggestion

logger = logging.getLogger(__name__)

class WebSearchClient:
    """
    Client for performing web searches using multiple search engines.
    """
    
    def __init__(self):
        """Initialize the web search client."""
        self.session: Optional[aiohttp.ClientSession] = None
        self.search_apis = {
            "serpapi": {
                "api_key": os.getenv("SERPAPI_API_KEY"),
                "base_url": "https://serpapi.com/search",
                "enabled": bool(os.getenv("SERPAPI_API_KEY"))
            },
            "bing": {
                "api_key": os.getenv("BING_SEARCH_API_KEY"),
                "base_url": "https://api.bing.microsoft.com/v7.0/search",
                "enabled": bool(os.getenv("BING_SEARCH_API_KEY"))
            }
        }
        
        # Rate limiting
        self.rate_limits = {
            "serpapi": {"calls_per_minute": 100, "last_call": None, "call_count": 0},
            "bing": {"calls_per_minute": 1000, "last_call": None, "call_count": 0}
        }
        
        logger.info("Initialized WebSearchClient")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search(self, query: str, search_type: str = "web", max_results: int = 10, **kwargs) -> List[SearchResult]:
        """
        Perform a web search using available search engines.
        
        Args:
            query: Search query string
            search_type: Type of search (web, news, images)
            max_results: Maximum number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            List of SearchResult objects
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        search_query = SearchQuery(
            query=query,
            search_type=search_type,
            max_results=max_results,
            **kwargs
        )
        
        logger.info(f"Performing {search_type} search for: {query}")
        
        # Try different search engines in order of preference
        for engine in ["serpapi", "bing"]:
            if self.search_apis[engine]["enabled"]:
                try:
                    results = await self._search_with_engine(engine, search_query)
                    if results:
                        logger.info(f"Successfully retrieved {len(results)} results from {engine}")
                        return results[:max_results]
                except Exception as e:
                    logger.warning(f"Search failed with {engine}: {str(e)}")
                    continue
        
        # Fallback to mock results if no API is available
        logger.warning("No search APIs available, using mock results")
        return await self._mock_search_results(search_query)
    
    async def _search_with_engine(self, engine: str, search_query: SearchQuery) -> List[SearchResult]:
        """Perform search with a specific engine."""
        
        # Check rate limits
        if not await self._check_rate_limit(engine):
            raise Exception(f"Rate limit exceeded for {engine}")
        
        if engine == "serpapi":
            return await self._search_serpapi(search_query)
        elif engine == "bing":
            return await self._search_bing(search_query)
        else:
            raise ValueError(f"Unsupported search engine: {engine}")
    
    async def _search_serpapi(self, search_query: SearchQuery) -> List[SearchResult]:
        """Search using SerpAPI."""
        api_key = self.search_apis["serpapi"]["api_key"]
        base_url = self.search_apis["serpapi"]["base_url"]
        
        params = {
            "q": search_query.query,
            "api_key": api_key,
            "engine": "google",
            "num": search_query.max_results,
            "hl": search_query.language,
            "gl": search_query.region
        }
        
        # Add search type specific parameters
        if search_query.search_type == "news":
            params["tbm"] = "nws"
        elif search_query.search_type == "images":
            params["tbm"] = "isch"
        
        # Add time filter
        if search_query.time_filter:
            time_filters = {
                "day": "qdr:d",
                "week": "qdr:w", 
                "month": "qdr:m",
                "year": "qdr:y"
            }
            if search_query.time_filter in time_filters:
                params["tbs"] = time_filters[search_query.time_filter]
        
        async with self.session.get(base_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_serpapi_results(data, search_query.search_type)
            else:
                raise Exception(f"SerpAPI request failed with status {response.status}")
    
    async def _search_bing(self, search_query: SearchQuery) -> List[SearchResult]:
        """Search using Bing Search API."""
        api_key = self.search_apis["bing"]["api_key"]
        base_url = self.search_apis["bing"]["base_url"]
        
        headers = {
            "Ocp-Apim-Subscription-Key": api_key
        }
        
        params = {
            "q": search_query.query,
            "count": search_query.max_results,
            "mkt": f"{search_query.language}-{search_query.region}",
            "safeSearch": "Strict" if search_query.safe_search else "Off"
        }
        
        # Modify URL for different search types
        if search_query.search_type == "news":
            base_url = base_url.replace("/v7.0/search", "/v7.0/news/search")
        elif search_query.search_type == "images":
            base_url = base_url.replace("/v7.0/search", "/v7.0/images/search")
        
        # Add time filter for news
        if search_query.search_type == "news" and search_query.time_filter:
            freshness_map = {
                "day": "Day",
                "week": "Week",
                "month": "Month"
            }
            if search_query.time_filter in freshness_map:
                params["freshness"] = freshness_map[search_query.time_filter]
        
        async with self.session.get(base_url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_bing_results(data, search_query.search_type)
            else:
                raise Exception(f"Bing API request failed with status {response.status}")
    
    def _parse_serpapi_results(self, data: Dict[str, Any], search_type: str) -> List[SearchResult]:
        """Parse results from SerpAPI response."""
        results = []
        
        if search_type == "web":
            organic_results = data.get("organic_results", [])
            for result in organic_results:
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("link", ""),
                    description=result.get("snippet", ""),
                    relevance_score=result.get("position", 0) / 10.0,  # Convert position to relevance
                    metadata={"source": "serpapi", "position": result.get("position")}
                )
                results.append(search_result)
        
        elif search_type == "news":
            news_results = data.get("news_results", [])
            for result in news_results:
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("link", ""),
                    description=result.get("snippet", ""),
                    published_date=self._parse_date(result.get("date")),
                    content_type="news",
                    metadata={"source": "serpapi", "source_name": result.get("source")}
                )
                results.append(search_result)
        
        elif search_type == "images":
            images_results = data.get("images_results", [])
            for result in images_results:
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("original", ""),
                    description=result.get("title", ""),
                    content_type="image",
                    metadata={
                        "source": "serpapi",
                        "thumbnail": result.get("thumbnail"),
                        "position": result.get("position")
                    }
                )
                results.append(search_result)
        
        return results
    
    def _parse_bing_results(self, data: Dict[str, Any], search_type: str) -> List[SearchResult]:
        """Parse results from Bing API response."""
        results = []
        
        if search_type == "web":
            web_pages = data.get("webPages", {}).get("value", [])
            for i, result in enumerate(web_pages):
                search_result = SearchResult(
                    title=result.get("name", ""),
                    url=result.get("url", ""),
                    description=result.get("snippet", ""),
                    published_date=self._parse_date(result.get("dateLastCrawled")),
                    relevance_score=(len(web_pages) - i) / len(web_pages),  # Higher for earlier results
                    metadata={"source": "bing", "display_url": result.get("displayUrl")}
                )
                results.append(search_result)
        
        elif search_type == "news":
            news_values = data.get("value", [])
            for result in news_values:
                search_result = SearchResult(
                    title=result.get("name", ""),
                    url=result.get("url", ""),
                    description=result.get("description", ""),
                    published_date=self._parse_date(result.get("datePublished")),
                    content_type="news",
                    metadata={
                        "source": "bing",
                        "provider": result.get("provider", [{}])[0].get("name", ""),
                        "category": result.get("category")
                    }
                )
                results.append(search_result)
        
        elif search_type == "images":
            images_values = data.get("value", [])
            for result in images_values:
                search_result = SearchResult(
                    title=result.get("name", ""),
                    url=result.get("contentUrl", ""),
                    description=result.get("name", ""),
                    content_type="image",
                    metadata={
                        "source": "bing",
                        "thumbnail": result.get("thumbnailUrl"),
                        "width": result.get("width"),
                        "height": result.get("height")
                    }
                )
                results.append(search_result)
        
        return results
    
    async def _mock_search_results(self, search_query: SearchQuery) -> List[SearchResult]:
        """Generate mock search results when no APIs are available."""
        mock_results = []
        
        for i in range(min(search_query.max_results, 5)):
            result = SearchResult(
                title=f"Mock Result {i+1} for '{search_query.query}'",
                url=f"https://example{i+1}.com/search-result",
                description=f"This is a mock search result for the query '{search_query.query}'. "
                           f"It demonstrates the search functionality when no real APIs are configured.",
                domain=f"example{i+1}.com",
                relevance_score=(5-i)/5,
                content_type=search_query.search_type,
                metadata={"source": "mock", "position": i+1}
            )
            mock_results.append(result)
        
        return mock_results
    
    async def extract_content(self, url: str) -> str:
        """
        Extract text content from a web page.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted text content
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    html = await response.text()
                    # Simple text extraction (can be enhanced with BeautifulSoup)
                    return self._extract_text_from_html(html)
                else:
                    logger.warning(f"Failed to fetch content from {url}: HTTP {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""
    
    def _extract_text_from_html(self, html: str) -> str:
        """Simple text extraction from HTML."""
        import re
        
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:5000]  # Limit to first 5000 characters
    
    async def get_suggestions(self, partial_query: str) -> List[str]:
        """
        Get search suggestions for a partial query.
        
        Args:
            partial_query: Partial search query
            
        Returns:
            List of suggested completions
        """
        # Mock suggestions (can be enhanced with real suggestion APIs)
        suggestions = [
            f"{partial_query} tutorial",
            f"{partial_query} guide",
            f"{partial_query} examples",
            f"{partial_query} best practices",
            f"{partial_query} 2024"
        ]
        
        return suggestions[:5]
    
    async def _check_rate_limit(self, engine: str) -> bool:
        """Check if we can make a request to the given engine."""
        rate_limit = self.rate_limits[engine]
        now = datetime.now()
        
        # Reset count if it's been more than a minute
        if rate_limit["last_call"] is None or (now - rate_limit["last_call"]).seconds >= 60:
            rate_limit["call_count"] = 0
            rate_limit["last_call"] = now
        
        # Check if we're under the limit
        if rate_limit["call_count"] < rate_limit["calls_per_minute"]:
            rate_limit["call_count"] += 1
            return True
        
        return False
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If no format matches, return None
            return None
            
        except Exception:
            return None
    
    async def close(self):
        """Close the client session."""
        if self.session:
            await self.session.close()
            self.session = None
