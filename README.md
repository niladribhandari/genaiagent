# GenAI Agent Platform

A comprehensive multi-agent platform for software development workflows, featuring intelligent orchestration, approval gates, and seamless integration between code generation, compilation, review, and search agents.

---

## 🏗️ Architecture Overview

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   React Frontend    │────│    MCP Server        │────│  Python Agents      │
│   (Port 3000)       │    │   (Port 3001)        │    │  (Various Ports)    │
│                     │    │                      │    │                     │
│ • Workflow Manager  │    │ • Tool Registration  │    │ • Code Generation   │
│ • API Spec Writer   │    │ • Agent Coordination │    │ • Code Compilation  │
│ • Progress Tracking │    │ • State Management   │    │ • Code Review       │
│ • Approval Gates    │    │ • Approval Handling  │    │ • GitHub Search     │
└─────────────────────┘    └──────────────────────┘    │ • Web Search        │
                                                        │ • API Spec Writing  │
                                                        │ • Workflow Orch.    │
                                                        └─────────────────────┘





```

---
![Homepage Screenshot]([(https://github.com/niladribhandari/genaiagent/blob/main/Screenshots/Screenshot%202025-09-16%20at%2018.43.04.png)])



## 🚀 Quick Start

### Prerequisites
- **Node.js** 16+ ([Download](https://nodejs.org/))
- **Python** 3.8+ ([Download](https://python.org/))
- **npm** (comes with Node.js)
- **pip3** (comes with Python)

### Installation
1. **Clone or navigate to the project directory**
2. **Run the automated setup**:
   ```bash
   ./setup-system.sh
   ```
3. **Configure environment variables** (see [Configuration](#configuration))
4. **Start the platform**:
   ```bash
   ./start-all.sh
   ```

### Manual Setup (if automated setup fails)
1. **Setup MCP Server**:
   ```bash
   cd mcp-server
   npm install
   npx tsc
   cd ..
   ```
2. **Setup React App**:
   ```bash
   cd developer-assistant-app
   npm install
   npm run build
   cd ..
   ```
3. **Setup Python Agents**:
   ```bash
   cd Agents/WorkflowOrchestrationAgent
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python orchestration_agent.py --init-db
   deactivate
   cd ../..
   ```

---

## 🔧 Configuration

### Environment Files
The setup script creates `.env` files for each component. Configure them with your specific settings:

#### MCP Server (mcp-server/.env)
```env
PORT=3001
NODE_ENV=development
OPENAI_API_KEY=your_openai_api_key_here
DB_PATH=./data/workflows.db
```
#### React App (developer-assistant-app/.env)
```env
REACT_APP_MCP_SERVER_URL=http://localhost:3001
REACT_APP_WORKFLOW_AGENT_URL=http://localhost:8080
GENERATE_SOURCEMAP=false
```
#### Workflow Agent (Agents/WorkflowOrchestrationAgent/.env)
```env
PORT=8080
HOST=localhost
DEBUG=true
DB_PATH=./data/workflows.db
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🎯 Core Features

### 1. Workflow Orchestration
- **Multi-Agent Coordination**: Seamlessly coordinate between 6+ specialized agents
- **Approval Gates**: User confirmation required between each workflow phase
- **State Management**: Persistent workflow state with SQLite database
- **Error Handling**: Robust error recovery and retry mechanisms

### 2. Intelligent Agents
- **Code Generation Agent**: Generate code from API specifications (multi-language, template-based)
- **Code Compilation Agent**: Compile and validate generated code (multi-language, dependency management)
- **Code Review Agent**: Automated code quality assessment (static analysis, best practices)
- **GitHub Search Agent**: Search GitHub repositories for code examples
- **Web Search Agent**: General web search for documentation and examples
- **API Spec Writing Agent**: Generate comprehensive API specifications (OpenAPI/Swagger)

