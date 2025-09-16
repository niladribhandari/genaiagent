# Code Compilation Agent

A comprehensive multi-language code compilation system that supports Java Spring Boot, .NET API, Python API, and Node.js API projects. The agent automatically detects project types, handles compilation processes, and provides detailed issue reporting.

## 🎯 Features

### Supported Project Types
- **Java Spring Boot** ✅ (Fully implemented)
  - Maven-based projects
  - Gradle-based projects (with wrapper support)
  - Auto-detection of Spring Boot applications
  - Comprehensive error parsing
- **.NET API** 🚧 (Planned)
- **Python API** 🚧 (Planned)  
- **Node.js API** 🚧 (Planned)

### Key Capabilities
- **Auto-detection** of project types based on build files
- **Detailed error reporting** with file locations and line numbers
- **Flexible build options** (custom goals, skip tests, timeouts)
- **Tool availability checking** (Maven, Gradle, etc.)
- **Compilation time tracking**
- **Structured issue classification** (errors vs warnings)
- **Build log capture** and analysis
- **Report generation** in human-readable and JSON formats

## 🚀 Quick Start

### Basic Usage

```python
from src.compilation_agent import CodeCompilationAgent, ProjectType

# Initialize the agent
agent = CodeCompilationAgent(config={
    "verbose": True,
    "timeout": 300
})

# Compile a Java Spring Boot project
result = agent.compile_project(
    project_path="/path/to/your/springboot/project",
    project_type=ProjectType.JAVA_SPRINGBOOT
)

# Check results
if result.status == CompilationStatus.SUCCESS:
    print("✅ Compilation successful!")
else:
    print(f"❌ Compilation failed with {len(result.get_errors())} errors")
    
# Generate detailed report
report = agent.generate_compilation_report(result)
print(report)
```

### Quick Functions

```python
from src.compilation_agent import compile_java_springboot, get_project_info

# Quick compilation
result = compile_java_springboot("/path/to/project", skip_tests=True)

# Quick project info
info = get_project_info("/path/to/project")
print(f"Project type: {info['project_type']}")
print(f"Source files: {info['source_files_count']}")
```

### Command Line Interface

```bash
# Basic compilation
python compile_cli.py /path/to/springboot/project

# With custom options
python compile_cli.py /path/to/project --skip-tests --verbose

# Maven-specific goals
python compile_cli.py /path/to/project --goals clean,compile,test

# Get project info only
python compile_cli.py /path/to/project --info-only

# Save detailed report
python compile_cli.py /path/to/project --report compilation_report.txt

# JSON output
python compile_cli.py /path/to/project --json-output
```

## 📁 Project Structure

```
CodeCompilation/
├── src/
│   └── compilation_agent.py      # Main compilation agent
├── demo_compilation.py           # Demo and examples
├── compile_cli.py                # Command line interface
└── README.md                     # This file
```

## 🔧 Configuration

### Agent Configuration

```python
config = {
    "verbose": True,           # Enable detailed output
    "timeout": 300,           # Compilation timeout (seconds)
    "cleanup_artifacts": False, # Clean up build artifacts after compilation
    
    # Tool paths (auto-detected if not specified)
    "maven_path": "mvn",
    "gradle_path": "gradle", 
    "dotnet_path": "dotnet",
    "python_path": "python3",
    "npm_path": "npm"
}

agent = CodeCompilationAgent(config=config)
```

### Build Options

#### Java Spring Boot (Maven)
```python
build_options = {
    "goals": ["clean", "compile", "test"],  # Maven goals
    "skip_tests": True,                     # Skip test execution
    "args": ["-q", "-DskipTests"]          # Additional Maven arguments
}
```

#### Java Spring Boot (Gradle)
```python
build_options = {
    "tasks": ["clean", "build"],           # Gradle tasks
    "skip_tests": True,                    # Skip test execution
    "args": ["--quiet", "--no-daemon"]    # Additional Gradle arguments
}
```

