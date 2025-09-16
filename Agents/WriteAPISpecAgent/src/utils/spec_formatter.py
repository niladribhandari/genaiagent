"""
Specification formatting utilities for API Specification Writing System
Handles formatting, serialization, and validation of API specifications
"""

import yaml
import json
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import re
from pathlib import Path

from ..models.search_models import (
    APISpecification, SpecificationFormat, ValidationIssue, 
    ValidationSeverity, ValidationResult
)


class SpecificationFormatter:
    """
    Handles formatting and serialization of API specifications.
    
    Supports multiple output formats:
    - OpenAPI YAML
    - OpenAPI JSON
    - Swagger YAML
    - Swagger JSON
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the formatter with configuration."""
        self.config = config or {}
        self.indent_size = self.config.get("indent_size", 2)
        self.line_width = self.config.get("line_width", 120)
        self.sort_keys = self.config.get("sort_keys", False)
        self.include_nulls = self.config.get("include_nulls", False)
        
        # YAML configuration
        self.yaml_config = {
            "default_flow_style": False,
            "indent": self.indent_size,
            "width": self.line_width,
            "sort_keys": self.sort_keys,
            "allow_unicode": True
        }
        
        # JSON configuration
        self.json_config = {
            "indent": self.indent_size,
            "sort_keys": self.sort_keys,
            "ensure_ascii": False,
            "separators": (',', ': ')
        }
    
    def format_specification(
        self,
        specification: Union[APISpecification, Dict[str, Any]],
        format_type: SpecificationFormat,
        validate: bool = True
    ) -> str:
        """
        Format specification to the requested format.
        
        Args:
            specification: The API specification to format
            format_type: The target format
            validate: Whether to validate before formatting
            
        Returns:
            Formatted specification as string
            
        Raises:
            ValueError: If specification is invalid or format is unsupported
        """
        # Convert to dictionary if needed
        if isinstance(specification, APISpecification):
            spec_dict = specification.to_dict()
        else:
            spec_dict = specification
        
        # Validate if requested
        if validate:
            validation_result = self.validate_specification(spec_dict)
            if not validation_result.is_valid:
                errors = [issue.message for issue in validation_result.get_errors()]
                raise ValueError(f"Specification validation failed: {'; '.join(errors)}")
        
        # Clean the specification
        spec_dict = self._clean_specification(spec_dict)
        
        # Add metadata
        spec_dict = self._add_metadata(spec_dict)
        
        # Format according to type
        if format_type in [SpecificationFormat.OPENAPI_YAML, SpecificationFormat.SWAGGER_YAML]:
            return self._format_yaml(spec_dict)
        elif format_type in [SpecificationFormat.OPENAPI_JSON, SpecificationFormat.SWAGGER_JSON]:
            return self._format_json(spec_dict)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _clean_specification(self, spec_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the specification dictionary."""
        cleaned = {}
        
        for key, value in spec_dict.items():
            if value is not None or self.include_nulls:
                if isinstance(value, dict):
                    cleaned_value = self._clean_specification(value)
                    if cleaned_value or self.include_nulls:
                        cleaned[key] = cleaned_value
                elif isinstance(value, list):
                    cleaned_value = [
                        self._clean_specification(item) if isinstance(item, dict) else item
                        for item in value if item is not None or self.include_nulls
                    ]
                    if cleaned_value or self.include_nulls:
                        cleaned[key] = cleaned_value
                else:
                    cleaned[key] = value
        
        return cleaned
    
    def _add_metadata(self, spec_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata to the specification."""
        # Add generation timestamp to info if not present
        if "info" in spec_dict:
            if "x-generated-at" not in spec_dict["info"]:
                spec_dict["info"]["x-generated-at"] = datetime.now().isoformat()
            
            if "x-generator" not in spec_dict["info"]:
                spec_dict["info"]["x-generator"] = "WriteAPISpecAgent"
        
        return spec_dict
    
    def _format_yaml(self, spec_dict: Dict[str, Any]) -> str:
        """Format specification as YAML."""
        try:
            # Use custom representer for better formatting
            yaml.add_representer(type(None), self._represent_none)
            
            formatted = yaml.dump(
                spec_dict,
                **self.yaml_config,
                Dumper=yaml.SafeDumper
            )
            
            # Post-process for better formatting
            formatted = self._post_process_yaml(formatted)
            
            return formatted
            
        except Exception as e:
            raise ValueError(f"Failed to format YAML: {str(e)}")
    
    def _format_json(self, spec_dict: Dict[str, Any]) -> str:
        """Format specification as JSON."""
        try:
            formatted = json.dumps(spec_dict, **self.json_config)
            return formatted
            
        except Exception as e:
            raise ValueError(f"Failed to format JSON: {str(e)}")
    
    def _represent_none(self, dumper, data):
        """Custom YAML representer for None values."""
        return dumper.represent_scalar('tag:yaml.org,2002:null', '')
    
    def _post_process_yaml(self, yaml_content: str) -> str:
        """Post-process YAML for better formatting."""
        lines = yaml_content.split('\n')
        processed_lines = []
        
        for i, line in enumerate(lines):
            # Add blank line before major sections
            if i > 0 and line and not line.startswith(' ') and not line.startswith('-'):
                if lines[i-1] and not lines[i-1].startswith('#'):
                    processed_lines.append('')
            
            processed_lines.append(line)
        
        # Remove trailing empty lines
        while processed_lines and not processed_lines[-1]:
            processed_lines.pop()
        
        return '\n'.join(processed_lines)
    
    def validate_specification(self, spec_dict: Dict[str, Any]) -> ValidationResult:
        """
        Validate the specification dictionary.
        
        Args:
            spec_dict: The specification dictionary to validate
            
        Returns:
            ValidationResult with validation details
        """
        issues = []
        warnings = []
        
        # Check required fields
        if "openapi" not in spec_dict:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Missing required field: openapi",
                location="root",
                suggestion="Add 'openapi' field with version (e.g., '3.0.3')"
            ))
        
        if "info" not in spec_dict:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Missing required field: info",
                location="root",
                suggestion="Add 'info' object with title and version"
            ))
        else:
            info = spec_dict["info"]
            if "title" not in info:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Missing required field: info.title",
                    location="info",
                    suggestion="Add 'title' field to info object"
                ))
            
            if "version" not in info:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Missing required field: info.version",
                    location="info",
                    suggestion="Add 'version' field to info object"
                ))
        
        # Check paths
        if "paths" not in spec_dict:
            warnings.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="No paths defined",
                location="root",
                suggestion="Add 'paths' object with API endpoints"
            ))
        else:
            self._validate_paths(spec_dict["paths"], issues, warnings)
        
        # Check components
        if "components" in spec_dict:
            self._validate_components(spec_dict["components"], issues, warnings)
        
        # Calculate scores
        error_count = len([issue for issue in issues if issue.severity == ValidationSeverity.ERROR])
        warning_count = len([issue for issue in issues if issue.severity == ValidationSeverity.WARNING])
        
        is_valid = error_count == 0
        quality_score = max(0, 100 - (error_count * 20) - (warning_count * 5))
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues + warnings,
            quality_score=quality_score / 100.0,
            metadata={
                "error_count": error_count,
                "warning_count": warning_count,
                "total_issues": len(issues) + len(warnings)
            }
        )
    
    def _validate_paths(self, paths: Dict[str, Any], issues: List[ValidationIssue], warnings: List[ValidationIssue]):
        """Validate paths section."""
        if not paths:
            warnings.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Paths object is empty",
                location="paths",
                suggestion="Add at least one endpoint to paths"
            ))
            return
        
        for path, path_item in paths.items():
            if not path.startswith('/'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Path '{path}' must start with '/'",
                    location=f"paths.{path}",
                    suggestion=f"Change path to '/{path}'"
                ))
            
            if not isinstance(path_item, dict):
                continue
            
            # Check for valid HTTP methods
            valid_methods = ["get", "post", "put", "delete", "patch", "head", "options", "trace"]
            
            for method, operation in path_item.items():
                if method.lower() not in valid_methods:
                    continue
                
                if not isinstance(operation, dict):
                    continue
                
                # Check required operation fields
                if "responses" not in operation:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Missing responses in {method.upper()} {path}",
                        location=f"paths.{path}.{method}",
                        suggestion="Add 'responses' object with at least one response"
                    ))
                
                if "summary" not in operation:
                    warnings.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Missing summary in {method.upper()} {path}",
                        location=f"paths.{path}.{method}",
                        suggestion="Add 'summary' field to describe the operation"
                    ))
    
    def _validate_components(self, components: Dict[str, Any], issues: List[ValidationIssue], warnings: List[ValidationIssue]):
        """Validate components section."""
        # Validate schemas
        if "schemas" in components:
            schemas = components["schemas"]
            for schema_name, schema in schemas.items():
                if not isinstance(schema, dict):
                    continue
                
                if "type" not in schema and "$ref" not in schema:
                    warnings.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Schema '{schema_name}' missing type or $ref",
                        location=f"components.schemas.{schema_name}",
                        suggestion="Add 'type' field or '$ref' to the schema"
                    ))
        
        # Validate security schemes
        if "securitySchemes" in components:
            security_schemes = components["securitySchemes"]
            for scheme_name, scheme in security_schemes.items():
                if not isinstance(scheme, dict):
                    continue
                
                if "type" not in scheme:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Security scheme '{scheme_name}' missing type",
                        location=f"components.securitySchemes.{scheme_name}",
                        suggestion="Add 'type' field to security scheme"
                    ))
    
    def format_for_file(
        self,
        specification: Union[APISpecification, Dict[str, Any]],
        file_path: Union[str, Path],
        format_type: Optional[SpecificationFormat] = None
    ) -> str:
        """
        Format specification for writing to a file.
        
        Args:
            specification: The specification to format
            file_path: The target file path
            format_type: The format type (auto-detected from extension if not provided)
            
        Returns:
            Formatted specification content
        """
        if format_type is None:
            # Auto-detect format from file extension
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            
            if extension in ['.yml', '.yaml']:
                format_type = SpecificationFormat.OPENAPI_YAML
            elif extension == '.json':
                format_type = SpecificationFormat.OPENAPI_JSON
            else:
                # Default to YAML
                format_type = SpecificationFormat.OPENAPI_YAML
        
        return self.format_specification(specification, format_type)
    
    def minify_json(self, json_content: str) -> str:
        """Minify JSON content."""
        try:
            data = json.loads(json_content)
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to minify JSON: {str(e)}")
    
    def prettify_json(self, json_content: str, indent: int = 2) -> str:
        """Prettify JSON content."""
        try:
            data = json.loads(json_content)
            return json.dumps(data, indent=indent, sort_keys=True, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to prettify JSON: {str(e)}")
    
    def convert_format(
        self,
        content: str,
        from_format: SpecificationFormat,
        to_format: SpecificationFormat
    ) -> str:
        """
        Convert specification from one format to another.
        
        Args:
            content: The specification content
            from_format: The source format
            to_format: The target format
            
        Returns:
            Converted specification content
        """
        # Parse the content
        if from_format in [SpecificationFormat.OPENAPI_YAML, SpecificationFormat.SWAGGER_YAML]:
            try:
                spec_dict = yaml.safe_load(content)
            except Exception as e:
                raise ValueError(f"Failed to parse YAML: {str(e)}")
        elif from_format in [SpecificationFormat.OPENAPI_JSON, SpecificationFormat.SWAGGER_JSON]:
            try:
                spec_dict = json.loads(content)
            except Exception as e:
                raise ValueError(f"Failed to parse JSON: {str(e)}")
        else:
            raise ValueError(f"Unsupported source format: {from_format}")
        
        # Format to target format
        return self.format_specification(spec_dict, to_format)
    
    def get_format_info(self, format_type: SpecificationFormat) -> Dict[str, Any]:
        """Get information about a format type."""
        format_info = {
            SpecificationFormat.OPENAPI_YAML: {
                "name": "OpenAPI YAML",
                "extension": ".yml",
                "mime_type": "application/x-yaml",
                "description": "OpenAPI 3.0+ specification in YAML format"
            },
            SpecificationFormat.OPENAPI_JSON: {
                "name": "OpenAPI JSON",
                "extension": ".json",
                "mime_type": "application/json",
                "description": "OpenAPI 3.0+ specification in JSON format"
            },
            SpecificationFormat.SWAGGER_YAML: {
                "name": "Swagger YAML",
                "extension": ".yml",
                "mime_type": "application/x-yaml",
                "description": "Swagger 2.0 specification in YAML format"
            },
            SpecificationFormat.SWAGGER_JSON: {
                "name": "Swagger JSON",
                "extension": ".json",
                "mime_type": "application/json",
                "description": "Swagger 2.0 specification in JSON format"
            }
        }
        
        return format_info.get(format_type, {})
    
    def extract_metadata(self, content: str, format_type: SpecificationFormat) -> Dict[str, Any]:
        """Extract metadata from specification content."""
        try:
            # Parse content
            if format_type in [SpecificationFormat.OPENAPI_YAML, SpecificationFormat.SWAGGER_YAML]:
                spec_dict = yaml.safe_load(content)
            else:
                spec_dict = json.loads(content)
            
            # Extract metadata
            metadata = {
                "openapi_version": spec_dict.get("openapi", spec_dict.get("swagger", "unknown")),
                "title": spec_dict.get("info", {}).get("title", ""),
                "version": spec_dict.get("info", {}).get("version", ""),
                "description": spec_dict.get("info", {}).get("description", ""),
                "paths_count": len(spec_dict.get("paths", {})),
                "schemas_count": len(spec_dict.get("components", {}).get("schemas", {})),
                "security_schemes_count": len(spec_dict.get("components", {}).get("securitySchemes", {})),
                "servers_count": len(spec_dict.get("servers", [])),
                "tags_count": len(spec_dict.get("tags", []))
            }
            
            # Calculate operations count
            operations_count = 0
            for path_item in spec_dict.get("paths", {}).values():
                if isinstance(path_item, dict):
                    operations_count += len([
                        method for method in path_item.keys()
                        if method.lower() in ["get", "post", "put", "delete", "patch", "head", "options"]
                    ])
            
            metadata["operations_count"] = operations_count
            
            return metadata
            
        except Exception as e:
            return {"error": f"Failed to extract metadata: {str(e)}"}


# Utility functions

def format_specification_quick(
    specification: Dict[str, Any],
    format_type: str = "yaml"
) -> str:
    """Quick format utility function."""
    formatter = SpecificationFormatter()
    
    if format_type.lower() in ["yaml", "yml"]:
        spec_format = SpecificationFormat.OPENAPI_YAML
    elif format_type.lower() == "json":
        spec_format = SpecificationFormat.OPENAPI_JSON
    else:
        raise ValueError(f"Unsupported format: {format_type}")
    
    return formatter.format_specification(specification, spec_format)


def validate_specification_quick(specification: Dict[str, Any]) -> bool:
    """Quick validation utility function."""
    formatter = SpecificationFormatter()
    result = formatter.validate_specification(specification)
    return result.is_valid
