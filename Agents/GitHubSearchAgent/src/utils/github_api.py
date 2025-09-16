"""
GitHub API utilities and wrappers.
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime, timedelta
import logging
import base64
import json
from asyncio_throttle import Throttler

from github import Github, GithubException
from ..models import RepositoryInfo, SearchQuery, CodeFile


class GitHubAPIClient:
    """Async GitHub API client with rate limiting and caching."""
    
    def __init__(self, token: str, requests_per_hour: int = 5000):
        self.token = token
        self.github = Github(token)
        self.session: Optional[aiohttp.ClientSession] = None
        self.throttler = Throttler(rate_limit=requests_per_hour, period=3600)
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(minutes=30)
        self.logger = logging.getLogger("github_api")
        
        # API endpoints
        self.base_url = "https://api.github.com"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, method: str, url: str, params: Dict = None) -> str:
        """Generate cache key for request."""
        return f"{method}:{url}:{json.dumps(params or {}, sort_keys=True)}"
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cache entry is still valid."""
        return datetime.now() - timestamp < self.cache_ttl
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make throttled API request with caching."""
        cache_key = self._get_cache_key(method, url, kwargs.get('params'))
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                self.logger.debug(f"Cache hit for {url}")
                return cached_data
        
        # Make throttled request
        async with self.throttler:
            try:
                if not self.session:
                    raise RuntimeError("Session not initialized. Use async context manager.")
                
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 403:
                        # Rate limit exceeded
                        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                        current_time = int(time.time())
                        wait_time = max(0, reset_time - current_time)
                        
                        self.logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds.")
                        await asyncio.sleep(wait_time + 1)
                        
                        # Retry request
                        async with self.session.request(method, url, **kwargs) as retry_response:
                            retry_response.raise_for_status()
                            data = await retry_response.json()
                    else:
                        response.raise_for_status()
                        data = await response.json()
                
                # Cache successful response
                self.cache[cache_key] = (data, datetime.now())
                return data
                
            except Exception as e:
                self.logger.error(f"API request failed: {method} {url} - {str(e)}")
                raise
    
    async def search_repositories(self, query: SearchQuery) -> List[RepositoryInfo]:
        """Search GitHub repositories."""
        self.logger.info(f"Searching repositories: {query.query}")
        
        # Build search query
        search_params = {
            "q": self._build_search_query(query),
            "sort": query.sort_by,
            "order": query.order,
            "per_page": min(query.max_results, 100)
        }
        
        try:
            data = await self._make_request("GET", f"{self.base_url}/search/repositories", 
                                          params=search_params)
            
            repositories = []
            for item in data.get("items", []):
                repo_info = self._parse_repository_data(item)
                repositories.append(repo_info)
            
            self.logger.info(f"Found {len(repositories)} repositories")
            return repositories
            
        except Exception as e:
            self.logger.error(f"Repository search failed: {str(e)}")
            raise
    
    def _build_search_query(self, query: SearchQuery) -> str:
        """Build GitHub search query string."""
        q_parts = [query.query]
        
        if query.language:
            q_parts.append(f"language:{query.language}")
        
        if query.min_stars > 0:
            q_parts.append(f"stars:>={query.min_stars}")
        
        if query.created_after:
            q_parts.append(f"created:>={query.created_after.strftime('%Y-%m-%d')}")
        
        if query.created_before:
            q_parts.append(f"created:<={query.created_before.strftime('%Y-%m-%d')}")
        
        for key, value in query.filters.items():
            q_parts.append(f"{key}:{value}")
        
        return " ".join(q_parts)
    
    def _parse_repository_data(self, data: Dict[str, Any]) -> RepositoryInfo:
        """Parse GitHub API repository data."""
        return RepositoryInfo(
            owner=data["owner"]["login"],
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            language=data.get("language"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            watchers=data.get("watchers_count", 0),
            size=data.get("size", 0),
            open_issues=data.get("open_issues_count", 0),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")) if data.get("updated_at") else None,
            pushed_at=datetime.fromisoformat(data["pushed_at"].replace("Z", "+00:00")) if data.get("pushed_at") else None,
            topics=data.get("topics", []),
            license=data.get("license", {}).get("name") if data.get("license") else None,
            default_branch=data.get("default_branch", "main"),
            is_fork=data.get("fork", False),
            is_archived=data.get("archived", False),
            is_private=data.get("private", False),
            clone_url=data.get("clone_url", ""),
            html_url=data.get("html_url", ""),
            api_url=data.get("url", "")
        )
    
    async def get_repository_details(self, owner: str, repo: str) -> RepositoryInfo:
        """Get detailed repository information."""
        self.logger.info(f"Getting repository details: {owner}/{repo}")
        
        try:
            # Get repository data
            repo_data = await self._make_request("GET", f"{self.base_url}/repos/{owner}/{repo}")
            
            # Get languages
            languages_data = await self._make_request("GET", f"{self.base_url}/repos/{owner}/{repo}/languages")
            
            repo_info = self._parse_repository_data(repo_data)
            repo_info.languages = languages_data
            
            return repo_info
            
        except Exception as e:
            self.logger.error(f"Failed to get repository details: {str(e)}")
            raise
    
    async def get_repository_files(self, owner: str, repo: str, path: str = "", 
                                 max_files: int = 100) -> AsyncGenerator[Dict[str, Any], None]:
        """Get repository files recursively."""
        self.logger.info(f"Getting files from {owner}/{repo}/{path}")
        
        try:
            contents_data = await self._make_request("GET", 
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}")
            
            if not isinstance(contents_data, list):
                contents_data = [contents_data]
            
            file_count = 0
            for item in contents_data:
                if file_count >= max_files:
                    break
                
                if item["type"] == "file":
                    yield item
                    file_count += 1
                elif item["type"] == "dir":
                    # Recursively get files from subdirectory
                    async for sub_item in self.get_repository_files(owner, repo, item["path"], 
                                                                   max_files - file_count):
                        yield sub_item
                        file_count += 1
                        if file_count >= max_files:
                            break
                            
        except Exception as e:
            self.logger.error(f"Failed to get repository files: {str(e)}")
            raise
    
    async def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get file content from repository."""
        try:
            file_data = await self._make_request("GET", 
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}")
            
            if file_data.get("encoding") == "base64":
                content = base64.b64decode(file_data["content"]).decode("utf-8", errors="ignore")
                return content
            
            return file_data.get("content")
            
        except Exception as e:
            self.logger.error(f"Failed to get file content: {path} - {str(e)}")
            return None
    
    async def search_code(self, query: str, repo: Optional[str] = None, 
                         language: Optional[str] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search code in repositories."""
        self.logger.info(f"Searching code: {query}")
        
        search_params = {
            "q": query,
            "per_page": min(max_results, 100)
        }
        
        if repo:
            search_params["q"] += f" repo:{repo}"
        
        if language:
            search_params["q"] += f" language:{language}"
        
        try:
            data = await self._make_request("GET", f"{self.base_url}/search/code", 
                                          params=search_params)
            
            return data.get("items", [])
            
        except Exception as e:
            self.logger.error(f"Code search failed: {str(e)}")
            raise
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                "core": {
                    "limit": rate_limit.core.limit,
                    "remaining": rate_limit.core.remaining,
                    "reset": rate_limit.core.reset.isoformat()
                },
                "search": {
                    "limit": rate_limit.search.limit,
                    "remaining": rate_limit.search.remaining,
                    "reset": rate_limit.search.reset.isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get rate limit status: {str(e)}")
            return {}
    
    def clear_cache(self):
        """Clear the API cache."""
        self.cache.clear()
        self.logger.info("API cache cleared")