## 📊 Data Models

### CompilationResult
```python
@dataclass
class CompilationResult:
    status: CompilationStatus              # SUCCESS, FAILED, WARNING, PENDING
    project_type: ProjectType              # Project type
    project_path: str                      # Path to project
    compilation_time: float                # Time taken in seconds
    issues: List[CompilationIssue]         # All compilation issues
    output_path: str                       # Build output directory
    build_logs: str                        # Complete build logs
    metadata: Dict[str, Any]               # Additional build information
```

### CompilationIssue
```python
@dataclass
class CompilationIssue:
    severity: str                          # "error", "warning", "info"
    message: str                           # Issue description
    file_path: str                         # File where issue occurred
    line_number: int                       # Line number (if available)
    column_number: int                     # Column number (if available)
    error_code: str                        # Error code (if available)
    suggestion: str                        # Suggested fix (if available)
```

## 🛠️ Java Spring Boot Support

### Maven Projects

The agent supports comprehensive Maven project compilation:

- **Auto-detection**: Recognizes `pom.xml` files
- **Spring Boot detection**: Looks for Spring Boot dependencies and annotations
- **Goal execution**: Supports any Maven goals (`clean`, `compile`, `test`, `package`, etc.)
- **Error parsing**: Extracts detailed error information from Maven output
- **Dependency resolution**: Reports dependency issues

Example Maven compilation:
```python
result = agent.compile_project(
    project_path="/path/to/maven/project",
    build_options={
        "goals": ["clean", "compile"],
        "skip_tests": True,
        "args": ["-q"]  # Quiet output
    }
)
```

### Gradle Projects

The agent supports Gradle projects with wrapper support:

- **Wrapper preference**: Uses `gradlew` if available, falls back to system Gradle
- **Task execution**: Supports any Gradle tasks (`clean`, `build`, `test`, etc.)
- **Error parsing**: Extracts compilation errors from Gradle output
- **Incremental builds**: Supports Gradle's incremental compilation features

Example Gradle compilation:
```python
result = agent.compile_project(
    project_path="/path/to/gradle/project", 
    build_options={
        "tasks": ["clean", "build"],
        "skip_tests": True,
        "args": ["--no-daemon"]
    }
)
```

### Error Parsing

The agent parses various error patterns:

#### Maven Error Patterns
- `[ERROR] compilation failure`
- `[ERROR] /path/to/File.java:[line,column] error message`
- `[WARNING] warning messages`

#### Gradle Error Patterns  
- `error: compilation error message`
- `/path/to/File.java:line: error: error message`
- `warning: warning message`

#### Java Compilation Errors
- Package declaration issues
- Import statement problems
- Syntax errors with line/column information
- Type resolution failures
- Method signature mismatches

## 📋 Example Output

### Successful Compilation
```
🔨 Starting compilation...
✅ Compilation successful!
   Time taken: 45.32 seconds
   Total issues: 2
   Errors: 0
   Warnings: 2
   Output: /path/to/project/target

🟡 Warnings (2):
   1. Unused import: java.util.List
      📄 src/main/java/com/example/Controller.java:5
   2. Deprecated method usage
      📄 src/main/java/com/example/Service.java:23
```

### Failed Compilation
```
🔨 Starting compilation...
❌ Compilation failed!
   Time taken: 12.45 seconds
   Total issues: 3
   Errors: 2
   Warnings: 1

🔴 Errors (2):
   1. cannot find symbol: variable undefinedVar
      📄 src/main/java/com/example/Controller.java:42:15
      💡 Check if the variable is declared and spelled correctly
   2. method doSomething() is already defined
      📄 src/main/java/com/example/Service.java:18:5
      💡 Remove the duplicate method or rename one of them
```

