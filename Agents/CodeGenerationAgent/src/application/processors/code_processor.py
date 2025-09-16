"""Code processing utilities."""

import logging
import re
from typing import List, Dict, Any, Set

try:
    from src.core.interfaces import CodeEnhancer
    from src.core.exceptions import CodeProcessingError
    from src.domain.models.code_models import GeneratedCode, CodeQuality
except ImportError:
    from core.interfaces import CodeEnhancer
    from core.exceptions import CodeProcessingError
    from domain.models.code_models import GeneratedCode, CodeQuality


class CodeProcessor(CodeEnhancer):
    """General code processing and enhancement utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def enhance_code(self, code: str, enhancement_type: str) -> str:
        """Apply specific enhancements to code."""
        try:
            if enhancement_type == "logging":
                return self._add_logging(code)
            elif enhancement_type == "error_handling":
                return self._add_error_handling(code)
            elif enhancement_type == "validation":
                return self._add_validation(code)
            elif enhancement_type == "documentation":
                return self._add_documentation(code)
            elif enhancement_type == "formatting":
                return self._format_code(code)
            else:
                self.logger.warning(f"Unknown enhancement type: {enhancement_type}")
                return code
                
        except Exception as e:
            raise CodeProcessingError(f"Error enhancing code with {enhancement_type}: {str(e)}")
    
    def _add_logging(self, code: str) -> str:
        """Add appropriate logging statements to code."""
        lines = code.split('\n')
        enhanced_lines = []
        
        # Track if we've added logger field
        logger_added = False
        in_class = False
        class_name = None
        
        for i, line in enumerate(lines):
            enhanced_lines.append(line)
            
            # Detect class declaration
            class_match = re.match(r'^\s*public\s+class\s+(\w+)', line)
            if class_match:
                in_class = True
                class_name = class_match.group(1)
                
                # Add logger field after class declaration
                if not logger_added and self._should_add_logger(lines):
                    enhanced_lines.append('')
                    enhanced_lines.append('    private static final Logger logger = LoggerFactory.getLogger({}.class);'.format(class_name))
                    enhanced_lines.append('')
                    logger_added = True
            
            # Add logging to method entries
            elif in_class and re.match(r'^\s*public\s+.*\s+\w+\s*\([^)]*\)\s*\{?\s*$', line):
                method_name = self._extract_method_name(line)
                if method_name:
                    enhanced_lines.append(f'        logger.debug("Entering {method_name}");')
        
        return '\n'.join(enhanced_lines)
    
    def _add_error_handling(self, code: str) -> str:
        """Add proper error handling to code."""
        lines = code.split('\n')
        enhanced_lines = []
        
        for line in lines:
            enhanced_lines.append(line)
            
            # Add try-catch around repository operations
            if 'repository.' in line and 'return' in line:
                # This is a simplistic approach - in reality, you'd want more sophisticated analysis
                try_line = line.replace('return ', 'try {\n            return ')
                enhanced_lines[-1] = try_line
                enhanced_lines.append('        } catch (Exception e) {')
                enhanced_lines.append('            logger.error("Database operation failed", e);')
                enhanced_lines.append('            throw new ServiceException("Operation failed: " + e.getMessage());')
                enhanced_lines.append('        }')
        
        return '\n'.join(enhanced_lines)
    
    def _add_validation(self, code: str) -> str:
        """Add input validation to code."""
        lines = code.split('\n')
        enhanced_lines = []
        
        for line in lines:
            enhanced_lines.append(line)
            
            # Add null checks for method parameters
            if re.match(r'^\s*public\s+.*\([^)]*\w+\s+\w+.*\)', line):
                params = self._extract_parameters(line)
                for param in params:
                    if not param.startswith('Long') and not param.startswith('int'):  # Skip primitive types
                        param_name = param.split()[-1]
                        enhanced_lines.append(f'        if ({param_name} == null) {{')
                        enhanced_lines.append(f'            throw new IllegalArgumentException("{param_name} cannot be null");')
                        enhanced_lines.append('        }')
        
        return '\n'.join(enhanced_lines)
    
    def _add_documentation(self, code: str) -> str:
        """Add JavaDoc documentation to code."""
        lines = code.split('\n')
        enhanced_lines = []
        
        for i, line in enumerate(lines):
            # Add class-level documentation
            if re.match(r'^\s*public\s+class\s+\w+', line):
                class_name = re.search(r'class\s+(\w+)', line).group(1)
                enhanced_lines.extend([
                    '/**',
                    f' * {class_name} class provides business logic and data access operations.',
                    ' * Generated by CodeGenerationAgent.',
                    ' */',
                ])
            
            # Add method-level documentation
            elif re.match(r'^\s*public\s+.*\s+\w+\s*\([^)]*\)', line):
                method_name = self._extract_method_name(line)
                params = self._extract_parameters(line)
                return_type = self._extract_return_type(line)
                
                enhanced_lines.extend([
                    '    /**',
                    f'     * {method_name} method.',
                    '     *'
                ])
                
                for param in params:
                    param_name = param.split()[-1]
                    enhanced_lines.append(f'     * @param {param_name} the {param_name}')
                
                if return_type and return_type != 'void':
                    enhanced_lines.append(f'     * @return {return_type}')
                
                enhanced_lines.append('     */')
            
            enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _format_code(self, code: str) -> str:
        """Apply consistent formatting to code."""
        # Basic formatting improvements
        lines = code.split('\n')
        formatted_lines = []
        
        indent_level = 0
        for line in lines:
            stripped = line.strip()
            
            # Adjust indent level
            if stripped.endswith('{'):
                formatted_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
                formatted_lines.append('    ' * indent_level + stripped)
            else:
                formatted_lines.append('    ' * indent_level + stripped)
        
        return '\n'.join(formatted_lines)
    
    def _should_add_logger(self, lines: List[str]) -> bool:
        """Check if logger should be added to class."""
        # Don't add logger if it already exists
        code_content = '\n'.join(lines)
        return 'Logger' not in code_content and 'logger' not in code_content
    
    def _extract_method_name(self, line: str) -> str:
        """Extract method name from method declaration."""
        match = re.search(r'\s+(\w+)\s*\(', line)
        return match.group(1) if match else ""
    
    def _extract_parameters(self, line: str) -> List[str]:
        """Extract parameters from method declaration."""
        match = re.search(r'\(([^)]*)\)', line)
        if not match:
            return []
        
        params_str = match.group(1).strip()
        if not params_str:
            return []
        
        # Simple parameter parsing - split by comma and clean up
        params = [param.strip() for param in params_str.split(',')]
        return [param for param in params if param]
    
    def _extract_return_type(self, line: str) -> str:
        """Extract return type from method declaration."""
        # Look for pattern: public/private [static] returnType methodName
        match = re.search(r'(public|private)\s+(static\s+)?(\w+(?:<[^>]+>)?)\s+\w+\s*\(', line)
        return match.group(3) if match else ""
    
    def analyze_code_quality(self, code: str) -> CodeQuality:
        """Analyze code quality and provide metrics."""
        issues = []
        suggestions = []
        strengths = []
        
        # Check for basic quality indicators
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Method length check
        method_lengths = self._get_method_lengths(lines)
        long_methods = [name for name, length in method_lengths.items() if length > 20]
        if long_methods:
            issues.append(f"Long methods detected: {', '.join(long_methods)}")
            suggestions.append("Consider breaking down long methods into smaller ones")
        
        # Documentation check
        if '/**' not in code:
            issues.append("Missing JavaDoc documentation")
            suggestions.append("Add comprehensive JavaDoc documentation")
        else:
            strengths.append("Contains documentation")
        
        # Error handling check
        if 'try' not in code and 'catch' not in code:
            issues.append("No error handling detected")
            suggestions.append("Add proper exception handling")
        else:
            strengths.append("Contains error handling")
        
        # Logging check
        if 'logger' not in code.lower():
            suggestions.append("Consider adding logging for better monitoring")
        else:
            strengths.append("Contains logging statements")
        
        # Calculate quality score
        score = 10
        score -= len(issues) * 1.5
        score -= len(long_methods) * 0.5
        score = max(1, min(10, score))
        
        return CodeQuality(
            score=int(score),
            issues=issues,
            suggestions=suggestions,
            strengths=strengths
        )
    
    def _get_method_lengths(self, lines: List[str]) -> Dict[str, int]:
        """Get lengths of all methods in the code."""
        methods = {}
        current_method = None
        method_start = 0
        brace_count = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Detect method start
            if re.match(r'^\s*(public|private|protected).*\w+\s*\([^)]*\)\s*\{?\s*$', stripped):
                method_name = self._extract_method_name(line)
                if method_name:
                    current_method = method_name
                    method_start = i
                    brace_count = stripped.count('{') - stripped.count('}')
            
            elif current_method:
                brace_count += stripped.count('{') - stripped.count('}')
                
                if brace_count <= 0:  # Method ended
                    methods[current_method] = i - method_start + 1
                    current_method = None
                    brace_count = 0
        
        return methods
