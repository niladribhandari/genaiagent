"""
Integration extractor utility for parsing external services from API specifications.
"""

from typing import Dict, List, Any, Optional
import re


class ExternalService:
    """Represents an external service integration."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.display_name = config.get('name', name)
        self.description = config.get('description', '')
        self.base_url = config.get('base_url', config.get('endpoint', ''))
        self.endpoints = config.get('endpoints', {})
        self.methods = config.get('methods', ['GET', 'POST'])
        self.features = config.get('features', [])
        self.authentication = config.get('authentication', {})
        self.resilience = config.get('resilience', {})
        self.timeout = config.get('timeout', 30000)
        
        # Generate client class name
        self.client_class_name = self._generate_client_class_name()
        self.service_variable_name = self._generate_service_variable_name()
    
    def _generate_client_class_name(self) -> str:
        """Generate Java class name for the client."""
        # Convert service name to PascalCase
        words = re.findall(r'\b\w+', self.name)
        class_name = ''.join(word.capitalize() for word in words)
        if not class_name.endswith('Client'):
            class_name += 'Client'
        return class_name
    
    def _generate_service_variable_name(self) -> str:
        """Generate variable name for dependency injection."""
        # Convert to camelCase
        words = re.findall(r'\b\w+', self.name.lower())
        if words:
            variable_name = words[0]
            for word in words[1:]:
                variable_name += word.capitalize()
        else:
            variable_name = 'service'
        
        if not variable_name.endswith('Client'):
            variable_name += 'Client'
        return variable_name
    
    def get_authentication_headers(self) -> List[str]:
        """Get authentication headers for HTTP requests."""
        auth_headers = []
        auth_type = self.authentication.get('type', '').upper()
        
        if auth_type == 'API_KEY':
            header_name = self.authentication.get('header', 'X-API-Key')
            config_key = self.authentication.get('config_key', 'API_KEY')
            auth_headers.append(f'headers.set("{header_name}", apiKey);')
        elif auth_type == 'BEARER_TOKEN':
            config_key = self.authentication.get('config_key', 'BEARER_TOKEN')
            auth_headers.append(f'headers.setBearerAuth(bearerToken);')
        elif auth_type == 'BASIC_AUTH':
            auth_headers.append(f'headers.setBasicAuth(username, password);')
        
        return auth_headers
    
    def get_resilience_config(self) -> Dict[str, Any]:
        """Get resilience configuration for circuit breaker, retry, etc."""
        return {
            'circuit_breaker': self.resilience.get('circuit_breaker', True),
            'retry_attempts': self.resilience.get('retry_attempts', 3),
            'timeout': self.resilience.get('timeout', self.timeout),
            'exponential_backoff': self.resilience.get('exponential_backoff', True),
            'fallback_enabled': self.resilience.get('fallback_enabled', True)
        }


class IntegrationExtractor:
    """Extract external service integrations from API specifications."""
    
    @staticmethod
    def extract_external_services(spec_data: Dict[str, Any]) -> List[ExternalService]:
        """
        Extract external services from API specification.
        
        Args:
            spec_data: The complete API specification data
            
        Returns:
            List of ExternalService objects
        """
        services = []
        
        # Look for integrations section
        integrations = spec_data.get('integrations', {})
        if not integrations:
            # Try alternative section names
            integrations = spec_data.get('external_services', {})
            if not integrations:
                integrations = spec_data.get('services', {})
        
        if isinstance(integrations, list):
            # Handle list format
            for service_config in integrations:
                if isinstance(service_config, dict) and 'name' in service_config:
                    service_name = service_config['name']
                    service = ExternalService(service_name, service_config)
                    services.append(service)
        elif isinstance(integrations, dict):
            # Handle dictionary format
            for service_name, service_config in integrations.items():
                if isinstance(service_config, dict):
                    service = ExternalService(service_name, service_config)
                    services.append(service)
        
        return services
    
    @staticmethod
    def get_integration_dependencies() -> List[str]:
        """Get Maven dependencies required for integrations."""
        return [
            'org.springframework.boot:spring-boot-starter-web',
            'org.springframework.boot:spring-boot-starter-webflux',
            'org.springframework.retry:spring-retry',
            'org.springframework.boot:spring-boot-starter-aop',
            'io.github.resilience4j:resilience4j-spring-boot2',
            'io.github.resilience4j:resilience4j-circuitbreaker',
            'io.github.resilience4j:resilience4j-retry',
            'io.github.resilience4j:resilience4j-timeout'
        ]
    
    @staticmethod
    def get_integration_configuration_properties(services: List[ExternalService]) -> Dict[str, str]:
        """Generate configuration properties for external services."""
        properties = {}
        
        for service in services:
            service_key = service.name.lower().replace(' ', '-').replace('_', '-')
            
            # Base URL
            properties[f'external.services.{service_key}.url'] = service.base_url or 'http://localhost:8080'
            
            # Timeout
            properties[f'external.services.{service_key}.timeout'] = str(service.timeout)
            
            # Resilience settings
            resilience = service.get_resilience_config()
            properties[f'external.services.{service_key}.circuit-breaker.enabled'] = str(resilience['circuit_breaker']).lower()
            properties[f'external.services.{service_key}.retry.max-attempts'] = str(resilience['retry_attempts'])
            
            # Authentication
            auth = service.authentication
            if auth:
                auth_type = auth.get('type', '').upper()
                if auth_type == 'API_KEY':
                    config_key = auth.get('config_key', f'{service_key.upper().replace("-", "_")}_API_KEY')
                    properties[f'external.services.{service_key}.auth.api-key'] = f'${{{config_key}:your-api-key}}'
                elif auth_type == 'BEARER_TOKEN':
                    config_key = auth.get('config_key', f'{service_key.upper().replace("-", "_")}_TOKEN')
                    properties[f'external.services.{service_key}.auth.bearer-token'] = f'${{{config_key}:your-bearer-token}}'
        
        return properties
    
    @staticmethod
    def generate_service_method_signatures(service: ExternalService) -> List[Dict[str, str]]:
        """Generate method signatures for service client."""
        methods = []
        
        # Default CRUD operations if no specific endpoints defined
        if not service.endpoints:
            methods.extend([
                {
                    'name': f'get{service.client_class_name.replace("Client", "")}',
                    'return_type': f'{service.client_class_name.replace("Client", "")}Response',
                    'parameters': 'UUID id',
                    'http_method': 'GET',
                    'path': f'/{service.name.lower()}s/{{id}}',
                    'description': f'Get {service.name.lower()} by ID'
                },
                {
                    'name': f'create{service.client_class_name.replace("Client", "")}',
                    'return_type': f'{service.client_class_name.replace("Client", "")}Response',
                    'parameters': f'{service.client_class_name.replace("Client", "")}Request request',
                    'http_method': 'POST',
                    'path': f'/{service.name.lower()}s',
                    'description': f'Create new {service.name.lower()}'
                },
                {
                    'name': f'update{service.client_class_name.replace("Client", "")}',
                    'return_type': f'{service.client_class_name.replace("Client", "")}Response',
                    'parameters': f'UUID id, {service.client_class_name.replace("Client", "")}Request request',
                    'http_method': 'PUT',
                    'path': f'/{service.name.lower()}s/{{id}}',
                    'description': f'Update {service.name.lower()}'
                }
            ])
        else:
            # Generate methods based on defined endpoints
            for endpoint_name, endpoint_config in service.endpoints.items():
                method_name = endpoint_name.replace('_', '').replace('-', '')
                methods.append({
                    'name': method_name,
                    'return_type': 'ResponseEntity<String>',
                    'parameters': 'Object request',
                    'http_method': endpoint_config.get('method', 'POST'),
                    'path': endpoint_config.get('path', f'/{endpoint_name}'),
                    'description': endpoint_config.get('description', f'{endpoint_name} operation')
                })
        
        # Add feature-based methods
        for feature in service.features:
            feature_method = feature.lower().replace(' ', '_').replace('-', '_')
            methods.append({
                'name': feature_method,
                'return_type': 'ResponseEntity<String>',
                'parameters': 'Object request',
                'http_method': 'POST',
                'path': f'/{feature_method}',
                'description': f'{feature} operation'
            })
        
        return methods


# Export main classes and functions
__all__ = ['ExternalService', 'IntegrationExtractor']
