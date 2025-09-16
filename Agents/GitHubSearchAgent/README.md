# GitHub Search Agent

# GitHub Search Agent

A sophisticated multi-agent system for GitHub repository search, analysis, and insights based on Agentic AI principles.

## 🎯 Overview

The GitHub Search Agent is a comprehensive system that leverages multiple specialized AI agents to provide intelligent GitHub repository search, code analysis, security assessment, trend analysis, and automated documentation generation.

## 🏗️ Architecture

### Core Components

- **AgentOrchestrator**: Central coordination system for managing multiple agents
- **BaseAgent**: Foundation framework for all specialized agents
- **GitHubSearchAgent**: Repository discovery and search capabilities
- **CodeAnalysisAgent**: Code quality and complexity analysis
- **SecurityAnalysisAgent**: Security vulnerability detection and assessment
- **TrendAnalysisAgent**: Technology trend analysis and market insights
- **DocumentationAgent**: Automated documentation generation

### Key Features

- 🔍 **Intelligent Search**: Advanced repository discovery with semantic understanding
- 📊 **Code Analysis**: Comprehensive code quality, complexity, and maintainability assessment
- 🛡️ **Security Scanning**: Automated vulnerability detection and security pattern analysis
- 📈 **Trend Analysis**: Technology trend monitoring and adoption insights
- 📚 **Auto Documentation**: Intelligent documentation generation from code
- 🤖 **Agentic AI**: Autonomous agents with goal-oriented execution
- ⚡ **Performance**: Async operations with rate limiting and caching

## 🚀 Quick Start

### Prerequisites

```bash
pip install aiohttp python-dotenv pyyaml
```

### Configuration

1. Create a `.env` file:
```bash
GITHUB_TOKEN=your_github_token_here
LOG_LEVEL=INFO
```

2. Update `config.yml` with your preferences:
```yaml
github:
  api_url: "https://api.github.com"
  rate_limit: 5000
  timeout: 30

search:
  max_results: 100
  cache_duration: 3600

analysis:
  max_file_size: 1048576
  supported_languages:
    - python
    - javascript
    - java
    - go
    - rust
```

### Basic Usage

```python
import asyncio
from src.github_search_agent import GitHubSearchSystem

async def main():
    system = GitHubSearchSystem()
    
    try:
        # Search repositories
        results = await system.smart_search(
            query="python machine learning",
            search_type="repositories",
            max_results=10
        )
        
        # Analyze a repository
        analysis = await system.analyze_repository("scikit-learn/scikit-learn")
        print(f"Quality Score: {analysis.quality_score}/100")
        
        # Security scan
        security = await system.scan_repository_security("scikit-learn/scikit-learn")
        print(f"Security Issues: {len(security.vulnerabilities)}")
        
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📖 Examples

### 1. Repository Search and Analysis
```python
# See examples/repository_search.py
python examples/repository_search.py
```

### 2. Security Assessment
```python
# See examples/security_analysis.py
python examples/security_analysis.py
```

### 3. Technology Trend Analysis
```python
# See examples/trend_analysis.py
python examples/trend_analysis.py
```

### 4. Documentation Generation
```python
# See examples/documentation_generation.py
python examples/documentation_generation.py
```

### 5. Complete Workflow
```python
# See examples/complete_workflow.py
python examples/complete_workflow.py
```

## 🔧 Advanced Usage

### Custom Agent Configuration

```python
from src.agentic.core import AgentOrchestrator
from src.agentic.github_search_agent import GitHubSearchAgent

# Create orchestrator with custom configuration
orchestrator = AgentOrchestrator()

# Add custom search agent
search_agent = GitHubSearchAgent(
    name="CustomSearchAgent",
    capabilities=["repository_search", "user_search", "code_search"]
)

orchestrator.add_agent(search_agent)

# Execute coordinated search
results = await orchestrator.execute_goal(
    goal="Find top Python ML repositories with high test coverage",
    context={"language": "python", "domain": "machine learning"}
)
```

### Multi-Agent Collaboration

```python
from src.github_search_agent import GitHubSearchSystem

system = GitHubSearchSystem()

# Compare multiple repositories
comparison = await system.compare_repositories([
    "django/django",
    "pallets/flask",
    "fastapi/fastapi"
])

# Get comprehensive insights
for repo_name, data in comparison["comparison_data"].items():
    print(f"{repo_name}: Quality={data['quality_score']}, Security={data['security_score']}")
```

### Technology Landscape Analysis

```python
# Analyze trending technologies
trends = await system.discover_trending_technologies(
    time_period="6months",
    categories=["web-frameworks", "ai-ml", "devops"]
)

