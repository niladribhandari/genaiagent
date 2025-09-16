"""Import management service."""

import re
import logging
from typing import Set, List, Dict, Tuple
from collections import defaultdict

try:
    from src.core.interfaces import ImportDetector
    from src.core.exceptions import ImportProcessingError
except ImportError:
    from core.interfaces import ImportDetector
    from core.exceptions import ImportProcessingError


class ImportManager(ImportDetector):
    """Implementation of import detection and management."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Standard library imports that don't need explicit management
        self.standard_imports = {
            'java.util', 'java.io', 'java.lang', 'java.math', 'java.time',
            'java.text', 'java.security', 'java.net', 'java.nio'
        }
        
        # Common framework imports
        self.framework_imports = {
            'springframework': 'org.springframework',
            'jackson': 'com.fasterxml.jackson',
            'hibernate': 'org.hibernate',
            'junit': 'org.junit',
            'mockito': 'org.mockito'
        }
    
    def detect_imports(self, code: str, file_type: str) -> List[str]:
        """Detect required imports from code."""
        if file_type.lower() == "java":
            return list(self._detect_java_imports(code))
        else:
            raise ImportProcessingError(f"File type {file_type} not supported")
    
    def supports_language(self, language: str) -> bool:
        """Check if this detector supports the given language."""
        return language.lower() in ["java"]
    
    def organize_imports(self, imports: Set[str]) -> List[str]:
        """Organize imports in proper order."""
        # Group imports by package
        grouped_imports = self._group_imports(imports)
        
        # Sort within each group
        organized = []
        
        # Standard library imports first
        if 'java' in grouped_imports:
            organized.extend(sorted(grouped_imports['java']))
            organized.append('')  # Empty line after standard imports
        
        # Third-party framework imports
        for framework in ['javax', 'org', 'com']:
            if framework in grouped_imports:
                organized.extend(sorted(grouped_imports[framework]))
                organized.append('')  # Empty line after each group
        
        # Project-specific imports (if any)
        remaining_groups = set(grouped_imports.keys()) - {'java', 'javax', 'org', 'com'}
        for group in sorted(remaining_groups):
            organized.extend(sorted(grouped_imports[group]))
            if remaining_groups:
                organized.append('')
        
        # Remove trailing empty line
        if organized and organized[-1] == '':
            organized.pop()
        
        return organized
    
    def add_missing_imports(self, code: str, required_imports: Set[str]) -> str:
        """Add missing imports to code."""
        existing_imports = self._extract_existing_imports(code)
        missing_imports = required_imports - existing_imports
        
        if not missing_imports:
            return code
        
        # Find the position to insert imports
        insertion_point = self._find_import_insertion_point(code)
        
        # Organize all imports (existing + missing)
        all_imports = existing_imports | missing_imports
        organized_imports = self.organize_imports(all_imports)
        
        # Create import statements
        import_statements = [f"import {imp};" for imp in organized_imports if imp != '']
        
        # Insert imports into code
        lines = code.split('\n')
        
        # Remove existing imports
        lines = [line for line in lines if not self._is_import_line(line)]
        
        # Insert new organized imports
        lines.insert(insertion_point, '\n'.join(import_statements) + '\n')
        
        return '\n'.join(lines)
    
    def _detect_java_imports(self, code: str) -> Set[str]:
        """Detect Java imports from code content."""
        required_imports = set()
        
        # Common patterns that require imports
        patterns = {
            # Spring Framework
            r'@RestController|@Controller|@Service|@Repository|@Component': 'org.springframework.stereotype',
            r'@RequestMapping|@GetMapping|@PostMapping|@PutMapping|@DeleteMapping': 'org.springframework.web.bind.annotation',
            r'@Autowired': 'org.springframework.beans.factory.annotation.Autowired',
            r'ResponseEntity': 'org.springframework.http.ResponseEntity',
            r'HttpStatus': 'org.springframework.http.HttpStatus',
            r'@PathVariable': 'org.springframework.web.bind.annotation.PathVariable',
            r'@RequestBody': 'org.springframework.web.bind.annotation.RequestBody',
            r'@RequestParam': 'org.springframework.web.bind.annotation.RequestParam',
            
            # JPA/Hibernate
            r'@Entity': 'javax.persistence.Entity',
            r'@Table': 'javax.persistence.Table',
            r'@Id': 'javax.persistence.Id',
            r'@GeneratedValue': 'javax.persistence.GeneratedValue',
            r'@Column': 'javax.persistence.Column',
            r'@JoinColumn': 'javax.persistence.JoinColumn',
            r'@OneToMany|@ManyToOne|@OneToOne|@ManyToMany': 'javax.persistence',
            
            # Common utilities
            r'\bList<': 'java.util.List',
            r'\bArrayList<': 'java.util.ArrayList',
            r'\bMap<': 'java.util.Map',
            r'\bHashMap<': 'java.util.HashMap',
            r'\bSet<': 'java.util.Set',
            r'\bHashSet<': 'java.util.HashSet',
            r'\bDate\b': 'java.util.Date',
            r'\bLocalDate\b': 'java.time.LocalDate',
            r'\bLocalDateTime\b': 'java.time.LocalDateTime',
            
            # Logging
            r'\bLogger\b': 'org.slf4j.Logger',
            r'LoggerFactory': 'org.slf4j.LoggerFactory',
            
            # JSON
            r'@JsonProperty|@JsonIgnore': 'com.fasterxml.jackson.annotation',
            
            # Validation
            r'@Valid|@NotNull|@NotEmpty|@Size': 'javax.validation'
        }
        
        # Check for pattern matches
        for pattern, import_base in patterns.items():
            if re.search(pattern, code):
                if isinstance(import_base, str):
                    # For specific imports like javax.persistence
                    if pattern in ['@OneToMany|@ManyToOne|@OneToOne|@ManyToMany']:
                        # Add specific relationship annotations
                        if '@OneToMany' in code:
                            required_imports.add('javax.persistence.OneToMany')
                        if '@ManyToOne' in code:
                            required_imports.add('javax.persistence.ManyToOne')
                        if '@OneToOne' in code:
                            required_imports.add('javax.persistence.OneToOne')
                        if '@ManyToMany' in code:
                            required_imports.add('javax.persistence.ManyToMany')
                    elif pattern == '@Valid|@NotNull|@NotEmpty|@Size':
                        # Add specific validation annotations
                        if '@Valid' in code:
                            required_imports.add('javax.validation.Valid')
                        if '@NotNull' in code:
                            required_imports.add('javax.validation.constraints.NotNull')
                        if '@NotEmpty' in code:
                            required_imports.add('javax.validation.constraints.NotEmpty')
                        if '@Size' in code:
                            required_imports.add('javax.validation.constraints.Size')
                    else:
                        # Add the full import
                        if '.' in import_base:
                            required_imports.add(import_base)
                        else:
                            # This is a base package, need specific class
                            required_imports.add(f"{import_base}.{pattern.split('|')[0].replace('@', '')}")
        
        # Look for existing import statements to understand naming patterns
        existing_imports = self._extract_existing_imports(code)
        
        return required_imports
    
    def _extract_existing_imports(self, code: str) -> Set[str]:
        """Extract existing imports from code."""
        imports = set()
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') and line.endswith(';'):
                import_stmt = line[7:-1].strip()  # Remove 'import ' and ';'
                imports.add(import_stmt)
        
        return imports
    
    def _group_imports(self, imports: Set[str]) -> Dict[str, List[str]]:
        """Group imports by top-level package."""
        groups = defaultdict(list)
        
        for imp in imports:
            if imp:  # Skip empty strings
                top_package = imp.split('.')[0]
                groups[top_package].append(imp)
        
        return dict(groups)
    
    def _find_import_insertion_point(self, code: str) -> int:
        """Find the best position to insert imports."""
        lines = code.split('\n')
        
        # Look for package declaration
        for i, line in enumerate(lines):
            if line.strip().startswith('package '):
                return i + 1
        
        # If no package declaration, insert at the beginning
        return 0
    
    def _is_import_line(self, line: str) -> bool:
        """Check if line is an import statement."""
        line = line.strip()
        return line.startswith('import ') and line.endswith(';')
