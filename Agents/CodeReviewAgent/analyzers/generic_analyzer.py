"""
Generic code analyzer for common patterns across languages.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any

from ..models.review_result import CodeIssue, Severity, IssueCategory


class GenericAnalyzer:
    """Generic analyzer for common code patterns."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the generic analyzer."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Analyze code and return list of generic issues."""
        issues = []
        lines = content.split('\n')
        
        # Run various checks
        issues.extend(self._check_code_quality(lines, file_path))
        issues.extend(self._check_security_patterns(lines, file_path))
        issues.extend(self._check_documentation(lines, file_path))
        issues.extend(self._check_complexity(lines, file_path))
        issues.extend(self._check_maintainability(lines, file_path))
        
        return issues
    
    def _check_code_quality(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check general code quality issues."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for long lines (general)
            if len(line) > 120:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    title="Long line",
                    description=f"Line {i} is {len(line)} characters long",
                    suggestion="Break long lines for better readability",
                    rule_id="generic_long_line"
                ))
            
            # Check for deep nesting (count indentation)
            if line.startswith('    ' * 4):  # 4 levels of indentation
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.MAINTAINABILITY,
                    title="Deep nesting",
                    description="Code is nested too deeply (4+ levels)",
                    suggestion="Consider extracting methods to reduce nesting",
                    rule_id="generic_deep_nesting"
                ))
            
            # Check for magic numbers
            magic_number_pattern = r'\b(?<![\w.])\d{2,}\b(?![\w.])'
            if re.search(magic_number_pattern, line_stripped):
                # Exclude common acceptable numbers
                excluded_numbers = ['100', '200', '404', '500', '1000', '0000']
                if not any(num in line_stripped for num in excluded_numbers):
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.LOW,
                        category=IssueCategory.MAINTAINABILITY,
                        title="Magic number",
                        description="Numeric literal should be replaced with named constant",
                        suggestion="Define a named constant for this value",
                        rule_id="generic_magic_number"
                    ))
            
            # Check for duplicate code patterns (simple)
            if len(line_stripped) > 20:
                for j, other_line in enumerate(lines[i:], i+1):
                    if j != i and line_stripped == other_line.strip() and len(line_stripped) > 30:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.MAINTAINABILITY,
                            title="Duplicate code",
                            description=f"Line {i} appears to be duplicated at line {j}",
                            suggestion="Extract common code into a method or constant",
                            rule_id="generic_duplicate_code"
                        ))
                        break
        
        return issues
    
    def _check_security_patterns(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check for generic security issues."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for potential password patterns
            password_patterns = [
                r'password\s*=\s*["\'][^"\']*["\']',
                r'pwd\s*=\s*["\'][^"\']*["\']',
                r'secret\s*=\s*["\'][^"\']*["\']',
                r'api[_-]?key\s*=\s*["\'][^"\']*["\']',
                r'token\s*=\s*["\'][^"\']*["\']'
            ]
            
            for pattern in password_patterns:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.HIGH,
                        category=IssueCategory.SECURITY,
                        title="Potential hardcoded credential",
                        description="Possible hardcoded password or API key",
                        suggestion="Use environment variables or secure configuration",
                        rule_id="generic_hardcoded_secret"
                    ))
            
            # Check for suspicious URLs or IP addresses
            if re.search(r'http://[^\s"\']+', line_stripped):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.SECURITY,
                    title="Insecure HTTP URL",
                    description="HTTP URL detected, consider using HTTPS",
                    suggestion="Use HTTPS for secure communication",
                    rule_id="generic_insecure_url"
                ))
            
            # Check for potential file path traversal
            if re.search(r'\.\./', line_stripped):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.SECURITY,
                    title="Potential path traversal",
                    description="Path traversal pattern detected",
                    suggestion="Validate and sanitize file paths",
                    rule_id="generic_path_traversal"
                ))
        
        return issues
    
    def _check_documentation(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check documentation quality."""
        issues = []
        
        # Check if file has header comment
        has_header = False
        for i in range(min(10, len(lines))):
            if any(keyword in lines[i].lower() for keyword in ['copyright', 'license', 'author', 'description']):
                has_header = True
                break
        
        if not has_header and len(lines) > 20:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=1,
                severity=Severity.LOW,
                category=IssueCategory.DOCUMENTATION,
                title="Missing file header",
                description="File lacks header comment with description or copyright",
                suggestion="Add file header with description, author, and license information",
                rule_id="generic_missing_header"
            ))
        
        # Check for TODO/FIXME comments that should be addressed
        for i, line in enumerate(lines, 1):
            if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.IGNORECASE):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.LOW,
                    category=IssueCategory.MAINTAINABILITY,
                    title="TODO/FIXME comment",
                    description="Code contains TODO or FIXME comment",
                    suggestion="Address the TODO/FIXME or convert to proper issue tracking",
                    rule_id="generic_todo_comment"
                ))
        
        return issues
    
    def _check_complexity(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check code complexity indicators."""
        issues = []
        
        # Simple cyclomatic complexity check
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'case', 'switch']
        
        current_function_start = None
        current_function_complexity = 0
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip().lower()
            
            # Detect function/method start (generic patterns)
            if any(pattern in line_stripped for pattern in ['def ', 'function ', 'public ', 'private ', 'protected ']):
                if current_function_start is not None and current_function_complexity > 10:
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=current_function_start,
                        severity=Severity.MEDIUM,
                        category=IssueCategory.MAINTAINABILITY,
                        title="High cyclomatic complexity",
                        description=f"Function has high complexity ({current_function_complexity})",
                        suggestion="Consider breaking down the function into smaller methods",
                        rule_id="generic_high_complexity"
                    ))
                
                current_function_start = i
                current_function_complexity = 1  # Base complexity
            
            # Count complexity-increasing keywords
            for keyword in complexity_keywords:
                if f'{keyword} ' in line_stripped or f'{keyword}(' in line_stripped:
                    current_function_complexity += 1
        
        # Check the last function
        if current_function_start is not None and current_function_complexity > 10:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=current_function_start,
                severity=Severity.MEDIUM,
                category=IssueCategory.MAINTAINABILITY,
                title="High cyclomatic complexity",
                description=f"Function has high complexity ({current_function_complexity})",
                suggestion="Consider breaking down the function into smaller methods",
                rule_id="generic_high_complexity"
            ))
        
        return issues
    
    def _check_maintainability(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check maintainability indicators."""
        issues = []
        
        # Check file length
        if len(lines) > 500:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=1,
                severity=Severity.MEDIUM,
                category=IssueCategory.MAINTAINABILITY,
                title="Large file",
                description=f"File has {len(lines)} lines, which may be too large",
                suggestion="Consider splitting large files into smaller, focused modules",
                rule_id="generic_large_file"
            ))
        
        # Check for very long functions (simple heuristic)
        in_function = False
        function_start = 0
        function_lines = 0
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if not stripped:
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            # Detect function start (generic)
            if any(keyword in stripped.lower() for keyword in ['def ', 'function ', 'public ', 'private ']):
                if in_function and function_lines > 50:
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=function_start,
                        severity=Severity.MEDIUM,
                        category=IssueCategory.MAINTAINABILITY,
                        title="Long function",
                        description=f"Function is {function_lines} lines long",
                        suggestion="Consider breaking long functions into smaller methods",
                        rule_id="generic_long_function"
                    ))
                
                in_function = True
                function_start = i
                function_lines = 1
                indent_level = current_indent
            elif in_function:
                if current_indent <= indent_level and stripped:
                    # Function ended
                    if function_lines > 50:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=function_start,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.MAINTAINABILITY,
                            title="Long function", 
                            description=f"Function is {function_lines} lines long",
                            suggestion="Consider breaking long functions into smaller methods",
                            rule_id="generic_long_function"
                        ))
                    in_function = False
                else:
                    function_lines += 1
        
        return issues