# Generate market insights
summary = await system.summarize_technology_landscape(
    technology="kubernetes",
    focus_areas=["adoption", "ecosystem", "alternatives"]
)
```

## 🛡️ Security Features

- **Vulnerability Detection**: Identifies common security patterns and anti-patterns
- **Dependency Analysis**: Scans for known vulnerable dependencies
- **Code Pattern Analysis**: Detects potentially dangerous code patterns
- **Security Score**: Comprehensive security assessment scoring

## 📊 Analytics and Insights

- **Code Quality Metrics**: Complexity, maintainability, test coverage
- **Performance Analysis**: Identifies performance bottlenecks and optimizations
- **Trend Monitoring**: Tracks technology adoption and popularity
- **Community Analysis**: Assesses project health and community engagement

## 🔌 Integration

### With Existing Systems

```python
# Integrate with CI/CD pipelines
from src.agentic.security_analysis_agent import SecurityAnalysisAgent

security_agent = SecurityAnalysisAgent()
results = await security_agent.scan_repository("your-org/your-repo")

# Fail build if critical vulnerabilities found
critical_vulns = [v for v in results.vulnerabilities if v.severity == "critical"]
if critical_vulns:
    raise Exception(f"Critical vulnerabilities found: {len(critical_vulns)}")
```

### Custom Agents

```python
from src.agentic.base_agent import BaseAgent

class CustomAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CustomAnalysisAgent",
            capabilities=["custom_analysis", "reporting"]
        )
    
    async def execute_goal(self, goal: str, context: dict) -> dict:
        # Implement custom analysis logic
        return {"analysis": "custom results"}
```

## 🌐 API Reference

### GitHubSearchSystem

Main system interface providing high-level operations:

- `smart_search(query, search_type, max_results)`: Intelligent repository search
- `analyze_repository(repo_name)`: Comprehensive repository analysis
- `scan_repository_security(repo_name)`: Security vulnerability assessment
- `assess_code_quality(repo_name)`: Code quality evaluation
- `discover_trending_technologies(time_period)`: Technology trend analysis
- `generate_comprehensive_docs(repository)`: Documentation generation
- `compare_repositories(repo_list)`: Multi-repository comparison

### Agent Framework

Core agent system for building custom agents:

- `BaseAgent`: Foundation class for all agents
- `AgentOrchestrator`: Coordination and workflow management
- `AgentCapability`: Capability definition and management

## 📈 Performance

- **Async Operations**: Non-blocking I/O for optimal performance
- **Rate Limiting**: Intelligent throttling to respect GitHub API limits
- **Caching**: Smart caching to reduce API calls and improve response times
- **Batch Processing**: Efficient handling of multiple repositories

## 🔍 Troubleshooting

### Common Issues

1. **Rate Limiting**: Ensure you have a valid GitHub token with sufficient quota
2. **Network Errors**: Check internet connectivity and GitHub API status
3. **Authentication**: Verify your GitHub token has required permissions

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

system = GitHubSearchSystem()
# Enable detailed logging for troubleshooting
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- GitHub API for providing comprehensive repository data
- Open source community for inspiration and best practices
- Agentic AI principles for system architecture guidance

## Features

- **Multi-Agent Architecture**: Specialized agents for different search and analysis tasks
- **Intelligent Repository Discovery**: Advanced search with relevance scoring
- **Code Analysis**: Deep code understanding and pattern detection
- **Semantic Search**: Natural language queries for finding relevant repositories
- **Trend Analysis**: Identify trending patterns and technologies
- **Security Analysis**: Vulnerability and security pattern detection
- **Documentation Generation**: Automatic documentation and summary generation

## Architecture

The system consists of 6 specialized agents:

1. **SearchAgent**: Repository discovery and filtering
2. **AnalysisAgent**: Code analysis and pattern detection  
3. **SecurityAgent**: Security vulnerability assessment
4. **TrendAgent**: Technology trend analysis
5. **DocumentationAgent**: Documentation and summary generation
6. **OrchestratorAgent**: Coordinates multi-agent workflows

## Quick Start

```python
from github_search_agent import GitHubSearchSystem

# Initialize the system
search_system = GitHubSearchSystem(github_token="your_token")

# Search for repositories
results = await search_system.search_repositories(
    query="machine learning frameworks python",
    max_results=10,
    include_analysis=True
)

# Analyze a specific repository
analysis = await search_system.analyze_repository(
    owner="tensorflow",
    repo="tensorflow"
)
```

## Configuration

Create a `.env` file:

```
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_key
```

## Installation

```bash
pip install -r requirements.txt
```
