#!/bin/bash

# Python Dependency Fix Script
# This script fixes common Python dependency issues in the GenAI Agent Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check Python version
check_python_version() {
    print_status "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ from https://python.org/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python version: $PYTHON_VERSION"
}

# Function to upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    python3 -m pip install --upgrade pip
    print_success "Pip upgraded successfully"
}

# Function to install wheel and setuptools
install_build_tools() {
    print_status "Installing build tools..."
    python3 -m pip install --upgrade setuptools wheel
    print_success "Build tools installed"
}

# Function to fix requirements files
fix_requirements_files() {
    print_status "Checking and fixing requirements files..."
    
    # List of agents to check
    agents=(
        "WorkflowOrchestrationAgent"
        "CodeCompilationAgent"
        "CodeReviewAgent"
        "GitHubSearchAgent"
        "WebSerarchAgent"
        "WriteAPISpecAgent"
    )
    
    for agent in "${agents[@]}"; do
        req_file="Agents/$agent/requirements.txt"
        if [ -f "$req_file" ]; then
            print_status "Checking $agent requirements..."
            
            # Remove problematic dependencies
            if grep -q "sqlite3" "$req_file"; then
                print_warning "Removing sqlite3 from $agent (built into Python)"
                sed -i.bak '/^sqlite3/d' "$req_file"
                rm -f "$req_file.bak"
            fi
            
            if grep -q "asyncio==" "$req_file"; then
                print_warning "Removing specific asyncio version from $agent (built into Python)"
                sed -i.bak '/^asyncio==/d' "$req_file"
                rm -f "$req_file.bak"
            fi
            
            print_success "$agent requirements checked"
        else
            print_warning "Requirements file not found for $agent: $req_file"
        fi
    done
}

# Function to create virtual environments
create_virtual_environments() {
    print_status "Creating virtual environments for agents..."
    
    agents=(
        "WorkflowOrchestrationAgent"
        "CodeCompilationAgent"
        "CodeReviewAgent"
        "GitHubSearchAgent"
        "WebSerarchAgent"
        "WriteAPISpecAgent"
    )
    
    for agent in "${agents[@]}"; do
        agent_dir="Agents/$agent"
        if [ -d "$agent_dir" ] && [ -f "$agent_dir/requirements.txt" ]; then
            print_status "Setting up virtual environment for $agent..."
            
            cd "$agent_dir"
            
            # Remove existing virtual environment if it exists
            if [ -d "venv" ]; then
                print_status "Removing existing virtual environment for $agent"
                rm -rf venv
            fi
            
            # Create new virtual environment
            python3 -m venv venv
            
            # Activate virtual environment and install dependencies
            source venv/bin/activate
            
            # Upgrade pip in the virtual environment
            pip install --upgrade pip setuptools wheel
            
            # Install requirements with better error handling
            if pip install -r requirements.txt; then
                print_success "$agent dependencies installed successfully"
            else
                print_error "Failed to install some dependencies for $agent"
                print_status "Trying to install with --no-deps flag for problematic packages..."
                
                # Try installing without dependencies for problematic packages
                pip install -r requirements.txt --no-deps || true
            fi
            
            deactivate
            cd - > /dev/null
        else
            print_warning "Skipping $agent (no requirements.txt found)"
        fi
    done
}

# Function to test imports
test_imports() {
    print_status "Testing Python imports..."
    
    agents=(
        "WorkflowOrchestrationAgent"
    )
    
    for agent in "${agents[@]}"; do
        agent_dir="Agents/$agent"
        if [ -d "$agent_dir" ] && [ -d "$agent_dir/venv" ]; then
            print_status "Testing imports for $agent..."
            
            cd "$agent_dir"
            source venv/bin/activate
            
            # Test basic imports
            if python -c "import sqlite3; print('sqlite3 import: OK')" 2>/dev/null; then
                print_success "$agent: sqlite3 import successful"
            else
                print_error "$agent: sqlite3 import failed"
            fi
            
            if python -c "import asyncio; print('asyncio import: OK')" 2>/dev/null; then
                print_success "$agent: asyncio import successful"
            else
                print_error "$agent: asyncio import failed"
            fi
            
            deactivate
            cd - > /dev/null
        fi
    done
}

# Function to install alternative packages
install_alternatives() {
    print_status "Installing alternative packages for common issues..."
    
    # For agents that might need specific SQLite functionality
    agents_needing_sqlite=(
        "WorkflowOrchestrationAgent"
    )
    
    for agent in "${agents_needing_sqlite[@]}"; do
        agent_dir="Agents/$agent"
        if [ -d "$agent_dir" ] && [ -d "$agent_dir/venv" ]; then
            print_status "Installing SQLite alternatives for $agent..."
            
            cd "$agent_dir"
            source venv/bin/activate
            
            # Install aiosqlite for async SQLite operations
            pip install aiosqlite>=0.19.0
            
            deactivate
            cd - > /dev/null
            
            print_success "SQLite alternatives installed for $agent"
        fi
    done
}

# Main function
main() {
    echo "🔧 Python Dependency Fix Script"
    echo "==============================="
    echo ""
    
    # Get current directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    cd "$SCRIPT_DIR"
    
    # Run fix steps
    check_python_version
    echo ""
    
    upgrade_pip
    echo ""
    
    install_build_tools
    echo ""
    
    fix_requirements_files
    echo ""
    
    create_virtual_environments
    echo ""
    
    install_alternatives
    echo ""
    
    test_imports
    echo ""
    
    print_success "🎉 Python dependency fixes complete!"
    echo ""
    echo "Next steps:"
    echo "1. Try running the setup script again: ./setup-system.sh"
    echo "2. If issues persist, check individual agent logs"
    echo "3. For CodeGenerationAgent, use: cd Agents/CodeGenerationAgent && pip install -e ."
    echo ""
}

# Run main function
main "$@"
