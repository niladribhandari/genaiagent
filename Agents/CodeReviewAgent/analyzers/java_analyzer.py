"""
Java code analyzer for identifying Java-specific issues.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any

from ..models.review_result import CodeIssue, Severity, IssueCategory


class JavaAnalyzer:
    """Analyzer specifically for Java code."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Java analyzer."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Analyze Java code and return list of issues."""
        issues = []
        lines = content.split('\n')
        
        # Run various checks
        issues.extend(self._check_naming_conventions(lines, file_path))
        issues.extend(self._check_exception_handling(lines, file_path))
        issues.extend(self._check_dependency_injection(lines, file_path))
        issues.extend(self._check_annotations(lines, file_path))
        issues.extend(self._check_security_patterns(lines, file_path))
        issues.extend(self._check_performance_patterns(lines, file_path))
        issues.extend(self._check_documentation(lines, file_path))
        issues.extend(self._check_spring_boot_patterns(lines, file_path))
        
        return issues
    
    def _check_naming_conventions(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check Java naming conventions."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check class names (PascalCase)
            class_match = re.search(r'class\s+(\w+)', line_stripped)
            if class_match:
                class_name = class_match.group(1)
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.MEDIUM,
                        category=IssueCategory.CODE_QUALITY,
                        title="Invalid class name",
                        description=f"Class name '{class_name}' should follow PascalCase convention",
                        suggestion="Use PascalCase for class names (e.g., MyClassName)",
                        rule_id="java_naming_class"
                    ))
            
            # Check method names (camelCase)
            method_match = re.search(r'(public|private|protected).*\s+(\w+)\s*\(', line_stripped)
            if method_match:
                method_name = method_match.group(2)
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', method_name) and method_name not in ['main']:
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.LOW,
                        category=IssueCategory.CODE_QUALITY,
                        title="Invalid method name",
                        description=f"Method name '{method_name}' should follow camelCase convention",
                        suggestion="Use camelCase for method names (e.g., myMethodName)",
                        rule_id="java_naming_method"
                    ))
            
            # Check constants (UPPER_SNAKE_CASE)
            constant_match = re.search(r'static\s+final.*\s+(\w+)\s*=', line_stripped)
            if constant_match:
                constant_name = constant_match.group(1)
                if not re.match(r'^[A-Z][A-Z0-9_]*$', constant_name):
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.LOW,
                        category=IssueCategory.CODE_QUALITY,
                        title="Invalid constant name",
                        description=f"Constant '{constant_name}' should use UPPER_SNAKE_CASE",
                        suggestion="Use UPPER_SNAKE_CASE for constants (e.g., MY_CONSTANT)",
                        rule_id="java_naming_constant"
                    ))
        
        return issues
    
    def _check_exception_handling(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check exception handling patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for empty catch blocks
            if 'catch' in line_stripped and '{' in line_stripped:
                # Look for empty catch block
                if i < len(lines):
                    next_line = lines[i].strip() if i < len(lines) else ""
                    if next_line == '}' or (next_line == '' and i+1 < len(lines) and lines[i+1].strip() == '}'):
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.HIGH,
                            category=IssueCategory.CODE_QUALITY,
                            title="Empty catch block",
                            description="Empty catch block suppresses exceptions silently",
                            suggestion="Add proper exception handling or at least log the exception",
                            rule_id="java_empty_catch"
                        ))
            
            # Check for catching generic Exception
            if re.search(r'catch\s*\(\s*Exception\s+\w+\)', line_stripped):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.CODE_QUALITY,
                    title="Catching generic Exception",
                    description="Catching generic Exception can hide specific error conditions",
                    suggestion="Catch specific exception types instead of generic Exception",
                    rule_id="java_generic_exception"
                ))
            
            # Check for printStackTrace usage
            if 'printStackTrace()' in line_stripped:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.BEST_PRACTICES,
                    title="Using printStackTrace",
                    description="printStackTrace should not be used in production code",
                    suggestion="Use proper logging framework instead of printStackTrace",
                    rule_id="java_print_stack_trace"
                ))
        
        return issues
    
    def _check_dependency_injection(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check dependency injection patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for field injection
            if '@Autowired' in line_stripped and i < len(lines):
                next_line = lines[i].strip() if i < len(lines) else ""
                if re.search(r'private.*\w+;', next_line):
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.MEDIUM,
                        category=IssueCategory.BEST_PRACTICES,
                        title="Field injection detected",
                        description="Field injection is not recommended, use constructor injection",
                        suggestion="Use constructor injection with @RequiredArgsConstructor or explicit constructor",
                        rule_id="java_field_injection"
                    ))
        
        return issues
    
    def _check_annotations(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check annotation usage."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for missing @Override
            if i < len(lines) - 1:
                current_line = line_stripped
                next_line = lines[i].strip() if i < len(lines) else ""
                
                if ('public' in next_line and any(method in next_line for method in 
                    ['equals(', 'hashCode(', 'toString(', 'compareTo('])):
                    if '@Override' not in current_line:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=i+1,
                            severity=Severity.LOW,
                            category=IssueCategory.BEST_PRACTICES,
                            title="Missing @Override annotation",
                            description="Method appears to override but lacks @Override annotation",
                            suggestion="Add @Override annotation to overridden methods",
                            rule_id="java_missing_override"
                        ))
        
        return issues
    
    def _check_security_patterns(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check for security anti-patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
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
                    rule_id="java_hardcoded_credentials"
                ))
            
            # Check for SQL concatenation
            if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*\+.*["\']', line_stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.HIGH,
                    category=IssueCategory.SECURITY,
                    title="Potential SQL injection",
                    description="SQL query appears to use string concatenation",
                    suggestion="Use parameterized queries or prepared statements",
                    rule_id="java_sql_injection"
                ))
        
        return issues
    
    def _check_performance_patterns(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check for performance anti-patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for string concatenation in loops
            if 'for (' in line_stripped or 'while (' in line_stripped:
                # Look for string concatenation in the next few lines
                for j in range(i, min(i + 10, len(lines))):
                    if j < len(lines) and '+=' in lines[j] and 'String' in lines[j]:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=j+1,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.PERFORMANCE,
                            title="String concatenation in loop",
                            description="String concatenation in loops can cause performance issues",
                            suggestion="Use StringBuilder for string concatenation in loops",
                            rule_id="java_string_concat_loop"
                        ))
                        break
        
        return issues
    
    def _check_documentation(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check documentation quality."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for public methods without Javadoc
            if line_stripped.startswith('public ') and '(' in line_stripped and '{' in line_stripped:
                # Look for Javadoc in previous lines
                has_javadoc = False
                for j in range(max(0, i-5), i):
                    if j < len(lines) and '/**' in lines[j]:
                        has_javadoc = True
                        break
                
                if not has_javadoc:
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=Severity.LOW,
                        category=IssueCategory.DOCUMENTATION,
                        title="Missing Javadoc",
                        description="Public method lacks Javadoc documentation",
                        suggestion="Add Javadoc documentation for public methods",
                        rule_id="java_missing_javadoc"
                    ))
        
        return issues
    
    def _check_spring_boot_patterns(self, lines: List[str], file_path: Path) -> List[CodeIssue]:
        """Check Spring Boot specific patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for @Transactional on class level for read operations
            if '@Transactional' in line_stripped and 'readOnly' not in line_stripped:
                # Look for GET mappings in the class
                for j in range(i, min(i + 50, len(lines))):
                    if j < len(lines) and '@GetMapping' in lines[j]:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.PERFORMANCE,
                            title="Missing readOnly for GET operations",
                            description="@Transactional without readOnly=true for read operations",
                            suggestion="Use @Transactional(readOnly=true) for read-only operations",
                            rule_id="spring_readonly_transaction"
                        ))
                        break
            
            # Check for missing @Valid on request bodies
            if '@RequestBody' in line_stripped and '@Valid' not in line_stripped:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    severity=Severity.MEDIUM,
                    category=IssueCategory.BEST_PRACTICES,
                    title="Missing @Valid annotation",
                    description="@RequestBody should be validated with @Valid",
                    suggestion="Add @Valid annotation to validate request body",
                    rule_id="spring_missing_valid"
                ))
        
        return issues
