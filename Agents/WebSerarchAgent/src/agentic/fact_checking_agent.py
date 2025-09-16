"""
Fact Checking Agent for verifying information accuracy and credibility.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentGoal, AgentCapability

logger = logging.getLogger(__name__)

class FactCheckingAgent(BaseAgent):
    """
    Specialized agent for fact-checking and credibility assessment.
    """
    
    def __init__(self, name: str = "FactCheckingAgent"):
        """Initialize the Fact Checking Agent."""
        capabilities = [
            AgentCapability(
                name="fact_verification",
                description="Verify facts and claims against reliable sources",
                input_types=["claims", "statements", "facts"],
                output_types=["verification_results", "credibility_scores", "fact_status"]
            ),
            AgentCapability(
                name="source_credibility",
                description="Assess the credibility and reliability of information sources",
                input_types=["urls", "sources", "websites"],
                output_types=["credibility_scores", "source_analysis", "reliability_ratings"]
            ),
            AgentCapability(
                name="cross_reference",
                description="Cross-reference information across multiple sources",
                input_types=["information", "claims", "data"],
                output_types=["cross_reference_results", "consistency_analysis", "source_agreement"]
            ),
            AgentCapability(
                name="bias_detection",
                description="Detect potential bias in content and sources",
                input_types=["content", "articles", "sources"],
                output_types=["bias_analysis", "bias_score", "neutrality_assessment"]
            )
        ]
        
        super().__init__(name, capabilities)
        self.fact_check_history: List[Dict[str, Any]] = []
        
        # Credible source patterns
        self.credible_domains = {
            "high": [".gov", ".edu", "reuters.com", "ap.org", "bbc.com", "nature.com", 
                    "sciencemag.org", "nejm.org", "who.int", "cdc.gov"],
            "medium": ["wikipedia.org", "britannica.com", "nytimes.com", "washingtonpost.com",
                      "theguardian.com", "economist.com", "npr.org"],
            "low": ["blog", "personal", "opinion", "social"]
        }
        
        logger.info(f"Initialized {name} with fact-checking capabilities")
    
    async def execute_goal(self, goal: AgentGoal) -> Dict[str, Any]:
        """
        Execute a fact-checking goal.
        
        Args:
            goal: The fact-checking goal to achieve
            
        Returns:
            Dictionary containing fact-checking results and analysis
        """
        goal_desc = goal.description.lower()
        context = goal.context or {}
        
        logger.info(f"FactCheckingAgent executing goal: {goal.description}")
        
        # Determine fact-checking type based on goal
        if "verify" in goal_desc or "check" in goal_desc:
            return await self._verify_facts(goal)
        elif "credibility" in goal_desc or "reliable" in goal_desc:
            return await self._assess_source_credibility(goal)
        elif "bias" in goal_desc:
            return await self._detect_bias(goal)
        elif "cross" in goal_desc or "reference" in goal_desc:
            return await self._cross_reference_information(goal)
        else:
            return await self._comprehensive_fact_check(goal)
    
    async def _comprehensive_fact_check(self, goal: AgentGoal) -> Dict[str, Any]:
        """Perform comprehensive fact-checking analysis."""
        context = goal.context or {}
        claims = self._extract_claims_from_goal(goal)
        sources = context.get("sources", [])
        
        logger.info(f"Performing comprehensive fact check on {len(claims)} claims")
        
        try:
            results = {
                "fact_check_type": "comprehensive",
                "timestamp": datetime.now(),
                "total_claims": len(claims),
                "analyses": {}
            }
            
            # Perform multiple fact-checking analyses
            analyses = await asyncio.gather(
                self._verify_claims(claims, sources),
                self._assess_sources_credibility(sources),
                self._detect_content_bias(claims, sources),
                self._cross_reference_claims(claims),
                return_exceptions=True
            )
            
            # Process results
            analysis_types = ["verification", "credibility", "bias", "cross_reference"]
            for i, analysis in enumerate(analyses):
                if not isinstance(analysis, Exception):
                    results["analyses"][analysis_types[i]] = analysis
                else:
                    logger.warning(f"Analysis {analysis_types[i]} failed: {str(analysis)}")
                    results["analyses"][analysis_types[i]] = {"error": str(analysis)}
            
            # Calculate overall credibility score
            results["overall_credibility"] = self._calculate_overall_credibility(results["analyses"])
            results["fact_check_summary"] = self._generate_fact_check_summary(results["analyses"])
            results["status"] = "completed"
            
            # Record fact check
            self.fact_check_history.append({
                "goal_id": goal.id,
                "fact_check_type": "comprehensive",
                "claims_count": len(claims),
                "credibility_score": results["overall_credibility"],
                "timestamp": datetime.now()
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive fact check failed: {str(e)}")
            return {
                "fact_check_type": "comprehensive",
                "status": "failed",
                "error": str(e)
            }
    
    async def _verify_facts(self, goal: AgentGoal) -> Dict[str, Any]:
        """Verify specific facts or claims."""
        claims = self._extract_claims_from_goal(goal)
        sources = goal.context.get("sources", [])
        
        try:
            verification_results = await self._verify_claims(claims, sources)
            
            return {
                "fact_check_type": "verification",
                "timestamp": datetime.now(),
                "claims_verified": len(claims),
                "verification": verification_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Fact verification failed: {str(e)}")
            return {
                "fact_check_type": "verification",
                "status": "failed",
                "error": str(e)
            }
    
    async def _assess_source_credibility(self, goal: AgentGoal) -> Dict[str, Any]:
        """Assess credibility of sources."""
        sources = goal.context.get("sources", [])
        urls = goal.context.get("urls", [])
        
        all_sources = sources + urls
        
        try:
            credibility_results = await self._assess_sources_credibility(all_sources)
            
            return {
                "fact_check_type": "source_credibility",
                "timestamp": datetime.now(),
                "sources_assessed": len(all_sources),
                "credibility": credibility_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Source credibility assessment failed: {str(e)}")
            return {
                "fact_check_type": "source_credibility",
                "status": "failed",
                "error": str(e)
            }
    
    async def _detect_bias(self, goal: AgentGoal) -> Dict[str, Any]:
        """Detect bias in content or sources."""
        content = goal.context.get("content", goal.description)
        sources = goal.context.get("sources", [])
        
        try:
            bias_results = await self._detect_content_bias([content], sources)
            
            return {
                "fact_check_type": "bias_detection",
                "timestamp": datetime.now(),
                "content_length": len(content),
                "bias": bias_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Bias detection failed: {str(e)}")
            return {
                "fact_check_type": "bias_detection",
                "status": "failed",
                "error": str(e)
            }
    
    async def _cross_reference_information(self, goal: AgentGoal) -> Dict[str, Any]:
        """Cross-reference information across sources."""
        claims = self._extract_claims_from_goal(goal)
        
        try:
            cross_ref_results = await self._cross_reference_claims(claims)
            
            return {
                "fact_check_type": "cross_reference",
                "timestamp": datetime.now(),
                "claims_cross_referenced": len(claims),
                "cross_reference": cross_ref_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Cross-reference failed: {str(e)}")
            return {
                "fact_check_type": "cross_reference",
                "status": "failed",
                "error": str(e)
            }
    
    async def _verify_claims(self, claims: List[str], sources: List[str]) -> Dict[str, Any]:
        """Verify individual claims against sources."""
        verification_results = []
        
        for claim in claims:
            claim_result = {
                "claim": claim,
                "verification_status": "unknown",
                "confidence": 0.0,
                "supporting_sources": [],
                "contradicting_sources": [],
                "evidence_strength": "weak"
            }
            
            # Simple claim verification (can be enhanced with ML models)
            # Look for keywords and patterns
            claim_keywords = claim.lower().split()
            
            supporting_count = 0
            contradicting_count = 0
            
            for source in sources:
                if isinstance(source, str):
                    source_content = source.lower()
                    
                    # Check if claim keywords appear in source
                    keyword_matches = sum(1 for keyword in claim_keywords if keyword in source_content)
                    
                    if keyword_matches >= len(claim_keywords) * 0.5:  # 50% keyword match
                        supporting_count += 1
                        claim_result["supporting_sources"].append(source[:100] + "...")
                    
                    # Look for contradictory words
                    contradictory_phrases = ["not", "false", "incorrect", "wrong", "disputed"]
                    if any(phrase in source_content for phrase in contradictory_phrases):
                        contradicting_count += 1
                        claim_result["contradicting_sources"].append(source[:100] + "...")
            
            # Determine verification status
            if supporting_count > contradicting_count:
                claim_result["verification_status"] = "likely_true"
                claim_result["confidence"] = min(supporting_count / max(len(sources), 1), 1.0)
                claim_result["evidence_strength"] = "strong" if supporting_count >= 3 else "moderate"
            elif contradicting_count > supporting_count:
                claim_result["verification_status"] = "likely_false"
                claim_result["confidence"] = min(contradicting_count / max(len(sources), 1), 1.0)
                claim_result["evidence_strength"] = "strong" if contradicting_count >= 3 else "moderate"
            else:
                claim_result["verification_status"] = "unverified"
                claim_result["confidence"] = 0.0
                claim_result["evidence_strength"] = "weak"
            
            verification_results.append(claim_result)
        
        return {
            "claim_verifications": verification_results,
            "total_verified": sum(1 for r in verification_results if r["verification_status"] != "unverified"),
            "likely_true": sum(1 for r in verification_results if r["verification_status"] == "likely_true"),
            "likely_false": sum(1 for r in verification_results if r["verification_status"] == "likely_false"),
            "unverified": sum(1 for r in verification_results if r["verification_status"] == "unverified")
        }
    
    async def _assess_sources_credibility(self, sources: List[str]) -> Dict[str, Any]:
        """Assess credibility of information sources."""
        credibility_assessments = []
        
        for source in sources:
            assessment = {
                "source": source,
                "credibility_score": 0.0,
                "credibility_level": "unknown",
                "factors": [],
                "warnings": []
            }
            
            if isinstance(source, str):
                source_lower = source.lower()
                
                # Check against credible domain patterns
                score = 0.0
                factors = []
                
                # High credibility domains
                for domain in self.credible_domains["high"]:
                    if domain in source_lower:
                        score += 0.8
                        factors.append(f"High credibility domain: {domain}")
                        break
                
                # Medium credibility domains
                for domain in self.credible_domains["medium"]:
                    if domain in source_lower:
                        score += 0.6
                        factors.append(f"Medium credibility domain: {domain}")
                        break
                
                # Low credibility indicators
                for indicator in self.credible_domains["low"]:
                    if indicator in source_lower:
                        score -= 0.3
                        assessment["warnings"].append(f"Low credibility indicator: {indicator}")
                
                # Additional credibility factors
                if "https://" in source:
                    score += 0.1
                    factors.append("Secure connection (HTTPS)")
                
                if any(word in source_lower for word in ["official", "government", "academic"]):
                    score += 0.2
                    factors.append("Official/academic source indicator")
                
                if any(word in source_lower for word in ["opinion", "blog", "personal"]):
                    score -= 0.2
                    assessment["warnings"].append("Opinion/personal content indicator")
                
                # Normalize score
                assessment["credibility_score"] = max(0.0, min(1.0, score))
                assessment["factors"] = factors
                
                # Determine credibility level
                if assessment["credibility_score"] >= 0.8:
                    assessment["credibility_level"] = "high"
                elif assessment["credibility_score"] >= 0.6:
                    assessment["credibility_level"] = "medium"
                elif assessment["credibility_score"] >= 0.4:
                    assessment["credibility_level"] = "moderate"
                else:
                    assessment["credibility_level"] = "low"
            
            credibility_assessments.append(assessment)
        
        # Calculate overall statistics
        scores = [a["credibility_score"] for a in credibility_assessments]
        avg_credibility = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "source_assessments": credibility_assessments,
            "average_credibility": avg_credibility,
            "high_credibility_sources": sum(1 for a in credibility_assessments if a["credibility_level"] == "high"),
            "medium_credibility_sources": sum(1 for a in credibility_assessments if a["credibility_level"] == "medium"),
            "low_credibility_sources": sum(1 for a in credibility_assessments if a["credibility_level"] == "low")
        }
    
    async def _detect_content_bias(self, content_list: List[str], sources: List[str]) -> Dict[str, Any]:
        """Detect bias in content and sources."""
        bias_results = []
        
        # Bias indicator words
        positive_bias_words = ["amazing", "incredible", "revolutionary", "perfect", "best"]
        negative_bias_words = ["terrible", "awful", "worst", "disaster", "catastrophe"]
        political_bias_words = ["liberal", "conservative", "leftist", "rightist", "propaganda"]
        
        for content in content_list:
            if isinstance(content, str):
                content_lower = content.lower()
                words = content_lower.split()
                
                positive_count = sum(1 for word in words if word in positive_bias_words)
                negative_count = sum(1 for word in words if word in negative_bias_words)
                political_count = sum(1 for word in words if word in political_bias_words)
                
                total_words = len(words)
                
                bias_result = {
                    "content": content[:200] + "..." if len(content) > 200 else content,
                    "bias_indicators": {
                        "positive_bias": positive_count / max(total_words, 1),
                        "negative_bias": negative_count / max(total_words, 1),
                        "political_bias": political_count / max(total_words, 1)
                    },
                    "overall_bias_score": 0.0,
                    "bias_type": "neutral",
                    "confidence": 0.0
                }
                
                # Calculate overall bias score
                max_bias = max(
                    bias_result["bias_indicators"]["positive_bias"],
                    bias_result["bias_indicators"]["negative_bias"],
                    bias_result["bias_indicators"]["political_bias"]
                )
                
                bias_result["overall_bias_score"] = max_bias
                bias_result["confidence"] = min(max_bias * 10, 1.0)  # Scale confidence
                
                # Determine bias type
                if bias_result["bias_indicators"]["positive_bias"] > 0.02:
                    bias_result["bias_type"] = "positive"
                elif bias_result["bias_indicators"]["negative_bias"] > 0.02:
                    bias_result["bias_type"] = "negative"
                elif bias_result["bias_indicators"]["political_bias"] > 0.01:
                    bias_result["bias_type"] = "political"
                else:
                    bias_result["bias_type"] = "neutral"
                
                bias_results.append(bias_result)
        
        return {
            "content_bias_analysis": bias_results,
            "average_bias_score": sum(r["overall_bias_score"] for r in bias_results) / max(len(bias_results), 1),
            "bias_types_detected": list(set(r["bias_type"] for r in bias_results if r["bias_type"] != "neutral")),
            "neutral_content_count": sum(1 for r in bias_results if r["bias_type"] == "neutral")
        }
    
    async def _cross_reference_claims(self, claims: List[str]) -> Dict[str, Any]:
        """Cross-reference claims for consistency."""
        if len(claims) < 2:
            return {
                "cross_reference_results": [],
                "consistency_score": 1.0,
                "conflicts_detected": 0
            }
        
        cross_ref_results = []
        conflicts = 0
        
        for i, claim1 in enumerate(claims):
            for j, claim2 in enumerate(claims[i+1:], i+1):
                # Simple consistency check based on keyword overlap
                words1 = set(claim1.lower().split())
                words2 = set(claim2.lower().split())
                
                overlap = len(words1.intersection(words2))
                total_unique = len(words1.union(words2))
                
                similarity = overlap / max(total_unique, 1)
                
                # Check for contradictory indicators
                contradictory_pairs = [
                    ("true", "false"), ("yes", "no"), ("increase", "decrease"),
                    ("up", "down"), ("good", "bad"), ("positive", "negative")
                ]
                
                is_contradictory = False
                for word1, word2 in contradictory_pairs:
                    if (word1 in words1 and word2 in words2) or (word2 in words1 and word1 in words2):
                        is_contradictory = True
                        conflicts += 1
                        break
                
                cross_ref_results.append({
                    "claim1_index": i,
                    "claim2_index": j,
                    "similarity": similarity,
                    "is_contradictory": is_contradictory,
                    "relationship": "contradictory" if is_contradictory else ("related" if similarity > 0.3 else "unrelated")
                })
        
        consistency_score = 1.0 - (conflicts / max(len(cross_ref_results), 1))
        
        return {
            "cross_reference_results": cross_ref_results,
            "consistency_score": consistency_score,
            "conflicts_detected": conflicts,
            "total_comparisons": len(cross_ref_results)
        }
    
    def _calculate_overall_credibility(self, analyses: Dict[str, Any]) -> float:
        """Calculate overall credibility score from all analyses."""
        scores = []
        
        # Credibility analysis score
        if "credibility" in analyses and "error" not in analyses["credibility"]:
            credibility = analyses["credibility"]
            scores.append(credibility.get("average_credibility", 0.0))
        
        # Verification score
        if "verification" in analyses and "error" not in analyses["verification"]:
            verification = analyses["verification"]
            total_claims = len(verification.get("claim_verifications", []))
            if total_claims > 0:
                true_claims = verification.get("likely_true", 0)
                scores.append(true_claims / total_claims)
        
        # Bias penalty
        if "bias" in analyses and "error" not in analyses["bias"]:
            bias = analyses["bias"]
            avg_bias = bias.get("average_bias_score", 0.0)
            bias_penalty = 1.0 - avg_bias  # Lower bias = higher credibility
            scores.append(bias_penalty)
        
        # Consistency score
        if "cross_reference" in analyses and "error" not in analyses["cross_reference"]:
            cross_ref = analyses["cross_reference"]
            consistency = cross_ref.get("consistency_score", 1.0)
            scores.append(consistency)
        
        return sum(scores) / max(len(scores), 1)
    
    def _generate_fact_check_summary(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate summary insights from fact-checking analyses."""
        summary = []
        
        # Verification summary
        if "verification" in analyses and "error" not in analyses["verification"]:
            verification = analyses["verification"]
            true_count = verification.get("likely_true", 0)
            false_count = verification.get("likely_false", 0)
            unverified_count = verification.get("unverified", 0)
            
            summary.append(f"Verification: {true_count} likely true, {false_count} likely false, {unverified_count} unverified")
        
        # Credibility summary
        if "credibility" in analyses and "error" not in analyses["credibility"]:
            credibility = analyses["credibility"]
            avg_cred = credibility.get("average_credibility", 0.0)
            summary.append(f"Average source credibility: {avg_cred:.1%}")
        
        # Bias summary
        if "bias" in analyses and "error" not in analyses["bias"]:
            bias = analyses["bias"]
            bias_types = bias.get("bias_types_detected", [])
            if bias_types:
                summary.append(f"Bias detected: {', '.join(bias_types)}")
            else:
                summary.append("No significant bias detected")
        
        # Consistency summary
        if "cross_reference" in analyses and "error" not in analyses["cross_reference"]:
            cross_ref = analyses["cross_reference"]
            conflicts = cross_ref.get("conflicts_detected", 0)
            if conflicts > 0:
                summary.append(f"Information conflicts detected: {conflicts}")
            else:
                summary.append("Information appears consistent")
        
        return summary
    
    def _extract_claims_from_goal(self, goal: AgentGoal) -> List[str]:
        """Extract claims to fact-check from goal context."""
        context = goal.context or {}
        
        # Try different context keys
        claims = context.get("claims", [])
        if not claims:
            claims = context.get("statements", [])
        if not claims:
            claims = context.get("facts", [])
        if not claims:
            content = context.get("content", goal.description)
            # Simple sentence splitting as fallback
            claims = [s.strip() for s in content.split('.') if s.strip()]
        
        return claims[:10]  # Limit to 10 claims for performance
    
    def get_fact_check_history(self) -> List[Dict[str, Any]]:
        """Get fact-checking history for this agent."""
        return self.fact_check_history.copy()
