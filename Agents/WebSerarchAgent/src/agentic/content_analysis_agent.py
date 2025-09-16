"""
Content Analysis Agent for processing and analyzing web content.
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentGoal, AgentCapability

logger = logging.getLogger(__name__)

class ContentAnalysisAgent(BaseAgent):
    """
    Specialized agent for analyzing web content, extracting insights, and processing text.
    """
    
    def __init__(self, name: str = "ContentAnalysisAgent"):
        """Initialize the Content Analysis Agent."""
        capabilities = [
            AgentCapability(
                name="text_analysis",
                description="Analyze text content for insights, sentiment, and key information",
                input_types=["text", "web_content", "documents"],
                output_types=["analysis_results", "insights", "structured_data"]
            ),
            AgentCapability(
                name="sentiment_analysis",
                description="Analyze sentiment and emotional tone of content",
                input_types=["text", "articles", "reviews"],
                output_types=["sentiment_score", "emotional_analysis", "mood_indicators"]
            ),
            AgentCapability(
                name="keyword_extraction",
                description="Extract key terms, topics, and themes from content",
                input_types=["text", "content"],
                output_types=["keywords", "topics", "themes", "entities"]
            ),
            AgentCapability(
                name="content_summarization",
                description="Create summaries and abstracts from long content",
                input_types=["articles", "documents", "web_pages"],
                output_types=["summaries", "abstracts", "key_points"]
            ),
            AgentCapability(
                name="language_detection",
                description="Detect language and linguistic patterns",
                input_types=["text", "content"],
                output_types=["language", "linguistic_features", "readability_score"]
            )
        ]
        
        super().__init__(name, capabilities)
        self.analysis_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized {name} with content analysis capabilities")
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """
        Execute a content analysis goal.
        
        Args:
            goal: The analysis goal to achieve
            
        Returns:
            Dictionary containing analysis results and insights
        """
        goal_desc = goal.description.lower()
        context = goal.context or {}
        
        logger.info(f"ContentAnalysisAgent executing goal: {goal.description}")
        
        # Determine analysis type based on goal
        if "sentiment" in goal_desc:
            return await self._sentiment_analysis(goal)
        elif "keywords" in goal_desc or "extract" in goal_desc:
            return await self._keyword_extraction(goal)
        elif "summarize" in goal_desc or "summary" in goal_desc:
            return await self._content_summarization(goal)
        elif "language" in goal_desc or "detect" in goal_desc:
            return await self._language_detection(goal)
        else:
            return await self._comprehensive_analysis(goal)
    
    async def _comprehensive_analysis(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform comprehensive content analysis."""
        content = self._extract_content_from_goal(goal)
        
        if not content:
            return {
                "analysis_type": "comprehensive",
                "status": "failed",
                "error": "No content provided for analysis"
            }
        
        logger.info(f"Performing comprehensive analysis on {len(content)} characters of content")
        
        try:
            results = {
                "analysis_type": "comprehensive",
                "timestamp": datetime.now(),
                "content_length": len(content),
                "analyses": {}
            }
            
            # Perform multiple analyses
            analyses = await asyncio.gather(
                self._analyze_sentiment(content),
                self._extract_keywords(content),
                self._detect_language(content),
                self._analyze_readability(content),
                self._extract_entities(content),
                return_exceptions=True
            )
            
            # Process results
            analysis_types = ["sentiment", "keywords", "language", "readability", "entities"]
            for i, analysis in enumerate(analyses):
                if not isinstance(analysis, Exception):
                    results["analyses"][analysis_types[i]] = analysis
                else:
                    logger.warning(f"Analysis {analysis_types[i]} failed: {str(analysis)}")
                    results["analyses"][analysis_types[i]] = {"error": str(analysis)}
            
            # Generate insights
            results["insights"] = self._generate_content_insights(results["analyses"])
            results["status"] = "completed"
            
            # Record analysis
            self.analysis_history.append({
                "goal_id": goal.id,
                "analysis_type": "comprehensive",
                "content_length": len(content),
                "timestamp": datetime.now()
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {str(e)}")
            return {
                "analysis_type": "comprehensive",
                "status": "failed",
                "error": str(e)
            }
    
    async def _sentiment_analysis(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform sentiment analysis on content."""
        content = self._extract_content_from_goal(goal)
        
        try:
            sentiment_result = await self._analyze_sentiment(content)
            
            return {
                "analysis_type": "sentiment",
                "timestamp": datetime.now(),
                "content_length": len(content),
                "sentiment": sentiment_result,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {
                "analysis_type": "sentiment",
                "status": "failed",
                "error": str(e)
            }
    
    async def _keyword_extraction(self, goal: AgentGoal) -> Dict[str, Any]:
        """Extract keywords and key phrases from content."""
        content = self._extract_content_from_goal(goal)
        
        try:
            keywords_result = await self._extract_keywords(content)
            
            return {
                "analysis_type": "keywords",
                "timestamp": datetime.now(),
                "content_length": len(content),
                "keywords": keywords_result,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return {
                "analysis_type": "keywords",
                "status": "failed",
                "error": str(e)
            }
    
    async def _content_summarization(self, goal: AgentGoal) -> Dict[str, Any]:
        """Summarize content into key points."""
        content = self._extract_content_from_goal(goal)
        
        try:
            summary = await self._create_summary(content)
            
            return {
                "analysis_type": "summarization",
                "timestamp": datetime.now(),
                "original_length": len(content),
                "summary": summary,
                "compression_ratio": len(summary["text"]) / len(content) if content else 0,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Content summarization failed: {str(e)}")
            return {
                "analysis_type": "summarization",
                "status": "failed",
                "error": str(e)
            }
    
    async def _language_detection(self, goal: AgentGoal) -> Dict[str, Any]:
        """Detect language and linguistic features."""
        content = self._extract_content_from_goal(goal)
        
        try:
            language_result = await self._detect_language(content)
            
            return {
                "analysis_type": "language_detection",
                "timestamp": datetime.now(),
                "content_length": len(content),
                "language": language_result,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return {
                "analysis_type": "language_detection",
                "status": "failed",
                "error": str(e)
            }
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content."""
        if not content:
            return {"score": 0.0, "label": "neutral", "confidence": 0.0}
        
        # Simple sentiment analysis (can be enhanced with ML models)
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic", 
            "positive", "happy", "love", "best", "awesome", "brilliant"
        ]
        negative_words = [
            "bad", "terrible", "awful", "horrible", "worst", "hate", 
            "negative", "sad", "disappointed", "poor", "useless"
        ]
        
        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_words = len(words)
        
        if total_words == 0:
            return {"score": 0.0, "label": "neutral", "confidence": 0.0}
        
        # Calculate sentiment score (-1 to 1)
        sentiment_score = (positive_count - negative_count) / total_words
        
        # Determine label
        if sentiment_score > 0.1:
            label = "positive"
        elif sentiment_score < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        # Calculate confidence
        confidence = min(abs(sentiment_score) * 5, 1.0)  # Scale to 0-1
        
        return {
            "score": sentiment_score,
            "label": label,
            "confidence": confidence,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "total_words": total_words
        }
    
    async def _extract_keywords(self, content: str) -> Dict[str, Any]:
        """Extract keywords and key phrases from content."""
        if not content:
            return {"keywords": [], "phrases": [], "entities": []}
        
        # Simple keyword extraction (can be enhanced with NLP libraries)
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "this", "that", "these", "those", "is", "are", 
            "was", "were", "be", "been", "have", "has", "had", "do", "does", "did"
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Extract potential entities (capitalized words)
        entities = list(set(re.findall(r'\b[A-Z][a-z]+\b', content)))
        
        # Extract phrases (simple bigrams)
        phrases = []
        for i in range(len(filtered_words) - 1):
            bigram = f"{filtered_words[i]} {filtered_words[i+1]}"
            phrases.append(bigram)
        
        phrase_freq = {}
        for phrase in phrases:
            phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1
        
        top_phrases = sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "keywords": [{"word": word, "frequency": freq} for word, freq in keywords],
            "phrases": [{"phrase": phrase, "frequency": freq} for phrase, freq in top_phrases],
            "entities": entities[:15],
            "total_unique_words": len(word_freq)
        }
    
    async def _detect_language(self, content: str) -> Dict[str, Any]:
        """Detect language and linguistic features."""
        if not content:
            return {"language": "unknown", "confidence": 0.0}
        
        # Simple language detection (can be enhanced with proper language detection libraries)
        # This is a basic implementation for demonstration
        
        english_indicators = ["the", "and", "is", "in", "to", "of", "a", "that", "it", "with"]
        spanish_indicators = ["el", "la", "de", "que", "y", "en", "un", "es", "se", "no"]
        french_indicators = ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir"]
        
        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)
        
        english_count = sum(1 for word in words if word in english_indicators)
        spanish_count = sum(1 for word in words if word in spanish_indicators)
        french_count = sum(1 for word in words if word in french_indicators)
        
        total_words = len(words)
        if total_words == 0:
            return {"language": "unknown", "confidence": 0.0}
        
        # Determine most likely language
        scores = {
            "english": english_count / total_words,
            "spanish": spanish_count / total_words,
            "french": french_count / total_words
        }
        
        detected_language = max(scores, key=scores.get)
        confidence = scores[detected_language]
        
        # Calculate readability metrics
        sentences = len(re.split(r'[.!?]+', content))
        avg_words_per_sentence = total_words / max(sentences, 1)
        
        return {
            "language": detected_language,
            "confidence": confidence,
            "total_words": total_words,
            "total_sentences": sentences,
            "avg_words_per_sentence": avg_words_per_sentence,
            "readability_score": self._calculate_readability_score(total_words, sentences)
        }
    
    async def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze readability and complexity of content."""
        if not content:
            return {"readability_score": 0, "reading_level": "unknown"}
        
        sentences = len(re.split(r'[.!?]+', content))
        words = len(re.findall(r'\b\w+\b', content))
        
        # Simple readability calculation
        readability_score = self._calculate_readability_score(words, sentences)
        
        # Determine reading level
        if readability_score >= 90:
            reading_level = "very_easy"
        elif readability_score >= 80:
            reading_level = "easy"
        elif readability_score >= 70:
            reading_level = "fairly_easy"
        elif readability_score >= 60:
            reading_level = "standard"
        elif readability_score >= 50:
            reading_level = "fairly_difficult"
        elif readability_score >= 30:
            reading_level = "difficult"
        else:
            reading_level = "very_difficult"
        
        return {
            "readability_score": readability_score,
            "reading_level": reading_level,
            "word_count": words,
            "sentence_count": sentences,
            "avg_words_per_sentence": words / max(sentences, 1)
        }
    
    async def _extract_entities(self, content: str) -> Dict[str, Any]:
        """Extract named entities from content."""
        if not content:
            return {"entities": [], "entity_types": {}}
        
        # Simple entity extraction (can be enhanced with NER models)
        # Extract potential person names (Title Case patterns)
        person_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        persons = re.findall(person_pattern, content)
        
        # Extract potential organizations (words ending with Corp, Inc, etc.)
        org_pattern = r'\b[A-Z][a-zA-Z\s]*(Corp|Inc|LLC|Ltd|Company|Organization)\b'
        organizations = re.findall(org_pattern, content)
        
        # Extract potential locations (capitalize words after 'in', 'at', 'from')
        location_pattern = r'\b(?:in|at|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        locations = re.findall(location_pattern, content)
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b'
        dates = re.findall(date_pattern, content)
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        
        entities = {
            "persons": list(set(persons)),
            "organizations": list(set(organizations)),
            "locations": list(set(locations)),
            "dates": list(set(dates)),
            "urls": list(set(urls))
        }
        
        return {
            "entities": entities,
            "entity_counts": {k: len(v) for k, v in entities.items()},
            "total_entities": sum(len(v) for v in entities.values())
        }
    
    async def _create_summary(self, content: str) -> Dict[str, Any]:
        """Create a summary of the content."""
        if not content:
            return {"text": "", "key_points": [], "summary_ratio": 0}
        
        # Simple extractive summarization
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return {
                "text": content,
                "key_points": sentences,
                "summary_ratio": 1.0
            }
        
        # Score sentences based on keyword frequency
        keywords_result = await self._extract_keywords(content)
        important_words = set(kw["word"] for kw in keywords_result["keywords"][:10])
        
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            words = re.findall(r'\b\w+\b', sentence.lower())
            for word in words:
                if word in important_words:
                    score += 1
            sentence_scores[i] = score / max(len(words), 1)
        
        # Select top sentences
        num_summary_sentences = max(1, len(sentences) // 3)
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_summary_sentences]
        top_sentences.sort(key=lambda x: x[0])  # Maintain original order
        
        summary_sentences = [sentences[i] for i, _ in top_sentences]
        summary_text = '. '.join(summary_sentences) + '.'
        
        return {
            "text": summary_text,
            "key_points": summary_sentences,
            "summary_ratio": len(summary_text) / len(content),
            "original_sentences": len(sentences),
            "summary_sentences": len(summary_sentences)
        }
    
    def _calculate_readability_score(self, words: int, sentences: int) -> float:
        """Calculate simplified readability score."""
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        
        # Simplified Flesch Reading Ease approximation
        score = 206.835 - (1.015 * avg_sentence_length)
        
        return max(0, min(100, score))
    
    def _generate_content_insights(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate insights from content analyses."""
        insights = []
        
        # Sentiment insights
        if "sentiment" in analyses and "error" not in analyses["sentiment"]:
            sentiment = analyses["sentiment"]
            insights.append(f"Content sentiment is {sentiment['label']} with {sentiment['confidence']:.1%} confidence")
        
        # Language insights
        if "language" in analyses and "error" not in analyses["language"]:
            lang = analyses["language"]
            insights.append(f"Content is in {lang['language']} with {lang['avg_words_per_sentence']:.1f} words per sentence")
        
        # Keyword insights
        if "keywords" in analyses and "error" not in analyses["keywords"]:
            keywords = analyses["keywords"]
            if keywords["keywords"]:
                top_keyword = keywords["keywords"][0]["word"]
                insights.append(f"Most frequent keyword is '{top_keyword}'")
        
        # Readability insights
        if "readability" in analyses and "error" not in analyses["readability"]:
            readability = analyses["readability"]
            insights.append(f"Content reading level is {readability['reading_level'].replace('_', ' ')}")
        
        # Entity insights
        if "entities" in analyses and "error" not in analyses["entities"]:
            entities = analyses["entities"]
            total_entities = entities["total_entities"]
            if total_entities > 0:
                insights.append(f"Content contains {total_entities} named entities")
        
        return insights
    
    def _extract_content_from_goal(self, goal: AgentGoal) -> str:
        """Extract content to analyze from goal context."""
        context = goal.context or {}
        
        # Try different context keys
        content = context.get("content", "")
        if not content:
            content = context.get("text", "")
        if not content:
            content = context.get("web_content", "")
        if not content:
            content = context.get("article", "")
        
        # If no content in context, use goal description
        if not content:
            content = goal.description
        
        return content
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis history for this agent."""
        return self.analysis_history.copy()
