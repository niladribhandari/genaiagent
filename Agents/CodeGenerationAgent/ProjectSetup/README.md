# ProjectSetup - Enhanced CodeGenerationAgent Configuration

This folder contains all setup and configuration files for the Enhanced CodeGenerationAgent system.

## 📋 Setup Files

### Core Configuration
- **`pyproject.toml`** - Python project configuration with dependencies, build settings, and metadata
- **`setup.sh`** - Automated setup script for installing dependencies and configuring the environment
- **`Makefile`** - Build automation and common development tasks

## 🚀 Quick Setup

### Automated Setup
```bash
cd ProjectSetup
chmod +x setup.sh
./setup.sh
```

This will:
- Install Python dependencies
- Set up virtual environment (if needed)
- Configure development environment
- Validate installation

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Or using poetry (if available)
poetry install
```

## 🔧 Build Commands

### Using Makefile
```bash
cd ProjectSetup

# Install dependencies
make install

# Run tests
make test

# Build package
make build

# Clean build artifacts
make clean

# Format code
make format

# Lint code
make lint
```

## 📦 Dependencies

The system requires:

### Core Dependencies
- **Python 3.9+**
- **OpenAI** - AI provider integration
- **LangChain** - Advanced AI capabilities
- **PyYAML** - YAML specification parsing
- **Jinja2** - Template processing

### Development Dependencies
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Code linting
- **mypy** - Type checking

### Optional Dependencies
- **langchain-community** - Extended LangChain features
- **anthropic** - Alternative AI provider
- **chromadb** - Vector database for embeddings

## ⚙️ Configuration

### Environment Variables
```bash
# Required for AI functionality
export OPENAI_API_KEY="your_openai_api_key"

# Optional
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export LOG_LEVEL="INFO"
```

### Project Configuration (pyproject.toml)
- Python version requirements
- Dependency specifications
- Build system configuration
- Development tool settings

## 🔍 Validation

After setup, validate installation:

```bash
# Run component tests
cd ../ApplicationTest
python3 test_phase3_direct.py

# Run full integration test
python3 test_phase3_integration.py
```

Expected output:
```
🎉 All core components ready for Phase 3 integration testing!
🏆 PHASE 3 COMPLETE: Enhanced CodeGenerationAgent Ready!
```

## 🛠️ Development Environment

### Recommended Setup
1. **Python 3.9+** with virtual environment
2. **IDE with Python support** (VS Code, PyCharm, etc.)
3. **Git** for version control
4. **Docker** (optional) for containerized development

### IDE Configuration
- Enable type checking (mypy)
- Configure code formatting (black)
- Set up linting (flake8)
- Configure test runner (pytest)

## 📁 File Details

### pyproject.toml
```toml
[build-system]
requires = ["setuptools", "wheel"]

[project]
name = "enhanced-codegen-agent"
version = "3.0.0"
description = "AI-powered business-intelligent code generation system"

dependencies = [
    "openai>=1.0.0",
    "langchain>=0.1.0",
    "pyyaml>=6.0",
    "jinja2>=3.1.0"
]
```

### setup.sh
Automated setup script that:
- Checks Python version
- Creates virtual environment
- Installs dependencies
- Configures environment
- Runs validation tests

### Makefile
Common development tasks:
- `make install` - Install dependencies
- `make test` - Run test suite
- `make build` - Build package
- `make format` - Format code
- `make lint` - Lint code

## 🔄 Updates

To update the system:

```bash
cd ProjectSetup

# Update dependencies
pip install --upgrade -r requirements.txt

# Re-run setup
./setup.sh

# Validate update
cd ../ApplicationTest
python3 run_tests.py
```

## 🎯 Production Deployment

For production deployment:

1. **Environment Setup**: Configure production environment variables
2. **Dependency Installation**: Install only production dependencies
3. **Configuration Validation**: Verify all configurations
4. **Security Review**: Check API keys and permissions
5. **Performance Testing**: Run load tests
6. **Monitoring Setup**: Configure logging and monitoring

## 📞 Support

If you encounter setup issues:

1. **Check Prerequisites**: Verify Python version and system requirements
2. **Review Logs**: Check setup.sh output for error messages
3. **Validate Environment**: Ensure all environment variables are set
4. **Test Components**: Run individual component tests
5. **Consult Documentation**: Check the Documents/ folder for additional info
