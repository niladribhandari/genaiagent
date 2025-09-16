#!/bin/bash

# Workflow Orchestration Agent Setup Script

set -e

echo "🚀 Setting up Workflow Orchestration Agent..."

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p workflow_storage/artifacts
mkdir -p workflow_storage/templates
mkdir -p tests
mkdir -p logs

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    python3 -m pip install -r requirements.txt
else
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create workflow templates
echo "📋 Creating workflow templates..."

cat > workflow_storage/templates/java_springboot.yaml << 'EOF'
id: java_springboot_standard
name: Java Spring Boot Standard Workflow
description: Complete Java Spring Boot application development workflow
technology: java_springboot
version: "1.0.0"

phases:
  - id: api_specification
    name: API Specification
    description: Generate OpenAPI specification based on requirements
    agent_type: api_spec_writer
    method: generate_spec
    dependencies: []
    approval_required: true
    timeout: 300
    max_retries: 3

  - id: code_generation
    name: Code Generation
    description: Generate Spring Boot application code
    agent_type: code_generation
    method: generate_project
    dependencies: [api_specification]
    approval_required: true
    timeout: 600
    max_retries: 2

  - id: code_review
    name: Code Review
    description: Automated code quality and security review
    agent_type: code_review
    method: review_project
    dependencies: [code_generation]
    approval_required: false
    timeout: 300
    max_retries: 1

  - id: compilation
    name: Compilation & Testing
    description: Compile and test the generated application
    agent_type: code_compilation
    method: compile_project
    dependencies: [code_generation]
    approval_required: false
    timeout: 900
    max_retries: 2

config:
  java_version: "17"
  spring_boot_version: "3.2.0"
  build_tool: maven
  package_name: com.generated.app
EOF

cat > workflow_storage/templates/nodejs_express.yaml << 'EOF'
id: nodejs_express_standard
name: Node.js Express Standard Workflow
description: Complete Node.js Express application development workflow
technology: nodejs_express
version: "1.0.0"

phases:
  - id: api_specification
    name: API Specification
    description: Generate OpenAPI specification based on requirements
    agent_type: api_spec_writer
    method: generate_spec
    dependencies: []
    approval_required: true
    timeout: 300
    max_retries: 3

  - id: code_generation
    name: Code Generation
    description: Generate Express.js application code
    agent_type: code_generation
    method: generate_project
    dependencies: [api_specification]
    approval_required: true
    timeout: 600
    max_retries: 2

  - id: code_review
    name: Code Review
    description: Automated code quality and security review
    agent_type: code_review
    method: review_project
    dependencies: [code_generation]
    approval_required: false
    timeout: 300
    max_retries: 1

  - id: testing
    name: Testing & Linting
    description: Run tests and linting
    agent_type: code_compilation
    method: test_project
    dependencies: [code_generation]
    approval_required: false
    timeout: 600
    max_retries: 2

config:
  node_version: "18"
  express_version: "4.18.0"
  typescript: true
  package_manager: npm
EOF

# Create basic test file
echo "🧪 Creating test files..."

cat > tests/test_orchestrator.py << 'EOF'
import asyncio
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration_agent import WorkflowOrchestrator, WorkflowStatus

@pytest.mark.asyncio
async def test_workflow_creation():
    """Test basic workflow creation"""
    orchestrator = WorkflowOrchestrator()
    
    result = await orchestrator.start_workflow(
        requirements="Test API creation",
        technology="java_springboot",
        output_path="/tmp/test-project"
    )
    
    assert result["success"] == True
    assert "workflow_id" in result
    assert result["status"] == "running"

@pytest.mark.asyncio
async def test_workflow_status():
    """Test workflow status retrieval"""
    orchestrator = WorkflowOrchestrator()
    
    # Start workflow
    result = await orchestrator.start_workflow(
        requirements="Test API creation",
        technology="java_springboot", 
        output_path="/tmp/test-project"
    )
    
    workflow_id = result["workflow_id"]
    
    # Get status
    status = await orchestrator.get_workflow_status(workflow_id)
    
    assert status is not None
    assert status["id"] == workflow_id
    assert "phases" in status
    assert "progress" in status

@pytest.mark.asyncio
async def test_approval_handling():
    """Test approval request handling"""
    orchestrator = WorkflowOrchestrator()
    
    # Start workflow
    result = await orchestrator.start_workflow(
        requirements="Test API creation",
        technology="java_springboot",
        output_path="/tmp/test-project",
        approval_mode="interactive"
    )
    
    workflow_id = result["workflow_id"]
    
    # Wait a bit for first phase to complete and request approval
    await asyncio.sleep(3)
    
    # Check for pending approvals
    approvals = orchestrator.get_pending_approvals()
    
    if approvals:
        approval = approvals[0]
        
        # Handle approval
        result = await orchestrator.handle_approval(
            workflow_id=approval["workflow_id"],
            phase_id=approval["phase_id"],
            action="approve",
            user_id="test_user"
        )
        
        assert result["success"] == True

def test_workflow_definitions():
    """Test workflow definition loading"""
    orchestrator = WorkflowOrchestrator()
    
    definitions = orchestrator.get_workflow_definitions()
    
    assert len(definitions) > 0
    assert any(d["technology"] == "java_springboot" for d in definitions)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF

