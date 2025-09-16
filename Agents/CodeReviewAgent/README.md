# Code Review Agent

A comprehensive Python-based code review agent that analyzes generated code for quality, security, maintainability, and best practices.

## Enhanced Features

### Context-Aware Review

The ReviewAgent now includes context from the code generation process:

- **Instruction Templates**: References the original instruction file used for generation
- **API Specifications**: Links to the API requirements that drove the generation
- **Traceability**: Full traceability from requirements through instruction templates to generated code

### Enhanced Reports

Reports now include:

```json
{
  "summary": {
    "total_files_reviewed": 6,
    "total_issues_found": 0,
    "review_context": {
      "instruction_file": "InstructionFiles/java_springboot.yml",
      "api_spec": "API-requirements/policy_management_spec.yml"
    }
  }
}
```

This provides complete traceability and context for code reviews, making it easier to:
- Understand the original requirements
- Validate that generated code meets specifications  
- Track changes and iterations
- Provide meaningful feedback in CI/CD pipelines

## Features

- **Multi-language Support**: Java, Python, JavaScript, and generic file analysis
- **Comprehensive Analysis**: Code quality, security patterns, documentation, complexity, and maintainability
- **Multiple Output Formats**: JSON, HTML, Markdown, and plain text reports
- **Configurable Rules**: Customizable analysis rules and thresholds
- **File Filtering**: Intelligent file discovery with ignore patterns
- **Detailed Reporting**: Issue categorization, severity levels, and actionable suggestions

## Installation

The ReviewAgent is part of the larger genaiagent project. No additional installation is required if you're using it within the project context.

## Usage

### Enhanced Workflow Mode (Recommended)

The ReviewAgent now supports the enhanced workflow that aligns with the code generation process:

```bash
# Review generated code with full context
python3 -m ReviewAgent.main \
  -i InstructionFiles/java_springboot.yml \
  -s API-requirements/policy_management_spec.yml \
  -p policy-generation

# Generate HTML report with context
python3 -m ReviewAgent.main \
  -i InstructionFiles/nodejs_express.yml \
  -s API-requirements/customer_update_spec.yml \
  -p customer-service \
  --format html \
  --output detailed_review.html

# Review with specific severity filtering
python3 -m ReviewAgent.main \
  -i InstructionFiles/java_springboot.yml \
  -s API-requirements/policy_management_spec.yml \
  -p policy-generation \
  --severity high \
  --verbose
```

### Enhanced Command Line Options

- `-i, --instruction-file`: Path to instruction template (e.g., `InstructionFiles/java_springboot.yml`)
- `-s, --api-spec`: Path to API requirements specification (e.g., `API-requirements/policy_management_spec.yml`)
- `-p, --project-path`: Path to generated source code project directory (e.g., `policy-generation`)
- `--output, -o`: Output file path (default: review_report.json)
- `--format, -f`: Output format - json, html, markdown, text (default: json)
- `--severity`: Minimum severity level - low, medium, high (default: medium)
- `--language`: Specific language to analyze - java, python, javascript, auto (default: auto)
- `--verbose, -v`: Enable verbose logging

### Legacy Mode

```bash
# Basic usage (legacy)
python3 -m ReviewAgent.main --source /path/to/generated/code --output review_report.json

# Generate an HTML report (legacy)
python3 -m ReviewAgent.main --source /path/to/code --format html --output report.html

# Review with specific severity threshold (legacy)
python3 -m ReviewAgent.main --source /path/to/code --severity medium --verbose
```

### Programmatic Usage

```python
from ReviewAgent.core.review_engine import ReviewEngine
from ReviewAgent.core.report_generator import ReportGenerator
from ReviewAgent.utils import FileScanner, LoggerConfig
from pathlib import Path

# Setup logging
LoggerConfig.setup_logging(level="INFO")

# Initialize components
scanner = FileScanner()
engine = ReviewEngine()
generator = ReportGenerator()

# Scan files
source_dir = Path("/path/to/code")
files = scanner.scan_directory(source_dir)

# Review files
results = engine.review_files(files)

# Generate report
output_path = Path("review_report.html")
generator.generate_html_report(results, output_path)
```

## Configuration

You can customize the review process using a configuration file:

```python
# Generate example configuration
python ReviewAgent/config_example.py config/my_config.json

# Use custom configuration
python -m ReviewAgent.main --source /path/to/code --rules config/my_config.json
```

### Configuration Options

- **Logging**: Level, output file, format customization
- **File Scanner**: Language filters, ignore patterns, file size limits
- **Analyzers**: Enable/disable specific rule categories
- **Thresholds**: Complexity, file size, line length limits
- **Output**: Report formats and content options

## Analysis Categories

### Java Analysis
- Naming conventions (classes, methods, variables)
- Exception handling patterns
- Spring Boot best practices
- Dependency injection usage
- Security vulnerabilities
- Code organization

### Python Analysis
- PEP 8 compliance
- Type hints usage
- Docstring quality
- Security patterns (eval/exec, credentials)
- Performance optimizations
- Import organization

### Generic Analysis
- Code quality issues (long lines, deep nesting)
- Magic numbers detection
- Duplicate code patterns
- Security patterns (hardcoded credentials, insecure URLs)
- Documentation completeness
- Complexity metrics

## Report Formats

### JSON Report
Structured data format suitable for integration with other tools:
```json
{
  "summary": {
    "total_files": 25,
    "total_issues": 42,
    "severity_breakdown": {...}
  },
  "files": [...],
  "metrics": {...}
}
```

### HTML Report
Rich, interactive web report with:
- Executive summary with charts
- File-by-file breakdown
- Issue categorization
- Code snippets with highlighting
- Actionable recommendations

### Markdown Report
Documentation-friendly format for README files and wikis.

### Text Report
Console-friendly plain text output for CI/CD pipelines.

## Integration

### CI/CD Pipeline
```yaml
# Example GitHub Actions step
- name: Code Review
  run: |
    python -m ReviewAgent.main \
      --source ./generated-code \
      --format json \
      --output review-results.json \
      --severity medium
    
    # Fail if high-severity issues found
    python -c "
    import json
    with open('review-results.json') as f:
        data = json.load(f)
    high_issues = data['summary']['severity_breakdown']['HIGH']
    exit(1 if high_issues > 0 else 0)
    "
```

### IDE Integration
The ReviewAgent can be integrated with VS Code or other IDEs through extensions or custom scripts.

## Architecture

```
ReviewAgent/
├── __init__.py              # Package initialization
├── main.py                  # CLI interface and orchestration
├── config_example.py        # Configuration examples
├── models/                  # Data models
│   ├── __init__.py
│   └── review_result.py     # Core data structures
├── core/                    # Core review engine
│   ├── __init__.py
│   ├── review_engine.py     # Main review orchestration
│   └── report_generator.py  # Multi-format report generation
├── analyzers/               # Language-specific analyzers
│   ├── __init__.py
│   ├── java_analyzer.py     # Java code analysis
│   ├── python_analyzer.py   # Python code analysis
│   └── generic_analyzer.py  # Generic file analysis
└── utils/                   # Utilities
    ├── __init__.py
    ├── file_scanner.py      # File discovery and filtering
    └── logger_config.py     # Logging configuration
```

## Contributing

When extending the ReviewAgent:

1. Add new analyzers in the `analyzers/` directory
2. Follow the existing analyzer interface pattern
3. Update the `ReviewEngine` to use new analyzers
4. Add appropriate tests and documentation
5. Update configuration examples

## License

This project is part of the genaiagent codebase. Please refer to the main project license.
