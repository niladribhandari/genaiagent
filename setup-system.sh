#!/bin/bash

# Complete System Setup Script for GenAI Agent Platform
# This script sets up the MCP server, React app, and all agents

set -e

echo "🚀 Setting up GenAI Agent Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ from https://python.org/"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        print_error "Node.js version 16+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python 3.8+ is required. Current version: $(python3 --version)"
        exit 1
    fi
    
    print_success "All requirements satisfied"
}

# Setup MCP Server
setup_mcp_server() {
    print_status "Setting up MCP Server..."
    
    cd mcp-server
    
    # Install dependencies
    print_status "Installing MCP server dependencies..."
    npm install
    
    # Build TypeScript
    print_status "Building TypeScript..."
    npx tsc
    
    print_success "MCP Server setup complete"
    cd ..
}

# Setup React App
setup_react_app() {
    print_status "Setting up React App..."
    
    cd developer-assistant-app
    
    # Install dependencies
    print_status "Installing React app dependencies..."
    npm install
    
    # Build the app
    print_status "Building React app..."
    npm run build
    
    print_success "React App setup complete"
    cd ..
}

# Setup Python Agents
setup_python_agents() {
    print_status "Setting up Python Agents..."
    
    # Setup WorkflowOrchestrationAgent
    if [ -d "Agents/WorkflowOrchestrationAgent" ]; then
        cd Agents/WorkflowOrchestrationAgent
        print_status "Setting up Workflow Orchestration Agent..."
        
        # Create virtual environment
        python3 -m venv venv
        source venv/bin/activate
        
        # Install dependencies
        pip install -r requirements.txt
        
        # Initialize database
        python orchestration_agent.py --init-db
        
        deactivate
        cd ../..
        print_success "Workflow Orchestration Agent setup complete"
    fi
    
    # Setup other agents
    for agent_dir in Agents/*/; do
        if [ -d "$agent_dir" ] && [ -f "$agent_dir/requirements.txt" ]; then
            agent_name=$(basename "$agent_dir")
            if [ "$agent_name" != "WorkflowOrchestrationAgent" ]; then
                print_status "Setting up $agent_name..."
                cd "$agent_dir"
                
                # Create virtual environment if it doesn't exist
                if [ ! -d "venv" ]; then
                    python3 -m venv venv
                fi
                
                source venv/bin/activate
                pip install -r requirements.txt
                deactivate
                
                cd - > /dev/null
                print_success "$agent_name setup complete"
            fi
        fi
    done
}

# Create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # MCP Server startup script
    cat > start-mcp-server.sh << 'EOF'
#!/bin/bash
echo "Starting MCP Server..."
cd mcp-server
npm start
EOF
    chmod +x start-mcp-server.sh
    
    # React App startup script
    cat > start-react-app.sh << 'EOF'
#!/bin/bash
echo "Starting React App..."
cd developer-assistant-app
npm start
EOF
    chmod +x start-react-app.sh
    
    # Workflow Agent startup script
    cat > start-workflow-agent.sh << 'EOF'
#!/bin/bash
echo "Starting Workflow Orchestration Agent..."
cd Agents/WorkflowOrchestrationAgent
source venv/bin/activate
python orchestration_agent.py --server
EOF
    chmod +x start-workflow-agent.sh
    
    # Complete system startup script
    cat > start-all.sh << 'EOF'
#!/bin/bash
echo "Starting complete GenAI Agent Platform..."

# Start MCP Server in background
echo "Starting MCP Server..."
cd mcp-server
npm start &
MCP_PID=$!
cd ..

# Wait a moment for MCP server to start
sleep 3

# Start Workflow Agent in background
echo "Starting Workflow Orchestration Agent..."
cd Agents/WorkflowOrchestrationAgent
source venv/bin/activate
python orchestration_agent.py --server &
WORKFLOW_PID=$!
cd ../..

# Wait a moment for workflow agent to start
sleep 3

# Start React App (this will block)
echo "Starting React App..."
cd developer-assistant-app
npm start &
REACT_PID=$!

# Function to handle cleanup on script exit
cleanup() {
    echo "Shutting down services..."
    kill $MCP_PID 2>/dev/null || true
    kill $WORKFLOW_PID 2>/dev/null || true
    kill $REACT_PID 2>/dev/null || true
    echo "All services stopped."
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Wait for React app (main process)
wait $REACT_PID
EOF
    chmod +x start-all.sh
    
    print_success "Startup scripts created"
}

# Create environment configuration
create_env_config() {
    print_status "Creating environment configuration..."
    
    # MCP Server environment
    if [ ! -f "mcp-server/.env" ]; then
        cat > mcp-server/.env << 'EOF'
# MCP Server Configuration
PORT=3001
NODE_ENV=development

# OpenAI Configuration (optional)
# OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DB_PATH=./data/workflows.db
EOF
        print_success "Created MCP server .env file"
    else
        print_warning "MCP server .env file already exists"
    fi
    
    # React App environment
    if [ ! -f "developer-assistant-app/.env" ]; then
        cat > developer-assistant-app/.env << 'EOF'
# React App Configuration
REACT_APP_MCP_SERVER_URL=http://localhost:3001
REACT_APP_WORKFLOW_AGENT_URL=http://localhost:8080
GENERATE_SOURCEMAP=false
EOF
        print_success "Created React app .env file"
    else
        print_warning "React app .env file already exists"
    fi
    
    # Workflow Agent environment
    if [ ! -f "Agents/WorkflowOrchestrationAgent/.env" ]; then
        cat > Agents/WorkflowOrchestrationAgent/.env << 'EOF'
# Workflow Orchestration Agent Configuration
PORT=8080
HOST=localhost
DEBUG=true

# Database Configuration
DB_PATH=./data/workflows.db

# Agent Paths (relative to this agent's directory)
CODE_GENERATION_AGENT_PATH=../CodeGenerationAgent
CODE_COMPILATION_AGENT_PATH=../CodeCompilationAgent
CODE_REVIEW_AGENT_PATH=../CodeReviewAgent
GITHUB_SEARCH_AGENT_PATH=../GitHubSearchAgent
WEB_SEARCH_AGENT_PATH=../WebSerarchAgent
API_SPEC_AGENT_PATH=../WriteAPISpecAgent

# OpenAI Configuration (if using)
# OPENAI_API_KEY=your_openai_api_key_here
EOF
        print_success "Created Workflow Agent .env file"
    else
        print_warning "Workflow Agent .env file already exists"
    fi
}

# Create data directories
create_directories() {
    print_status "Creating data directories..."
    
    mkdir -p mcp-server/data
    mkdir -p Agents/WorkflowOrchestrationAgent/data
    mkdir -p logs
    
    print_success "Data directories created"
}

# Main setup function
main() {
    echo "🔧 GenAI Agent Platform Setup"
    echo "=============================="
    echo ""
    
    # Get current directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    cd "$SCRIPT_DIR"
    
    # Run setup steps
    check_requirements
    echo ""
    
    create_directories
    echo ""
    
    create_env_config
    echo ""
    
    setup_mcp_server
    echo ""
    
    setup_react_app
    echo ""
    
    setup_python_agents
    echo ""
    
    create_startup_scripts
    echo ""
    
    print_success "🎉 Setup complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Configure your .env files with appropriate API keys and settings"
    echo "2. Start the complete system with: ./start-all.sh"
    echo "3. Or start components individually:"
    echo "   - MCP Server: ./start-mcp-server.sh"
    echo "   - React App: ./start-react-app.sh"
    echo "   - Workflow Agent: ./start-workflow-agent.sh"
    echo ""
    echo "🌐 Access Points:"
    echo "- React App: http://localhost:3000"
    echo "- MCP Server: http://localhost:3001"
    echo "- Workflow Agent: http://localhost:8080"
    echo ""
    echo "📚 Documentation: See README.md for detailed usage instructions"
    echo ""
}

# Run main function
main "$@"