### 3. Enhanced UI Components
- **Workflow Manager**: Real-time progress tracking, approval interface, artifact management, audit trail
- **API Spec Writer**: Visual preview, template system, validation, export options
- **Generated Projects**: File explorer, project details, compilation and review tabs

---

## 🔄 Workflow Process

### Standard Development Workflow
1. **API Specification Creation**: Use the API Spec Writer to define your API
2. **Requirement Review & Approval**: Review and approve generated specification
3. **Code Generation**: Automatic code generation from API spec
4. **Code Compilation**: Automated compilation and error reporting
5. **Code Review**: Automated code quality assessment
6. **Research & Enhancement**: GitHub and web search for improvements

### Approval Gates
Each workflow step includes an approval gate where users can:
- **Review**: Examine agent outputs and recommendations
- **Approve**: Continue to the next phase
- **Reject**: Stop workflow or request modifications
- **Modify**: Edit outputs before proceeding

---

## 🛠️ Development

### Project Structure
```
genaiagent/
├── mcp-server/                 # MCP Server (TypeScript)
│   ├── src/
│   │   ├── server.ts          # Main server with enhanced tools
│   │   ├── agents.ts          # Agent wrapper classes
│   │   └── workflow-orchestrator.ts  # Workflow orchestration engine
│   └── package.json
├── developer-assistant-app/    # React Frontend
│   ├── src/
│   │   ├── App.tsx           # Main application with tabs
│   │   └── components/
│   │       ├── EnhancedWorkflowManager.tsx
│   │       └── APISpecWriter.tsx
│   └── package.json
├── Agents/                    # Python Agents
│   ├── WorkflowOrchestrationAgent/  # Main orchestration agent
│   ├── CodeGenerationAgent/   
│   ├── CodeCompilationAgent/  
│   ├── CodeReviewAgent/       
│   ├── GitHubSearchAgent/     
│   ├── WebSerarchAgent/       
│   └── WriteAPISpecAgent/     
└── setup-system.sh           # Automated setup script
```

### Running in Development Mode
#### Start Individual Components
1. **MCP Server**:
   ```bash
   ./start-mcp-server.sh
   # or manually:
   cd mcp-server && npm run dev
   ```
2. **React App**:
   ```bash
   ./start-react-app.sh
   # or manually:
   cd developer-assistant-app && npm start
   ```
3. **Workflow Agent**:
   ```bash
   ./start-workflow-agent.sh
   # or manually:
   cd Agents/WorkflowOrchestrationAgent
   source venv/bin/activate
   python orchestration_agent.py --server
   ```
#### Start Complete System
```bash
./start-all.sh
```

### Making Changes
1. **Backend Changes** (MCP Server):
   - Edit TypeScript files in `mcp-server/src/`
   - Rebuild with `npx tsc`
   - Restart server
2. **Frontend Changes** (React App):
   - Edit React components in `developer-assistant-app/src/`
   - Hot reload enabled in development mode
3. **Agent Changes** (Python):
   - Edit Python files in respective agent directories
   - Restart the specific agent or workflow orchestrator

---

## 🌐 API Reference

### MCP Server Tools
- `start_enhanced_workflow(spec, options)` - Start new workflow with approval gates
- `get_enhanced
├── Agents/                    # Python Agents
│   ├── WorkflowOrchestrationAgent/  # Main orchestration agent
│   ├── CodeGenerationAgent/   
│   ├── CodeCompilationAgent/  
│   ├── CodeReviewAgent/       
│   ├── GitHubSearchAgent/     
│   ├── WebSerarchAgent/       
│   └── WriteAPISpecAgent/     
└── setup-system.sh           # Automated setup script
```

### Running in Development Mode

#### Start Individual Components

1. **MCP Server**:
   ```bash
   ./start-mcp-server.sh
   # or manually:
   cd mcp-server && npm run dev
   ```

2. **React App**:
   ```bash
   ./start-react-app.sh
   # or manually:
   cd developer-assistant-app && npm start
   ```

