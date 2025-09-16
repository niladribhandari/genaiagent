"""
File scanner utility for discovering and filtering files for review.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Set, Dict, Any


class FileScanner:
    """Utility for scanning and filtering files for code review."""
    
    # Default file extensions for different languages
    DEFAULT_EXTENSIONS = {
        'java': ['.java'],
        'python': ['.py'],
        'javascript': ['.js', '.jsx', '.ts', '.tsx'],
        'csharp': ['.cs'],
        'cpp': ['.cpp', '.c', '.h', '.hpp'],
        'php': ['.php'],
        'ruby': ['.rb'],
        'go': ['.go'],
        'rust': ['.rs'],
        'kotlin': ['.kt'],
        'scala': ['.scala'],
        'swift': ['.swift'],
        'config': ['.yml', '.yaml', '.json', '.xml', '.properties', '.conf', '.ini'],
        'docker': ['Dockerfile', '.dockerignore'],
        'build': ['.gradle', '.maven', 'pom.xml', 'build.gradle', 'CMakeLists.txt', 'Makefile'],
        'web': ['.html', '.css', '.scss', '.less'],
        'sql': ['.sql'],
        'shell': ['.sh', '.bash', '.zsh', '.fish']
    }
    
    # Default ignore patterns
    DEFAULT_IGNORE_PATTERNS = [
        # Version control
        '.git/*',
        '.svn/*',
        '.hg/*',
        
        # Build outputs
        'target/*',
        'build/*',
        'dist/*',
        'out/*',
        'bin/*',
        '*.class',
        '*.jar',
        '*.war',
        '*.ear',
        
        # Dependencies
        'node_modules/*',
        '.m2/*',
        '.gradle/*',
        '__pycache__/*',
        '*.pyc',
        '*.pyo',
        '.venv/*',
        'venv/*',
        'env/*',
        
        # IDE files
        '.idea/*',
        '.vscode/*',
        '*.iml',
        '.project',
        '.classpath',
        '.settings/*',
        
        # OS files
        '.DS_Store',
        'Thumbs.db',
        
        # Logs
        '*.log',
        'logs/*',
        
        # Temporary files
        '*.tmp',
        '*.temp',
        '*.swp',
        '*.bak',
        
        # Generated files
        '*.generated.*',
        '*-generated.*',
        '*.min.js',
        '*.min.css'
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the file scanner."""
        self.config = config or {}
        self.extensions = self._get_extensions()
        self.ignore_patterns = self._get_ignore_patterns()
        
    def _get_extensions(self) -> Set[str]:
        """Get file extensions to include."""
        config_extensions = self.config.get('extensions', [])
        languages = self.config.get('languages', [])
        
        extensions = set()
        
        # Add configured extensions
        extensions.update(config_extensions)
        
        # Add extensions for specified languages
        for language in languages:
            if language in self.DEFAULT_EXTENSIONS:
                extensions.update(self.DEFAULT_EXTENSIONS[language])
        
        # If no specific config, use common code files
        if not extensions:
            for lang_exts in self.DEFAULT_EXTENSIONS.values():
                extensions.update(lang_exts)
        
        return extensions
    
    def _get_ignore_patterns(self) -> List[str]:
        """Get ignore patterns."""
        config_ignore = self.config.get('ignore_patterns', [])
        use_default_ignore = self.config.get('use_default_ignore', True)
        
        patterns = []
        
        if use_default_ignore:
            patterns.extend(self.DEFAULT_IGNORE_PATTERNS)
        
        patterns.extend(config_ignore)
        
        return patterns
    
    def scan_directory(self, directory: Path) -> List[Path]:
        """Scan directory and return list of files to review."""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            root_path = Path(root)
            
            # Filter directories to skip ignored ones
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(root_path / d)]
            
            for filename in filenames:
                file_path = root_path / filename
                
                if self._should_include_file(file_path):
                    files.append(file_path)
        
        return sorted(files)
    
    def scan_files(self, file_paths: List[str]) -> List[Path]:
        """Scan specific files and return those that should be reviewed."""
        files = []
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if file_path.exists() and file_path.is_file():
                if self._should_include_file(file_path):
                    files.append(file_path)
        
        return files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in review."""
        # Check if file matches ignore patterns
        if self._matches_ignore_patterns(file_path):
            return False
        
        # Check file extension
        if self.extensions:
            file_extension = file_path.suffix.lower()
            file_name = file_path.name
            
            # Check extension or special filenames
            if file_extension not in self.extensions and file_name not in self.extensions:
                return False
        
        # Check file size (skip very large files)
        max_size = self.config.get('max_file_size_mb', 10) * 1024 * 1024
        try:
            if file_path.stat().st_size > max_size:
                return False
        except OSError:
            return False
        
        return True
    
    def _should_ignore_dir(self, dir_path: Path) -> bool:
        """Check if directory should be ignored."""
        return self._matches_ignore_patterns(dir_path)
    
    def _matches_ignore_patterns(self, path: Path) -> bool:
        """Check if path matches any ignore patterns."""
        path_str = str(path).replace('\\', '/')
        
        for pattern in self.ignore_patterns:
            # Handle directory patterns
            if pattern.endswith('/*'):
                dir_pattern = pattern[:-2]
                if fnmatch.fnmatch(path_str, dir_pattern) or f'/{dir_pattern}/' in path_str:
                    return True
            # Handle file patterns
            elif fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
            # Handle patterns with path separators
            elif '/' in pattern and pattern in path_str:
                return True
        
        return False
    
    def get_language_for_file(self, file_path: Path) -> str:
        """Determine the programming language for a file."""
        extension = file_path.suffix.lower()
        filename = file_path.name.lower()
        
        # Check by extension
        for language, extensions in self.DEFAULT_EXTENSIONS.items():
            if extension in extensions or filename in extensions:
                return language
        
        # Special cases
        if filename in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
            return 'docker'
        
        if filename.endswith(('.yml', '.yaml')):
            return 'config'
        
        if filename in ['makefile', 'cmakelist.txt']:
            return 'build'
        
        return 'unknown'
    
    def filter_by_language(self, files: List[Path], languages: List[str]) -> List[Path]:
        """Filter files by programming language."""
        if not languages:
            return files
        
        filtered_files = []
        for file_path in files:
            file_language = self.get_language_for_file(file_path)
            if file_language in languages:
                filtered_files.append(file_path)
        
        return filtered_files
    
    def get_file_stats(self, files: List[Path]) -> Dict[str, Any]:
        """Get statistics about the scanned files."""
        stats = {
            'total_files': len(files),
            'by_language': {},
            'by_extension': {},
            'total_size_bytes': 0
        }
        
        for file_path in files:
            # Language stats
            language = self.get_language_for_file(file_path)
            stats['by_language'][language] = stats['by_language'].get(language, 0) + 1
            
            # Extension stats
            extension = file_path.suffix.lower() or 'no_extension'
            stats['by_extension'][extension] = stats['by_extension'].get(extension, 0) + 1
            
            # Size stats
            try:
                stats['total_size_bytes'] += file_path.stat().st_size
            except OSError:
                pass
        
        return stats
