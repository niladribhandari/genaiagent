# Workflow Orchestration Agent

The Workflow Orchestration Agent serves as the central coordinator for all development workflow processes in the Developer Assistant system. It manages complex multi-agent workflows with approval gates, dependency management, and intelligent routing.

## Key Features

### 🔄 Workflow Orchestration
- **Multi-Agent Coordination**: Seamlessly coordinates between CodeGeneration, CodeCompilation, CodeReview, GitHubSearch, WebSearch, and APISpecWriter agents
- **Dependency Management**: Ensures phases execute in correct order based on dependencies
- **Parallel Execution**: Supports concurrent execution of independent phases
- **Error Handling**: Automatic retry logic with configurable retry counts and timeouts

### ✋ Approval Gate Management  
- **Interactive Approvals**: Pause workflow execution for user review and approval
- **Contextual Information**: Provides rich context for approval decisions including phase results, artifacts, and next steps
- **Multiple Approval Actions**: Approve, Modify, Retry, Skip, or Cancel phases
- **Batch Approvals**: Support for auto-approval and batch processing modes

### 💾 State Management
- **Persistent Storage**: SQLite database for workflow state persistence
- **Recovery**: Ability to resume workflows after system restarts
- **Audit Trail**: Complete audit log of all workflow actions and decisions
- **Real-time Updates**: Live status updates and progress tracking

### 📊 Progress Tracking
- **Visual Progress**: Real-time progress indicators and completion estimates
- **Artifact Management**: Track and manage generated files, specifications, and reports
- **Performance Metrics**: Execution time tracking and performance analysis

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Workflow Orchestrator                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Phase     │  │  Approval   │  │   State     │         │
│  │  Manager    │  │  Gateway    │  │  Manager    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    Agent Registry                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐ │
│  │   Code    │ │   Code    │ │   Code    │ │  API Spec   │ │
│  │   Gen     │ │  Review   │ │  Compile  │ │   Writer    │ │
│  └───────────┘ └───────────┘ └───────────┘ └─────────────┘ │
│                                                             │
│  ┌───────────┐ ┌───────────┐                               │
│  │  GitHub   │ │    Web    │                               │
│  │  Search   │ │  Search   │                               │
│  └───────────┘ └───────────┘                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Workflow Definitions

### Standard Java Spring Boot Workflow
1. **API Specification** - Generate OpenAPI spec from requirements
2. **Code Generation** - Generate Spring Boot application code  
3. **Code Review** - Automated quality and security review
4. **Compilation & Testing** - Build and test the application

### Standard Node.js Express Workflow  
1. **API Specification** - Generate OpenAPI spec from requirements
2. **Code Generation** - Generate Express.js application code
3. **Code Review** - Automated quality and security review
4. **Testing & Linting** - Run tests and code linting

## API Interface

### Start Workflow
```python
result = await orchestrator.start_workflow(
    requirements="Create a REST API for user management",
    technology="java_springboot", 
    output_path="/tmp/project",
    approval_mode="interactive"
)
```

### Get Status
```python
status = await orchestrator.get_workflow_status(workflow_id)
```

### Handle Approvals
```python
result = await orchestrator.handle_approval(
    workflow_id=workflow_id,
    phase_id=phase_id,
    action="approve",  # approve, modify, retry, skip, cancel
    modifications={"config": "updated"},
    user_id="user123"
)
```

### Get Pending Approvals
```python
approvals = orchestrator.get_pending_approvals()
```

## Configuration

### Phase Configuration
```python
WorkflowPhase(
    id="code_generation",
    name="Code Generation", 
    description="Generate application code",
    agent_type="code_generation",
    method="generate_project",
    dependencies=["api_specification"],
    approval_required=True,
    timeout=600,  # 10 minutes
    max_retries=3
)
```

### Technology-Specific Settings
```python
config = {
    "java_springboot": {
        "java_version": "17",
        "spring_boot_version": "3.2.0", 
        "build_tool": "maven"
    },
    "nodejs_express": {
        "node_version": "18",
        "express_version": "4.18.0",
        "typescript": True
    }
}
```

## Integration with MCP Server

The orchestration agent is integrated with the MCP server through enhanced workflow tools:

