# WriteAPISpecAgent - Agentic AI API Specification Writing System

## 🎯 Overview

WriteAPISpecAgent is a sophisticated multi-agent system that automatically generates comprehensive API specifications from user requirements using Agentic AI principles. The system leverages autonomous agents that collaborate intelligently to analyze requirements, design APIs, write specifications, validate outputs, and generate documentation.

## ✨ Key Features

### 🤖 Agentic AI Architecture
- **Autonomous Agents**: Self-directed agents with specialized capabilities
- **Goal-Oriented Execution**: Agents work towards specific objectives with measurable outcomes
- **Intelligent Collaboration**: Agents coordinate and share information seamlessly
- **Performance Tracking**: Built-in monitoring and optimization of agent performance
- **Adaptive Learning**: Agents improve their performance based on feedback and results

### 🔧 Specialized Agents
1. **RequirementAnalysisAgent**: Analyzes user requirements and extracts API specifications
2. **APIDesignAgent**: Designs comprehensive API structure and architecture
3. **SpecificationWriterAgent**: Generates properly formatted OpenAPI specifications
4. **ValidationAgent**: Validates specifications for correctness and best practices
5. **DocumentationAgent**: Creates comprehensive API documentation and examples

### 📊 Core Capabilities
- **OpenAPI 3.0+ Specification Generation**: Complete, valid specifications in YAML/JSON
- **RESTful API Design**: Best practices for REST API architecture
- **Security Implementation**: JWT, API keys, OAuth2, and other security schemes
- **Data Model Generation**: Comprehensive schemas for request/response objects
- **Documentation Generation**: Getting started guides, API reference, examples
- **Validation & Quality Assurance**: Syntax validation, best practices checking
- **Multi-format Support**: YAML, JSON output with proper formatting

## 🏗️ Architecture

```
WriteAPISpecAgent/
├── src/
│   ├── agentic/                    # Agentic AI Framework
│   │   ├── base_agent.py          # Foundation agent framework
│   │   ├── agent_orchestrator.py  # Multi-agent coordination
│   │   ├── requirement_analysis_agent.py
│   │   ├── api_design_agent.py
│   │   ├── specification_writer_agent.py
│   │   ├── validation_agent.py
│   │   └── documentation_agent.py
│   ├── models/                     # Data Models
│   │   └── search_models.py       # Core data structures
│   ├── utils/                      # Utilities
│   │   ├── spec_formatter.py      # Specification formatting
│   │   └── file_manager.py        # File operations
│   └── api_spec_writer_system.py  # Main orchestrator
├── demo_agentic.py                 # Complete usage examples
└── README.md
```

## 🚀 Quick Start

### Installation

```bash
# Clone or ensure you're in the WriteAPISpecAgent directory
cd WriteAPISpecAgent

# Install dependencies (if using pip)
pip install pyyaml asyncio pathlib
```

### Basic Usage

```python
import asyncio
from src.api_spec_writer_system import APISpecWriterSystem
from src.models.search_models import UserRequirement

async def generate_api_spec():
    # Define your requirements
    requirements = UserRequirement(
        id="my_api_req",
        title="My API",
        description="A comprehensive API for my application",
        functional_requirements=[
            "Create and manage users",
            "Handle authentication and authorization",
            "Manage data entities",
            "Provide search capabilities"
        ],
        business_entities=["User", "Product", "Order"],
        security_requirements=["JWT authentication", "Role-based access"]
    )
    
    # Initialize the system
    system = APISpecWriterSystem()
    
    # Generate specification
    result = await system.generate_specification(requirements)
    
    if result["success"]:
        print("✅ API Specification generated successfully!")
        print(f"📁 Saved to: {result['file_path']}")
    else:
        print(f"❌ Generation failed: {result['error']}")

# Run the example
asyncio.run(generate_api_spec())
```

### Demo Example

Run the comprehensive demo to see all features:

```bash
python demo_agentic.py
```

This will:
1. Create a complete Customer Management API specification
2. Show individual agent capabilities
3. Demonstrate file management features
4. Save results to the `API-requirements` folder

## 📖 Detailed Usage

### Individual Agent Usage

