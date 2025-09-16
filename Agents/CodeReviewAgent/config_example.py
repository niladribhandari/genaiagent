"""
Example configuration for ReviewAgent
"""

# Example configuration dictionary
EXAMPLE_CONFIG = {
    "logging": {
        "level": "INFO",
        "console_output": True,
        "log_file": "logs/review_agent.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "max_file_size_mb": 10,
        "backup_count": 5
    },
    
    "file_scanner": {
        "languages": ["java", "python", "javascript"],
        "extensions": [".java", ".py", ".js", ".ts"],
        "ignore_patterns": [
            "target/*",
            "node_modules/*",
            "*.class",
            "*.jar"
        ],
        "use_default_ignore": True,
        "max_file_size_mb": 10
    },
    
    "analyzers": {
        "java": {
            "enabled": True,
            "rules": {
                "check_naming_conventions": True,
                "check_exception_handling": True,
                "check_dependency_injection": True,
                "check_spring_annotations": True,
                "check_security_patterns": True
            }
        },
        
        "python": {
            "enabled": True,
            "rules": {
                "check_pep8": True,
                "check_type_hints": True,
                "check_docstrings": True,
                "check_security": True,
                "check_performance": True
            }
        },
        
        "generic": {
            "enabled": True,
            "rules": {
                "check_code_quality": True,
                "check_security_patterns": True,
                "check_documentation": True,
                "check_complexity": True,
                "check_maintainability": True
            }
        }
    },
    
    "thresholds": {
        "max_file_lines": 500,
        "max_function_lines": 50,
        "max_complexity": 10,
        "max_line_length": 120
    },
    
    "output": {
        "formats": ["json", "html"],
        "include_source_snippets": True,
        "include_metrics": True,
        "severity_filter": "low"  # low, medium, high
    }
}


def load_config_from_file(config_path: str) -> dict:
    """Load configuration from a JSON file."""
    import json
    from pathlib import Path
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        return json.load(f)


def save_example_config(output_path: str):
    """Save the example configuration to a file."""
    import json
    from pathlib import Path
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(EXAMPLE_CONFIG, f, indent=2)
    
    print(f"Example configuration saved to: {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        save_example_config(sys.argv[1])
    else:
        save_example_config("config/review_agent_config.json")
