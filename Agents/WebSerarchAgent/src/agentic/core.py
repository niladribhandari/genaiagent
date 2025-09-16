"""
Core orchestration system for managing multiple agents.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentGoal, AgentCapability

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Central orchestrator for coordinating multiple agents.
    Implements high-level goal decomposition and agent coordination.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_history: List[Dict[str, Any]] = []
        
        logger.info("Initialized AgentOrchestrator")
    
    def add_agent(self, agent: BaseAgent):
        """Add an agent to the orchestrator."""
        self.agents[agent.name] = agent
        logger.info(f"Added agent to orchestrator: {agent.name}")
        
        # Auto-connect agents based on compatible capabilities
        self._auto_connect_agents(agent)
    
    def _auto_connect_agents(self, new_agent: BaseAgent):
        """Automatically connect agents with compatible capabilities."""
        for existing_agent in self.agents.values():
            if existing_agent.name != new_agent.name:
                # Check for capability compatibility
                if self._agents_compatible(new_agent, existing_agent):
                    new_agent.connect_agent(existing_agent)
                    logger.info(f"Auto-connected compatible agents: {new_agent.name} <-> {existing_agent.name}")
    
    def _agents_compatible(self, agent1: BaseAgent, agent2: BaseAgent) -> bool:
        """Check if two agents have compatible capabilities for collaboration."""
        # Simple compatibility check - can be enhanced with more sophisticated logic
        agent1_outputs = set()
        agent2_inputs = set()
        
        for cap in agent1.capabilities.values():
            agent1_outputs.update(cap.output_types)
        
        for cap in agent2.capabilities.values():
            agent2_inputs.update(cap.input_types)
        
        return bool(agent1_outputs.intersection(agent2_inputs))
    
    async def execute_goal(self, goal_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a high-level goal by decomposing it and coordinating agents.
        
        Args:
            goal_description: High-level description of what to achieve
            context: Additional context for goal execution
            
        Returns:
            Comprehensive results from all involved agents
        """
        if context is None:
            context = {}
        
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        
        logger.info(f"Starting workflow {workflow_id}: {goal_description}")
        
        # Decompose goal into sub-goals for different agents
        sub_goals = await self._decompose_goal(goal_description, context)
        
        # Track workflow
        self.active_workflows[workflow_id] = {
            "description": goal_description,
            "context": context,
            "sub_goals": sub_goals,
            "start_time": datetime.now(),
            "status": "running",
            "results": {}
        }
        
        try:
            # Execute sub-goals in parallel or sequence based on dependencies
            results = await self._execute_sub_goals(workflow_id, sub_goals)
            
            # Synthesize final result
            final_result = await self._synthesize_results(goal_description, results, context)
            
            # Update workflow status
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["results"] = final_result
            self.active_workflows[workflow_id]["end_time"] = datetime.now()
            
            # Move to history
            self.workflow_history.append(self.active_workflows[workflow_id])
            del self.active_workflows[workflow_id]
            
            logger.info(f"Completed workflow {workflow_id}")
            
            return final_result
            
        except Exception as e:
            # Handle workflow failure
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            self.active_workflows[workflow_id]["end_time"] = datetime.now()
            
            logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            raise
    
    async def _decompose_goal(self, goal_description: str, context: Dict[str, Any]) -> List[AgentGoal]:
        """
        Decompose a high-level goal into sub-goals for specific agents.
        
        This is a simplified implementation - in a real system, this could use
        AI-powered goal decomposition.
        """
        sub_goals = []
        
        # Analyze goal to determine required capabilities
        goal_lower = goal_description.lower()
        
        # Web search goals
        if any(keyword in goal_lower for keyword in ["search", "find", "lookup", "information"]):
            sub_goals.append(AgentGoal(
                id=f"search_{datetime.now().timestamp()}",
                description=f"Search for information: {goal_description}",
                target_outcome="Relevant search results and web content",
                priority=8,
                context=context
            ))
        
        # Content analysis goals
        if any(keyword in goal_lower for keyword in ["analyze", "understand", "extract", "content"]):
            sub_goals.append(AgentGoal(
                id=f"analysis_{datetime.now().timestamp()}",
                description=f"Analyze content for: {goal_description}",
                target_outcome="Structured analysis and insights",
                priority=7,
                context=context
            ))
        
        # Fact checking goals
        if any(keyword in goal_lower for keyword in ["verify", "check", "validate", "facts", "accuracy"]):
            sub_goals.append(AgentGoal(
                id=f"factcheck_{datetime.now().timestamp()}",
                description=f"Fact check information: {goal_description}",
                target_outcome="Verified facts and credibility assessment",
                priority=9,
                context=context
            ))
        
        # Summarization goals
        if any(keyword in goal_lower for keyword in ["summarize", "summary", "overview", "brief"]):
            sub_goals.append(AgentGoal(
                id=f"summary_{datetime.now().timestamp()}",
                description=f"Summarize information: {goal_description}",
                target_outcome="Concise and comprehensive summary",
                priority=6,
                context=context
            ))
        
        # Trend monitoring goals
        if any(keyword in goal_lower for keyword in ["trend", "trending", "popular", "latest", "recent"]):
            sub_goals.append(AgentGoal(
                id=f"trends_{datetime.now().timestamp()}",
                description=f"Monitor trends for: {goal_description}",
                target_outcome="Trend analysis and insights",
                priority=5,
                context=context
            ))
        
        # If no specific patterns matched, create a general search goal
        if not sub_goals:
            sub_goals.append(AgentGoal(
                id=f"general_{datetime.now().timestamp()}",
                description=goal_description,
                target_outcome="Comprehensive information and analysis",
                priority=7,
                context=context
            ))
        
        logger.info(f"Decomposed goal into {len(sub_goals)} sub-goals")
        return sub_goals
    
    async def _execute_sub_goals(self, workflow_id: str, sub_goals: List[AgentGoal]) -> Dict[str, Any]:
        """Execute sub-goals using appropriate agents."""
        results = {}
        
        # Sort sub-goals by priority
        sorted_goals = sorted(sub_goals, key=lambda g: g.priority, reverse=True)
        
        for goal in sorted_goals:
            # Find the best agent for this goal
            best_agent = self._find_best_agent(goal)
            
            if best_agent:
                logger.info(f"Assigning goal {goal.id} to agent {best_agent.name}")
                
                try:
                    result = await best_agent.set_goal(goal)
                    results[goal.id] = {
                        "agent": best_agent.name,
                        "goal": goal,
                        "result": result,
                        "status": "completed"
                    }
                    
                    # Update workflow status
                    self.active_workflows[workflow_id]["results"][goal.id] = result
                    
                except Exception as e:
                    logger.error(f"Goal {goal.id} failed with agent {best_agent.name}: {str(e)}")
                    results[goal.id] = {
                        "agent": best_agent.name,
                        "goal": goal,
                        "error": str(e),
                        "status": "failed"
                    }
            else:
                logger.warning(f"No suitable agent found for goal: {goal.description}")
                results[goal.id] = {
                    "agent": None,
                    "goal": goal,
                    "error": "No suitable agent found",
                    "status": "failed"
                }
        
        return results
    
    def _find_best_agent(self, goal: AgentGoal) -> Optional[BaseAgent]:
        """Find the best agent to handle a specific goal."""
        # Simplified agent selection based on goal description keywords
        goal_desc = goal.description.lower()
        
        # Priority-based agent selection
        agent_priorities = {
            "WebSearchAgent": ["search", "find", "lookup", "web", "internet"],
            "ContentAnalysisAgent": ["analyze", "analysis", "content", "extract", "understand"],
            "FactCheckingAgent": ["verify", "check", "fact", "validate", "accuracy", "credible"],
            "SummarizationAgent": ["summarize", "summary", "brief", "overview"],
            "TrendMonitoringAgent": ["trend", "trending", "popular", "latest", "recent"]
        }
        
        best_agent = None
        best_score = 0
        
        for agent_name, keywords in agent_priorities.items():
            if agent_name in self.agents:
                score = sum(1 for keyword in keywords if keyword in goal_desc)
                if score > best_score:
                    best_score = score
                    best_agent = self.agents[agent_name]
        
        # If no specific match, return the first available agent
        if not best_agent and self.agents:
            best_agent = list(self.agents.values())[0]
        
        return best_agent
    
    async def _synthesize_results(self, goal_description: str, results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple agents into a coherent final result."""
        
        successful_results = {k: v for k, v in results.items() if v["status"] == "completed"}
        failed_results = {k: v for k, v in results.items() if v["status"] == "failed"}
        
        synthesis = {
            "original_goal": goal_description,
            "context": context,
            "total_sub_goals": len(results),
            "successful_sub_goals": len(successful_results),
            "failed_sub_goals": len(failed_results),
            "agents_involved": list(set(r["agent"] for r in results.values() if r["agent"])),
            "results_by_agent": {},
            "synthesized_insights": [],
            "confidence_score": len(successful_results) / len(results) if results else 0
        }
        
        # Organize results by agent
        for result_data in successful_results.values():
            agent_name = result_data["agent"]
            if agent_name not in synthesis["results_by_agent"]:
                synthesis["results_by_agent"][agent_name] = []
            synthesis["results_by_agent"][agent_name].append(result_data["result"])
        
        # Generate insights from successful results
        if successful_results:
            synthesis["synthesized_insights"] = await self._generate_insights(successful_results, goal_description)
        
        # Add error summary if there were failures
        if failed_results:
            synthesis["errors"] = [r["error"] for r in failed_results.values()]
        
        return synthesis
    
    async def _generate_insights(self, successful_results: Dict[str, Any], goal_description: str) -> List[str]:
        """Generate insights from successful agent results."""
        insights = []
        
        # Simple insight generation - can be enhanced with AI
        insights.append(f"Successfully processed {len(successful_results)} sub-goals for: {goal_description}")
        
        # Agent-specific insights
        agent_contributions = {}
        for result_data in successful_results.values():
            agent_name = result_data["agent"]
            agent_contributions[agent_name] = agent_contributions.get(agent_name, 0) + 1
        
        for agent, count in agent_contributions.items():
            insights.append(f"{agent} contributed {count} successful result(s)")
        
        return insights
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the orchestrator and all agents."""
        return {
            "orchestrator_status": "active",
            "total_agents": len(self.agents),
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.workflow_history),
            "agents": {name: agent.get_status_report() for name, agent in self.agents.items()},
            "recent_workflows": self.workflow_history[-5:] if self.workflow_history else []
        }
