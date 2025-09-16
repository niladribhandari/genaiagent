"""
File management utilities for API Specification Writing System
Handles file operations, directory management, and specification storage
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
import shutil
import tempfile

from ..models.search_models import (
    SpecificationResult, SpecificationFormat, UserRequirement,
    ValidationResult, WorkflowStatus
)
from .spec_formatter import SpecificationFormatter


class APISpecFileManager:
    """
    Manages file operations for API specifications.
    
    Handles:
    - Writing specifications to files
    - Reading existing specifications
    - Managing specification versions
    - Backup and restore operations
    - Directory organization
    """
    
    def __init__(self, 
                 base_directory: str = "./API-requirements",
                 backup_enabled: bool = True,
                 version_control: bool = True):
        """
        Initialize the file manager.
        
        Args:
            base_directory: Base directory for storing specifications
            backup_enabled: Whether to create backups before overwriting
            version_control: Whether to maintain version history
        """
        self.base_directory = Path(base_directory)
        self.backup_enabled = backup_enabled
        self.version_control = version_control
        self.formatter = SpecificationFormatter()
        
        # Create directory structure
        self._ensure_directory_structure()
    
    def _ensure_directory_structure(self):
        """Ensure the required directory structure exists."""
        directories = [
            self.base_directory,
            self.base_directory / "specs",
            self.base_directory / "backups",
            self.base_directory / "versions",
            self.base_directory / "documentation",
            self.base_directory / "examples"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_specification(self,
                          specification_result: SpecificationResult,
                          filename: Optional[str] = None,
                          subdirectory: str = "specs") -> str:
        """
        Save specification to file.
        
        Args:
            specification_result: The specification result to save
            filename: Custom filename (auto-generated if not provided)
            subdirectory: Subdirectory within base directory
            
        Returns:
            Path to the saved file
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title = specification_result.specification.info.title.lower().replace(" ", "_")
            title = "".join(c for c in title if c.isalnum() or c == "_")
            extension = specification_result.get_file_extension()
            filename = f"{title}_{timestamp}{extension}"
        
        # Ensure filename has correct extension
        if not filename.endswith(specification_result.get_file_extension()):
            filename += specification_result.get_file_extension()
        
        # Construct full path
        target_dir = self.base_directory / subdirectory
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / filename
        
        # Create backup if file exists
        if file_path.exists() and self.backup_enabled:
            self._create_backup(file_path)
        
        # Save the specification
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(specification_result.content)
            
            # Save documentation if available
            if specification_result.documentation:
                self._save_documentation(specification_result, filename)
            
            # Save examples if available
            if specification_result.examples:
                self._save_examples(specification_result, filename)
            
            # Save metadata
            self._save_metadata(specification_result, file_path)
            
            # Version control
            if self.version_control:
                self._create_version(file_path, specification_result)
            
            return str(file_path)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save specification: {str(e)}")
    
    def load_specification(self, file_path: Union[str, Path]) -> SpecificationResult:
        """
        Load specification from file.
        
        Args:
            file_path: Path to the specification file
            
        Returns:
            SpecificationResult instance
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Specification file not found: {file_path}")
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine format from extension
            extension = file_path.suffix.lower()
            if extension in ['.yml', '.yaml']:
                spec_format = SpecificationFormat.OPENAPI_YAML
                spec_dict = yaml.safe_load(content)
            elif extension == '.json':
                spec_format = SpecificationFormat.OPENAPI_JSON
                spec_dict = json.loads(content)
            else:
                raise ValueError(f"Unsupported file extension: {extension}")
            
            # Create APISpecification from dict
            from ..models.search_models import APISpecification, APIInfo
            
            # Extract info
            info_dict = spec_dict.get("info", {})
            api_info = APIInfo(
                title=info_dict.get("title", "Unknown API"),
                version=info_dict.get("version", "1.0.0"),
                description=info_dict.get("description", "")
            )
            
            # Create specification
            specification = APISpecification(
                openapi=spec_dict.get("openapi", "3.0.3"),
                info=api_info
            )
            
            # Load additional data
            documentation = self._load_documentation(file_path)
            examples = self._load_examples(file_path)
            metadata = self._load_metadata(file_path)
            
            return SpecificationResult(
                specification=specification,
                format=spec_format,
                content=content,
                documentation=documentation,
                examples=examples,
                generation_metadata=metadata
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to load specification: {str(e)}")
    
    def _create_backup(self, file_path: Path):
        """Create backup of existing file."""
        backup_dir = self.base_directory / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
    
    def _create_version(self, file_path: Path, specification_result: SpecificationResult):
        """Create version entry for the specification."""
        version_dir = self.base_directory / "versions" / file_path.stem
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Get version number
        version_files = list(version_dir.glob("v*.json"))
        next_version = len(version_files) + 1
        
        # Create version entry
        version_info = {
            "version": next_version,
            "timestamp": datetime.now().isoformat(),
            "api_version": specification_result.specification.info.version,
            "api_title": specification_result.specification.info.title,
            "format": specification_result.format.value,
            "file_path": str(file_path),
            "metadata": specification_result.generation_metadata
        }
        
        version_file = version_dir / f"v{next_version:03d}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, default=str)
    
    def _save_documentation(self, specification_result: SpecificationResult, filename: str):
        """Save documentation separately."""
        doc_dir = self.base_directory / "documentation"
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        doc_filename = f"{Path(filename).stem}_documentation.md"
        doc_path = doc_dir / doc_filename
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(specification_result.documentation)
    
    def _save_examples(self, specification_result: SpecificationResult, filename: str):
        """Save examples separately."""
        examples_dir = self.base_directory / "examples"
        examples_dir.mkdir(parents=True, exist_ok=True)
        
        examples_filename = f"{Path(filename).stem}_examples.json"
        examples_path = examples_dir / examples_filename
        
        with open(examples_path, 'w', encoding='utf-8') as f:
            json.dump(specification_result.examples, f, indent=2, default=str)
    
    def _save_metadata(self, specification_result: SpecificationResult, file_path: Path):
        """Save metadata separately."""
        metadata_dir = self.base_directory / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "file_path": str(file_path),
            "created_at": specification_result.created_at.isoformat(),
            "format": specification_result.format.value,
            "api_title": specification_result.specification.info.title,
            "api_version": specification_result.specification.info.version,
            "generation_metadata": specification_result.generation_metadata,
            "validation_result": {
                "is_valid": specification_result.validation_result.is_valid,
                "quality_score": specification_result.validation_result.quality_score
            } if specification_result.validation_result else None
        }
        
        metadata_filename = f"{file_path.stem}_metadata.json"
        metadata_path = metadata_dir / metadata_filename
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def _load_documentation(self, file_path: Path) -> str:
        """Load documentation if available."""
        doc_dir = self.base_directory / "documentation"
        doc_filename = f"{file_path.stem}_documentation.md"
        doc_path = doc_dir / doc_filename
        
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _load_examples(self, file_path: Path) -> Dict[str, Any]:
        """Load examples if available."""
        examples_dir = self.base_directory / "examples"
        examples_filename = f"{file_path.stem}_examples.json"
        examples_path = examples_dir / examples_filename
        
        if examples_path.exists():
            with open(examples_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Load metadata if available."""
        metadata_dir = self.base_directory / "metadata"
        metadata_filename = f"{file_path.stem}_metadata.json"
        metadata_path = metadata_dir / metadata_filename
        
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                return metadata.get("generation_metadata", {})
        return {}
    
    def list_specifications(self, subdirectory: str = "specs") -> List[Dict[str, Any]]:
        """
        List all specifications in a directory.
        
        Args:
            subdirectory: Subdirectory to list
            
        Returns:
            List of specification info dictionaries
        """
        spec_dir = self.base_directory / subdirectory
        if not spec_dir.exists():
            return []
        
        specifications = []
        
        for file_path in spec_dir.glob("*.{yml,yaml,json}"):
            try:
                # Load basic info
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.suffix.lower() in ['.yml', '.yaml']:
                        spec_dict = yaml.safe_load(f)
                    else:
                        spec_dict = json.load(f)
                
                info = spec_dict.get("info", {})
                
                spec_info = {
                    "file_path": str(file_path),
                    "filename": file_path.name,
                    "title": info.get("title", "Unknown"),
                    "version": info.get("version", "1.0.0"),
                    "description": info.get("description", ""),
                    "format": "yaml" if file_path.suffix.lower() in ['.yml', '.yaml'] else "json",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "created": datetime.fromtimestamp(file_path.stat().st_ctime)
                }
                
                specifications.append(spec_info)
                
            except Exception as e:
                # Skip files that can't be parsed
                continue
        
        # Sort by modification time (newest first)
        specifications.sort(key=lambda x: x["modified"], reverse=True)
        
        return specifications
    
    def delete_specification(self, file_path: Union[str, Path], create_backup: bool = True):
        """
        Delete a specification file.
        
        Args:
            file_path: Path to the specification file
            create_backup: Whether to create backup before deletion
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Specification file not found: {file_path}")
        
        if create_backup and self.backup_enabled:
            self._create_backup(file_path)
        
        # Delete main file
        file_path.unlink()
        
        # Delete associated files
        self._delete_associated_files(file_path)
    
    def _delete_associated_files(self, file_path: Path):
        """Delete associated documentation, examples, and metadata files."""
        stem = file_path.stem
        
        # Delete documentation
        doc_path = self.base_directory / "documentation" / f"{stem}_documentation.md"
        if doc_path.exists():
            doc_path.unlink()
        
        # Delete examples
        examples_path = self.base_directory / "examples" / f"{stem}_examples.json"
        if examples_path.exists():
            examples_path.unlink()
        
        # Delete metadata
        metadata_path = self.base_directory / "metadata" / f"{stem}_metadata.json"
        if metadata_path.exists():
            metadata_path.unlink()
    
    def get_versions(self, specification_name: str) -> List[Dict[str, Any]]:
        """
        Get version history for a specification.
        
        Args:
            specification_name: Name of the specification (without extension)
            
        Returns:
            List of version information
        """
        version_dir = self.base_directory / "versions" / specification_name
        
        if not version_dir.exists():
            return []
        
        versions = []
        
        for version_file in sorted(version_dir.glob("v*.json")):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_info = json.load(f)
                versions.append(version_info)
            except Exception:
                continue
        
        return versions
    
    def restore_version(self, specification_name: str, version: int) -> str:
        """
        Restore a specific version of a specification.
        
        Args:
            specification_name: Name of the specification
            version: Version number to restore
            
        Returns:
            Path to the restored file
        """
        version_dir = self.base_directory / "versions" / specification_name
        version_file = version_dir / f"v{version:03d}.json"
        
        if not version_file.exists():
            raise FileNotFoundError(f"Version {version} not found for {specification_name}")
        
        # Load version info
        with open(version_file, 'r', encoding='utf-8') as f:
            version_info = json.load(f)
        
        original_path = Path(version_info["file_path"])
        
        # Find the backup file for this version
        backup_dir = self.base_directory / "backups"
        
        # This would require more sophisticated backup tracking
        # For now, we'll just raise an error
        raise NotImplementedError("Version restoration requires enhanced backup tracking")
    
    def export_specification(self,
                           file_path: Union[str, Path],
                           target_path: Union[str, Path],
                           target_format: Optional[SpecificationFormat] = None,
                           include_documentation: bool = True,
                           include_examples: bool = True) -> str:
        """
        Export specification to a different location/format.
        
        Args:
            file_path: Source specification file
            target_path: Target location
            target_format: Target format (auto-detect if None)
            include_documentation: Whether to include documentation
            include_examples: Whether to include examples
            
        Returns:
            Path to the exported file
        """
        # Load specification
        spec_result = self.load_specification(file_path)
        
        # Convert format if needed
        if target_format and target_format != spec_result.format:
            spec_result.content = self.formatter.convert_format(
                spec_result.content,
                spec_result.format,
                target_format
            )
            spec_result.format = target_format
        
        # Write to target location
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(spec_result.content)
        
        # Export documentation if requested
        if include_documentation and spec_result.documentation:
            doc_path = target_path.with_suffix('.md')
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(spec_result.documentation)
        
        # Export examples if requested
        if include_examples and spec_result.examples:
            examples_path = target_path.with_suffix('.examples.json')
            with open(examples_path, 'w', encoding='utf-8') as f:
                json.dump(spec_result.examples, f, indent=2, default=str)
        
        return str(target_path)
    
    def cleanup_old_files(self, days: int = 30):
        """
        Clean up old backup and version files.
        
        Args:
            days: Number of days to keep files
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        # Clean backups
        backup_dir = self.base_directory / "backups"
        if backup_dir.exists():
            for backup_file in backup_dir.glob("*"):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
        
        # Clean old versions (keep at least 5 versions per specification)
        version_dir = self.base_directory / "versions"
        if version_dir.exists():
            for spec_dir in version_dir.iterdir():
                if spec_dir.is_dir():
                    version_files = sorted(spec_dir.glob("v*.json"))
                    # Keep at least 5 versions
                    if len(version_files) > 5:
                        for version_file in version_files[:-5]:
                            if version_file.stat().st_mtime < cutoff_time:
                                version_file.unlink()
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage statistics for the specification directory."""
        def get_dir_size(path: Path) -> int:
            """Get total size of directory."""
            total = 0
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
            return total
        
        stats = {
            "total_size": get_dir_size(self.base_directory),
            "specs_size": get_dir_size(self.base_directory / "specs"),
            "backups_size": get_dir_size(self.base_directory / "backups"),
            "versions_size": get_dir_size(self.base_directory / "versions"),
            "documentation_size": get_dir_size(self.base_directory / "documentation"),
            "examples_size": get_dir_size(self.base_directory / "examples")
        }
        
        # Convert to human readable
        for key, size in stats.items():
            if size > 1024 * 1024:  # MB
                stats[f"{key}_human"] = f"{size / (1024 * 1024):.2f} MB"
            elif size > 1024:  # KB
                stats[f"{key}_human"] = f"{size / 1024:.2f} KB"
            else:
                stats[f"{key}_human"] = f"{size} B"
        
        return stats


# Utility functions

def save_specification_quick(
    content: str,
    filename: str,
    directory: str = "./API-requirements"
) -> str:
    """Quick save utility function."""
    file_manager = APISpecFileManager(directory)
    
    # Create a minimal SpecificationResult
    from ..models.search_models import APISpecification, APIInfo, SpecificationFormat, SpecificationResult
    
    # Determine format
    if filename.endswith(('.yml', '.yaml')):
        spec_format = SpecificationFormat.OPENAPI_YAML
    else:
        spec_format = SpecificationFormat.OPENAPI_JSON
    
    # Create minimal specification
    api_info = APIInfo(title="API Specification", version="1.0.0")
    specification = APISpecification(info=api_info)
    
    spec_result = SpecificationResult(
        specification=specification,
        format=spec_format,
        content=content
    )
    
    return file_manager.save_specification(spec_result, filename)