```python
from src.agentic.requirement_analysis_agent import RequirementAnalysisAgent
from src.agentic.base_agent import Goal

# Create and use a specific agent
analysis_agent = RequirementAnalysisAgent()

goal = Goal(
    id="analyze_my_requirements",
    objective="analyze_user_requirements",
    parameters={
        "requirements": {
            "title": "User Management API",
            "description": "Handle user operations",
            "functional_requirements": [
                "Create users",
                "Update profiles",
                "Authenticate users"
            ]
        }
    }
)

result = await analysis_agent.execute_goal(goal)
```

### Workflow Orchestration

```python
from src.agentic.agent_orchestrator import AgentOrchestrator

# Create orchestrator
orchestrator = AgentOrchestrator()

# Register agents
orchestrator.register_agent(RequirementAnalysisAgent())
orchestrator.register_agent(APIDesignAgent())
# ... register other agents

# Create workflow
workflow = orchestrator.create_workflow("my_api_generation")

# Add steps with dependencies
workflow.add_step("analyze", {
    "agent": "requirement_analysis_agent",
    "objective": "analyze_user_requirements",
    "parameters": {"requirements": requirements_dict}
})

workflow.add_step("design", {
    "agent": "api_design_agent",
    "objective": "design_api_structure",
    "parameters": {"project_name": "My API"},
    "depends_on": ["analyze"]
})

# Execute workflow
results = await orchestrator.execute_workflow(workflow.id)
```

### File Management

```python
from src.utils.file_manager import APISpecFileManager

# Initialize file manager
file_manager = APISpecFileManager(base_directory="./API-requirements")

# List existing specifications
specs = file_manager.list_specifications()
print(f"Found {len(specs)} specifications")

# Load a specification
spec_result = file_manager.load_specification("./API-requirements/my_api.yml")

# Export to different format
file_manager.export_specification(
    "my_api.yml", 
    "my_api.json", 
    target_format=SpecificationFormat.OPENAPI_JSON
)
```

### Specification Formatting

```python
from src.utils.spec_formatter import SpecificationFormatter

formatter = SpecificationFormatter()

# Format specification
formatted_yaml = formatter.format_specification(
    spec_dict, 
    SpecificationFormat.OPENAPI_YAML
)

# Validate specification
validation_result = formatter.validate_specification(spec_dict)
print(f"Valid: {validation_result.is_valid}")
print(f"Quality Score: {validation_result.quality_score}")
```

## 🔧 Configuration

### Agent Configuration

Each agent can be configured with custom parameters:

```python
config = {
    "analysis_depth": "comprehensive",
    "design_patterns": ["REST", "resource-oriented"],
    "validation_strict": True,
    "documentation_include_examples": True
}

agent = RequirementAnalysisAgent(config=config)
```

### File Manager Configuration

```python
file_manager = APISpecFileManager(
    base_directory="./custom-output",
    backup_enabled=True,
    version_control=True
)
```

### Formatter Configuration

```python
formatter = SpecificationFormatter({
    "indent_size": 2,
    "line_width": 120,
    "sort_keys": True,
    "include_nulls": False
})
```

## 📊 Agent Capabilities

### RequirementAnalysisAgent
- **Entity Extraction**: Identifies business entities from requirements
- **Endpoint Analysis**: Suggests API endpoints based on functionality
- **Pattern Recognition**: Recognizes common API patterns and conventions
- **Security Analysis**: Identifies security requirements and constraints
- **Data Model Inference**: Suggests data structures and relationships

### APIDesignAgent
- **RESTful Design**: Creates REST-compliant API structures
- **Resource Modeling**: Designs resource hierarchies and relationships
- **HTTP Method Mapping**: Assigns appropriate HTTP methods to operations
- **Schema Generation**: Creates JSON schemas for request/response objects
- **Security Architecture**: Designs authentication and authorization schemes

### SpecificationWriterAgent
- **OpenAPI Generation**: Creates complete OpenAPI 3.0+ specifications
- **Format Support**: Generates YAML and JSON formatted specifications
- **Component Organization**: Structures reusable components and schemas
- **Documentation Integration**: Embeds comprehensive documentation
- **Example Generation**: Creates realistic request/response examples

### ValidationAgent
- **Syntax Validation**: Ensures OpenAPI specification syntax correctness
- **Completeness Checking**: Verifies all required fields are present
- **Best Practices**: Checks adherence to API design best practices
- **Security Validation**: Validates security scheme implementations
- **Quality Scoring**: Provides quantitative quality assessments