# Create demo script
echo "🎬 Creating demo script..."

cat > demo.py << 'EOF'
#!/usr/bin/env python3
"""
Demo script for the Workflow Orchestration Agent
"""

import asyncio
from orchestration_agent import WorkflowOrchestrator

async def main():
    print("🚀 Workflow Orchestration Agent Demo")
    print("====================================\n")
    
    orchestrator = WorkflowOrchestrator()
    
    # Show available workflow definitions
    print("📋 Available Workflow Definitions:")
    definitions = orchestrator.get_workflow_definitions()
    for i, definition in enumerate(definitions, 1):
        print(f"   {i}. {definition['name']}")
        print(f"      Technology: {definition['technology']}")
        print(f"      Phases: {len(definition['phases'])}")
        print()
    
    # Start a demo workflow
    print("🎯 Starting Demo Workflow...")
    result = await orchestrator.start_workflow(
        requirements="Create a REST API for managing a simple todo list with CRUD operations",
        technology="java_springboot",
        output_path="/tmp/demo-todo-api",
        approval_mode="interactive"
    )
    
    if not result["success"]:
        print(f"❌ Failed to start workflow: {result['error']}")
        return
    
    workflow_id = result["workflow_id"]
    print(f"✅ Workflow started: {workflow_id}")
    print(f"   Status: {result['status']}")
    print(f"   Phases: {len(result['phases'])}")
    
    # Monitor workflow progress
    print("\n📊 Monitoring Workflow Progress...")
    
    while True:
        await asyncio.sleep(2)
        
        # Get current status
        status = await orchestrator.get_workflow_status(workflow_id)
        if not status:
            print("❌ Could not retrieve workflow status")
            break
        
        print(f"\n🔄 Status: {status['status']}")
        print(f"   Progress: {status['progress']['percentage']}%")
        print(f"   Current Phase: {status.get('current_phase', 'None')}")
        
        # Show phase status
        for phase in status['phases']:
            icon = {
                'pending': '⏳',
                'running': '⚡',
                'completed': '✅', 
                'failed': '❌',
                'waiting_approval': '⏸️',
                'skipped': '⏭️'
            }.get(phase['status'], '❓')
            
            print(f"     {icon} {phase['name']}: {phase['status']}")
        
        # Handle pending approvals
        approvals = orchestrator.get_pending_approvals()
        workflow_approvals = [a for a in approvals if a['workflow_id'] == workflow_id]
        
        if workflow_approvals:
            print(f"\n⏸️  Pending Approvals: {len(workflow_approvals)}")
            
            for approval in workflow_approvals:
                print(f"\n📋 Approval Required: {approval['phase_name']}")
                print(f"   Description: {approval['phase_description']}")
                
                if approval.get('result'):
                    print(f"   Result Preview: {str(approval['result'])[:100]}...")
                
                # Auto-approve for demo (in real usage, this would be user input)
                print("   🤖 Auto-approving for demo...")
                
                approval_result = await orchestrator.handle_approval(
                    workflow_id=approval['workflow_id'],
                    phase_id=approval['phase_id'],
                    action="approve",
                    user_id="demo_user"
                )
                
                if approval_result["success"]:
                    print(f"   ✅ {approval_result['message']}")
                else:
                    print(f"   ❌ Approval failed: {approval_result['error']}")
        
        # Check if workflow is done
        if status['status'] in ['completed', 'failed', 'cancelled']:
            break
    
    # Final status
    print(f"\n🏁 Final Status: {status['status']}")
    print(f"   Progress: {status['progress']['percentage']}%")
    print(f"   Artifacts: {len(status.get('artifacts', []))}")
    
    if status.get('artifacts'):
        print("\n📁 Generated Artifacts:")
        for artifact in status['artifacts']:
            print(f"   📄 {artifact['name']} ({artifact['type']})")
    
    print("\n✨ Demo Complete!")

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x demo.py

# Set permissions
echo "🔧 Setting permissions..."
chmod +x orchestration_agent.py
chmod +x setup.sh

# Create systemd service file (optional)
echo "⚙️  Creating systemd service template..."

cat > workflow-orchestrator.service << 'EOF'
[Unit]
Description=Workflow Orchestration Agent
After=network.target

[Service]
Type=simple
User=orchestrator
Group=orchestrator
WorkingDirectory=/path/to/WorkflowOrchestrationAgent
ExecStart=/usr/bin/python3 orchestration_agent.py
Restart=always
RestartSec=5
Environment=PYTHONPATH=/path/to/WorkflowOrchestrationAgent

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Setup complete!"
echo ""
echo "🎯 Next Steps:"
echo "   1. Run the demo: python3 demo.py"
echo "   2. Run tests: python3 -m pytest tests/ -v"
echo "   3. Start the agent: python3 orchestration_agent.py"
echo ""
echo "📚 Documentation:"
echo "   - README.md: Complete documentation"
echo "   - workflow_storage/templates/: Workflow templates" 
echo "   - tests/: Test files"
echo ""
echo "🔧 Configuration:"
echo "   - Edit workflow_storage/templates/ to customize workflows"
echo "   - Modify orchestration_agent.py for custom agent integrations"
echo "   - Update workflow-orchestrator.service for systemd deployment"
