"""
Data models for API Specification Writing System
Defines core entities and data structures
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SpecificationFormat(Enum):
    """Supported specification formats."""
    OPENAPI_YAML = "openapi_yaml"
    OPENAPI_JSON = "openapi_json"
    SWAGGER_YAML = "swagger_yaml"
    SWAGGER_JSON = "swagger_json"


class SecuritySchemeType(Enum):
    """Security scheme types."""
    API_KEY = "apiKey"
    HTTP = "http"
    OAUTH2 = "oauth2"
    OPENID_CONNECT = "openIdConnect"


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"
    OPTIONS = "options"


class ParameterLocation(Enum):
    """Parameter locations."""
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    COOKIE = "cookie"


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class UserRequirement:
    """Represents user requirements for API specification."""
    id: str
    title: str
    description: str
    functional_requirements: List[str] = field(default_factory=list)
    non_functional_requirements: List[str] = field(default_factory=list)
    business_entities: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    security_requirements: List[str] = field(default_factory=list)
    data_formats: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    path: str
    method: HTTPMethod
    summary: str
    description: str = ""
    operation_id: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: List['APIParameter'] = field(default_factory=list)
    request_body: Optional['RequestBody'] = None
    responses: Dict[str, 'APIResponse'] = field(default_factory=dict)
    security: List[Dict[str, List[str]]] = field(default_factory=list)
    deprecated: bool = False
    examples: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIParameter:
    """Represents an API parameter."""
    name: str
    location: ParameterLocation
    description: str = ""
    required: bool = False
    deprecated: bool = False
    schema: Dict[str, Any] = field(default_factory=dict)
    example: Any = None
    examples: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestBody:
    """Represents a request body."""
    description: str = ""
    content: Dict[str, 'MediaType'] = field(default_factory=dict)
    required: bool = False


@dataclass
class MediaType:
    """Represents a media type."""
    schema: Dict[str, Any] = field(default_factory=dict)
    example: Any = None
    examples: Dict[str, Any] = field(default_factory=dict)
    encoding: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIResponse:
    """Represents an API response."""
    description: str
    headers: Dict[str, 'Header'] = field(default_factory=dict)
    content: Dict[str, MediaType] = field(default_factory=dict)
    links: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Header:
    """Represents a response header."""
    description: str = ""
    required: bool = False
    deprecated: bool = False
    schema: Dict[str, Any] = field(default_factory=dict)
    example: Any = None


@dataclass
class SecurityScheme:
    """Represents a security scheme."""
    type: SecuritySchemeType
    description: str = ""
    name: str = ""
    location: str = ""  # For apiKey type
    scheme: str = ""  # For http type
    bearer_format: str = ""  # For http bearer
    flows: Dict[str, Any] = field(default_factory=dict)  # For oauth2
    openid_connect_url: str = ""  # For openIdConnect


@dataclass
class APIInfo:
    """Represents API information."""
    title: str
    version: str
    description: str = ""
    terms_of_service: str = ""
    contact: Dict[str, str] = field(default_factory=dict)
    license: Dict[str, str] = field(default_factory=dict)


@dataclass
class Server:
    """Represents an API server."""
    url: str
    description: str = ""
    variables: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class Tag:
    """Represents an API tag."""
    name: str
    description: str = ""
    external_docs: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExternalDocumentation:
    """Represents external documentation."""
    description: str = ""
    url: str = ""


@dataclass
class APISpecification:
    """Complete API specification."""
    openapi: str = "3.0.3"
    info: APIInfo = field(default_factory=lambda: APIInfo("API", "1.0.0"))
    servers: List[Server] = field(default_factory=list)
    paths: Dict[str, Dict[str, APIEndpoint]] = field(default_factory=dict)
    components: Dict[str, Any] = field(default_factory=dict)
    security: List[Dict[str, List[str]]] = field(default_factory=list)
    tags: List[Tag] = field(default_factory=list)
    external_docs: Optional[ExternalDocumentation] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert specification to dictionary format."""
        spec_dict = {
            "openapi": self.openapi,
            "info": {
                "title": self.info.title,
                "version": self.info.version,
                "description": self.info.description
            }
        }
        
        if self.info.terms_of_service:
            spec_dict["info"]["termsOfService"] = self.info.terms_of_service
        
        if self.info.contact:
            spec_dict["info"]["contact"] = self.info.contact
        
        if self.info.license:
            spec_dict["info"]["license"] = self.info.license
        
        if self.servers:
            spec_dict["servers"] = [
                {"url": server.url, "description": server.description}
                for server in self.servers
            ]
        
        # Convert paths
        if self.paths:
            spec_dict["paths"] = {}
            for path, methods in self.paths.items():
                spec_dict["paths"][path] = {}
                for method_name, endpoint in methods.items():
                    spec_dict["paths"][path][method_name] = self._endpoint_to_dict(endpoint)
        
        if self.components:
            spec_dict["components"] = self.components
        
        if self.security:
            spec_dict["security"] = self.security
        
        if self.tags:
            spec_dict["tags"] = [
                {"name": tag.name, "description": tag.description}
                for tag in self.tags
            ]
        
        if self.external_docs:
            spec_dict["externalDocs"] = {
                "description": self.external_docs.description,
                "url": self.external_docs.url
            }
        
        return spec_dict
    
    def _endpoint_to_dict(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Convert endpoint to dictionary format."""
        endpoint_dict = {
            "summary": endpoint.summary,
            "description": endpoint.description
        }
        
        if endpoint.operation_id:
            endpoint_dict["operationId"] = endpoint.operation_id
        
        if endpoint.tags:
            endpoint_dict["tags"] = endpoint.tags
        
        if endpoint.parameters:
            endpoint_dict["parameters"] = [
                self._parameter_to_dict(param) for param in endpoint.parameters
            ]
        
        if endpoint.request_body:
            endpoint_dict["requestBody"] = self._request_body_to_dict(endpoint.request_body)
        
        if endpoint.responses:
            endpoint_dict["responses"] = {
                status: self._response_to_dict(response)
                for status, response in endpoint.responses.items()
            }
        
        if endpoint.security:
            endpoint_dict["security"] = endpoint.security
        
        if endpoint.deprecated:
            endpoint_dict["deprecated"] = True
        
        return endpoint_dict
    
    def _parameter_to_dict(self, parameter: APIParameter) -> Dict[str, Any]:
        """Convert parameter to dictionary format."""
        param_dict = {
            "name": parameter.name,
            "in": parameter.location.value,
            "description": parameter.description,
            "required": parameter.required
        }
        
        if parameter.schema:
            param_dict["schema"] = parameter.schema
        
        if parameter.example is not None:
            param_dict["example"] = parameter.example
        
        if parameter.examples:
            param_dict["examples"] = parameter.examples
        
        if parameter.deprecated:
            param_dict["deprecated"] = True
        
        return param_dict
    
    def _request_body_to_dict(self, request_body: RequestBody) -> Dict[str, Any]:
        """Convert request body to dictionary format."""
        body_dict = {
            "description": request_body.description,
            "required": request_body.required
        }
        
        if request_body.content:
            body_dict["content"] = {
                media_type: self._media_type_to_dict(media)
                for media_type, media in request_body.content.items()
            }
        
        return body_dict
    
    def _media_type_to_dict(self, media_type: MediaType) -> Dict[str, Any]:
        """Convert media type to dictionary format."""
        media_dict = {}
        
        if media_type.schema:
            media_dict["schema"] = media_type.schema
        
        if media_type.example is not None:
            media_dict["example"] = media_type.example
        
        if media_type.examples:
            media_dict["examples"] = media_type.examples
        
        if media_type.encoding:
            media_dict["encoding"] = media_type.encoding
        
        return media_dict
    
    def _response_to_dict(self, response: APIResponse) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        response_dict = {
            "description": response.description
        }
        
        if response.headers:
            response_dict["headers"] = {
                name: self._header_to_dict(header)
                for name, header in response.headers.items()
            }
        
        if response.content:
            response_dict["content"] = {
                media_type: self._media_type_to_dict(media)
                for media_type, media in response.content.items()
            }
        
        if response.links:
            response_dict["links"] = response.links
        
        return response_dict
    
    def _header_to_dict(self, header: Header) -> Dict[str, Any]:
        """Convert header to dictionary format."""
        header_dict = {
            "description": header.description
        }
        
        if header.required:
            header_dict["required"] = True
        
        if header.schema:
            header_dict["schema"] = header.schema
        
        if header.example is not None:
            header_dict["example"] = header.example
        
        if header.deprecated:
            header_dict["deprecated"] = True
        
        return header_dict


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: ValidationSeverity
    message: str
    location: str = ""
    code: str = ""
    suggestion: str = ""
    examples: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Represents validation results."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    quality_score: float = 0.0
    completeness_score: float = 0.0
    security_score: float = 0.0
    best_practices_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_errors(self) -> List[ValidationIssue]:
        """Get all error issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]
    
    def get_warnings(self) -> List[ValidationIssue]:
        """Get all warning issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]
    
    def get_info(self) -> List[ValidationIssue]:
        """Get all info issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.INFO]


