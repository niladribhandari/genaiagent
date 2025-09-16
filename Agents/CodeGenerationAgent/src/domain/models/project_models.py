"""Project structure and entity models."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class EntityInfo:
    """Information about an entity in the specification."""
    name: str
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    
    @property
    def name_lower(self) -> str:
        return self.name.lower()
    
    @property 
    def name_upper(self) -> str:
        return self.name.upper()
    
    @property
    def name_plural(self) -> str:
        # Simple pluralization - can be enhanced
        if self.name.endswith('y'):
            return self.name[:-1] + 'ies'
        elif self.name.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return self.name + 'es'
        else:
            return self.name + 's'


@dataclass
class ProjectStructure:
    """Project structure configuration."""
    base_package: str
    output_directory: str
    framework: str = "spring_boot"
    language: str = "java"
    directories: List[str] = field(default_factory=list)
    
    def get_package_path(self, subpackage: str = "") -> str:
        """Get package path for a given subpackage."""
        package = self.base_package
        if subpackage:
            package = f"{package}.{subpackage}"
        return package.replace('.', '/')
    
    def get_output_path(self, file_type: str, entity_name: str, extension: str = ".java") -> Path:
        """Get output file path for a given file type and entity."""
        package_path = self.get_package_path(file_type)
        filename = f"{entity_name}{file_type.title()}{extension}"
        return Path(self.output_directory) / "src" / "main" / self.language / package_path / filename
