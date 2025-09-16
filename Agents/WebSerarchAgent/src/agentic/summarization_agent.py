"""
Summarization Agent for creating concise summaries and abstracts.
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentGoal, AgentCapability

logger = logging.getLogger(__name__)

class SummarizationAgent(BaseAgent):
    """
    Specialized agent for creating summaries, abstracts, and key point extraction.
    """
    
    def __init__(self, name: str = "SummarizationAgent"):
        """Initialize the Summarization Agent."""
        capabilities = [
            AgentCapability(
                name="text_summarization",
                description="Create concise summaries from long text content",
                input_types=["text", "articles", "documents", "web_content"],
                output_types=["summaries", "abstracts", "condensed_text"]
            ),
            AgentCapability(
                name="key_points_extraction",
                description="Extract key points and main ideas from content",
                input_types=["content", "articles", "reports"],
                output_types=["key_points", "main_ideas", "highlights"]
            ),
            AgentCapability(
                name="multi_document_summary",
                description="Summarize multiple documents into a coherent overview",
                input_types=["document_list", "multiple_sources", "article_collection"],
                output_types=["unified_summary", "comprehensive_overview", "synthesis"]
            ),
            AgentCapability(
                name="bullet_point_generation",
                description="Convert content into structured bullet points",
                input_types=["text", "content", "articles"],
                output_types=["bullet_points", "structured_list", "formatted_summary"]
            ),
            AgentCapability(
                name="executive_summary",
                description="Create executive-level summaries for business content",
                input_types=["reports", "business_content", "analysis"],
                output_types=["executive_summary", "business_brief", "decision_summary"]
            )
        ]
        
        super().__init__(name, capabilities)
        self.summarization_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized {name} with summarization capabilities")
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """
        Execute a summarization goal.
        
        Args:
            goal: The summarization goal to achieve
            
        Returns:
            Dictionary containing summarization results
        """
        goal_desc = goal.description.lower()
        context = goal.context or {}
        
        logger.info(f"SummarizationAgent executing goal: {goal.description}")
        
        # Determine summarization type based on goal
        if "executive" in goal_desc:
            return await self._create_executive_summary(goal)
        elif "bullet" in goal_desc or "points" in goal_desc:
            return await self._create_bullet_points(goal)
        elif "key points" in goal_desc or "main ideas" in goal_desc:
            return await self._extract_key_points(goal)
        elif "multiple" in goal_desc or "documents" in goal_desc:
            return await self._multi_document_summary(goal)
        else:
            return await self._text_summarization(goal)
    
    async def _text_summarization(self, goal: AgentGoal) -> Dict[str, Any]:
        """Create a standard text summary."""
        content = self._extract_content_from_goal(goal)
        summary_length = goal.context.get("summary_length", "medium")
        
        if not content:
            return {
                "summarization_type": "text_summary",
                "status": "failed",
                "error": "No content provided for summarization"
            }
        
        logger.info(f"Creating {summary_length} summary of {len(content)} characters")
        
        try:
            # Determine target length based on request
            if summary_length == "short":
                target_ratio = 0.1  # 10% of original
                max_sentences = 3
            elif summary_length == "long":
                target_ratio = 0.4  # 40% of original
                max_sentences = 10
            else:  # medium
                target_ratio = 0.25  # 25% of original
                max_sentences = 6
            
            summary_result = await self._create_extractive_summary(content, target_ratio, max_sentences)
            
            results = {
                "summarization_type": "text_summary",
                "timestamp": datetime.now(),
                "original_length": len(content),
                "summary": summary_result,
                "compression_ratio": len(summary_result["text"]) / len(content),
                "status": "completed"
            }
            
            # Record summarization
            self.summarization_history.append({
                "goal_id": goal.id,
                "summarization_type": "text_summary",
                "original_length": len(content),
                "summary_length": len(summary_result["text"]),
                "compression_ratio": results["compression_ratio"],
                "timestamp": datetime.now()
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Text summarization failed: {str(e)}")
            return {
                "summarization_type": "text_summary",
                "status": "failed",
                "error": str(e)
            }
    
    async def _extract_key_points(self, goal: AgentGoal) -> Dict[str, Any]:
        """Extract key points from content."""
        content = self._extract_content_from_goal(goal)
        max_points = goal.context.get("max_points", 5)
        
        try:
            key_points = await self._identify_key_points(content, max_points)
            
            return {
                "summarization_type": "key_points",
                "timestamp": datetime.now(),
                "content_length": len(content),
                "key_points": key_points,
                "total_points": len(key_points["points"]),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Key points extraction failed: {str(e)}")
            return {
                "summarization_type": "key_points",
                "status": "failed",
                "error": str(e)
            }
    
    async def _create_bullet_points(self, goal: AgentGoal) -> Dict[str, Any]:
        """Create structured bullet points from content."""
        content = self._extract_content_from_goal(goal)
        
        try:
            bullet_points = await self._generate_bullet_points(content)
            
            return {
                "summarization_type": "bullet_points",
                "timestamp": datetime.now(),
                "content_length": len(content),
                "bullet_points": bullet_points,
                "total_bullets": len(bullet_points["bullets"]),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Bullet points creation failed: {str(e)}")
            return {
                "summarization_type": "bullet_points",
                "status": "failed",
                "error": str(e)
            }
    
    async def _create_executive_summary(self, goal: AgentGoal) -> Dict[str, Any]:
        """Create an executive-level summary."""
        content = self._extract_content_from_goal(goal)
        
        try:
            exec_summary = await self._generate_executive_summary(content)
            
            return {
                "summarization_type": "executive_summary",
                "timestamp": datetime.now(),
                "content_length": len(content),
                "executive_summary": exec_summary,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Executive summary creation failed: {str(e)}")
            return {
                "summarization_type": "executive_summary",
                "status": "failed",
                "error": str(e)
            }
    
    async def _multi_document_summary(self, goal: AgentGoal) -> Dict[str, Any]:
        """Create a summary from multiple documents."""
        documents = goal.context.get("documents", [])
        content_list = goal.context.get("content_list", [])
        
        all_content = documents + content_list
        
        if not all_content:
            # Try to extract from single content field
            single_content = self._extract_content_from_goal(goal)
            if single_content:
                # Split into sections as if they were separate documents
                sections = self._split_into_sections(single_content)
                all_content = sections
        
        try:
            multi_summary = await self._create_multi_document_summary(all_content)
            
            return {
                "summarization_type": "multi_document",
                "timestamp": datetime.now(),
                "documents_processed": len(all_content),
                "total_content_length": sum(len(str(doc)) for doc in all_content),
                "multi_summary": multi_summary,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Multi-document summary failed: {str(e)}")
            return {
                "summarization_type": "multi_document",
                "status": "failed",
                "error": str(e)
            }
    
    async def _create_extractive_summary(self, content: str, target_ratio: float, max_sentences: int) -> Dict[str, Any]:
        """Create extractive summary by selecting important sentences."""
        if not content:
            return {"text": "", "sentences": [], "method": "extractive"}
        
        # Split into sentences
        sentences = self._split_sentences(content)
        
        if len(sentences) <= max_sentences:
            return {
                "text": content,
                "sentences": sentences,
                "method": "extractive",
                "selection_reason": "Content already short enough"
            }
        
        # Score sentences
        sentence_scores = await self._score_sentences(sentences, content)
        
        # Select top sentences
        target_count = min(max_sentences, max(1, int(len(sentences) * target_ratio)))
        
        # Sort by score and select top sentences
        scored_sentences = [(score, i, sentence) for i, (sentence, score) in enumerate(zip(sentences, sentence_scores))]
        scored_sentences.sort(reverse=True)
        
        selected_sentences = scored_sentences[:target_count]
        # Sort selected sentences by original order
        selected_sentences.sort(key=lambda x: x[1])
        
        summary_sentences = [sentence for _, _, sentence in selected_sentences]
        summary_text = " ".join(summary_sentences)
        
        return {
            "text": summary_text,
            "sentences": summary_sentences,
            "method": "extractive",
            "selection_reason": f"Selected top {target_count} sentences out of {len(sentences)}",
            "sentence_scores": [score for score, _, _ in selected_sentences]
        }
    
    async def _identify_key_points(self, content: str, max_points: int) -> Dict[str, Any]:
        """Identify key points from content."""
        if not content:
            return {"points": [], "method": "extraction"}
        
        # Split content into sentences
        sentences = self._split_sentences(content)
        
        # Identify sentences that likely contain key points
        key_point_indicators = [
            "important", "key", "main", "primary", "significant", "crucial", 
            "essential", "fundamental", "critical", "major", "notably", 
            "firstly", "secondly", "finally", "in conclusion", "therefore"
        ]
        
        key_points = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Score based on key indicators
            score = 0
            for indicator in key_point_indicators:
                if indicator in sentence_lower:
                    score += 1
            
            # Bonus for sentences with numbers/statistics
            if re.search(r'\d+%|\d+\.\d+|\$\d+', sentence):
                score += 2
            
            # Bonus for sentences at beginning/end of paragraphs
            if sentence.strip().endswith('.') and len(sentence.split()) > 5:
                score += 1
            
            if score > 0:
                key_points.append({
                    "text": sentence.strip(),
                    "score": score,
                    "category": self._categorize_key_point(sentence)
                })
        
        # Sort by score and take top points
        key_points.sort(key=lambda x: x["score"], reverse=True)
        selected_points = key_points[:max_points]
        
        return {
            "points": selected_points,
            "total_candidates": len(key_points),
            "method": "extraction",
            "categories": list(set(point["category"] for point in selected_points))
        }
    
    async def _generate_bullet_points(self, content: str) -> Dict[str, Any]:
        """Generate structured bullet points."""
        if not content:
            return {"bullets": [], "structure": "flat"}
        
        # Split into logical sections
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        bullets = []
        
        for para in paragraphs:
            # Extract main idea from paragraph
            sentences = self._split_sentences(para)
            if sentences:
                # Use first sentence as main bullet, others as sub-bullets
                main_bullet = sentences[0].strip()
                
                # Clean up the main bullet
                if main_bullet.endswith('.'):
                    main_bullet = main_bullet[:-1]
                
                bullet_item = {
                    "main": main_bullet,
                    "sub_points": [],
                    "level": 1
                }
                
                # Add sub-points from remaining sentences
                for sentence in sentences[1:3]:  # Limit to 2 sub-points per main point
                    sub_point = sentence.strip()
                    if sub_point.endswith('.'):
                        sub_point = sub_point[:-1]
                    
                    if len(sub_point) > 20:  # Only add substantial sub-points
                        bullet_item["sub_points"].append(sub_point)
                
                bullets.append(bullet_item)
        
        return {
            "bullets": bullets,
            "total_main_points": len(bullets),
            "total_sub_points": sum(len(b["sub_points"]) for b in bullets),
            "structure": "hierarchical"
        }
    
    async def _generate_executive_summary(self, content: str) -> Dict[str, Any]:
        """Generate executive-level summary with key sections."""
        if not content:
            return {"sections": {}, "overview": ""}
        
        # Executive summary typically includes: Overview, Key Findings, Recommendations, Conclusion
        
        sentences = self._split_sentences(content)
        
        # Identify different types of content
        overview_sentences = []
        findings_sentences = []
        recommendation_sentences = []
        conclusion_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            if any(word in sentence_lower for word in ["overview", "introduction", "background", "context"]):
                overview_sentences.append(sentence)
            elif any(word in sentence_lower for word in ["found", "discovered", "revealed", "showed", "indicated"]):
                findings_sentences.append(sentence)
            elif any(word in sentence_lower for word in ["recommend", "suggest", "should", "propose", "advise"]):
                recommendation_sentences.append(sentence)
            elif any(word in sentence_lower for word in ["conclusion", "summary", "finally", "in closing"]):
                conclusion_sentences.append(sentence)
            else:
                # Default to findings if unclear
                findings_sentences.append(sentence)
        
        # Create sections
        sections = {}
        
        if overview_sentences:
            sections["overview"] = " ".join(overview_sentences[:2])  # Max 2 sentences
        elif sentences:
            sections["overview"] = sentences[0]  # Use first sentence as overview
        
        if findings_sentences:
            sections["key_findings"] = " ".join(findings_sentences[:3])  # Max 3 sentences
        
        if recommendation_sentences:
            sections["recommendations"] = " ".join(recommendation_sentences[:2])  # Max 2 sentences
        
        if conclusion_sentences:
            sections["conclusion"] = " ".join(conclusion_sentences[:1])  # Max 1 sentence
        elif sentences:
            sections["conclusion"] = sentences[-1]  # Use last sentence as conclusion
        
        # Create overall executive summary
        exec_text_parts = []
        for section_name in ["overview", "key_findings", "recommendations", "conclusion"]:
            if section_name in sections:
                exec_text_parts.append(sections[section_name])
        
        executive_text = " ".join(exec_text_parts)
        
        return {
            "sections": sections,
            "overview": executive_text,
            "section_count": len(sections),
            "total_length": len(executive_text)
        }
    
    async def _create_multi_document_summary(self, documents: List[str]) -> Dict[str, Any]:
        """Create unified summary from multiple documents."""
        if not documents:
            return {"unified_summary": "", "document_summaries": [], "synthesis": ""}
        
        # Summarize each document individually
        doc_summaries = []
        all_key_points = []
        
        for i, doc in enumerate(documents):
            if isinstance(doc, str) and doc.strip():
                doc_summary = await self._create_extractive_summary(doc, 0.3, 4)
                doc_summaries.append({
                    "document_index": i,
                    "summary": doc_summary["text"],
                    "original_length": len(doc)
                })
                
                # Extract key points from this document
                key_points = await self._identify_key_points(doc, 3)
                all_key_points.extend([point["text"] for point in key_points["points"]])
        
        # Create unified summary from all document summaries
        combined_summaries = " ".join([ds["summary"] for ds in doc_summaries])
        unified_summary = await self._create_extractive_summary(combined_summaries, 0.6, 6)
        
        # Find common themes across documents
        common_themes = self._identify_common_themes(all_key_points)
        
        return {
            "unified_summary": unified_summary["text"],
            "document_summaries": doc_summaries,
            "synthesis": {
                "common_themes": common_themes,
                "total_documents": len(documents),
                "total_original_length": sum(ds["original_length"] for ds in doc_summaries),
                "unified_length": len(unified_summary["text"])
            },
            "key_insights": all_key_points[:10]  # Top 10 key insights
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _split_into_sections(self, content: str) -> List[str]:
        """Split content into logical sections."""
        # Split by double newlines (paragraphs)
        sections = [s.strip() for s in content.split('\n\n') if s.strip()]
        
        # If no clear sections, split by length
        if len(sections) <= 1 and len(content) > 1000:
            chunk_size = len(content) // 3
            sections = [
                content[i:i+chunk_size] 
                for i in range(0, len(content), chunk_size)
                if content[i:i+chunk_size].strip()
            ]
        
        return sections
    
    async def _score_sentences(self, sentences: List[str], full_content: str) -> List[float]:
        """Score sentences for importance in summarization."""
        scores = []
        
        # Calculate word frequencies in full content
        words = re.findall(r'\b\w+\b', full_content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Remove very common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        for sentence in sentences:
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            sentence_words = [w for w in sentence_words if w not in stop_words]
            
            # Score based on word frequencies
            score = 0.0
            for word in sentence_words:
                score += word_freq.get(word, 0)
            
            # Normalize by sentence length
            if sentence_words:
                score = score / len(sentence_words)
            
            # Bonus for position (first and last sentences often important)
            position_bonus = 0.0
            sentence_index = sentences.index(sentence)
            if sentence_index == 0 or sentence_index == len(sentences) - 1:
                position_bonus = 0.2
            
            # Bonus for sentences with numbers/dates
            if re.search(r'\d+', sentence):
                position_bonus += 0.1
            
            scores.append(score + position_bonus)
        
        return scores
    
    def _categorize_key_point(self, sentence: str) -> str:
        """Categorize a key point by its content."""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ["data", "number", "percent", "%", "statistics"]):
            return "statistics"
        elif any(word in sentence_lower for word in ["recommend", "suggest", "should", "propose"]):
            return "recommendation"
        elif any(word in sentence_lower for word in ["problem", "issue", "challenge", "concern"]):
            return "problem"
        elif any(word in sentence_lower for word in ["solution", "approach", "method", "strategy"]):
            return "solution"
        elif any(word in sentence_lower for word in ["result", "outcome", "conclusion", "finding"]):
            return "result"
        else:
            return "general"
    
    def _identify_common_themes(self, key_points: List[str]) -> List[str]:
        """Identify common themes across multiple key points."""
        if not key_points:
            return []
        
        # Simple theme identification based on word frequency
        all_words = []
        for point in key_points:
            words = re.findall(r'\b\w+\b', point.lower())
            # Filter out common words
            filtered_words = [w for w in words if len(w) > 3 and w not in {"this", "that", "with", "from", "they", "have", "been", "were", "will"}]
            all_words.extend(filtered_words)
        
        # Count word frequencies
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most common words as themes
        common_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [theme[0] for theme in common_themes if theme[1] >= 2]  # Must appear at least twice
    
    def _extract_content_from_goal(self, goal: AgentGoal) -> str:
        """Extract content to summarize from goal context."""
        context = goal.context or {}
        
        # Try different context keys
        content = context.get("content", "")
        if not content:
            content = context.get("text", "")
        if not content:
            content = context.get("article", "")
        if not content:
            content = context.get("document", "")
        
        # If no content in context, use goal description
        if not content:
            content = goal.description
        
        return content
    
    def get_summarization_history(self) -> List[Dict[str, Any]]:
        """Get summarization history for this agent."""
        return self.summarization_history.copy()
