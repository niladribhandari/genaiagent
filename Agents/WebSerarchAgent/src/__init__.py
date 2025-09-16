"""
Main module for Web Search System.
"""

from .web_search_system import WebSearchSystem, quick_search
from .agentic import (
    AgentOrchestrator, WebSearchAgent, ContentAnalysisAgent,
    FactCheckingAgent, SummarizationAgent, TrendMonitoringAgent
)
from .utils import WebSearchClient
from .models import SearchResult, SearchQuery, WebContent
from .config import get_config, update_config

__all__ = [
    'WebSearchSystem',
    'quick_search',
    'AgentOrchestrator',
    'WebSearchAgent', 
    'ContentAnalysisAgent',
    'FactCheckingAgent',
    'SummarizationAgent',
    'TrendMonitoringAgent',
    'WebSearchClient',
    'SearchResult',
    'SearchQuery', 
    'WebContent',
    'get_config',
    'update_config'
]

__version__ = "1.0.0"
