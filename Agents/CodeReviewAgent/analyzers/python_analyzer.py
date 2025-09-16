"""
Python code analyzer for identifying Python-specific issues.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any

from ..models.review_result import CodeIssue, Severity, IssueCategory


class PythonAnalyzer:
    """Analyzer specifically for Python code."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Python analyzer."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Analyze Python code and return list of issues."""
        issues = []
        lines = content.split('\n')
        
        # Run various checks
        issues.extend(self._check_pep8_compliance(lines, file_path))
        issues.extend(self._check_type_hints(lines, file_path))
        issues.extend(self._check_docstrings(lines, file_path))
        issues.extend(self._check_security_patterns(lines, file_path))
        issues.extend(self._check_performance_patterns(lines, file_path))
        issues.extend(self._check_exception_handling(lines, file_path))
        issues.extend(self._check_imports(lines, file_path))
        
        return issues
    
    def _check_pep8_compliance(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check PEP 8 compliance."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 88:  # Using 88 as recommended by Black
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    title="Line too long",
                    description=f"Line {i} is {len(line)} characters long (max 88 recommended)",
                    suggestion="Break long lines or use parentheses for line continuation",
                    rule_id="python_line_length"
                ))
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    title="Trailing whitespace",
                    description="Line has trailing whitespace",
                    suggestion="Remove trailing whitespace",
                    rule_id="python_trailing_whitespace"
                ))
            
            # Check for multiple statements on one line
            line_stripped = line.strip()
            if ';' in line_stripped and not line_stripped.startswith('#'):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.CODE_QUALITY,
                    title="Multiple statements on one line",
                    description="Multiple statements on one line reduce readability",
                    suggestion="Put each statement on a separate line",
                    rule_id="python_multiple_statements"
                ))
        
        return issues
    
    def _check_type_hints(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check for missing type hints."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check function definitions for type hints
            func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\)', line_stripped)
            if func_match and not line_stripped.startswith('#'):
                func_name = func_match.group(1)
                params = func_match.group(2)
                
                # Skip special methods and private methods for now
                if not func_name.startswith('_'):
                    # Check for parameter type hints
                    if params and ':' not in params and 'self' not in params:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.LOW,
                            category=IssueCategory.MAINTAINABILITY,
                            title="Missing parameter type hints",
                            description=f"Function '{func_name}' parameters lack type hints",
                            suggestion="Add type hints to function parameters",
                            rule_id="python_missing_param_types"
                        ))
                    
                    # Check for return type hints
                    if '->' not in line_stripped:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.LOW,
                            category=IssueCategory.MAINTAINABILITY,
                            title="Missing return type hint",
                            description=f"Function '{func_name}' lacks return type hint",
                            suggestion="Add return type hint to function",
                            rule_id="python_missing_return_type"
                        ))
        
        return issues
    
    def _check_docstrings(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check for missing or inadequate docstrings."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for class definitions without docstrings
            if line_stripped.startswith('class '):
                has_docstring = False
                for j in range(i, min(i + 3, len(lines))):
                    if j < len(lines) and ('"""' in lines[j] or "'''" in lines[j]):
                        has_docstring = True
                        break
                
                if not has_docstring:
                    class_match = re.search(r'class\s+(\w+)', line_stripped)
                    class_name = class_match.group(1) if class_match else "Unknown"
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.MEDIUM,
                        category=IssueCategory.DOCUMENTATION,
                        title="Missing class docstring",
                        description=f"Class '{class_name}' lacks docstring",
                        suggestion="Add docstring to describe the class purpose",
                        rule_id="python_missing_class_docstring"
                    ))
            
            # Check for public function definitions without docstrings
            func_match = re.search(r'def\s+(\w+)', line_stripped)
            if func_match and not line_stripped.startswith('#'):
                func_name = func_match.group(1)
                
                # Only check public functions
                if not func_name.startswith('_'):
                    has_docstring = False
                    for j in range(i, min(i + 3, len(lines))):
                        if j < len(lines) and ('"""' in lines[j] or "'''" in lines[j]):
                            has_docstring = True
                            break
                    
                    if not has_docstring:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.DOCUMENTATION,
                            title="Missing function docstring",
                            description=f"Public function '{func_name}' lacks docstring",
                            suggestion="Add docstring to describe function purpose, parameters, and return value",
                            rule_id="python_missing_function_docstring"
                        ))
        
        return issues
    
    def _check_security_patterns(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check for security anti-patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for eval usage
            if 'eval(' in line_stripped:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.CRITICAL,
                    category=IssueCategory.SECURITY,
                    title="Use of eval()",
                    description="eval() can execute arbitrary code and is a security risk",
                    suggestion="Use safer alternatives like ast.literal_eval() or avoid dynamic code execution",
                    rule_id="python_eval_usage"
                ))
            
            # Check for exec usage
            if 'exec(' in line_stripped:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.CRITICAL,
                    category=IssueCategory.SECURITY,
                    title="Use of exec()",
                    description="exec() can execute arbitrary code and is a security risk",
                    suggestion="Avoid dynamic code execution or use safer alternatives",
                    rule_id="python_exec_usage"
                ))
            
            # Check for hardcoded passwords/secrets
            if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', line_stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.CRITICAL,
                    category=IssueCategory.SECURITY,
                    title="Hardcoded credentials",
                    description="Hardcoded passwords or secrets detected",
                    suggestion="Use environment variables or configuration files for sensitive data",
                    rule_id="python_hardcoded_credentials"
                ))
            
            # Check for SQL injection risks
            if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*%.*["\']', line_stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.HIGH,
                    category=IssueCategory.SECURITY,
                    title="Potential SQL injection",
                    description="SQL query appears to use string formatting",
                    suggestion="Use parameterized queries or ORM methods",
                    rule_id="python_sql_injection"
                ))
        
        return issues
    
    def _check_performance_patterns(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check for performance anti-patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for inefficient list operations
            if re.search(r'for\s+\w+\s+in.*:.*\.append\(', line_stripped):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.PERFORMANCE,
                    title="Consider list comprehension",
                    description="Loop with append can often be replaced with list comprehension",
                    suggestion="Use list comprehension for better performance and readability",
                    rule_id="python_list_comprehension"
                ))
            
            # Check for inefficient string concatenation
            if re.search(r'for\s+.*:\s*\w+\s*\+=.*str', line_stripped):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.PERFORMANCE,
                    title="Inefficient string concatenation",
                    description="String concatenation in loops is inefficient",
                    suggestion="Use ''.join() or f-strings for better performance",
                    rule_id="python_string_concat"
                ))
        
        return issues
    
    def _check_exception_handling(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check exception handling patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for bare except clauses
            if line_stripped == 'except:':
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.HIGH,
                    category=IssueCategory.CODE_QUALITY,
                    title="Bare except clause",
                    description="Bare except clauses catch all exceptions including system exits",
                    suggestion="Catch specific exception types instead of using bare except",
                    rule_id="python_bare_except"
                ))
            
            # Check for catching Exception without handling
            if 'except Exception:' in line_stripped:
                # Look for pass or empty block
                if i < len(lines):
                    next_line = lines[i].strip() if i < len(lines) else ""
                    if next_line == 'pass':
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.CODE_QUALITY,
                            title="Exception silently ignored",
                            description="Exception is caught but ignored with pass",
                            suggestion="Add proper exception handling or at least logging",
                            rule_id="python_ignored_exception"
                        ))
        
        return issues
    
    def _check_imports(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check import patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for wildcard imports
            if re.search(r'from\s+\w+\s+import\s+\*', line_stripped):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.BEST_PRACTICES,
                    title="Wildcard import",
                    description="Wildcard imports pollute the namespace and reduce readability",
                    suggestion="Import specific names or use qualified imports",
                    rule_id="python_wildcard_import"
                ))
            
            # Check for unused imports (basic check)
            import_match = re.search(r'import\s+(\w+)', line_stripped)
            if import_match and not line_stripped.startswith('from'):
                module_name = import_match.group(1)
                # Very basic check - see if module is used in file
                content = '\n'.join(lines)
                if content.count(module_name) == 1:  # Only appears in import
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.LOW,
                        category=IssueCategory.CODE_QUALITY,
                        title="Potentially unused import",
                        description=f"Import '{module_name}' may not be used",
                        suggestion="Remove unused imports to keep code clean",
                        rule_id="python_unused_import"
                    ))
        
        return issues
