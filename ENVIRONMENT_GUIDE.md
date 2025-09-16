# Environment Configuration Guide

## 📋 Overview

This guide covers the environment configuration for the GenAI Agent Platform. The system uses multiple environment files to configure different components securely and flexibly.

## 🗂️ Environment Files Structure

```
genaiagent/
├── .env.global                              # Global system configuration
├── mcp-server/.env                          # MCP Server configuration
├── developer-assistant-app/.env             # React App configuration
└── Agents/
    ├── WorkflowOrchestrationAgent/.env      # Workflow orchestration
    ├── CodeGenerationAgent/.env             # Code generation
    ├── CodeCompilationAgent/.env            # Code compilation
    ├── CodeReviewAgent/.env                 # Code review
    ├── GitHubSearchAgent/.env               # GitHub search
    ├── WebSerarchAgent/.env                 # Web search
    └── WriteAPISpecAgent/.env               # API specification
```

## 🔧 Quick Setup

### 1. Check Environment Status
```bash
./manage-env.sh status
```

### 2. Set API Keys Interactively
```bash
./manage-env.sh set-keys
```

### 3. Sync Global Variables
```bash
./manage-env.sh sync
```

## 🔑 Required API Keys

### OpenAI API Key (Recommended)
- **Purpose**: Powers AI features across multiple agents
- **Agents**: Code Generation, Code Review, API Spec Writing, Web Search (summarization)
- **How to get**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
- **Setup**: 
  ```bash
  # Set in .env.global
  OPENAI_API_KEY=sk-your-key-here
  ```

### GitHub Personal Access Token (Optional)
- **Purpose**: Enhanced GitHub search capabilities, higher rate limits
- **Agent**: GitHub Search Agent
- **How to get**: GitHub Settings → Developer settings → Personal access tokens
- **Permissions needed**: `public_repo`, `read:user`
- **Setup**:
  ```bash
  # Set in .env.global
  GITHUB_TOKEN=ghp_your-token-here
  ```