@dataclass
class AnalysisResult:
    """Represents requirement analysis results."""
    entities: List[str] = field(default_factory=list)
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    data_models: List[Dict[str, Any]] = field(default_factory=list)
    security_requirements: List[str] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    api_patterns: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DesignResult:
    """Represents API design results."""
    api_structure: Dict[str, Any] = field(default_factory=dict)
    paths: Dict[str, Any] = field(default_factory=dict)
    schemas: Dict[str, Any] = field(default_factory=dict)
    security_schemes: Dict[str, Any] = field(default_factory=dict)
    components: Dict[str, Any] = field(default_factory=dict)
    design_patterns: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpecificationResult:
    """Represents the final specification generation result."""
    specification: APISpecification
    format: SpecificationFormat
    content: str
    documentation: str = ""
    examples: Dict[str, Any] = field(default_factory=dict)
    validation_result: Optional[ValidationResult] = None
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_file_extension(self) -> str:
        """Get appropriate file extension for the format."""
        if self.format in [SpecificationFormat.OPENAPI_YAML, SpecificationFormat.SWAGGER_YAML]:
            return ".yml"
        elif self.format in [SpecificationFormat.OPENAPI_JSON, SpecificationFormat.SWAGGER_JSON]:
            return ".json"
        else:
            return ".yml"
    
    def get_filename(self, base_name: str = "api_spec") -> str:
        """Get filename with appropriate extension."""
        return f"{base_name}{self.get_file_extension()}"


