#!/usr/bin/env python3
"""
Workflow Orchestration Agent

This agent serves as the central coordinator for all development workflow processes.
It manages the execution flow, handles approvals, maintains state, and ensures
proper coordination between all other agents in the system.

Key Responsibilities:
1. Workflow Definition and Management
2. Agent Coordination and Communication  
3. Approval Gate Management
4. State Persistence and Recovery
5. Error Handling and Rollback
6. Progress Tracking and Reporting
"""

import json
import yaml
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class PhaseStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"
    SKIPPED = "skipped"

class ApprovalAction(Enum):
    APPROVE = "approve"
    MODIFY = "modify"
    RETRY = "retry"
    SKIP = "skip"
    CANCEL = "cancel"

@dataclass
class WorkflowPhase:
    id: str
    name: str
    description: str
    agent_type: str
    method: str
    dependencies: List[str]
    condition: Optional[str] = None
    approval_required: bool = False
    status: PhaseStatus = PhaseStatus.PENDING
    input_data: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300  # seconds
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowDefinition:
    id: str
    name: str
    description: str
    technology: str
    phases: List[WorkflowPhase]
    config: Dict[str, Any]
    created_at: datetime
    created_by: str
    version: str = "1.0.0"

@dataclass
class WorkflowInstance:
    id: str
    definition_id: str
    status: WorkflowStatus
    current_phase: Optional[str] = None
    requirements: str = ""
    technology: str = ""
    output_path: str = ""
    approval_mode: str = "interactive"
    phases: List[WorkflowPhase] = None
    created_at: datetime = None
    updated_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    progress: Dict[str, Any] = None
    artifacts: List[Dict[str, Any]] = None
    audit_log: List[Dict[str, Any]] = None

@dataclass
class ApprovalRequest:
    id: str
    workflow_id: str
    phase_id: str
    phase_name: str
    phase_description: str
    result: Optional[Dict[str, Any]] = None
    artifacts: List[Dict[str, Any]] = None
    options: List[Dict[str, str]] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None