### Google Search API (Optional)
- **Purpose**: Enhanced web search capabilities
- **Agent**: Web Search Agent
- **How to get**: 
  1. [Google Cloud Console](https://console.cloud.google.com/)
  2. Enable Custom Search API
  3. Create Custom Search Engine
- **Setup**:
  ```bash
  # Set in .env.global
  GOOGLE_API_KEY=your-api-key-here
  GOOGLE_CSE_ID=your-search-engine-id
  ```

## 📁 Component-Specific Configuration

### MCP Server (.env)
```bash
# Core Configuration
PORT=3001                    # Server port
NODE_ENV=development         # Environment mode
DB_PATH=./data/workflows.db  # Database location

# Optional Features
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
LOG_LEVEL=info
AGENT_TIMEOUT=300000
MAX_CONCURRENT_WORKFLOWS=10
```

### React App (.env)
```bash
# Server URLs
REACT_APP_MCP_SERVER_URL=http://localhost:3001
REACT_APP_WORKFLOW_AGENT_URL=http://localhost:8080

# Build Configuration
GENERATE_SOURCEMAP=false
SKIP_PREFLIGHT_CHECK=true

# Feature Flags
REACT_APP_ENABLE_DEBUG_MODE=true
REACT_APP_ENABLE_WORKFLOW_TEMPLATES=true
```

### Workflow Orchestration Agent (.env)
```bash
# Server Configuration
PORT=8080
HOST=localhost
DEBUG=true

# Database
DB_PATH=./data/workflows.db

# Agent Paths (relative paths to other agents)
CODE_GENERATION_AGENT_PATH=../CodeGenerationAgent
CODE_COMPILATION_AGENT_PATH=../CodeCompilationAgent
# ... other agent paths
```

### Individual Agent Configuration

Each agent has its own `.env` file with specific settings:

#### Code Generation Agent
- Language support configuration
- Template directories
- Output formatting options
- Code validation settings

#### Code Compilation Agent
- Compiler paths and settings
- Build configurations
- Supported languages
- Error handling options

#### Code Review Agent
- Review criteria and weights
- Static analysis tool configuration
- Quality thresholds
- Report formatting

#### GitHub Search Agent
- Search filters and limits
- Repository criteria
- Content analysis settings
- Rate limiting configuration

#### Web Search Agent
- Search engine preferences
- Content processing options
- Domain filtering
- Summarization settings

#### API Spec Writing Agent
- Specification formats
- Template configuration
- Validation settings
- Documentation options

## 🛠️ Environment Management Commands

### Check Status
```bash
./manage-env.sh status
```
Shows the status of all environment files and API keys.

### Validate Configuration
```bash
./manage-env.sh validate
```
Validates all environment files for required variables.

### Sync Global Variables
```bash
./manage-env.sh sync
```
Syncs variables from `.env.global` to component files.

### Backup Environment Files
```bash
./manage-env.sh backup
```
Creates a timestamped backup of all environment files.

### Restore from Backup
```bash
./manage-env.sh restore env_backup_20250824_143022
```
Restores environment files from a backup directory.

### Set API Keys Interactively
```bash
./manage-env.sh set-keys
```
Interactive prompt to set API keys in the global configuration.

## 🔒 Security Best Practices

### 1. Never Commit API Keys
- All `.env` files are in `.gitignore`
- Use placeholder values in documentation
- Share keys securely via encrypted channels

### 2. Use Environment-Specific Configuration
- Different configurations for development/production
- Separate API keys for different environments
- Monitor API usage and set appropriate limits

### 3. Regular Key Rotation
- Rotate API keys periodically
- Monitor for unauthorized usage
- Use minimal required permissions

### 4. Backup Configuration
- Regular backups of environment files
- Secure storage of backup files
- Document configuration changes

## 🚨 Troubleshooting

### Missing Environment Files
```bash
# Check which files are missing
./manage-env.sh status

# Recreate missing files by running setup
./setup-system.sh
```

### Invalid Configuration
```bash
# Validate all files
./manage-env.sh validate

# Check specific component logs
tail -f logs/mcp-server.log
tail -f logs/orchestration.log
```

### API Key Issues
```bash
# Check if keys are set
./manage-env.sh status

# Set keys interactively
./manage-env.sh set-keys

# Manually edit global file
nano .env.global
```

### Port Conflicts
```bash
# Check which ports are in use
lsof -i :3000
lsof -i :3001
lsof -i :8080

# Change ports in respective .env files
# Update CORS_ORIGINS accordingly
```

## 📝 Environment Variables Reference

### Global Variables (Synced Across Components)
- `OPENAI_API_KEY` - OpenAI API access
- `OPENAI_MODEL` - Default AI model
- `GITHUB_TOKEN` - GitHub API access
- `LOG_LEVEL` - Logging verbosity
- `ENABLE_DEBUG_MODE` - Debug features

### Port Configuration
- `MCP_SERVER_PORT=3001` - MCP Server
- `REACT_APP_PORT=3000` - React App
- `WORKFLOW_AGENT_PORT=8080` - Workflow Agent

### Database Configuration
- `DB_TYPE=sqlite` - Database type
- `DB_PATH=./data/workflows.db` - Database location
- `ENABLE_DB_LOGGING=false` - Database query logging

### Feature Flags
- `ENABLE_WORKFLOW_TEMPLATES=true` - Template system
- `ENABLE_APPROVAL_GATES=true` - User approval gates
- `ENABLE_AUDIT_TRAIL=true` - Activity logging
- `ENABLE_METRICS=true` - Performance metrics

## 🎯 Production Deployment

### Environment Preparation
1. **Create production environment files**:
   ```bash
   cp .env.global .env.production
   # Edit production-specific values
   ```

2. **Set production API keys**:
   ```bash
   # Use production OpenAI API key
   # Use production GitHub token
   # Configure production database
   ```

3. **Update URLs and ports**:
   ```bash
   # Update all localhost URLs to production domains
   # Configure reverse proxy settings
   # Set up SSL certificates
   ```

### Security Checklist
- [ ] All API keys are production-ready
- [ ] Database credentials are secure
- [ ] CORS origins are restricted
- [ ] Debug mode is disabled
- [ ] Logging levels are appropriate
- [ ] Rate limiting is configured
- [ ] Health checks are enabled

## 📞 Support

If you encounter issues with environment configuration:

1. **Check the status**: `./manage-env.sh status`
2. **Validate configuration**: `./manage-env.sh validate`
3. **Review logs**: Check `logs/` directory for error messages
4. **Backup and restore**: Use backup/restore functions if needed
5. **Recreate files**: Run `./setup-system.sh` to regenerate files

For additional help, refer to the main [README.md](README.md) or create an issue in the project repository.
