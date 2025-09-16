# Fix Compilation Issues Agent

## Overview

The FixCompilationIssuesAgent is designed to automatically analyze and fix compilation errors in Java Spring Boot projects. It uses OpenAI to understand compilation errors and generate appropriate fixes.

## Features

- **Error Analysis**: Parses compilation errors and identifies root causes
- **Intelligent Fixes**: Uses AI to generate context-aware fixes for compilation issues
- **File Modification**: Applies fixes directly to source files
- **Backup Creation**: Creates backups before making changes
- **Fix Reporting**: Provides detailed reports of changes made

## Usage

### Command Line
```bash
python main_agentic.py --project-path "/path/to/project" --compilation-errors "error_data.json"
```

### Programmatic Usage
```python
from fix_compilation_agent import FixCompilationIssuesAgent

agent = FixCompilationIssuesAgent()
result = agent.fix_compilation_issues(
    project_path="/path/to/project",
    errors=compilation_errors
)
```

## Configuration

The agent requires:
- OpenAI API key (set via OPENAI_API_KEY environment variable)
- Project path
- Compilation error data

## Output

Returns a structured result containing:
- Fixed files list
- Applied changes summary
- Remaining errors (if any)
- Backup locations
