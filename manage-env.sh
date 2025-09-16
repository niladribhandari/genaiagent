#!/bin/bash

# Environment Configuration Management Script
# This script helps manage environment files across all projects

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

# Function to check if .env file exists
check_env_file() {
    local file_path=$1
    local component_name=$2
    
    if [ -f "$file_path" ]; then
        print_success "$component_name environment file exists: $file_path"
        return 0
    else
        print_error "$component_name environment file missing: $file_path"
        return 1
    fi
}

# Function to validate environment file content
validate_env_file() {
    local file_path=$1
    local component_name=$2
    
    if [ ! -f "$file_path" ]; then
        print_error "File not found: $file_path"
        return 1
    fi
    
    # Check for common required variables
    local required_vars=()
    case "$component_name" in
        "MCP Server")
            required_vars=("PORT" "NODE_ENV" "DB_PATH")
            ;;
        "React App")
            required_vars=("REACT_APP_MCP_SERVER_URL" "REACT_APP_WORKFLOW_AGENT_URL")
            ;;
        "Workflow Agent")
            required_vars=("PORT" "HOST" "DB_PATH")
            ;;
        *)
            required_vars=("AGENT_NAME" "AGENT_VERSION")
            ;;
    esac
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$file_path" && ! grep -q "^# $var=" "$file_path"; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_success "$component_name environment file is valid"
        return 0
    else
        print_warning "$component_name environment file missing variables: ${missing_vars[*]}"
        return 1
    fi
}

# Function to copy global environment variables to component files
sync_global_vars() {
    local global_file=".env.global"
    
    if [ ! -f "$global_file" ]; then
        print_error "Global environment file not found: $global_file"
        return 1
    fi
    
    print_status "Syncing global environment variables..."
    
    # Extract global variables that should be synced
    local global_vars=(
        "OPENAI_API_KEY"
        "OPENAI_MODEL"
        "GITHUB_TOKEN"
        "LOG_LEVEL"
        "ENABLE_DEBUG_MODE"
    )
    
    for var in "${global_vars[@]}"; do
        local value=$(grep "^$var=" "$global_file" 2>/dev/null | cut -d'=' -f2- || echo "")
        if [ -n "$value" ]; then
            print_status "Syncing $var to component files..."
            
            # Update each component's .env file
            for env_file in mcp-server/.env developer-assistant-app/.env Agents/*/.env; do
                if [ -f "$env_file" ]; then
                    if grep -q "^$var=" "$env_file"; then
                        # Update existing variable
                        sed -i.bak "s/^$var=.*/$var=$value/" "$env_file"
                        rm -f "$env_file.bak"
                    elif grep -q "^# $var=" "$env_file"; then
                        # Uncomment and update
                        sed -i.bak "s/^# $var=.*/$var=$value/" "$env_file"
                        rm -f "$env_file.bak"
                    fi
                fi
            done
        fi
    done
    
    print_success "Global variable sync complete"
}

# Function to create backup of all environment files
backup_env_files() {
    local backup_dir="env_backup_$(date +%Y%m%d_%H%M%S)"
    print_status "Creating backup of environment files in $backup_dir..."
    
    mkdir -p "$backup_dir"
    
    # Backup all .env files
    find . -name ".env*" -type f | while read -r file; do
        local relative_path=$(dirname "$file")
        mkdir -p "$backup_dir/$relative_path"
        cp "$file" "$backup_dir/$file"
    done
    
    print_success "Backup created in $backup_dir"
}