### JSON Output
```json
{
  "status": "failed",
  "project_type": "java_springboot", 
  "compilation_time": 12.45,
  "summary": {
    "total_issues": 3,
    "errors": 2,
    "warnings": 1,
    "build_successful": false
  },
  "issues": [
    {
      "severity": "error",
      "message": "cannot find symbol: variable undefinedVar",
      "file_path": "src/main/java/com/example/Controller.java",
      "line_number": 42,
      "column_number": 15
    }
  ]
}
```

## 🎯 Use Cases

### 1. Continuous Integration
```python
# CI/CD pipeline integration
def ci_compile_check(project_path):
    result = compile_java_springboot(project_path, skip_tests=False)
    
    if result.status != CompilationStatus.SUCCESS:
        # Fail the build
        print("❌ Build failed!")
        for error in result.get_errors():
            print(f"ERROR: {error.message}")
        return False
    
    return True
```

### 2. Development Environment
```python
# IDE-like compilation checking
def check_compilation_status(project_path):
    agent = CodeCompilationAgent(config={"verbose": False})
    result = agent.compile_project(project_path, build_options={"goals": ["compile"]})
    
    return {
        "compilable": result.status == CompilationStatus.SUCCESS,
        "error_count": len(result.get_errors()),
        "warning_count": len(result.get_warnings()),
        "issues": result.issues
    }
```

### 3. Code Quality Analysis
```python
# Analyze code quality based on compilation
def analyze_code_quality(project_path):
    result = compile_java_springboot(project_path)
    
    quality_score = 100
    quality_score -= len(result.get_errors()) * 10     # -10 per error
    quality_score -= len(result.get_warnings()) * 2    # -2 per warning
    
    return max(0, quality_score)
```

## 🔍 Troubleshooting

### Common Issues

1. **Maven/Gradle not found**
   ```
   Error: Maven (mvn) is not available in PATH
   ```
   **Solution**: Install Maven/Gradle or specify custom paths in config

2. **Compilation timeout**
   ```
   Error: Maven compilation timed out after 300 seconds
   ```
   **Solution**: Increase timeout in config or optimize build

3. **Permission denied**
   ```
   Error: Permission denied accessing project directory
   ```
   **Solution**: Check file permissions and user access

4. **Invalid project structure**
   ```
   Error: No pom.xml or build.gradle found
   ```
   **Solution**: Ensure you're pointing to a valid project root

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use verbose configuration
config = {"verbose": True, "timeout": 600}
agent = CodeCompilationAgent(config=config)
```

### Build Tool Verification

```python
# Check if tools are available
agent = CodeCompilationAgent()

tools = ["maven", "gradle", "dotnet", "python", "npm"]
for tool in tools:
    available = agent._check_tool_availability(tool)
    print(f"{tool}: {'✅ Available' if available else '❌ Not found'}")
```

## 🚀 Future Enhancements

### Planned Features
- **.NET Core/5+ API compilation** with `dotnet build`
- **Python API validation** with syntax checking and dependency resolution
- **Node.js/TypeScript compilation** with npm/yarn support
- **Docker-based compilation** for consistent environments
- **Parallel multi-project compilation**
- **Integration with popular IDEs** (VS Code, IntelliJ)
- **Custom rule engines** for organization-specific compilation standards

### .NET API Support (Coming Soon)
```python
# Future .NET API compilation
result = agent.compile_project(
    project_path="/path/to/dotnet/project",
    project_type=ProjectType.DOTNET_API,
    build_options={
        "configuration": "Release",
        "framework": "net6.0",
        "restore": True
    }
)
```

### Python API Support (Coming Soon)
```python
# Future Python API validation
result = agent.compile_project(
    project_path="/path/to/python/project",
    project_type=ProjectType.PYTHON_API,
    build_options={
        "check_syntax": True,
        "check_imports": True,
        "install_dependencies": True
    }
)
```

## 📄 License

This project is part of the larger genaiagent workspace and follows the same licensing terms.

---

**Start with Java Spring Boot compilation - provide project path and get detailed compilation results with issue reporting!** 🚀