@dataclass
class WorkflowStatus:
    """Represents workflow execution status."""
    workflow_id: str
    current_step: str
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    total_steps: int = 0
    progress_percentage: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    is_complete: bool = False
    is_failed: bool = False
    error_message: str = ""
    results: Dict[str, Any] = field(default_factory=dict)
    
    def mark_step_complete(self, step: str):
        """Mark a step as completed."""
        if step not in self.completed_steps:
            self.completed_steps.append(step)
        if step in self.failed_steps:
            self.failed_steps.remove(step)
        self._update_progress()
    
    def mark_step_failed(self, step: str, error: str = ""):
        """Mark a step as failed."""
        if step not in self.failed_steps:
            self.failed_steps.append(step)
        if step in self.completed_steps:
            self.completed_steps.remove(step)
        if error:
            self.error_message = error
        self.is_failed = True
        self._update_progress()
    
    def _update_progress(self):
        """Update progress percentage."""
        if self.total_steps > 0:
            self.progress_percentage = (len(self.completed_steps) / self.total_steps) * 100
            
            if len(self.completed_steps) == self.total_steps:
                self.is_complete = True
                self.end_time = datetime.now()


# Utility functions for creating data models

def create_user_requirement(
    title: str,
    description: str,
    functional_reqs: List[str] = None,
    entities: List[str] = None
) -> UserRequirement:
    """Create a UserRequirement instance with defaults."""
    return UserRequirement(
        id=f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        title=title,
        description=description,
        functional_requirements=functional_reqs or [],
        business_entities=entities or []
    )


def create_api_endpoint(
    path: str,
    method: Union[HTTPMethod, str],
    summary: str,
    description: str = ""
) -> APIEndpoint:
    """Create an APIEndpoint instance with defaults."""
    if isinstance(method, str):
        method = HTTPMethod(method.lower())
    
    return APIEndpoint(
        path=path,
        method=method,
        summary=summary,
        description=description,
        operation_id=f"{method.value}_{path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}"
    )


def create_api_parameter(
    name: str,
    location: Union[ParameterLocation, str],
    param_type: str = "string",
    required: bool = False,
    description: str = ""
) -> APIParameter:
    """Create an APIParameter instance with defaults."""
    if isinstance(location, str):
        location = ParameterLocation(location)
    
    return APIParameter(
        name=name,
        location=location,
        description=description,
        required=required,
        schema={"type": param_type}
    )


def create_validation_issue(
    severity: Union[ValidationSeverity, str],
    message: str,
    location: str = "",
    suggestion: str = ""
) -> ValidationIssue:
    """Create a ValidationIssue instance."""
    if isinstance(severity, str):
        severity = ValidationSeverity(severity)
    
    return ValidationIssue(
        severity=severity,
        message=message,
        location=location,
        suggestion=suggestion
    )
