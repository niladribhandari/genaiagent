"""
Trend Monitoring Agent for tracking and analyzing trends.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentGoal, AgentCapability

logger = logging.getLogger(__name__)

class TrendMonitoringAgent(BaseAgent):
    """
    Specialized agent for monitoring trends, tracking popularity, and analyzing patterns.
    """
    
    def __init__(self, name: str = "TrendMonitoringAgent"):
        """Initialize the Trend Monitoring Agent."""
        capabilities = [
            AgentCapability(
                name="trend_detection",
                description="Detect emerging trends from search data and content",
                input_types=["search_results", "content", "keywords"],
                output_types=["trends", "trending_topics", "popularity_metrics"]
            ),
            AgentCapability(
                name="popularity_tracking",
                description="Track popularity and interest levels over time",
                input_types=["topics", "keywords", "search_queries"],
                output_types=["popularity_scores", "interest_trends", "engagement_metrics"]
            ),
            AgentCapability(
                name="temporal_analysis",
                description="Analyze how trends change over time periods",
                input_types=["historical_data", "time_series", "trend_data"],
                output_types=["temporal_patterns", "trend_evolution", "forecasts"]
            ),
            AgentCapability(
                name="comparative_analysis",
                description="Compare trends across different topics or time periods",
                input_types=["multiple_trends", "comparison_topics", "datasets"],
                output_types=["trend_comparisons", "relative_popularity", "competitive_analysis"]
            ),
            AgentCapability(
                name="trend_prediction",
                description="Predict future trend directions and potential viral content",
                input_types=["current_trends", "historical_patterns", "indicators"],
                output_types=["predictions", "forecasts", "trend_projections"]
            )
        ]
        
        super().__init__(name, capabilities)
        self.trend_history: List[Dict[str, Any]] = []
        self.trend_database: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info(f"Initialized {name} with trend monitoring capabilities")
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """
        Execute a trend monitoring goal.
        
        Args:
            goal: The trend monitoring goal to achieve
            
        Returns:
            Dictionary containing trend analysis results
        """
        goal_desc = goal.description.lower()
        context = goal.context or {}
        
        logger.info(f"TrendMonitoringAgent executing goal: {goal.description}")
        
        # Determine trend analysis type based on goal
        if "detect" in goal_desc or "emerging" in goal_desc:
            return await self._detect_trends(goal)
        elif "popularity" in goal_desc or "tracking" in goal_desc:
            return await self._track_popularity(goal)
        elif "compare" in goal_desc or "comparison" in goal_desc:
            return await self._compare_trends(goal)
        elif "predict" in goal_desc or "forecast" in goal_desc:
            return await self._predict_trends(goal)
        elif "temporal" in goal_desc or "time" in goal_desc:
            return await self._temporal_analysis(goal)
        else:
            return await self._comprehensive_trend_analysis(goal)
    
    async def _comprehensive_trend_analysis(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform comprehensive trend analysis."""
        context = goal.context or {}
        search_results = context.get("search_results", [])
        content_list = context.get("content_list", [])
        keywords = context.get("keywords", [])
        
        logger.info(f"Performing comprehensive trend analysis")
        
        try:
            results = {
                "trend_analysis_type": "comprehensive",
                "timestamp": datetime.now(),
                "analyses": {}
            }
            
            # Perform multiple trend analyses
            analyses = await asyncio.gather(
                self._analyze_trending_keywords(search_results, content_list),
                self._analyze_content_trends(content_list),
                self._analyze_temporal_patterns(search_results),
                self._analyze_engagement_trends(search_results),
                return_exceptions=True
            )
            
            # Process results
            analysis_types = ["keywords", "content", "temporal", "engagement"]
            for i, analysis in enumerate(analyses):
                if not isinstance(analysis, Exception):
                    results["analyses"][analysis_types[i]] = analysis
                else:
                    logger.warning(f"Trend analysis {analysis_types[i]} failed: {str(analysis)}")
                    results["analyses"][analysis_types[i]] = {"error": str(analysis)}
            
            # Generate trend insights
            results["trend_insights"] = self._generate_trend_insights(results["analyses"])
            results["trending_score"] = self._calculate_trending_score(results["analyses"])
            results["status"] = "completed"
            
            # Record trend analysis
            self.trend_history.append({
                "goal_id": goal.id,
                "analysis_type": "comprehensive",
                "trending_score": results["trending_score"],
                "timestamp": datetime.now()
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive trend analysis failed: {str(e)}")
            return {
                "trend_analysis_type": "comprehensive",
                "status": "failed",
                "error": str(e)
            }
    
    async def _detect_trends(self, goal: AgentGoal) -> Dict[str, Any]:
        """Detect emerging trends from data."""
        context = goal.context or {}
        search_results = context.get("search_results", [])
        content_list = context.get("content_list", [])
        
        try:
            trend_detection = await self._analyze_trending_keywords(search_results, content_list)
            
            return {
                "trend_analysis_type": "detection",
                "timestamp": datetime.now(),
                "trend_detection": trend_detection,
                "emerging_trends": trend_detection.get("emerging_keywords", []),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Trend detection failed: {str(e)}")
            return {
                "trend_analysis_type": "detection",
                "status": "failed",
                "error": str(e)
            }
    
    async def _track_popularity(self, goal: AgentGoal) -> Dict[str, Any]:
        """Track popularity metrics for topics."""
        context = goal.context or {}
        topics = context.get("topics", [])
        search_results = context.get("search_results", [])
        
        try:
            popularity_metrics = await self._calculate_popularity_metrics(topics, search_results)
            
            return {
                "trend_analysis_type": "popularity_tracking",
                "timestamp": datetime.now(),
                "topics_tracked": len(topics),
                "popularity_metrics": popularity_metrics,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Popularity tracking failed: {str(e)}")
            return {
                "trend_analysis_type": "popularity_tracking",
                "status": "failed",
                "error": str(e)
            }
    
    async def _compare_trends(self, goal: AgentGoal) -> Dict[str, Any]:
        """Compare trends across different topics or time periods."""
        context = goal.context or {}
        comparison_topics = context.get("comparison_topics", [])
        datasets = context.get("datasets", [])
        
        try:
            comparison_results = await self._perform_trend_comparison(comparison_topics, datasets)
            
            return {
                "trend_analysis_type": "comparison",
                "timestamp": datetime.now(),
                "topics_compared": len(comparison_topics),
                "comparison_results": comparison_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Trend comparison failed: {str(e)}")
            return {
                "trend_analysis_type": "comparison",
                "status": "failed",
                "error": str(e)
            }
    
    async def _predict_trends(self, goal: AgentGoal) -> Dict[str, Any]:
        """Predict future trend directions."""
        context = goal.context or {}
        current_trends = context.get("current_trends", [])
        historical_data = context.get("historical_data", [])
        
        try:
            predictions = await self._generate_trend_predictions(current_trends, historical_data)
            
            return {
                "trend_analysis_type": "prediction",
                "timestamp": datetime.now(),
                "trends_analyzed": len(current_trends),
                "predictions": predictions,
                "forecast_period": "next_30_days",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Trend prediction failed: {str(e)}")
            return {
                "trend_analysis_type": "prediction",
                "status": "failed",
                "error": str(e)
            }
    
    async def _temporal_analysis(self, goal: AgentGoal) -> Dict[str, Any]:
        """Analyze trends over time periods."""
        context = goal.context or {}
        time_series_data = context.get("time_series_data", [])
        search_results = context.get("search_results", [])
        
        try:
            temporal_patterns = await self._analyze_temporal_patterns(search_results, time_series_data)
            
            return {
                "trend_analysis_type": "temporal",
                "timestamp": datetime.now(),
                "temporal_patterns": temporal_patterns,
                "time_periods_analyzed": len(temporal_patterns.get("periods", [])),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Temporal analysis failed: {str(e)}")
            return {
                "trend_analysis_type": "temporal",
                "status": "failed",
                "error": str(e)
            }
    
    async def _analyze_trending_keywords(self, search_results: List[Any], content_list: List[str]) -> Dict[str, Any]:
        """Analyze trending keywords from search results and content."""
        
        # Extract keywords from search results
        all_keywords = []
        
        # Process search results
        for result in search_results:
            if hasattr(result, 'title') and result.title:
                all_keywords.extend(self._extract_keywords_from_text(result.title))
            if hasattr(result, 'description') and result.description:
                all_keywords.extend(self._extract_keywords_from_text(result.description))
        
        # Process content
        for content in content_list:
            if isinstance(content, str):
                all_keywords.extend(self._extract_keywords_from_text(content))
        
        # Count keyword frequencies
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Identify trending keywords (high frequency)
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        
        trending_keywords = []
        for keyword, freq in sorted_keywords[:20]:  # Top 20 keywords
            trending_keywords.append({
                "keyword": keyword,
                "frequency": freq,
                "trend_score": self._calculate_keyword_trend_score(keyword, freq, len(all_keywords)),
                "category": self._categorize_keyword(keyword)
            })
        
        # Identify emerging keywords (moderate frequency but growing)
        emerging_keywords = []
        for keyword, freq in sorted_keywords[20:50]:  # Next 30 keywords
            if freq >= 3:  # Must appear at least 3 times
                emerging_keywords.append({
                    "keyword": keyword,
                    "frequency": freq,
                    "emergence_score": freq / max(len(all_keywords), 1),
                    "category": self._categorize_keyword(keyword)
                })
        
        return {
            "trending_keywords": trending_keywords,
            "emerging_keywords": emerging_keywords,
            "total_keywords_analyzed": len(keyword_freq),
            "keyword_diversity": len(keyword_freq) / max(len(all_keywords), 1),
            "top_categories": self._get_top_keyword_categories(trending_keywords)
        }
    
    async def _analyze_content_trends(self, content_list: List[str]) -> Dict[str, Any]:
        """Analyze trends in content topics and themes."""
        
        if not content_list:
            return {"content_trends": [], "trending_themes": [], "content_patterns": {}}
        
        # Analyze content themes
        themes = []
        content_length_trends = []
        publication_patterns = {}
        
        for content in content_list:
            if isinstance(content, str):
                # Extract themes
                content_themes = self._extract_themes_from_content(content)
                themes.extend(content_themes)
                
                # Track content length
                content_length_trends.append(len(content))
        
        # Count theme frequencies
        theme_freq = {}
        for theme in themes:
            theme_freq[theme] = theme_freq.get(theme, 0) + 1
        
        # Identify trending themes
        trending_themes = []
        for theme, freq in sorted(theme_freq.items(), key=lambda x: x[1], reverse=True)[:15]:
            trending_themes.append({
                "theme": theme,
                "frequency": freq,
                "popularity_score": freq / len(content_list) if content_list else 0,
                "trend_direction": "rising"  # Simplified - could use historical data
            })
        
        # Analyze content patterns
        content_patterns = {
            "average_length": sum(content_length_trends) / len(content_length_trends) if content_length_trends else 0,
            "length_trend": "increasing" if len(content_length_trends) > 1 and content_length_trends[-1] > content_length_trends[0] else "stable",
            "content_variety": len(set(themes)),
            "most_common_theme": max(theme_freq, key=theme_freq.get) if theme_freq else None
        }
        
        return {
            "content_trends": trending_themes,
            "trending_themes": [t["theme"] for t in trending_themes[:10]],
            "content_patterns": content_patterns,
            "theme_diversity": len(theme_freq) / max(len(themes), 1)
        }
    
    async def _analyze_temporal_patterns(self, search_results: List[Any], time_series_data: List[Any] = None) -> Dict[str, Any]:
        """Analyze how trends change over time."""
        
        # Simulate temporal analysis (in real implementation, would use actual timestamps)
        current_time = datetime.now()
        time_periods = [
            {"period": "last_hour", "start": current_time - timedelta(hours=1)},
            {"period": "last_day", "start": current_time - timedelta(days=1)},
            {"period": "last_week", "start": current_time - timedelta(weeks=1)},
            {"period": "last_month", "start": current_time - timedelta(days=30)}
        ]
        
        temporal_patterns = []
        
        for period in time_periods:
            # Simulate activity for this period
            period_activity = len(search_results) * (0.5 + (period["period"] == "last_day") * 0.3)
            
            temporal_patterns.append({
                "period": period["period"],
                "activity_level": period_activity,
                "trend_direction": "increasing" if period_activity > len(search_results) * 0.5 else "stable",
                "key_topics": self._get_period_topics(search_results, period["period"]),
                "engagement_score": min(period_activity / 10, 1.0)
            })
        
        # Identify peak periods
        peak_period = max(temporal_patterns, key=lambda x: x["activity_level"])
        
        return {
            "periods": temporal_patterns,
            "peak_period": peak_period["period"],
            "overall_trend": "growing" if peak_period["period"] in ["last_day", "last_hour"] else "stable",
            "trend_acceleration": "moderate",
            "seasonal_patterns": self._detect_seasonal_patterns(temporal_patterns)
        }
    
    async def _analyze_engagement_trends(self, search_results: List[Any]) -> Dict[str, Any]:
        """Analyze engagement and interest trends."""
        
        if not search_results:
            return {"engagement_metrics": {}, "interest_trends": [], "viral_potential": 0.0}
        
        # Calculate engagement metrics
        total_results = len(search_results)
        
        # Simulate engagement metrics (in real implementation, would use actual data)
        engagement_metrics = {
            "search_volume": total_results,
            "interest_score": min(total_results / 50, 1.0),  # Normalize to 0-1
            "virality_indicator": 0.3 + (total_results > 100) * 0.4,
            "user_engagement": 0.7 if total_results > 50 else 0.4,
            "content_shareability": self._calculate_shareability_score(search_results)
        }
        
        # Analyze interest trends
        interest_trends = []
        for i, result in enumerate(search_results[:10]):  # Top 10 results
            interest_score = (10 - i) / 10  # Higher score for top results
            
            interest_trends.append({
                "topic": getattr(result, 'title', f'Topic {i+1}'),
                "interest_score": interest_score,
                "trend_momentum": "high" if interest_score > 0.7 else "medium" if interest_score > 0.4 else "low",
                "viral_potential": interest_score * engagement_metrics["virality_indicator"]
            })
        
        # Calculate overall viral potential
        viral_potential = (
            engagement_metrics["interest_score"] * 0.3 +
            engagement_metrics["virality_indicator"] * 0.4 +
            engagement_metrics["content_shareability"] * 0.3
        )
        
        return {
            "engagement_metrics": engagement_metrics,
            "interest_trends": interest_trends,
            "viral_potential": viral_potential,
            "trending_momentum": "high" if viral_potential > 0.7 else "medium" if viral_potential > 0.4 else "low"
        }
    
    async def _calculate_popularity_metrics(self, topics: List[str], search_results: List[Any]) -> Dict[str, Any]:
        """Calculate popularity metrics for specific topics."""
        
        popularity_metrics = []
        
        for topic in topics:
            topic_lower = topic.lower()
            
            # Count mentions in search results
            mentions = 0
            relevance_score = 0.0
            
            for result in search_results:
                result_text = ""
                if hasattr(result, 'title') and result.title:
                    result_text += result.title.lower() + " "
                if hasattr(result, 'description') and result.description:
                    result_text += result.description.lower()
                
                if topic_lower in result_text:
                    mentions += 1
                    # Calculate relevance based on position and frequency
                    relevance_score += result_text.count(topic_lower) * 0.1
            
            # Calculate popularity score
            popularity_score = (mentions / max(len(search_results), 1)) * 0.7 + min(relevance_score, 1.0) * 0.3
            
            popularity_metrics.append({
                "topic": topic,
                "mentions": mentions,
                "popularity_score": popularity_score,
                "trend_level": "high" if popularity_score > 0.6 else "medium" if popularity_score > 0.3 else "low",
                "growth_potential": self._calculate_growth_potential(topic, mentions, len(search_results))
            })
        
        return {
            "topic_metrics": popularity_metrics,
            "most_popular": max(popularity_metrics, key=lambda x: x["popularity_score"]) if popularity_metrics else None,
            "average_popularity": sum(m["popularity_score"] for m in popularity_metrics) / max(len(popularity_metrics), 1),
            "trending_topics": [m["topic"] for m in popularity_metrics if m["trend_level"] in ["high", "medium"]]
        }
    
    async def _perform_trend_comparison(self, comparison_topics: List[str], datasets: List[Any]) -> Dict[str, Any]:
        """Compare trends across different topics."""
        
        if len(comparison_topics) < 2:
            return {"comparison_results": [], "winner": None, "insights": []}
        
        topic_comparisons = []
        
        for i, topic1 in enumerate(comparison_topics):
            for topic2 in comparison_topics[i+1:]:
                # Simulate comparison metrics
                topic1_score = len(topic1) * 0.1 + hash(topic1) % 100 / 100
                topic2_score = len(topic2) * 0.1 + hash(topic2) % 100 / 100
                
                comparison = {
                    "topic1": topic1,
                    "topic2": topic2,
                    "topic1_score": topic1_score,
                    "topic2_score": topic2_score,
                    "winner": topic1 if topic1_score > topic2_score else topic2,
                    "score_difference": abs(topic1_score - topic2_score),
                    "competitiveness": "high" if abs(topic1_score - topic2_score) < 0.2 else "moderate"
                }
                
                topic_comparisons.append(comparison)
        
        # Find overall winner
        topic_scores = {}
        for comparison in topic_comparisons:
            topic_scores[comparison["topic1"]] = topic_scores.get(comparison["topic1"], 0) + comparison["topic1_score"]
            topic_scores[comparison["topic2"]] = topic_scores.get(comparison["topic2"], 0) + comparison["topic2_score"]
        
        overall_winner = max(topic_scores, key=topic_scores.get) if topic_scores else None
        
        # Generate insights
        insights = [
            f"Compared {len(comparison_topics)} topics across multiple metrics",
            f"Overall trending leader: {overall_winner}" if overall_winner else "No clear leader identified",
            f"Most competitive comparison: {min(topic_comparisons, key=lambda x: x['score_difference'])['topic1']} vs {min(topic_comparisons, key=lambda x: x['score_difference'])['topic2']}" if topic_comparisons else "No comparisons available"
        ]
        
        return {
            "comparison_results": topic_comparisons,
            "overall_winner": overall_winner,
            "topic_scores": topic_scores,
            "insights": insights,
            "competitiveness_level": "high" if any(c["competitiveness"] == "high" for c in topic_comparisons) else "moderate"
        }
    
    async def _generate_trend_predictions(self, current_trends: List[Any], historical_data: List[Any]) -> Dict[str, Any]:
        """Generate predictions for future trend directions."""
        
        predictions = []
        
        # Analyze current trends for prediction
        for i, trend in enumerate(current_trends[:10]):  # Limit to top 10 trends
            trend_name = str(trend) if not isinstance(trend, dict) else trend.get("name", f"Trend {i+1}")
            
            # Simple prediction logic (can be enhanced with ML)
            momentum_score = (10 - i) / 10  # Higher for top trends
            stability_score = 0.7 + (i % 3) * 0.1  # Simulate stability
            
            # Predict future direction
            if momentum_score > 0.7:
                direction = "rising"
                confidence = 0.8
            elif momentum_score > 0.4:
                direction = "stable"
                confidence = 0.6
            else:
                direction = "declining"
                confidence = 0.5
            
            predictions.append({
                "trend": trend_name,
                "current_momentum": momentum_score,
                "predicted_direction": direction,
                "confidence": confidence,
                "time_horizon": "30_days",
                "peak_probability": momentum_score * 0.8,
                "factors": [
                    "Current momentum" if momentum_score > 0.6 else "Moderate interest",
                    "Market stability" if stability_score > 0.7 else "Market uncertainty"
                ]
            })
        
        # Generate overall forecast
        rising_trends = [p for p in predictions if p["predicted_direction"] == "rising"]
        declining_trends = [p for p in predictions if p["predicted_direction"] == "declining"]
        
        overall_forecast = {
            "market_sentiment": "bullish" if len(rising_trends) > len(declining_trends) else "bearish",
            "volatility": "high" if len(rising_trends) + len(declining_trends) > len(predictions) * 0.6 else "moderate",
            "next_big_trend": rising_trends[0]["trend"] if rising_trends else None,
            "trends_to_watch": [p["trend"] for p in predictions[:3]]
        }
        
        return {
            "trend_predictions": predictions,
            "overall_forecast": overall_forecast,
            "prediction_confidence": sum(p["confidence"] for p in predictions) / max(len(predictions), 1),
            "forecast_period": "next_30_days"
        }
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text."""
        import re
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "this", "that", "these", "those", "is", "are", 
            "was", "were", "be", "been", "have", "has", "had", "do", "does", "did"
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def _categorize_keyword(self, keyword: str) -> str:
        """Categorize a keyword by topic."""
        keyword_lower = keyword.lower()
        
        tech_words = ["ai", "machine", "learning", "technology", "software", "digital", "data", "cloud"]
        business_words = ["market", "business", "economy", "finance", "investment", "growth", "company"]
        health_words = ["health", "medical", "wellness", "fitness", "disease", "treatment", "therapy"]
        entertainment_words = ["movie", "music", "game", "entertainment", "celebrity", "sports", "show"]
        
        if any(word in keyword_lower for word in tech_words):
            return "technology"
        elif any(word in keyword_lower for word in business_words):
            return "business"
        elif any(word in keyword_lower for word in health_words):
            return "health"
        elif any(word in keyword_lower for word in entertainment_words):
            return "entertainment"
        else:
            return "general"
    
    def _calculate_keyword_trend_score(self, keyword: str, frequency: int, total_keywords: int) -> float:
        """Calculate trending score for a keyword."""
        # Simple scoring based on frequency and keyword characteristics
        base_score = frequency / max(total_keywords, 1)
        
        # Bonus for shorter, impactful keywords
        length_bonus = max(0, (10 - len(keyword)) / 10) * 0.1
        
        # Bonus for tech/trending categories
        category_bonus = 0.1 if self._categorize_keyword(keyword) in ["technology", "business"] else 0
        
        return min(base_score + length_bonus + category_bonus, 1.0)
    
    def _get_top_keyword_categories(self, trending_keywords: List[Dict[str, Any]]) -> List[str]:
        """Get most popular keyword categories."""
        category_counts = {}
        for keyword_data in trending_keywords:
            category = keyword_data["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return sorted(category_counts.keys(), key=lambda x: category_counts[x], reverse=True)[:5]
    
    def _extract_themes_from_content(self, content: str) -> List[str]:
        """Extract themes from content."""
        # Simple theme extraction based on common patterns
        themes = []
        
        content_lower = content.lower()
        
        # Look for theme indicators
        theme_patterns = {
            "innovation": ["innovation", "breakthrough", "new", "novel", "revolutionary"],
            "growth": ["growth", "increase", "expansion", "rising", "growing"],
            "challenge": ["challenge", "problem", "issue", "difficulty", "crisis"],
            "opportunity": ["opportunity", "potential", "chance", "possibility"],
            "technology": ["technology", "tech", "digital", "ai", "software"],
            "sustainability": ["sustainable", "green", "environmental", "climate", "eco"]
        }
        
        for theme, indicators in theme_patterns.items():
            if any(indicator in content_lower for indicator in indicators):
                themes.append(theme)
        
        return themes
    
    def _get_period_topics(self, search_results: List[Any], period: str) -> List[str]:
        """Get key topics for a specific time period."""
        # Simulate period-specific topics
        topics = []
        
        for i, result in enumerate(search_results[:5]):  # Top 5 for each period
            if hasattr(result, 'title') and result.title:
                topics.append(result.title[:50])  # Truncate for readability
            else:
                topics.append(f"Topic {i+1} for {period}")
        
        return topics
    
    def _detect_seasonal_patterns(self, temporal_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect seasonal patterns in trends."""
        # Simple seasonal pattern detection
        activity_levels = [p["activity_level"] for p in temporal_patterns]
        
        if not activity_levels:
            return {"pattern_detected": False}
        
        avg_activity = sum(activity_levels) / len(activity_levels)
        variance = sum((x - avg_activity) ** 2 for x in activity_levels) / len(activity_levels)
        
        return {
            "pattern_detected": variance > avg_activity * 0.5,
            "pattern_type": "cyclical" if variance > avg_activity else "stable",
            "peak_periods": [p["period"] for p in temporal_patterns if p["activity_level"] > avg_activity],
            "low_periods": [p["period"] for p in temporal_patterns if p["activity_level"] < avg_activity]
        }
    
    def _calculate_shareability_score(self, search_results: List[Any]) -> float:
        """Calculate content shareability score."""
        if not search_results:
            return 0.0
        
        # Simple shareability based on result diversity and relevance
        unique_domains = set()
        total_relevance = 0.0
        
        for result in search_results:
            if hasattr(result, 'url') and result.url:
                domain = result.url.split('/')[2] if '/' in result.url else result.url
                unique_domains.add(domain)
            
            if hasattr(result, 'relevance_score') and result.relevance_score:
                total_relevance += result.relevance_score
        
        domain_diversity = len(unique_domains) / max(len(search_results), 1)
        avg_relevance = total_relevance / max(len(search_results), 1)
        
        return (domain_diversity * 0.6 + avg_relevance * 0.4)
    
    def _calculate_growth_potential(self, topic: str, mentions: int, total_results: int) -> str:
        """Calculate growth potential for a topic."""
        mention_ratio = mentions / max(total_results, 1)
        
        if mention_ratio > 0.5:
            return "high"
        elif mention_ratio > 0.2:
            return "medium"
        else:
            return "low"
    
    def _generate_trend_insights(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analyses."""
        insights = []
        
        # Keywords insights
        if "keywords" in analyses and "error" not in analyses["keywords"]:
            keywords = analyses["keywords"]
            if keywords.get("trending_keywords"):
                top_keyword = keywords["trending_keywords"][0]["keyword"]
                insights.append(f"Top trending keyword: '{top_keyword}'")
        
        # Content insights
        if "content" in analyses and "error" not in analyses["content"]:
            content = analyses["content"]
            if content.get("trending_themes"):
                top_theme = content["trending_themes"][0]
                insights.append(f"Most popular content theme: '{top_theme}'")
        
        # Temporal insights
        if "temporal" in analyses and "error" not in analyses["temporal"]:
            temporal = analyses["temporal"]
            peak_period = temporal.get("peak_period")
            if peak_period:
                insights.append(f"Peak activity period: {peak_period}")
        
        # Engagement insights
        if "engagement" in analyses and "error" not in analyses["engagement"]:
            engagement = analyses["engagement"]
            viral_potential = engagement.get("viral_potential", 0)
            if viral_potential > 0.7:
                insights.append("High viral potential detected")
            elif viral_potential > 0.4:
                insights.append("Moderate viral potential detected")
        
        return insights
    
    def _calculate_trending_score(self, analyses: Dict[str, Any]) -> float:
        """Calculate overall trending score from analyses."""
        scores = []
        
        # Keywords score
        if "keywords" in analyses and "error" not in analyses["keywords"]:
            keywords = analyses["keywords"]
            if keywords.get("trending_keywords"):
                avg_keyword_score = sum(k["trend_score"] for k in keywords["trending_keywords"][:5]) / 5
                scores.append(avg_keyword_score)
        
        # Engagement score
        if "engagement" in analyses and "error" not in analyses["engagement"]:
            engagement = analyses["engagement"]
            viral_potential = engagement.get("viral_potential", 0)
            scores.append(viral_potential)
        
        # Temporal momentum score
        if "temporal" in analyses and "error" not in analyses["temporal"]:
            temporal = analyses["temporal"]
            if temporal.get("overall_trend") == "growing":
                scores.append(0.8)
            else:
                scores.append(0.5)
        
        return sum(scores) / max(len(scores), 1)
    
    def get_trend_history(self) -> List[Dict[str, Any]]:
        """Get trend monitoring history for this agent."""
        return self.trend_history.copy()
    
    def update_trend_database(self, topic: str, trend_data: Dict[str, Any]):
        """Update the trend database with new data."""
        if topic not in self.trend_database:
            self.trend_database[topic] = []
        
        trend_entry = {
            "timestamp": datetime.now(),
            "data": trend_data
        }
        
        self.trend_database[topic].append(trend_entry)
        
        # Keep only recent entries (last 100 per topic)
        if len(self.trend_database[topic]) > 100:
            self.trend_database[topic] = self.trend_database[topic][-100:]