# Function to restore environment files from backup
restore_env_files() {
    local backup_dir=$1
    
    if [ -z "$backup_dir" ]; then
        print_error "Please specify backup directory"
        return 1
    fi
    
    if [ ! -d "$backup_dir" ]; then
        print_error "Backup directory not found: $backup_dir"
        return 1
    fi
    
    print_status "Restoring environment files from $backup_dir..."
    
    find "$backup_dir" -name ".env*" -type f | while read -r file; do
        local target_file=${file#$backup_dir/}
        local target_dir=$(dirname "$target_file")
        mkdir -p "$target_dir"
        cp "$file" "$target_file"
        print_status "Restored: $target_file"
    done
    
    print_success "Environment files restored from backup"
}

# Function to set API keys interactively
set_api_keys() {
    print_status "Setting API keys interactively..."
    
    # OpenAI API Key
    echo -n "Enter OpenAI API Key (leave empty to skip): "
    read -r openai_key
    if [ -n "$openai_key" ]; then
        # Update global file
        if grep -q "^# OPENAI_API_KEY=" ".env.global"; then
            sed -i.bak "s/^# OPENAI_API_KEY=.*/OPENAI_API_KEY=$openai_key/" ".env.global"
        else
            echo "OPENAI_API_KEY=$openai_key" >> ".env.global"
        fi
        print_success "OpenAI API key set"
    fi
    
    # GitHub Token
    echo -n "Enter GitHub Personal Access Token (leave empty to skip): "
    read -r github_token
    if [ -n "$github_token" ]; then
        # Update global file
        if grep -q "^# GITHUB_TOKEN=" ".env.global"; then
            sed -i.bak "s/^# GITHUB_TOKEN=.*/GITHUB_TOKEN=$github_token/" ".env.global"
        else
            echo "GITHUB_TOKEN=$github_token" >> ".env.global"
        fi
        print_success "GitHub token set"
    fi
    
    # Google API Key
    echo -n "Enter Google API Key for search (leave empty to skip): "
    read -r google_key
    if [ -n "$google_key" ]; then
        # Update global file
        if grep -q "^# GOOGLE_API_KEY=" ".env.global"; then
            sed -i.bak "s/^# GOOGLE_API_KEY=.*/GOOGLE_API_KEY=$google_key/" ".env.global"
        else
            echo "GOOGLE_API_KEY=$google_key" >> ".env.global"
        fi
        print_success "Google API key set"
    fi
    
    # Sync to component files
    sync_global_vars
    
    print_success "API keys configuration complete"
}

# Function to show environment status
show_env_status() {
    echo "Environment Configuration Status"
    echo "==============================="
    echo ""
    
    # Define all environment files
    local env_files=(
        ".env.global:Global Configuration"
        "mcp-server/.env:MCP Server"
        "developer-assistant-app/.env:React App"
        "Agents/WorkflowOrchestrationAgent/.env:Workflow Agent"
        "Agents/CodeGenerationAgent/.env:Code Generation Agent"
        "Agents/CodeCompilationAgent/.env:Code Compilation Agent"
        "Agents/CodeReviewAgent/.env:Code Review Agent"
        "Agents/GitHubSearchAgent/.env:GitHub Search Agent"
        "Agents/WebSerarchAgent/.env:Web Search Agent"
        "Agents/WriteAPISpecAgent/.env:API Spec Agent"
    )
    
    local total_files=${#env_files[@]}
    local valid_files=0
    
    for env_entry in "${env_files[@]}"; do
        local file_path=${env_entry%%:*}
        local component_name=${env_entry##*:}
        
        echo -n "Checking $component_name... "
        if check_env_file "$file_path" "$component_name" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            if validate_env_file "$file_path" "$component_name" >/dev/null 2>&1; then
                valid_files=$((valid_files + 1))
            fi
        else
            echo -e "${RED}✗${NC}"
        fi
    done
    
    echo ""
    echo "Status: $valid_files/$total_files environment files are valid"
    
    # Check for API keys
    echo ""
    echo "API Keys Status:"
    echo "==============="
    
    if grep -q "^OPENAI_API_KEY=" ".env.global" 2>/dev/null; then
        echo -e "OpenAI API Key: ${GREEN}Set${NC}"
    else
        echo -e "OpenAI API Key: ${YELLOW}Not Set${NC}"
    fi
    
    if grep -q "^GITHUB_TOKEN=" ".env.global" 2>/dev/null; then
        echo -e "GitHub Token: ${GREEN}Set${NC}"
    else
        echo -e "GitHub Token: ${YELLOW}Not Set${NC}"
    fi
    
    if grep -q "^GOOGLE_API_KEY=" ".env.global" 2>/dev/null; then
        echo -e "Google API Key: ${GREEN}Set${NC}"
    else
        echo -e "Google API Key: ${YELLOW}Not Set${NC}"
    fi
}

# Main function
main() {
    echo "🔧 Environment Configuration Manager"
    echo "===================================="
    echo ""
    
    case "${1:-status}" in
        "status")
            show_env_status
            ;;
        "validate")
            print_status "Validating all environment files..."
            show_env_status
            ;;
        "sync")
            sync_global_vars
            ;;
        "backup")
            backup_env_files
            ;;
        "restore")
            restore_env_files "$2"
            ;;
        "set-keys")
            set_api_keys
            ;;
        "help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  status      Show environment configuration status (default)"
            echo "  validate    Validate all environment files"
            echo "  sync        Sync global variables to component files"
            echo "  backup      Create backup of all environment files"
            echo "  restore     Restore environment files from backup"
            echo "  set-keys    Set API keys interactively"
            echo "  help        Show this help message"
            echo ""
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