3. **Workflow Agent**:
   ```bash
   ./start-workflow-agent.sh
   # or manually:
   cd Agents/WorkflowOrchestrationAgent
   source venv/bin/activate
   python orchestration_agent.py --server
   ```

#### Start Complete System
```bash
./start-all.sh
```

### Making Changes

1. **Backend Changes** (MCP Server):
   - Edit TypeScript files in `mcp-server/src/`
   - Rebuild with `npx tsc`
   - Restart server

2. **Frontend Changes** (React App):
   - Edit React components in `developer-assistant-app/src/`
   - Hot reload enabled in development mode

3. **Agent Changes** (Python):
   - Edit Python files in respective agent directories
   - Restart the specific agent or workflow orchestrator

## 🌐 API Reference

### MCP Server Tools

#### Enhanced Workflow Management
- `start_enhanced_workflow(spec, options)` - Start new workflow with approval gates
- `get_enhanced_workflow_status(workflow_id)` - Get detailed workflow status
- `approve_workflow_step(workflow_id, step_id, approved, feedback)` - Handle step approvals
- `get_workflow_templates()` - Get available workflow templates

#### API Specification
- `generate_api_spec(requirements, template)` - Generate API specifications
- `validate_api_spec(spec)` - Validate API specifications
- `get_api_templates()` - Get available API templates

### Workflow Agent API

#### HTTP Endpoints
- `POST /workflow/start` - Start new workflow
- `GET /workflow/{id}/status` - Get workflow status
- `POST /workflow/{id}/approve` - Approve workflow step
- `GET /workflows` - List all workflows
- `GET /templates` - Get workflow templates

### Agent Integration

Each agent exposes a standardized interface:
```python
class BaseAgent:
    def process(self, input_data: Dict) -> Dict
    def validate_input(self, input_data: Dict) -> bool
    def get_capabilities(self) -> Dict
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Default ports: React (3000), MCP Server (3001), Workflow Agent (8080)
   - Change ports in respective `.env` files

2. **Python Virtual Environment Issues**
   - Ensure Python 3.8+ is installed
   - Recreate virtual environments if needed:
     ```bash
     rm -rf venv
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```

3. **Node.js Dependencies**
   - Clear npm cache: `npm cache clean --force`
   - Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

4. **Database Issues**
   - Delete and recreate database:
     ```bash
     rm -f Agents/WorkflowOrchestrationAgent/data/workflows.db
     python orchestration_agent.py --init-db
     ```

### Logs and Debugging

- **MCP Server Logs**: Console output when running server
- **React App Logs**: Browser console and terminal output
- **Agent Logs**: Check `logs/` directory for agent-specific logs
- **Workflow Logs**: SQLite database contains execution history

### Performance Optimization

1. **Database Optimization**
   - Regular cleanup of old workflow data
   - Index optimization for large datasets

2. **Frontend Optimization**
   - Enable production builds for better performance
   - Use React DevTools for component profiling

3. **Agent Optimization**
   - Configure agent timeout settings
   - Implement caching for frequently used data

## 🤝 Contributing

1. **Fork the Repository**
2. **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow TypeScript/React best practices for frontend
- Use Python type hints for agent development
- Include tests for new functionality
- Update documentation for API changes
- Follow existing code style and conventions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- **Documentation**: This README and inline code comments
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for general questions

## 🔮 Roadmap

### Upcoming Features
- [ ] Advanced workflow templates
- [ ] Machine learning model integration
- [ ] Enhanced security and authentication
- [ ] Cloud deployment options
- [ ] Advanced analytics and reporting
- [ ] Plugin system for custom agents
- [ ] Multi-tenant support
- [ ] Real-time collaboration features

### Version History
- **v1.0.0** - Initial release with core workflow orchestration
- **v1.1.0** - Enhanced UI components and approval gates
- **v1.2.0** - Advanced agent integration and templates
- **v2.0.0** - Complete platform rewrite with improved architecture

---

**Built with ❤️ for developers, by developers**
