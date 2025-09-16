"""
Code analysis utilities for the GitHub search agent.
"""

import ast
import re
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
import os

from ..models import CodeFile, SecurityIssue


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    line_start: int
    line_end: int
    parameters: List[str]
    complexity: int = 0
    docstring: Optional[str] = None


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    line_start: int
    line_end: int
    methods: List[FunctionInfo]
    inheritance: List[str]
    docstring: Optional[str] = None


class CodeAnalyzer:
    """Analyzes code files for structure, complexity, and quality."""
    
    def __init__(self):
        self.logger = logging.getLogger("code_analyzer")
        
        # Language-specific patterns
        self.language_patterns = {
            "python": {
                "imports": r"^(?:from\s+\S+\s+)?import\s+(.+)$",
                "functions": r"^def\s+(\w+)\s*\(",
                "classes": r"^class\s+(\w+)(?:\([^)]*\))?:",
                "comments": r"#.*$",
                "docstrings": r'"""[\s\S]*?"""'
            },
            "javascript": {
                "imports": r"^(?:import|const|let|var)\s+.*?from\s+['\"]([^'\"]+)['\"]",
                "functions": r"(?:function\s+(\w+)|(\w+)\s*=\s*(?:function|\([^)]*\)\s*=>))",
                "classes": r"class\s+(\w+)(?:\s+extends\s+\w+)?",
                "comments": r"//.*$",
                "docstrings": r'/\*\*[\s\S]*?\*/'
            },
            "java": {
                "imports": r"^import\s+([^;]+);",
                "functions": r"(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*{",
                "classes": r"(?:public\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?",
                "comments": r"//.*$",
                "docstrings": r'/\*\*[\s\S]*?\*/'
            }
        }
        
        # Security patterns
        self.security_patterns = {
            "sql_injection": [
                r"(?i)(?:SELECT|INSERT|UPDATE|DELETE).*?(?:\+|%|\|{2})",
                r"(?i)execute\s*\(\s*[\"'][^\"']*[\"']\s*\+",
                r"(?i)query\s*\(\s*[\"'][^\"']*[\"']\s*\+"
            ],
            "xss": [
                r"innerHTML\s*=.*?\+",
                r"document\.write\s*\(",
                r"eval\s*\(",
                r"(?i)(<script|javascript:)"
            ],
            "hardcoded_secrets": [
                r"(?i)(password|secret|key|token)\s*[:=]\s*[\"'][^\"']{8,}[\"']",
                r"(?i)(api_key|apikey|access_token)\s*[:=]\s*[\"'][^\"']{10,}[\"']",
                r"(?i)(private_key|secret_key)\s*[:=]\s*[\"'][^\"']{20,}[\"']"
            ],
            "path_traversal": [
                r"\.\.\/",
                r"\.\.\\",
                r"os\.path\.join.*?\.\."
            ],
            "command_injection": [
                r"(?i)(?:system|exec|popen|subprocess)\s*\([^)]*\+",
                r"(?i)os\.system\s*\([^)]*%",
                r"(?i)shell=True"
            ]
        }
    
    def analyze_file(self, file_path: str, content: str, language: str) -> CodeFile:
        """Analyze a single code file."""
        self.logger.debug(f"Analyzing file: {file_path}")
        
        lines = content.split('\n')
        line_count = len(lines)
        
        # Basic analysis
        functions = self._extract_functions(content, language)
        classes = self._extract_classes(content, language)
        imports = self._extract_imports(content, language)
        
        # Calculate complexity and quality scores
        complexity_score = self._calculate_complexity(content, language)
        quality_score = self._calculate_quality_score(content, language)
        
        return CodeFile(
            path=file_path,
            content=content,
            language=language,
            size=len(content),
            lines=line_count,
            functions=functions,
            classes=classes,
            imports=imports,
            complexity_score=complexity_score,
            quality_score=quality_score
        )
    
    def _extract_functions(self, content: str, language: str) -> List[str]:
        """Extract function names from code."""
        if language not in self.language_patterns:
            return []
        
        pattern = self.language_patterns[language].get("functions", "")
        if not pattern:
            return []
        
        functions = []
        for match in re.finditer(pattern, content, re.MULTILINE):
            # Handle different capture groups
            for group in match.groups():
                if group and group.isidentifier():
                    functions.append(group)
                    break
        
        return list(set(functions))
    
    def _extract_classes(self, content: str, language: str) -> List[str]:
        """Extract class names from code."""
        if language not in self.language_patterns:
            return []
        
        pattern = self.language_patterns[language].get("classes", "")
        if not pattern:
            return []
        
        classes = []
        for match in re.finditer(pattern, content, re.MULTILINE):
            if match.group(1):
                classes.append(match.group(1))
        
        return list(set(classes))
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements from code."""
        if language not in self.language_patterns:
            return []
        
        pattern = self.language_patterns[language].get("imports", "")
        if not pattern:
            return []
        
        imports = []
        for match in re.finditer(pattern, content, re.MULTILINE):
            if match.group(1):
                # Clean up import statement
                import_stmt = match.group(1).strip()
                imports.append(import_stmt)
        
        return list(set(imports))
    
    def _calculate_complexity(self, content: str, language: str) -> float:
        """Calculate cyclomatic complexity."""
        if language == "python":
            return self._calculate_python_complexity(content)
        
        # Basic complexity for other languages
        complexity_keywords = [
            "if", "else", "elif", "while", "for", "try", "catch", "switch", "case"
        ]
        
        complexity = 1  # Base complexity
        for keyword in complexity_keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', content, re.IGNORECASE))
        
        # Normalize by lines of code
        lines = len(content.split('\n'))
        return min(complexity / max(lines, 1) * 100, 100.0)
    
    def _calculate_python_complexity(self, content: str) -> float:
        """Calculate Python-specific complexity using AST."""
        try:
            tree = ast.parse(content)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, 
                                   ast.ExceptHandler, ast.With, ast.Assert)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
                elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, 
                                     ast.GeneratorExp)):
                    complexity += 1
            
            # Normalize by number of functions/methods
            function_count = sum(1 for node in ast.walk(tree) 
                               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
            
            return min(complexity / max(function_count, 1) * 10, 100.0)
            
        except SyntaxError:
            # Fallback to regex-based analysis
            return self._calculate_complexity_regex(content)
    
    def _calculate_complexity_regex(self, content: str) -> float:
        """Fallback complexity calculation using regex."""
        complexity_patterns = [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bwhile\b', r'\bfor\b',
            r'\btry\b', r'\bexcept\b', r'\bwith\b', r'\bassert\b'
        ]
        
        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, content))
        
        lines = len(content.split('\n'))
        return min(complexity / max(lines, 1) * 100, 100.0)
    
    def _calculate_quality_score(self, content: str, language: str) -> float:
        """Calculate code quality score."""
        score = 100.0
        lines = content.split('\n')
        
        # Deduct points for various quality issues
        
        # Long lines
        long_lines = sum(1 for line in lines if len(line) > 120)
        score -= (long_lines / len(lines)) * 10
        
        # Lack of comments
        if language in self.language_patterns:
            comment_pattern = self.language_patterns[language].get("comments", "")
            if comment_pattern:
                comment_lines = sum(1 for line in lines if re.search(comment_pattern, line))
                comment_ratio = comment_lines / max(len(lines), 1)
                if comment_ratio < 0.1:  # Less than 10% comments
                    score -= 15
        
        # TODO conditions
        todo_count = len(re.findall(r'(?i)todo|fixme|hack', content))
        score -= min(todo_count * 2, 10)
        
        # Code duplication (basic check)
        unique_lines = len(set(line.strip() for line in lines if line.strip()))
        total_lines = len([line for line in lines if line.strip()])
        duplication_ratio = 1 - (unique_lines / max(total_lines, 1))
        score -= duplication_ratio * 20
        
        # Very long functions (basic heuristic)
        if language == "python":
            function_blocks = re.split(r'\ndef\s+', content)
            long_functions = sum(1 for block in function_blocks if len(block.split('\n')) > 50)
            score -= long_functions * 5
        
        return max(score, 0.0)
    
    def detect_security_issues(self, file_path: str, content: str, language: str) -> List[SecurityIssue]:
        """Detect potential security issues in code."""
        self.logger.debug(f"Scanning for security issues: {file_path}")
        
        issues = []
        lines = content.split('\n')
        
        for issue_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        severity = self._get_security_severity(issue_type)
                        description = self._get_security_description(issue_type)
                        recommendation = self._get_security_recommendation(issue_type)
                        
                        issue = SecurityIssue(
                            severity=severity,
                            type=issue_type,
                            description=description,
                            file_path=file_path,
                            line_number=line_num,
                            recommendation=recommendation
                        )
                        issues.append(issue)
        
        return issues
    
    def _get_security_severity(self, issue_type: str) -> str:
        """Get severity level for security issue type."""
        severity_map = {
            "sql_injection": "HIGH",
            "xss": "HIGH",
            "hardcoded_secrets": "CRITICAL",
            "path_traversal": "MEDIUM",
            "command_injection": "HIGH"
        }
        return severity_map.get(issue_type, "MEDIUM")
    
    def _get_security_description(self, issue_type: str) -> str:
        """Get description for security issue type."""
        descriptions = {
            "sql_injection": "Potential SQL injection vulnerability detected",
            "xss": "Potential Cross-Site Scripting (XSS) vulnerability detected",
            "hardcoded_secrets": "Hardcoded secret or API key detected",
            "path_traversal": "Potential path traversal vulnerability detected",
            "command_injection": "Potential command injection vulnerability detected"
        }
        return descriptions.get(issue_type, f"Security issue of type {issue_type} detected")
    
    def _get_security_recommendation(self, issue_type: str) -> str:
        """Get recommendation for security issue type."""
        recommendations = {
            "sql_injection": "Use parameterized queries or prepared statements",
            "xss": "Sanitize user input and use output encoding",
            "hardcoded_secrets": "Use environment variables or secure configuration",
            "path_traversal": "Validate and sanitize file paths",
            "command_injection": "Validate input and use safe execution methods"
        }
        return recommendations.get(issue_type, "Review and remediate security issue")
    
    def get_language_from_extension(self, file_path: str) -> Optional[str]:
        """Determine programming language from file extension."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".kt": "kotlin",
            ".swift": "swift",
            ".scala": "scala",
            ".clj": "clojure",
            ".hs": "haskell",
            ".ml": "ocaml",
            ".sh": "shell",
            ".bash": "shell",
            ".zsh": "shell",
            ".ps1": "powershell",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".less": "less",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".md": "markdown",
            ".dockerfile": "dockerfile"
        }
        
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Special case for Dockerfile
        if path.name.lower() in ["dockerfile", "dockerfile.dev", "dockerfile.prod"]:
            return "dockerfile"
        
        return extension_map.get(extension)
    
    def analyze_repository_structure(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze overall repository structure."""
        self.logger.info(f"Analyzing repository structure with {len(file_paths)} files")
        
        # Language distribution
        languages = {}
        file_types = {}
        
        for file_path in file_paths:
            language = self.get_language_from_extension(file_path)
            if language:
                languages[language] = languages.get(language, 0) + 1
            
            extension = Path(file_path).suffix.lower()
            file_types[extension] = file_types.get(extension, 0) + 1
        
        # Project type detection
        project_type = self._detect_project_type(file_paths)
        
        # Framework detection
        frameworks = self._detect_frameworks(file_paths)
        
        return {
            "total_files": len(file_paths),
            "languages": languages,
            "file_types": file_types,
            "project_type": project_type,
            "frameworks": frameworks,
            "structure_score": self._calculate_structure_score(file_paths)
        }
    
    def _detect_project_type(self, file_paths: List[str]) -> str:
        """Detect project type based on files."""
        file_names = [Path(fp).name.lower() for fp in file_paths]
        
        # Web application indicators
        if any(f in file_names for f in ["package.json", "yarn.lock", "webpack.config.js"]):
            return "web_application"
        
        # Python project indicators
        if any(f in file_names for f in ["setup.py", "requirements.txt", "pyproject.toml", "pipfile"]):
            return "python_project"
        
        # Java project indicators
        if any(f in file_names for f in ["pom.xml", "build.gradle", "build.xml"]):
            return "java_project"
        
        # Mobile app indicators
        if any(f in file_names for f in ["info.plist", "androidmanifest.xml"]):
            return "mobile_application"
        
        # Library/framework indicators
        if any(f in file_names for f in ["makefile", "cmake.txt", "cargo.toml"]):
            return "library"
        
        return "unknown"
    
    def _detect_frameworks(self, file_paths: List[str]) -> List[str]:
        """Detect frameworks used in the project."""
        frameworks = []
        file_names = [Path(fp).name.lower() for fp in file_paths]
        file_contents = []  # Would need actual file contents for better detection
        
        # Framework detection based on files
        framework_indicators = {
            "react": ["package.json"],  # Would check package.json content
            "angular": ["angular.json", ".angular-cli.json"],
            "vue": ["vue.config.js"],
            "django": ["manage.py", "settings.py"],
            "flask": ["app.py"],  # Common but not definitive
            "express": ["package.json"],  # Would check dependencies
            "spring": ["pom.xml", "application.properties"],
            "rails": ["gemfile", "config.ru"],
            "laravel": ["artisan", "composer.json"],
            "symfony": ["composer.json"],  # Would check dependencies
        }
        
        for framework, indicators in framework_indicators.items():
            if any(indicator in file_names for indicator in indicators):
                frameworks.append(framework)
        
        return frameworks
    
    def _calculate_structure_score(self, file_paths: List[str]) -> float:
        """Calculate repository structure quality score."""
        score = 100.0
        
        # Check for common structure patterns
        has_readme = any("readme" in Path(fp).name.lower() for fp in file_paths)
        has_license = any("license" in Path(fp).name.lower() for fp in file_paths)
        has_gitignore = any(".gitignore" in Path(fp).name.lower() for fp in file_paths)
        has_tests = any("test" in fp.lower() for fp in file_paths)
        has_docs = any("doc" in fp.lower() for fp in file_paths)
        
        if not has_readme:
            score -= 20
        if not has_license:
            score -= 10
        if not has_gitignore:
            score -= 5
        if not has_tests:
            score -= 15
        if not has_docs:
            score -= 10
        
        # Check directory organization
        directories = set(Path(fp).parent for fp in file_paths)
        if len(directories) == 1:  # Everything in root
            score -= 20
        
        return max(score, 0.0)