- `start_enhanced_workflow` - Start new workflow with advanced features
- `get_enhanced_workflow_status` - Get detailed workflow status
- `handle_enhanced_approval` - Process approval decisions
- `get_enhanced_pending_approvals` - Retrieve pending approvals
- `get_workflow_templates` - List available workflow templates

## Storage & Persistence

### Database Schema
```sql
-- Workflows table
CREATE TABLE workflows (
    id TEXT PRIMARY KEY,
    definition_id TEXT,
    status TEXT,
    data TEXT,  -- JSON workflow data
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Approvals table  
CREATE TABLE approvals (
    id TEXT PRIMARY KEY,
    workflow_id TEXT,
    phase_id TEXT,
    data TEXT,  -- JSON approval data
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Audit log table
CREATE TABLE audit_log (
    id TEXT PRIMARY KEY,
    workflow_id TEXT,
    action TEXT,
    phase_id TEXT,
    user_id TEXT,
    data TEXT,  -- JSON action data
    timestamp TIMESTAMP
);
```

### File Structure
```
workflow_storage/
├── workflows.db           # SQLite database
├── artifacts/            # Generated files and outputs
│   ├── {workflow_id}/   
│   │   ├── api_spec.yaml
│   │   ├── generated_code/
│   │   └── reports/
└── templates/            # Workflow templates
    ├── java_springboot.yaml
    └── nodejs_express.yaml
```

## Example Usage

### Basic Workflow Execution
```python
import asyncio
from orchestration_agent import WorkflowOrchestrator

async def main():
    orchestrator = WorkflowOrchestrator()
    
    # Start workflow
    result = await orchestrator.start_workflow(
        requirements="Build a user management API with authentication",
        technology="java_springboot",
        output_path="/tmp/user-api"
    )
    
    workflow_id = result["workflow_id"]
    print(f"Started workflow: {workflow_id}")
    
    # Monitor progress
    while True:
        status = await orchestrator.get_workflow_status(workflow_id)
        print(f"Status: {status['status']} - {status['progress']['percentage']}%")
        
        if status['status'] in ['completed', 'failed']:
            break
            
        # Handle approvals
        approvals = orchestrator.get_pending_approvals()
        for approval in approvals:
            if approval['workflow_id'] == workflow_id:
                await orchestrator.handle_approval(
                    workflow_id, approval['phase_id'], "approve"
                )
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Workflow Definition
```python
# Define custom workflow phases
custom_phases = [
    WorkflowPhase(
        id="requirements_analysis",
        name="Requirements Analysis",
        agent_type="ai_analyzer", 
        method="analyze_requirements",
        dependencies=[],
        approval_required=True
    ),
    WorkflowPhase(
        id="architecture_design", 
        name="Architecture Design",
        agent_type="architect_agent",
        method="design_architecture", 
        dependencies=["requirements_analysis"],
        approval_required=True
    ),
    # ... more phases
]

# Create workflow definition
workflow_def = WorkflowDefinition(
    id="custom_enterprise_workflow",
    name="Enterprise Application Workflow",
    technology="java_springboot",
    phases=custom_phases,
    config={"enterprise_features": True}
)
```

## Error Handling & Recovery

### Automatic Retry Logic
- Configurable retry counts per phase
- Exponential backoff for retries
- Different retry strategies for different error types

### Recovery Mechanisms
- Workflow state restoration from database
- Resume from last successful phase
- Manual intervention points for complex failures

### Monitoring & Alerting
- Phase execution time monitoring
- Error rate tracking
- Performance metrics collection
- Integration with monitoring systems

## Best Practices

1. **Define Clear Phase Dependencies** - Ensure proper execution order
2. **Set Appropriate Timeouts** - Prevent hanging workflows
3. **Use Approval Gates Strategically** - Balance automation with control
4. **Monitor Resource Usage** - Track agent performance and resources
5. **Implement Proper Error Handling** - Graceful degradation and recovery
6. **Regular State Cleanup** - Archive completed workflows
7. **Security Considerations** - Validate user permissions for approvals

## Future Enhancements

- **Workflow Templates** - Pre-built templates for common patterns
- **Conditional Execution** - Dynamic phase execution based on conditions
- **Parallel Phase Execution** - Concurrent execution of independent phases  
- **External Integrations** - Webhooks and API integrations
- **Advanced Scheduling** - Cron-like scheduling for automated workflows
- **Multi-tenant Support** - Isolated workflows for different organizations
