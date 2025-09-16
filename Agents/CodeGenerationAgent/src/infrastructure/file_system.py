"""File system operations service."""

import os
import sys
import logging
from pathlib import Path
from typing import List

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)

import os
import json
import yaml
import logging
from pathlib import Path
from typing import List

try:
    from src.core.interfaces import FileSystemProvider
    from src.core.exceptions import FileSystemError
except ImportError:
    try:
        from core.interfaces import FileSystemProvider
        from core.exceptions import FileSystemError
    except ImportError:
        # Define basic interfaces if not available
        class FileSystemProvider:
            def write_file(self, path: str, content: str) -> bool: pass
            def read_file(self, path: str) -> str: pass
            def create_directory(self, path: str) -> bool: pass
            def list_directory(self, path: str) -> List[str]: pass
        
        class FileSystemError(Exception):
            pass


class FileSystemService(FileSystemProvider):
    """Implementation of file system operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def read_file(self, file_path: str) -> str:
        """Read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileSystemError(f"File not found: {file_path}")
        except IOError as e:
            raise FileSystemError(f"Error reading file {file_path}: {str(e)}")
    
    def write_file(self, file_path: str, content: str) -> None:
        """Write content to file."""
        try:
            # Create parent directories if they don't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.debug(f"Successfully wrote file: {file_path}")
            
        except IOError as e:
            raise FileSystemError(f"Error writing file {file_path}: {str(e)}")
    
    def create_directories(self, dir_path: str) -> None:
        """Create directory structure."""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directories: {dir_path}")
        except OSError as e:
            raise FileSystemError(f"Error creating directories {dir_path}: {str(e)}")
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in directory matching pattern."""
        try:
            path = Path(directory)
            if not path.exists():
                return []
            
            return [str(f) for f in path.glob(pattern) if f.is_file()]
        except OSError as e:
            raise FileSystemError(f"Error listing files in {directory}: {str(e)}")
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            return Path(file_path).stat().st_size
        except OSError as e:
            raise FileSystemError(f"Error getting file size for {file_path}: {str(e)}")
