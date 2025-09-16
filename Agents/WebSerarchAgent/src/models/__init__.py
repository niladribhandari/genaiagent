"""
Models for web search system.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class SearchQuery:
    """Represents a search query with parameters."""
    query: str
    search_type: str = "web"  # web, news, images, academic
    max_results: int = 10
    language: str = "en"
    region: str = "us"
    safe_search: bool = True
    time_filter: Optional[str] = None  # day, week, month, year
    
@dataclass
class SearchResult:
    """Represents a single search result."""
    title: str
    url: str
    description: str
    domain: Optional[str] = None
    published_date: Optional[datetime] = None
    relevance_score: Optional[float] = None
    content_type: str = "webpage"
    language: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Extract domain from URL
        if self.url and not self.domain:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(self.url)
                self.domain = parsed.netloc
            except:
                self.domain = "unknown"

@dataclass
class NewsResult(SearchResult):
    """Represents a news search result with additional fields."""
    source: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    
@dataclass
class ImageResult(SearchResult):
    """Represents an image search result."""
    image_url: str = ""
    thumbnail_url: str = ""
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    
@dataclass
class WebContent:
    """Represents extracted web page content."""
    url: str
    title: str
    content: str
    extracted_text: str
    html: Optional[str] = None
    metadata: Dict[str, Any] = None
    extraction_timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now()

@dataclass
class SearchSuggestion:
    """Represents a search suggestion."""
    suggestion: str
    relevance_score: float
    search_volume: Optional[int] = None
    trend_direction: str = "stable"  # rising, falling, stable
