"""
Specialized review agents for AgenticAI code review system.
Each agent focuses on specific aspects of code quality and security.
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
from pathlib import Path

from .core import BaseAgent, AgentGoal, AgentTask, AgentState, Priority
from .capabilities import (
    FileDiscoveryCapability, JavaAnalysisCapability, 
    PythonAnalysisCapability, GenericAnalysisCapability,
    ReportGenerationCapability
)


class FileDiscoveryAgent(BaseAgent):
    """Agent responsible for intelligent file discovery and classification."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "FileDiscoveryAgent", config)
        self.capabilities = [FileDiscoveryCapability(config)]
        self.agent_type = "file_discovery"
        self.logger = logging.getLogger(__name__)
    
    async def analyze_situation(self, context: Dict[str, Any]) -> List[AgentGoal]:
        """Analyze the current situation to understand file discovery needs."""
        project_path = context.get("project_path", ".")
        goal = AgentGoal(
            id="file_discovery_goal",
            description="Discover and classify files for code review",
            priority=Priority.HIGH,
            success_criteria={"files_discovered": True},
            context={"project_path": project_path}
        )
        return [goal]
    
    async def plan_actions(self, goals: List[AgentGoal]) -> List[AgentTask]:
        """Plan actions based on the analyzed goals."""
        context = goals[0].context if goals else {}
        return self.make_autonomous_decision(context)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the project structure and discover files for review."""
        self.state = AgentState.ANALYZING
        
        try:
            project_path = context.get("project_path", ".")
            
            # Create discovery task
            discovery_task = AgentTask(
                id="file_discovery_main",
                goal_id="file_discovery_goal",
                description="Discover files in project",
                task_type="file_discovery",
                input_data={
                    "project_path": project_path,
                    "extensions": [".java", ".py", ".js", ".ts", ".yml", ".yaml", ".xml", ".json"]
                },
                expected_output={"discovered_files": [], "total_count": 0},
                priority=Priority.HIGH
            )
            
            # Execute file discovery
            discovery_result = await self.capabilities[0].execute(discovery_task, context)
            
            # Classify discovered files
            if discovery_result.get("discovered_files"):
                classification_task = AgentTask(
                    id="file_classification",
                    task_type="file_classification",
                    priority=Priority.MEDIUM,
                    input_data={"files": discovery_result["discovered_files"]}
                )
                
                classification_result = await self.capabilities[0].execute(classification_task, context)
                discovery_result.update(classification_result)
            
            self.state = AgentState.COMPLETED
            self.analysis_results = discovery_result
            
            self.logger.info(f"File discovery completed: {discovery_result.get('total_count', 0)} files found")
            
            return discovery_result
            
        except Exception as e:
            self.state = AgentState.FAILED
            self.logger.error(f"File discovery failed: {e}")
            return {"error": str(e), "files": []}
    
    def make_autonomous_decision(self, context: Dict[str, Any]) -> List[AgentTask]:
        """Make autonomous decisions about file discovery strategy."""
        tasks = []
        
        # Adapt discovery based on project size
        project_path = Path(context.get("project_path", "."))
        try:
            # Count total files quickly
            total_files = len(list(project_path.rglob("*")))
            
            if total_files > 1000:
                # Large project - be more selective
                tasks.append(AgentTask(
                    id="selective_discovery",
                    goal_id="file_discovery_goal",
                    description="Selective file discovery for large project",
                    task_type="file_filtering",
                    input_data={
                        "criteria": {
                            "max_size_mb": 1,
                            "exclude_patterns": ["target/", "build/", "node_modules/", ".git/"]
                        }
                    },
                    expected_output={"filtered_files": []},
                    priority=Priority.HIGH
                ))
            else:
                # Small project - comprehensive discovery
                tasks.append(AgentTask(
                    id="comprehensive_discovery",
                    task_type="file_discovery",
                    priority=Priority.MEDIUM,
                    input_data={"project_path": str(project_path)}
                ))
                
        except Exception:
            # Fallback to standard discovery
            tasks.append(AgentTask(
                id="standard_discovery",
                task_type="file_discovery",
                priority=Priority.MEDIUM,
                input_data={"project_path": str(project_path)}
            ))
        
        return tasks


class CodeQualityAgent(BaseAgent):
    """Agent focused on code quality analysis including complexity, structure, and patterns."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "CodeQualityAgent", config)
        self.capabilities = [
            JavaAnalysisCapability(config),
            PythonAnalysisCapability(config),
            GenericAnalysisCapability(config)
        ]
        self.agent_type = "code_quality"
        self.logger = logging.getLogger(__name__)
    
    async def analyze_situation(self, context: Dict[str, Any]) -> List[AgentGoal]:
        """Analyze the current situation to understand code quality needs."""
        files = context.get("files", [])
        goal = AgentGoal(
            id="code_quality_goal",
            description="Analyze code quality, complexity, and structure",
            priority=Priority.HIGH,
            success_criteria={"quality_analyzed": True},
            context={"files": files}
        )
        return [goal]
    
    async def plan_actions(self, goals: List[AgentGoal]) -> List[AgentTask]:
        """Plan actions based on the analyzed goals."""
        context = goals[0].context if goals else {}
        return self.make_autonomous_decision(context)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive code quality analysis."""
        self.state = AgentState.ANALYZING
        
        try:
            files = context.get("files", [])
            if not files:
                return {"message": "No files provided for analysis", "results": {}}
            
            # Separate files by type
            java_files = [f for f in files if str(f).endswith('.java')]
            python_files = [f for f in files if str(f).endswith('.py')]
            other_files = [f for f in files if not (str(f).endswith('.java') or str(f).endswith('.py'))]
            
            analysis_results = {}
            
            # Java analysis
            if java_files:
                java_tasks = await self._create_java_analysis_tasks(java_files)
                java_results = await self._execute_java_analysis(java_tasks, context)
                analysis_results["java_analysis"] = java_results
            
            # Python analysis
            if python_files:
                python_task = AgentTask(
                    id="python_analysis",
                    task_type="python_complexity_analysis",
                    priority=Priority.HIGH,
                    input_data={"files": python_files}
                )
                python_results = await self.capabilities[1].execute(python_task, context)
                analysis_results["python_analysis"] = python_results
            
            # Generic analysis for other files
            if other_files:
                generic_task = AgentTask(
                    id="generic_analysis",
                    task_type="generic_standards_check",
                    priority=Priority.MEDIUM,
                    input_data={"files": other_files}
                )
                generic_results = await self.capabilities[2].execute(generic_task, context)
                analysis_results["generic_analysis"] = generic_results
            
            # Calculate overall quality metrics
            quality_metrics = self._calculate_quality_metrics(analysis_results)
            analysis_results["quality_metrics"] = quality_metrics
            
            self.state = AgentState.COMPLETED
            self.analysis_results = analysis_results
            
            self.logger.info(f"Code quality analysis completed for {len(files)} files")
            
            return analysis_results
            
        except Exception as e:
            self.state = AgentState.FAILED
            self.logger.error(f"Code quality analysis failed: {e}")
            return {"error": str(e), "results": {}}
    
    async def _create_java_analysis_tasks(self, java_files: List[str]) -> List[AgentTask]:
        """Create Java analysis tasks based on autonomous decision making."""
        tasks = []
        
        # Always check complexity
        tasks.append(AgentTask(
            id="java_complexity",
            task_type="complexity_analysis",
            priority=Priority.HIGH,
            input_data={"files": java_files}
        ))
        
        # Check structure for Spring Boot projects
        if any("Application.java" in str(f) for f in java_files):
            tasks.append(AgentTask(
                id="java_structure",
                task_type="structure_analysis",
                priority=Priority.HIGH,
                input_data={"files": java_files, "project_type": "spring_boot"}
            ))
        
        # Pattern analysis for larger codebases
        if len(java_files) > 10:
            tasks.append(AgentTask(
                id="java_patterns",
                task_type="pattern_analysis",
                priority=Priority.MEDIUM,
                input_data={"files": java_files, "patterns": ["mvc", "dependency_injection"]}
            ))
        
        # Standards check
        tasks.append(AgentTask(
            id="java_standards",
            task_type="java_standards_check",
            priority=Priority.MEDIUM,
            input_data={"files": java_files, "standards": ["naming", "formatting", "structure"]}
        ))
        
        return tasks
    
    async def _execute_java_analysis(self, tasks: List[AgentTask], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Java analysis tasks."""
        java_capability = self.capabilities[0]
        results = {}
        
        for task in tasks:
            try:
                task_result = await java_capability.execute(task, context)
                results[task.task_id] = task_result
            except Exception as e:
                self.logger.error(f"Java analysis task {task.task_id} failed: {e}")
                results[task.task_id] = {"error": str(e)}
        
        return results
    
    def _calculate_quality_metrics(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall quality metrics from analysis results."""
        metrics = {
            "overall_score": 0.0,
            "complexity_score": 0.0,
            "structure_score": 0.0,
            "standards_score": 0.0,
            "total_issues": 0,
            "critical_issues": 0
        }
        
        # Extract metrics from Java analysis
        java_analysis = analysis_results.get("java_analysis", {})
        if java_analysis:
            if "java_complexity" in java_analysis:
                complexity_result = java_analysis["java_complexity"]
                violations = complexity_result.get("violations", [])
                metrics["complexity_score"] = max(0.0, 1.0 - len(violations) * 0.1)
            
            if "java_structure" in java_analysis:
                structure_result = java_analysis["java_structure"]
                metrics["structure_score"] = structure_result.get("structure_score", 0.0)
            
            if "java_standards" in java_analysis:
                standards_result = java_analysis["java_standards"]
                metrics["standards_score"] = standards_result.get("compliance_score", 0.0)
        
        # Extract metrics from Python analysis
        python_analysis = analysis_results.get("python_analysis", {})
        if python_analysis:
            total_issues = python_analysis.get("total_issues", 0)
            metrics["total_issues"] += total_issues
        
        # Calculate overall score
        scores = [metrics["complexity_score"], metrics["structure_score"], metrics["standards_score"]]
        scores = [s for s in scores if s > 0]  # Only count calculated scores
        metrics["overall_score"] = sum(scores) / len(scores) if scores else 0.8
        
        return metrics
    
    def make_autonomous_decision(self, context: Dict[str, Any]) -> List[AgentTask]:
        """Make autonomous decisions about quality analysis strategy."""
        files = context.get("files", [])
        tasks = []
        
        # Adaptive analysis based on file count and types
        if len(files) > 50:
            # Large codebase - focus on critical issues
            tasks.append(AgentTask(
                id="critical_quality_check",
                task_type="complexity_analysis",
                priority=Priority.CRITICAL,
                input_data={"files": files, "focus": "critical_only"}
            ))
        else:
            # Smaller codebase - comprehensive analysis
            tasks.append(AgentTask(
                id="comprehensive_quality_check",
                task_type="structure_analysis",
                priority=Priority.HIGH,
                input_data={"files": files}
            ))
        
        return tasks


class SecurityAnalysisAgent(BaseAgent):
    """Agent specialized in security vulnerability detection and analysis."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "SecurityAnalysisAgent", config)
        self.capabilities = [JavaAnalysisCapability(config)]
        self.agent_type = "security"
        self.logger = logging.getLogger(__name__)
    
    async def analyze_situation(self, context: Dict[str, Any]) -> List[AgentGoal]:
        """Analyze the current situation to understand security needs."""
        files = context.get("files", [])
        goal = AgentGoal(
            id="security_analysis_goal",
            description="Analyze code for security vulnerabilities",
            priority=Priority.CRITICAL,
            success_criteria={"security_analyzed": True},
            context={"files": files}
        )
        return [goal]
    
    async def plan_actions(self, goals: List[AgentGoal]) -> List[AgentTask]:
        """Plan actions based on the analyzed goals."""
        context = goals[0].context if goals else {}
        return self.make_autonomous_decision(context)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive security analysis."""
        self.state = AgentState.ANALYZING
        
        try:
            files = context.get("files", [])
            if not files:
                return {"message": "No files provided for security analysis", "vulnerabilities": []}
            
            # Focus on code files that might contain vulnerabilities
            code_files = [f for f in files if str(f).endswith(('.java', '.py', '.js', '.ts'))]
            
            security_results = {
                "vulnerabilities": [],
                "risk_assessment": {},
                "security_score": 0.0
            }
            
            # Run security scans
            security_tasks = await self._create_security_tasks(code_files)
            
            for task in security_tasks:
                try:
                    if self.capabilities[0].can_handle(task):
                        task_result = await self.capabilities[0].execute(task, context)
                        security_results["vulnerabilities"].extend(task_result.get("vulnerabilities", []))
                        
                        if "risk_level" in task_result:
                            security_results["risk_assessment"][task.task_type] = task_result["risk_level"]
                
                except Exception as e:
                    self.logger.error(f"Security task {task.task_id} failed: {e}")
            
            # Calculate overall security score
            security_results["security_score"] = self._calculate_security_score(security_results)
            
            self.state = AgentState.COMPLETED
            self.analysis_results = security_results
            
            self.logger.info(f"Security analysis completed: {len(security_results['vulnerabilities'])} vulnerabilities found")
            
            return security_results
            
        except Exception as e:
            self.state = AgentState.FAILED
            self.logger.error(f"Security analysis failed: {e}")
            return {"error": str(e), "vulnerabilities": []}
    
    async def _create_security_tasks(self, files: List[str]) -> List[AgentTask]:
        """Create security analysis tasks."""
        tasks = []
        
        # Injection vulnerability scan
        tasks.append(AgentTask(
            id="injection_scan",
            task_type="injection_scan",
            priority=Priority.CRITICAL,
            input_data={"files": files}
        ))
        
        # Authentication/Authorization scan
        tasks.append(AgentTask(
            id="auth_scan",
            task_type="auth_scan",
            priority=Priority.HIGH,
            input_data={"files": files}
        ))
        
        # Cryptography scan
        tasks.append(AgentTask(
            id="crypto_scan",
            task_type="crypto_scan",
            priority=Priority.HIGH,
            input_data={"files": files}
        ))
        
        return tasks
    
    def _calculate_security_score(self, security_results: Dict[str, Any]) -> float:
        """Calculate overall security score."""
        vulnerabilities = security_results.get("vulnerabilities", [])
        
        if not vulnerabilities:
            return 1.0
        
        # Weight vulnerabilities by severity
        score = 1.0
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "MEDIUM")
            if severity == "CRITICAL":
                score -= 0.3
            elif severity == "HIGH":
                score -= 0.2
            elif severity == "MEDIUM":
                score -= 0.1
            else:  # LOW
                score -= 0.05
        
        return max(0.0, score)
    
    def make_autonomous_decision(self, context: Dict[str, Any]) -> List[AgentTask]:
        """Make autonomous decisions about security analysis strategy."""
        files = context.get("files", [])
        tasks = []
        
        # Web applications need comprehensive security analysis
        if any("Controller" in str(f) or "controller" in str(f) for f in files):
            tasks.append(AgentTask(
                id="web_security_scan",
                task_type="injection_scan",
                priority=Priority.CRITICAL,
                input_data={"files": files, "focus": "web_vulnerabilities"}
            ))
        
        # Database interaction files need injection scanning
        db_files = [f for f in files if any(keyword in str(f).lower() 
                                           for keyword in ["repository", "dao", "service"])]
        if db_files:
            tasks.append(AgentTask(
                id="database_security_scan",
                task_type="injection_scan",
                priority=Priority.HIGH,
                input_data={"files": db_files}
            ))
        
        return tasks


class ComplianceAgent(BaseAgent):
    """Agent focused on coding standards compliance and best practices."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "ComplianceAgent", config)
        self.capabilities = [
            JavaAnalysisCapability(config),
            PythonAnalysisCapability(config),
            GenericAnalysisCapability(config)
        ]
        self.agent_type = "compliance"
        self.logger = logging.getLogger(__name__)
    
    async def analyze_situation(self, context: Dict[str, Any]) -> List[AgentGoal]:
        """Analyze the current situation to understand compliance needs."""
        files = context.get("files", [])
        goal = AgentGoal(
            id="compliance_goal",
            description="Analyze code for standards compliance",
            priority=Priority.HIGH,
            success_criteria={"compliance_checked": True},
            context={"files": files}
        )
        return [goal]
    
    async def plan_actions(self, goals: List[AgentGoal]) -> List[AgentTask]:
        """Plan actions based on the analyzed goals."""
        context = goals[0].context if goals else {}
        return self.make_autonomous_decision(context)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform compliance analysis against coding standards."""
        self.state = AgentState.ANALYZING
        
        try:
            files = context.get("files", [])
            instruction_context = context.get("instruction_context", {})
            
            compliance_results = {
                "standards_compliance": {},
                "violations": [],
                "compliance_score": 0.0,
                "recommendations": []
            }
            
            # Analyze different file types
            java_files = [f for f in files if str(f).endswith('.java')]
            python_files = [f for f in files if str(f).endswith('.py')]
            
            # Java standards compliance
            if java_files:
                java_compliance = await self._analyze_java_compliance(java_files, context)
                compliance_results["standards_compliance"]["java"] = java_compliance
            
            # Python standards compliance
            if python_files:
                python_compliance = await self._analyze_python_compliance(python_files, context)
                compliance_results["standards_compliance"]["python"] = python_compliance
            
            # Check instruction compliance
            if instruction_context:
                instruction_compliance = await self._check_instruction_compliance(files, instruction_context)
                compliance_results["instruction_compliance"] = instruction_compliance
            
            # Calculate overall compliance score
            compliance_results["compliance_score"] = self._calculate_compliance_score(compliance_results)
            
            # Generate recommendations
            compliance_results["recommendations"] = self._generate_compliance_recommendations(compliance_results)
            
            self.state = AgentState.COMPLETED
            self.analysis_results = compliance_results
            
            self.logger.info(f"Compliance analysis completed with score: {compliance_results['compliance_score']:.2f}")
            
            return compliance_results
            
        except Exception as e:
            self.state = AgentState.FAILED
            self.logger.error(f"Compliance analysis failed: {e}")
            return {"error": str(e), "compliance_score": 0.0}
    
    async def _analyze_java_compliance(self, java_files: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Java coding standards compliance."""
        java_capability = self.capabilities[0]
        
        standards_task = AgentTask(
            id="java_standards_compliance",
            task_type="java_standards_check",
            priority=Priority.HIGH,
            input_data={
                "files": java_files,
                "standards": ["naming", "formatting", "structure", "documentation"]
            }
        )
        
        return await java_capability.execute(standards_task, context)
    
    async def _analyze_python_compliance(self, python_files: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Python coding standards compliance."""
        python_capability = self.capabilities[1]
        
        standards_task = AgentTask(
            id="python_standards_compliance",
            task_type="python_standards_check",
            priority=Priority.HIGH,
            input_data={"files": python_files}
        )
        
        return await python_capability.execute(standards_task, context)
    
    async def _check_instruction_compliance(self, files: List[str], instruction_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with specific instructions."""
        compliance_issues = []
        
        # Check if required components are present
        required_components = instruction_context.get("required_components", [])
        for component in required_components:
            component_found = any(component.lower() in str(f).lower() for f in files)
            if not component_found:
                compliance_issues.append(f"Missing required component: {component}")
        
        return {
            "issues": compliance_issues,
            "compliance_score": 1.0 - (len(compliance_issues) * 0.1)
        }
    
    def _calculate_compliance_score(self, compliance_results: Dict[str, Any]) -> float:
        """Calculate overall compliance score."""
        scores = []
        
        # Java compliance score
        java_compliance = compliance_results.get("standards_compliance", {}).get("java", {})
        if java_compliance:
            scores.append(java_compliance.get("compliance_score", 0.8))
        
        # Python compliance score
        python_compliance = compliance_results.get("standards_compliance", {}).get("python", {})
        if python_compliance:
            scores.append(python_compliance.get("compliance_score", 0.8))
        
        # Instruction compliance score
        instruction_compliance = compliance_results.get("instruction_compliance", {})
        if instruction_compliance:
            scores.append(instruction_compliance.get("compliance_score", 0.8))
        
        return sum(scores) / len(scores) if scores else 0.8
    
    def _generate_compliance_recommendations(self, compliance_results: Dict[str, Any]) -> List[str]:
        """Generate compliance improvement recommendations."""
        recommendations = []
        
        compliance_score = compliance_results.get("compliance_score", 0.8)
        
        if compliance_score < 0.7:
            recommendations.append("Implement automated code formatting tools")
            recommendations.append("Establish code review checklist for standards compliance")
        
        if compliance_score < 0.5:
            recommendations.append("Conduct team training on coding standards")
            recommendations.append("Set up pre-commit hooks for standards checking")
        
        return recommendations
    
    def make_autonomous_decision(self, context: Dict[str, Any]) -> List[AgentTask]:
        """Make autonomous decisions about compliance analysis strategy."""
        files = context.get("files", [])
        tasks = []
        
        # Different strategies based on project characteristics
        if len(files) > 100:
            # Large project - sample-based compliance check
            sample_files = files[:20]  # Check first 20 files
            tasks.append(AgentTask(
                id="sample_compliance_check",
                task_type="java_standards_check",
                priority=Priority.HIGH,
                input_data={"files": sample_files}
            ))
        else:
            # Small project - comprehensive compliance check
            tasks.append(AgentTask(
                id="comprehensive_compliance_check",
                task_type="java_standards_check",
                priority=Priority.MEDIUM,
                input_data={"files": files}
            ))
        
        return tasks


class ReportGenerationAgent(BaseAgent):
    """Agent responsible for synthesizing results and generating comprehensive reports."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "ReportGenerationAgent", config)
        self.capabilities = [ReportGenerationCapability(config)]
        self.agent_type = "reporting"
        self.logger = logging.getLogger(__name__)
    
    async def analyze_situation(self, context: Dict[str, Any]) -> List[AgentGoal]:
        """Analyze the current situation to understand reporting needs."""
        agent_results = context.get("agent_results", {})
        goal = AgentGoal(
            id="report_generation_goal",
            description="Synthesize results and generate comprehensive report",
            priority=Priority.MEDIUM,
            success_criteria={"report_generated": True},
            context={"agent_results": agent_results}
        )
        return [goal]
    
    async def plan_actions(self, goals: List[AgentGoal]) -> List[AgentTask]:
        """Plan actions based on the analyzed goals."""
        context = goals[0].context if goals else {}
        return self.make_autonomous_decision(context)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis report from all agent results."""
        self.state = AgentState.ANALYZING
        
        try:
            agent_results = context.get("agent_results", {})
            report_format = context.get("report_format", "json")
            
            # Synthesize results from all agents
            synthesis_task = AgentTask(
                id="synthesize_results",
                task_type="synthesize_results",
                priority=Priority.HIGH,
                input_data={"agent_results": agent_results}
            )
            
            synthesis_result = await self.capabilities[0].execute(synthesis_task, context)
            
            # Generate comprehensive report
            report_task = AgentTask(
                id="generate_comprehensive_report",
                task_type="generate_report",
                priority=Priority.HIGH,
                input_data={
                    "agent_results": agent_results,
                    "format": report_format,
                    "synthesis": synthesis_result.get("synthesis", {})
                }
            )
            
            report_result = await self.capabilities[0].execute(report_task, context)
            
            # Create executive summary
            summary_task = AgentTask(
                id="create_executive_summary",
                task_type="create_summary",
                priority=Priority.MEDIUM,
                input_data={"agent_results": agent_results}
            )
            
            summary_result = await self.capabilities[0].execute(summary_task, context)
            
            # Combine all results
            final_report = {
                "comprehensive_report": report_result.get("comprehensive_report", {}),
                "synthesis": synthesis_result.get("synthesis", {}),
                "executive_summary": summary_result.get("executive_summary", {}),
                "metadata": {
                    "agent_count": len(agent_results),
                    "report_generated_by": self.agent_id,
                    "report_format": report_format
                }
            }
            
            self.state = AgentState.COMPLETED
            self.analysis_results = final_report
            
            self.logger.info("Comprehensive report generation completed")
            
            return final_report
            
        except Exception as e:
            self.state = AgentState.FAILED
            self.logger.error(f"Report generation failed: {e}")
            return {"error": str(e), "report": {}}
    
    def make_autonomous_decision(self, context: Dict[str, Any]) -> List[AgentTask]:
        """Make autonomous decisions about report generation strategy."""
        agent_results = context.get("agent_results", {})
        tasks = []
        
        # Determine report complexity based on results
        total_issues = sum(len(result.get("issues", [])) for result in agent_results.values() 
                          if isinstance(result, dict))
        
        if total_issues > 50:
            # Many issues - focus on prioritization
            tasks.append(AgentTask(
                id="priority_focused_report",
                task_type="generate_report",
                priority=Priority.HIGH,
                input_data={
                    "agent_results": agent_results,
                    "focus": "high_priority_issues"
                }
            ))
        else:
            # Fewer issues - comprehensive report
            tasks.append(AgentTask(
                id="comprehensive_report",
                task_type="generate_report",
                priority=Priority.MEDIUM,
                input_data={
                    "agent_results": agent_results,
                    "format": "detailed"
                }
            ))
        
        return tasks
