#!/bin/bash

# AgenticAI Code Generation System - Development Setup Script
# =============================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
VENV_NAME="venv"
PROJECT_NAME="AgenticAI Code Generation System"

# Functions
print_header() {
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${BLUE}  $PROJECT_NAME - Development Setup${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

check_python_version() {
    print_step "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python $PYTHON_MIN_VERSION or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    print_info "Found Python $PYTHON_VERSION"
    
    if [[ $(echo "$PYTHON_VERSION $PYTHON_MIN_VERSION" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
        print_error "Python $PYTHON_MIN_VERSION or higher is required. Found $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python version check passed"
}

create_virtual_environment() {
    print_step "Creating virtual environment..."
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment already exists. Removing and recreating..."
        rm -rf "$VENV_NAME"
    fi
    
    python3 -m venv "$VENV_NAME"
    print_success "Virtual environment created: $VENV_NAME"
}

activate_virtual_environment() {
    print_step "Activating virtual environment..."
    source "$VENV_NAME/bin/activate"
    print_info "Virtual environment activated"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
}

install_dependencies() {
    print_step "Installing dependencies..."
    
    # Install development dependencies
    print_info "Installing development dependencies..."
    pip install -e ".[dev,docs]"
    
    print_success "Dependencies installed successfully"
}

setup_pre_commit_hooks() {
    print_step "Setting up pre-commit hooks..."
    
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        print_success "Pre-commit hooks installed"
    else
        print_info "Installing pre-commit..."
        pip install pre-commit
        pre-commit install
        print_success "Pre-commit installed and hooks set up"
    fi
}

create_development_directories() {
    print_step "Creating development directories..."
    
    mkdir -p generated_examples
    mkdir -p logs
    mkdir -p .agentic_cache
    
    print_success "Development directories created"
}

run_initial_tests() {
    print_step "Running initial tests..."
    
    if make test > /dev/null 2>&1; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed. Run 'make test' for details."
    fi
}

setup_development_config() {
    print_step "Setting up development configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.development .env
        print_info "Development environment configuration copied to .env"
    else
        print_info "Environment configuration already exists"
    fi
}

display_completion_message() {
    echo
    echo -e "${GREEN}=======================================================${NC}"
    echo -e "${GREEN}  Setup Complete!${NC}"
    echo -e "${GREEN}=======================================================${NC}"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Activate the virtual environment:"
    echo -e "     ${YELLOW}source $VENV_NAME/bin/activate${NC}"
    echo
    echo -e "  2. Run tests to verify setup:"
    echo -e "     ${YELLOW}make test${NC}"
    echo
    echo -e "  3. Try the demo:"
    echo -e "     ${YELLOW}make demo${NC}"
    echo
    echo -e "  4. View available commands:"
    echo -e "     ${YELLOW}make help${NC}"
    echo
    echo -e "  5. Start developing with AgenticAI!"
    echo
    echo -e "${BLUE}Quick development workflow:${NC}"
    echo -e "  • ${YELLOW}make dev-setup${NC} - Complete development setup"
    echo -e "  • ${YELLOW}make pre-commit${NC} - Run all pre-commit checks"
    echo -e "  • ${YELLOW}make quick-test${NC} - Quick test run"
    echo -e "  • ${YELLOW}make format${NC} - Format code"
    echo -e "  • ${YELLOW}make clean${NC} - Clean build artifacts"
    echo
}

# Main execution
main() {
    print_header
    
    check_python_version
    create_virtual_environment
    activate_virtual_environment
    install_dependencies
    setup_development_config
    create_development_directories
    setup_pre_commit_hooks
    run_initial_tests
    
    display_completion_message
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --help, -h    Show this help message"
        echo "  --clean       Clean existing setup and start fresh"
        exit 0
        ;;
    --clean)
        print_info "Cleaning existing setup..."
        rm -rf "$VENV_NAME" generated_examples logs .agentic_cache .env
        print_success "Cleanup complete"
        ;;
esac

# Run main function
main