class AgentInterface:
    """Base interface for all agents"""
    
    def __init__(self, agent_path: str):
        self.agent_path = agent_path
        self.name = self.__class__.__name__
    
    async def execute(self, method: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific method on the agent"""
        raise NotImplementedError("Subclasses must implement execute method")
    
    async def health_check(self) -> bool:
        """Check if the agent is healthy and responding"""
        try:
            result = await self.execute("health_check", {})
            return result.get("status") == "healthy"
        except:
            return False

class CodeGenerationAgent(AgentInterface):
    """Wrapper for Code Generation Agent"""
    
    async def execute(self, method: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if method == "generate_project":
            return await self._generate_project(input_data)
        elif method == "health_check":
            return {"status": "healthy", "agent": "CodeGenerationAgent"}
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _generate_project(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate code generation
        await asyncio.sleep(2)  # Simulate processing time
        return {
            "success": True,
            "generated_files": [
                "src/main/java/com/example/Application.java",
                "src/main/java/com/example/controller/UserController.java",
                "src/main/resources/application.yml"
            ],
            "project_structure": {
                "src": ["main", "test"],
                "pom.xml": "maven_config"
            },
            "message": "Project generated successfully"
        }

class CodeCompilationAgent(AgentInterface):
    """Wrapper for Code Compilation Agent"""
    
    async def execute(self, method: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if method == "compile_project":
            return await self._compile_project(input_data)
        elif method == "health_check":
            return {"status": "healthy", "agent": "CodeCompilationAgent"}
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _compile_project(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate compilation
        await asyncio.sleep(3)  # Simulate compilation time
        return {
            "success": True,
            "compilation_result": "SUCCESS",
            "build_output": "Build completed successfully",
            "test_results": {
                "total": 10,
                "passed": 10,
                "failed": 0
            },
            "artifacts": ["target/app.jar"]
        }

class CodeReviewAgent(AgentInterface):
    """Wrapper for Code Review Agent"""
    
    async def execute(self, method: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if method == "review_project":
            return await self._review_project(input_data)
        elif method == "health_check":
            return {"status": "healthy", "agent": "CodeReviewAgent"}
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _review_project(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate code review
        await asyncio.sleep(2)  # Simulate review time
        return {
            "success": True,
            "quality_score": 8.5,
            "security_score": 9.0,
            "issues": [
                {
                    "type": "warning",
                    "file": "UserController.java",
                    "line": 45,
                    "message": "Consider adding input validation"
                }
            ],
            "recommendations": [
                "Add more unit tests",
                "Implement proper error handling"
            ]
        }

class APISpecWriterAgent(AgentInterface):
    """Wrapper for API Specification Writer Agent"""
    
    async def execute(self, method: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if method == "generate_spec":
            return await self._generate_spec(input_data)
        elif method == "health_check":
            return {"status": "healthy", "agent": "APISpecWriterAgent"}
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _generate_spec(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate API spec generation
        await asyncio.sleep(1)  # Simulate processing time
        
        spec_content = """
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: API for managing users
paths:
  /users:
    get:
      summary: Get all users
      responses:
        '200':
          description: List of users
    post:
      summary: Create a new user
      responses:
        '201':
          description: User created
"""
        
        return {
            "success": True,
            "specification": spec_content.strip(),
            "format": "yaml",
            "endpoints": [
                {"method": "GET", "path": "/users"},
                {"method": "POST", "path": "/users"}
            ],
            "schemas": ["User", "UserRequest", "ErrorResponse"]
        }

class WorkflowOrchestrator:
    """
    Main orchestration engine that coordinates all workflow activities
    """
    
    def __init__(self, storage_path: str = "./workflow_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize database
        self.db_path = self.storage_path / "workflows.db"
        self._init_database()
        
        # Agent registry
        self.agents: Dict[str, AgentInterface] = {
            "code_generation": CodeGenerationAgent("../CodeGenerationAgent"),
            "code_compilation": CodeCompilationAgent("../CodeCompilationAgent"),
            "code_review": CodeReviewAgent("../CodeReviewAgent"),
            "api_spec_writer": APISpecWriterAgent("../WriteAPISpecAgent")
        }
        
        # In-memory state
        self.active_workflows: Dict[str, WorkflowInstance] = {}
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        
        # Thread pool for concurrent execution
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize built-in workflow definitions
        self._load_builtin_workflows()
        
        logger.info("Workflow Orchestrator initialized")
    
    def _init_database(self):
        """Initialize SQLite database for persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workflows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                definition_id TEXT,
                status TEXT,
                data TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Approvals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                workflow_id TEXT,
                phase_id TEXT,
                data TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                workflow_id TEXT,
                action TEXT,
                phase_id TEXT,
                user_id TEXT,
                data TEXT,
                timestamp TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_builtin_workflows(self):
        """Load built-in workflow definitions"""
        
        # Java Spring Boot workflow
        java_workflow = WorkflowDefinition(
            id="java_springboot_standard",
            name="Java Spring Boot Standard Workflow",
            description="Complete Java Spring Boot application development workflow",
            technology="java_springboot",
            phases=[
                WorkflowPhase(
                    id="api_specification",
                    name="API Specification",
                    description="Generate OpenAPI specification",
                    agent_type="api_spec_writer",
                    method="generate_spec",
                    dependencies=[],
                    approval_required=True
                ),
                WorkflowPhase(
                    id="code_generation",
                    name="Code Generation",
                    description="Generate Spring Boot application code",
                    agent_type="code_generation",
                    method="generate_project",
                    dependencies=["api_specification"],
                    approval_required=True
                ),
                WorkflowPhase(
                    id="code_review",
                    name="Code Review",
                    description="Automated code quality review",
                    agent_type="code_review",
                    method="review_project",
                    dependencies=["code_generation"],
                    approval_required=False
                ),
                WorkflowPhase(
                    id="compilation",
                    name="Compilation & Testing",
                    description="Compile and test the application",
                    agent_type="code_compilation",
                    method="compile_project",
                    dependencies=["code_generation"],
                    approval_required=False
                )
            ],
            config={
                "java_version": "17",
                "spring_boot_version": "3.2.0",
                "build_tool": "maven"
            },
            created_at=datetime.now(),
            created_by="system"
        )
        
        self.workflow_definitions[java_workflow.id] = java_workflow
        logger.info(f"Loaded workflow definition: {java_workflow.name}")
    
    async def start_workflow(
        self, 
        requirements: str,
        technology: str,
        output_path: str,
        definition_id: Optional[str] = None,
        approval_mode: str = "interactive",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a new workflow instance"""
        
        # Select workflow definition
        if not definition_id:
            definition_id = f"{technology}_standard"
        
        if definition_id not in self.workflow_definitions:
            return {
                "success": False,
                "error": f"Workflow definition not found: {definition_id}"
            }
        
        definition = self.workflow_definitions[definition_id]
        workflow_id = f"workflow_{int(datetime.now().timestamp())}_{hash(requirements) % 10000}"
        
        # Create workflow instance
        workflow = WorkflowInstance(
            id=workflow_id,
            definition_id=definition_id,
            status=WorkflowStatus.RUNNING,
            requirements=requirements,
            technology=technology,
            output_path=output_path,
            approval_mode=approval_mode,
            phases=[WorkflowPhase(**asdict(phase)) for phase in definition.phases],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            started_at=datetime.now(),
            progress={"total": len(definition.phases), "completed": 0, "percentage": 0},
            artifacts=[],
            audit_log=[]
        )
        
        # Store workflow
        self.active_workflows[workflow_id] = workflow
        await self._persist_workflow(workflow)
        
        # Add initial audit entry
        await self._add_audit_entry(
            workflow_id=workflow_id,
            action="workflow_started",
            data={
                "requirements": requirements,
                "technology": technology,
                "definition_id": definition_id
            }
        )
        
        # Start first phase
        asyncio.create_task(self._execute_next_phase(workflow_id))
        
        logger.info(f"Started workflow {workflow_id} with definition {definition_id}")
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "phases": [
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status.value,
                    "dependencies": p.dependencies
                }
                for p in workflow.phases
            ]
        }
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status"""
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            workflow = await self._load_workflow(workflow_id)
        
        if not workflow:
            return None
        
        return {
            "id": workflow.id,
            "status": workflow.status.value,
            "current_phase": workflow.current_phase,
            "progress": workflow.progress,
            "phases": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "status": p.status.value,
                    "start_time": p.start_time.isoformat() if p.start_time else None,
                    "end_time": p.end_time.isoformat() if p.end_time else None,
                    "retry_count": p.retry_count,
                    "error": p.error,
                    "dependencies": p.dependencies
                }
                for p in workflow.phases
            ],
            "artifacts": workflow.artifacts,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "estimated_completion": self._estimate_completion(workflow)
        }
    
    async def handle_approval(
        self,
        workflow_id: str,
        phase_id: str,
        action: str,
        modifications: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None,
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """Handle approval decision for a workflow phase"""
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"success": False, "error": "Workflow not found"}
        
        phase = next((p for p in workflow.phases if p.id == phase_id), None)
        if not phase:
            return {"success": False, "error": "Phase not found"}
        
        approval_key = f"{workflow_id}:{phase_id}"
        if approval_key in self.pending_approvals:
            del self.pending_approvals[approval_key]
        
        # Add audit entry
        await self._add_audit_entry(
            workflow_id=workflow_id,
            action=f"approval_{action}",
            phase_id=phase_id,
            user_id=user_id,
            data={"action": action, "modifications": modifications, "feedback": feedback}
        )
        
        try:
            action_enum = ApprovalAction(action)
            
            if action_enum == ApprovalAction.APPROVE:
                phase.status = PhaseStatus.COMPLETED
                phase.end_time = datetime.now()
                self._update_progress(workflow)
                asyncio.create_task(self._execute_next_phase(workflow_id))
                
            elif action_enum == ApprovalAction.MODIFY:
                if modifications:
                    phase.result = {**(phase.result or {}), **modifications}
                phase.status = PhaseStatus.COMPLETED
                phase.end_time = datetime.now()
                self._update_progress(workflow)
                asyncio.create_task(self._execute_next_phase(workflow_id))
                
            elif action_enum == ApprovalAction.RETRY:
                phase.status = PhaseStatus.PENDING
                phase.error = None
                phase.retry_count = 0
                asyncio.create_task(self._execute_phase(workflow_id, phase_id))
                
            elif action_enum == ApprovalAction.SKIP:
                phase.status = PhaseStatus.SKIPPED
                phase.end_time = datetime.now()
                self._update_progress(workflow)
                asyncio.create_task(self._execute_next_phase(workflow_id))
                
            elif action_enum == ApprovalAction.CANCEL:
                workflow.status = WorkflowStatus.CANCELLED
                workflow.completed_at = datetime.now()
            
            workflow.updated_at = datetime.now()
            await self._persist_workflow(workflow)
            
            return {"success": True, "message": f"Phase {action} successful"}
            
        except ValueError:
            return {"success": False, "error": f"Invalid action: {action}"}
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approval requests"""
        return [
            {
                "workflow_id": approval.workflow_id,
                "phase_id": approval.phase_id,
                "phase_name": approval.phase_name,
                "phase_description": approval.phase_description,
                "result": approval.result,
                "artifacts": approval.artifacts,
                "options": approval.options,
                "created_at": approval.created_at.isoformat() if approval.created_at else None,
                "context": approval.context
            }
            for approval in self.pending_approvals.values()
        ]
    
    def get_workflow_definitions(self) -> List[Dict[str, Any]]:
        """Get available workflow definitions"""
        return [
            {
                "id": wd.id,
                "name": wd.name,
                "description": wd.description,
                "technology": wd.technology,
                "phases": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description,
                        "dependencies": p.dependencies,
                        "approval_required": p.approval_required
                    }
                    for p in wd.phases
                ],
                "config": wd.config
            }
            for wd in self.workflow_definitions.values()
        ]
    
    async def _execute_next_phase(self, workflow_id: str):
        """Execute the next available phase in the workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.RUNNING:
            return
        
        next_phase = self._find_next_phase(workflow)
        if not next_phase:
            # Workflow completed
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.current_phase = None
            workflow.updated_at = datetime.now()
            await self._persist_workflow(workflow)
            
            await self._add_audit_entry(
                workflow_id=workflow_id,
                action="workflow_completed",
                data={"completion_time": workflow.completed_at.isoformat()}
            )
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            return
        
        await self._execute_phase(workflow_id, next_phase.id)
    
    def _find_next_phase(self, workflow: WorkflowInstance) -> Optional[WorkflowPhase]:
        """Find the next phase that can be executed"""
        for phase in workflow.phases:
            if phase.status != PhaseStatus.PENDING:
                continue
            
            # Check dependencies
            dependencies_met = all(
                any(p.id == dep_id and p.status == PhaseStatus.COMPLETED for p in workflow.phases)
                for dep_id in phase.dependencies
            )
            
            if dependencies_met:
                return phase
        
        return None
    
    async def _execute_phase(self, workflow_id: str, phase_id: str):
        """Execute a specific workflow phase"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        phase = next((p for p in workflow.phases if p.id == phase_id), None)
        if not phase:
            return
        
        phase.status = PhaseStatus.RUNNING
        phase.start_time = datetime.now()
        workflow.current_phase = phase_id
        workflow.updated_at = datetime.now()
        
        logger.info(f"Executing phase {phase_id} for workflow {workflow_id}")
        
        try:
            # Prepare input data
            input_data = self._prepare_phase_input(workflow, phase)
            
            # Get the appropriate agent
            agent = self.agents.get(phase.agent_type)
            if not agent:
                raise Exception(f"Agent not found: {phase.agent_type}")
            
            # Execute the agent method
            result = await agent.execute(phase.method, input_data)
            
            if result.get("success", True):
                phase.result = result
                
                # Create artifacts if applicable
                if result.get("generated_files"):
                    for file_path in result["generated_files"]:
                        workflow.artifacts.append({
                            "id": f"artifact_{int(datetime.now().timestamp())}",
                            "type": "file",
                            "name": Path(file_path).name,
                            "path": file_path,
                            "phase_id": phase.id,
                            "created_at": datetime.now().isoformat()
                        })
                
                if phase.approval_required and workflow.approval_mode == "interactive":
                    phase.status = PhaseStatus.WAITING_APPROVAL
                    await self._create_approval_request(workflow, phase)
                else:
                    phase.status = PhaseStatus.COMPLETED
                    phase.end_time = datetime.now()
                    self._update_progress(workflow)
                    asyncio.create_task(self._execute_next_phase(workflow_id))
            else:
                raise Exception(result.get("error", "Phase execution failed"))
        
        except Exception as error:
            phase.status = PhaseStatus.FAILED
            phase.error = str(error)
            phase.end_time = datetime.now()
            
            logger.error(f"Phase {phase_id} failed: {error}")
            
            if phase.retry_count < phase.max_retries:
                phase.retry_count += 1
                logger.info(f"Retrying phase {phase_id} (attempt {phase.retry_count})")
                await asyncio.sleep(5)  # Wait before retry
                asyncio.create_task(self._execute_phase(workflow_id, phase_id))
            else:
                workflow.status = WorkflowStatus.FAILED
                workflow.error = f"Phase {phase.name} failed: {phase.error}"
                await self._add_audit_entry(
                    workflow_id=workflow_id,
                    action="workflow_failed",
                    phase_id=phase_id,
                    data={"error": str(error)}
                )
        
        workflow.updated_at = datetime.now()
        await self._persist_workflow(workflow)
    
    def _prepare_phase_input(self, workflow: WorkflowInstance, phase: WorkflowPhase) -> Dict[str, Any]:
        """Prepare input data for a phase execution"""
        base_input = {
            "workflow_id": workflow.id,
            "phase_id": phase.id,
            "requirements": workflow.requirements,
            "technology": workflow.technology,
            "output_path": workflow.output_path,
            "config": self.workflow_definitions[workflow.definition_id].config
        }
        
        # Add results from dependency phases
        dependency_results = {}
        for dep_id in phase.dependencies:
            dep_phase = next((p for p in workflow.phases if p.id == dep_id), None)
            if dep_phase and dep_phase.result:
                dependency_results[dep_id] = dep_phase.result
        
        base_input["dependencies"] = dependency_results
        base_input["previous_phases"] = [
            p for p in workflow.phases if p.status == PhaseStatus.COMPLETED
        ]
        
        return base_input
    
    async def _create_approval_request(self, workflow: WorkflowInstance, phase: WorkflowPhase):
        """Create an approval request for a phase"""
        approval_id = f"{workflow.id}:{phase.id}"
        
        approval = ApprovalRequest(
            id=approval_id,
            workflow_id=workflow.id,
            phase_id=phase.id,
            phase_name=phase.name,
            phase_description=phase.description,
            result=phase.result,
            artifacts=[a for a in workflow.artifacts if a.get("phase_id") == phase.id],
            options=[
                {"id": "approve", "label": "Approve & Continue", "action": "approve"},
                {"id": "modify", "label": "Modify & Continue", "action": "modify"},
                {"id": "retry", "label": "Retry Phase", "action": "retry"},
                {"id": "skip", "label": "Skip Phase", "action": "skip"}
            ],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            context={
                "next_phase": self._find_next_phase(workflow),
                "estimated_time": self._estimate_phase_time(phase),
                "dependencies": self._prepare_phase_input(workflow, phase)["dependencies"]
            }
        )
        
        self.pending_approvals[approval_id] = approval
        
        logger.info(f"Created approval request for phase {phase.id} in workflow {workflow.id}")
    
    def _update_progress(self, workflow: WorkflowInstance):
        """Update workflow progress metrics"""
        completed_phases = sum(
            1 for p in workflow.phases 
            if p.status in [PhaseStatus.COMPLETED, PhaseStatus.SKIPPED]
        )
        
        workflow.progress = {
            "total": len(workflow.phases),
            "completed": completed_phases,
            "percentage": round((completed_phases / len(workflow.phases)) * 100)
        }
    
    def _estimate_completion(self, workflow: WorkflowInstance) -> str:
        """Estimate workflow completion time"""
        remaining_phases = sum(
            1 for p in workflow.phases if p.status == PhaseStatus.PENDING
        )
        
        avg_phase_time = 5  # 5 minutes average
        estimated_minutes = remaining_phases * avg_phase_time
        
        if estimated_minutes < 60:
            return f"{estimated_minutes} minutes"
        else:
            hours = estimated_minutes // 60
            minutes = estimated_minutes % 60
            return f"{hours}h {minutes}m"
    
    def _estimate_phase_time(self, phase: WorkflowPhase) -> int:
        """Estimate phase execution time in minutes"""
        time_estimates = {
            "api_specification": 2,
            "code_generation": 5,
            "code_review": 3,
            "compilation": 4,
            "deployment": 3
        }
        return time_estimates.get(phase.id, 5) * 60  # Convert to seconds
    
    async def _persist_workflow(self, workflow: WorkflowInstance):
        """Persist workflow to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        workflow_data = {
            "id": workflow.id,
            "definition_id": workflow.definition_id,
            "status": workflow.status.value,
            "current_phase": workflow.current_phase,
            "requirements": workflow.requirements,
            "technology": workflow.technology,
            "output_path": workflow.output_path,
            "approval_mode": workflow.approval_mode,
            "phases": [asdict(p) for p in workflow.phases],
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "error": workflow.error,
            "progress": workflow.progress,
            "artifacts": workflow.artifacts,
            "audit_log": workflow.audit_log
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO workflows 
            (id, definition_id, status, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            workflow.id,
            workflow.definition_id,
            workflow.status.value,
            json.dumps(workflow_data),
            workflow.created_at,
            workflow.updated_at
        ))
        
        conn.commit()
        conn.close()
    
    async def _load_workflow(self, workflow_id: str) -> Optional[WorkflowInstance]:
        """Load workflow from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT data FROM workflows WHERE id = ?",
            (workflow_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        data = json.loads(result[0])
        
        # Convert back to workflow instance
        workflow = WorkflowInstance(
            id=data["id"],
            definition_id=data["definition_id"],
            status=WorkflowStatus(data["status"]),
            current_phase=data.get("current_phase"),
            requirements=data.get("requirements", ""),
            technology=data.get("technology", ""),
            output_path=data.get("output_path", ""),
            approval_mode=data.get("approval_mode", "interactive"),
            phases=[
                WorkflowPhase(
                    id=p["id"],
                    name=p["name"],
                    description=p["description"],
                    agent_type=p["agent_type"],
                    method=p["method"],
                    dependencies=p["dependencies"],
                    condition=p.get("condition"),
                    approval_required=p.get("approval_required", False),
                    status=PhaseStatus(p["status"]),
                    input_data=p.get("input_data"),
                    result=p.get("result"),
                    error=p.get("error"),
                    start_time=datetime.fromisoformat(p["start_time"]) if p.get("start_time") else None,
                    end_time=datetime.fromisoformat(p["end_time"]) if p.get("end_time") else None,
                    retry_count=p.get("retry_count", 0),
                    max_retries=p.get("max_retries", 3),
                    timeout=p.get("timeout", 300),
                    metadata=p.get("metadata")
                )
                for p in data.get("phases", [])
            ],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error=data.get("error"),
            progress=data.get("progress", {}),
            artifacts=data.get("artifacts", []),
            audit_log=data.get("audit_log", [])
        )
        
        self.active_workflows[workflow_id] = workflow
        return workflow
    
    async def _add_audit_entry(
        self,
        workflow_id: str,
        action: str,
        phase_id: Optional[str] = None,
        user_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """Add entry to audit log"""
        entry_id = f"audit_{int(datetime.now().timestamp())}"
        timestamp = datetime.now()
        
        # Add to workflow audit log
        workflow = self.active_workflows.get(workflow_id)
        if workflow:
            workflow.audit_log.append({
                "id": entry_id,
                "timestamp": timestamp.isoformat(),
                "action": action,
                "phase_id": phase_id,
                "user_id": user_id,
                "data": data
            })
        
        # Persist to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log 
            (id, workflow_id, action, phase_id, user_id, data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id,
            workflow_id,
            action,
            phase_id,
            user_id,
            json.dumps(data) if data else None,
            timestamp
        ))
        
        conn.commit()
        conn.close()


# Demo/Testing Functions
async def demo_workflow():
    """Demonstrate the workflow orchestrator"""
    
    orchestrator = WorkflowOrchestrator()
    
    print("=== Workflow Orchestrator Demo ===\n")
    
    # Start a workflow
    print("1. Starting a Java Spring Boot workflow...")
    result = await orchestrator.start_workflow(
        requirements="Create a REST API for user management with CRUD operations",
        technology="java_springboot",
        output_path="/tmp/demo-project",
        approval_mode="interactive"
    )
    
    if result["success"]:
        workflow_id = result["workflow_id"]
        print(f"   ✓ Workflow started: {workflow_id}")
        print(f"   ✓ Status: {result['status']}")
        print(f"   ✓ Phases: {len(result['phases'])}")
    else:
        print(f"   ✗ Failed to start workflow: {result['error']}")
        return
    
    # Wait a bit for execution
    await asyncio.sleep(3)
    
    # Check status
    print("\n2. Checking workflow status...")
    status = await orchestrator.get_workflow_status(workflow_id)
    if status:
        print(f"   ✓ Status: {status['status']}")
        print(f"   ✓ Progress: {status['progress']['percentage']}%")
        print(f"   ✓ Current Phase: {status.get('current_phase', 'None')}")
        
        for phase in status['phases']:
            print(f"     - {phase['name']}: {phase['status']}")
    
    # Check pending approvals
    print("\n3. Checking pending approvals...")
    approvals = orchestrator.get_pending_approvals()
    print(f"   ✓ Pending approvals: {len(approvals)}")
    
    for approval in approvals:
        print(f"     - {approval['phase_name']} (Workflow: {approval['workflow_id']})")
        
        # Auto-approve for demo
        print(f"       → Auto-approving {approval['phase_name']}...")
        approval_result = await orchestrator.handle_approval(
            workflow_id=approval['workflow_id'],
            phase_id=approval['phase_id'],
            action="approve",
            user_id="demo_user"
        )
        
        if approval_result["success"]:
            print(f"       ✓ {approval_result['message']}")
        else:
            print(f"       ✗ {approval_result['error']}")
    
    # Wait for completion
    print("\n4. Waiting for workflow completion...")
    
    for i in range(10):  # Wait up to 30 seconds
        await asyncio.sleep(3)
        status = await orchestrator.get_workflow_status(workflow_id)
        
        if status and status['status'] in ['completed', 'failed']:
            break
        
        # Handle any new approvals
        approvals = orchestrator.get_pending_approvals()
        for approval in approvals:
            if approval['workflow_id'] == workflow_id:
                await orchestrator.handle_approval(
                    workflow_id=approval['workflow_id'],
                    phase_id=approval['phase_id'],
                    action="approve",
                    user_id="demo_user"
                )
    
    # Final status
    print("\n5. Final workflow status...")
    final_status = await orchestrator.get_workflow_status(workflow_id)
    if final_status:
        print(f"   ✓ Final Status: {final_status['status']}")
        print(f"   ✓ Progress: {final_status['progress']['percentage']}%")
        print(f"   ✓ Artifacts: {len(final_status['artifacts'])}")
        
        for artifact in final_status['artifacts']:
            print(f"     - {artifact['name']} ({artifact['type']})")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_workflow())