### DocumentationAgent
- **Getting Started Guides**: Creates beginner-friendly introductions
- **API Reference**: Generates comprehensive endpoint documentation
- **Code Examples**: Provides examples in multiple programming languages
- **Authentication Docs**: Documents authentication and authorization
- **Error Handling**: Documents error responses and troubleshooting

## 🔄 Workflow Patterns

### Sequential Processing
```python
# Steps execute one after another
workflow.add_step("step1", {...})
workflow.add_step("step2", {..., "depends_on": ["step1"]})
workflow.add_step("step3", {..., "depends_on": ["step2"]})
```

### Parallel Processing
```python
# Steps execute concurrently
workflow.add_step("analysis", {...})
workflow.add_step("research", {...})
workflow.add_step("synthesis", {..., "depends_on": ["analysis", "research"]})
```

### Conditional Execution
```python
# Steps execute based on conditions
workflow.add_step("validate", {...})
workflow.add_step("fix_errors", {..., "condition": "validation_failed"})
```

## 📁 Output Structure

The system saves outputs to the `API-requirements` folder:

```
API-requirements/
├── specs/                  # Generated specifications
│   ├── customer_api.yml
│   └── user_management.json
├── documentation/          # Generated documentation
│   ├── customer_api_documentation.md
│   └── user_management_docs.md
├── examples/              # Code examples
│   ├── customer_api_examples.json
│   └── curl_examples.sh
├── backups/               # Backup files
├── versions/              # Version history
└── metadata/              # Generation metadata
```

## 🎯 Use Cases

### Enterprise API Development
- **Microservices Architecture**: Generate specifications for microservice APIs
- **API Gateway Integration**: Create gateway-compatible specifications
- **Team Collaboration**: Share specifications across development teams
- **Documentation Portal**: Generate documentation for developer portals

### Rapid Prototyping
- **Quick API Design**: Rapidly prototype API structures from requirements
- **Validation Early**: Validate API design before implementation
- **Stakeholder Review**: Generate specifications for stakeholder approval
- **Implementation Guide**: Use specifications to guide development

### API Governance
- **Standards Compliance**: Ensure APIs follow organizational standards
- **Quality Assurance**: Validate API quality and completeness
- **Documentation Consistency**: Maintain consistent API documentation
- **Version Management**: Track API specification versions

## 🔍 Advanced Features

### Performance Tracking
```python
# Get agent performance metrics
performance = agent.get_performance_metrics()
print(f"Success Rate: {performance['success_rate']}")
print(f"Average Execution Time: {performance['avg_execution_time']}")
```

### Custom Capabilities
```python
# Add custom capabilities to agents
agent.add_capability("custom_analysis")
agent.add_knowledge("domain_patterns", custom_patterns)
```

### Workflow Optimization
```python
# Optimize workflow execution
orchestrator.optimize_workflow(workflow_id)

# Get workflow performance
stats = orchestrator.get_workflow_stats(workflow_id)
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **File Permission Issues**: Check write permissions for output directory
3. **Invalid YAML**: Use the validation agent to check specification syntax
4. **Agent Initialization**: Verify agent configuration parameters

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug configuration
config = {"debug": True, "verbose": True}
agent = RequirementAnalysisAgent(config=config)
```

### Validation Issues

```python
# Get detailed validation results
validation_result = formatter.validate_specification(spec_dict)

for issue in validation_result.issues:
    print(f"{issue.severity}: {issue.message}")
    if issue.suggestion:
        print(f"Suggestion: {issue.suggestion}")
```

## 🤝 Contributing

The WriteAPISpecAgent system is designed to be extensible:

### Adding New Agents
1. Inherit from `SpecializedAgent`
2. Implement required methods
3. Register with orchestrator
4. Add to workflow steps

### Custom Formatters
1. Extend `SpecificationFormatter`
2. Add new format types
3. Implement format-specific logic

### Enhanced Capabilities
1. Add new agent capabilities
2. Implement capability-specific logic
3. Update orchestrator selection criteria

## 📄 License

This project is part of the larger genaiagent workspace and follows the same licensing terms.

## 🔗 Related Projects

- **CodeGenerationAgent**: Code generation from specifications
- **ReviewAgent**: Agentic code and specification review
- **GitHubSearch**: Repository analysis and code search

---

**Built with Agentic AI principles for intelligent, autonomous API specification generation** 🚀
