"""Spring Boot project generator."""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from core.interfaces import CodeGenerator
    from core.exceptions import CodeGenerationError
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode
    from domain.models.project_models import ProjectStructure, FileInfo
    from application.services.code_generation_service import CodeGenerationService
    from .dto_generator import DTOGenerator
    from .repository_generator import RepositoryGenerator
    from .mapper_generator import MapperGenerator
    from .validation_generator import ValidationGenerator
    from .workflow_generator import WorkflowGenerator
    from .calculation_generator import CalculationGenerator
    from .event_generator import EventGenerator
    from .audit_generator import AuditGenerator
except ImportError as e:
    # Fallback for standalone usage
    class CodeGenerator:
        pass
    class CodeGenerationError(Exception):
        pass
    class GenerationContext:
        pass
    class GeneratedCode:
        pass
    class ProjectStructure:
        pass
    class FileInfo:
        pass
    class CodeGenerationService:
        pass
    class DTOGenerator:
        pass
    class RepositoryGenerator:
        pass
    class MapperGenerator:
        pass
    class ValidationGenerator:
        pass
    class WorkflowGenerator:
        pass
    class CalculationGenerator:
        pass
    class EventGenerator:
        pass
    class AuditGenerator:
        pass


class SpringBootGenerator:
    """Generator for Spring Boot projects."""
    
    def __init__(self, code_generation_service: CodeGenerationService):
        self.code_service = code_generation_service
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized generators
        self.dto_generator = DTOGenerator(code_generation_service)
        self.repository_generator = RepositoryGenerator(code_generation_service)
        self.mapper_generator = MapperGenerator(code_generation_service)
        self.validation_generator = ValidationGenerator(code_generation_service)
        self.workflow_generator = WorkflowGenerator(code_generation_service)
        self.calculation_generator = CalculationGenerator(code_generation_service)
        self.event_generator = EventGenerator(code_generation_service)
        self.audit_generator = AuditGenerator(code_generation_service)
    
    def generate_project(self, context: GenerationContext) -> ProjectStructure:
        """Generate complete Spring Boot project structure."""
        try:
            project_files = []
            
            # Generate main application class
            app_context = self._create_application_context(context)
            app_code = self.code_service.generate_code(app_context)
            project_files.append(FileInfo(
                path=self._get_application_path(context),
                content=app_code.content,
                file_type="java"
            ))
            
            # Generate entity classes
            for entity_name in context.entities or [context.entity_name]:
                if entity_name:
                    entity_context = self._create_entity_context(context, entity_name)
                    entity_code = self.code_service.generate_code(entity_context)
                    project_files.append(FileInfo(
                        path=self._get_entity_path(context, entity_name),
                        content=entity_code.content,
                        file_type="java"
                    ))
            
            # Generate repository classes
            for entity_name in context.entities or [context.entity_name]:
                if entity_name:
                    repo_context = self._create_repository_context(context, entity_name)
                    repo_code = self.code_service.generate_code(repo_context)
                    project_files.append(FileInfo(
                        path=self._get_repository_path(context, entity_name),
                        content=repo_code.content,
                        file_type="java"
                    ))
            
            # Generate service classes
            for entity_name in context.entities or [context.entity_name]:
                if entity_name:
                    service_context = self._create_service_context(context, entity_name)
                    service_code = self.code_service.generate_code(service_context)
                    project_files.append(FileInfo(
                        path=self._get_service_path(context, entity_name),
                        content=service_code.content,
                        file_type="java"
                    ))
            
            # Generate controller classes
            for entity_name in context.entities or [context.entity_name]:
                if entity_name:
                    controller_context = self._create_controller_context(context, entity_name)
                    controller_code = self.code_service.generate_code(controller_context)
                    project_files.append(FileInfo(
                        path=self._get_controller_path(context, entity_name),
                        content=controller_code.content,
                        file_type="java"
                    ))
            
            # Generate enhanced DTOs with validation
            for entity_name in context.entities or [context.entity_name]:
                if entity_name:
                    # Generate Request DTO
                    request_dto_context = self._create_request_dto_context(context, entity_name)
                    request_dto_code = self.dto_generator.generate_request_dto(request_dto_context)
                    project_files.append(FileInfo(
                        path=self._get_request_dto_path(context, entity_name),
                        content=request_dto_code.content,
                        file_type="java"
                    ))
                    
                    # Generate Response DTO
                    response_dto_context = self._create_response_dto_context(context, entity_name)
                    response_dto_code = self.dto_generator.generate_response_dto(response_dto_context)
                    project_files.append(FileInfo(
                        path=self._get_response_dto_path(context, entity_name),
                        content=response_dto_code.content,
                        file_type="java"
                    ))
            
            # Generate enhanced repositories
            for entity_name in context.entities or [context.entity_name]:
                if entity_name:
                    enhanced_repo_context = self._create_enhanced_repository_context(context, entity_name)
                    enhanced_repo_code = self.repository_generator.generate_repository(enhanced_repo_context)
                    project_files.append(FileInfo(
                        path=self._get_repository_path(context, entity_name),
                        content=enhanced_repo_code.content,
                        file_type="java"
                    ))
            
            # Generate mappers for entity-DTO conversion
            for entity_name in context.entities or [context.entity_name]:
                if entity_name:
                    mapper_context = self._create_mapper_context(context, entity_name)
                    mapper_code = self.mapper_generator.generate_mapper(mapper_context)
                    project_files.append(FileInfo(
                        path=self._get_mapper_path(context, entity_name),
                        content=mapper_code.content,
                        file_type="java"
                    ))
            
            # Generate business logic components if required
            if self._requires_business_logic(context):
                for entity_name in context.entities or [context.entity_name]:
                    if entity_name:
                        # Generate workflow service
                        workflow_context = self._create_workflow_context(context, entity_name)
                        workflow_code = self.workflow_generator.generate_workflow(workflow_context)
                        project_files.append(FileInfo(
                            path=self._get_workflow_path(context, entity_name),
                            content=workflow_code.content,
                            file_type="java"
                        ))
                        
                        # Generate calculation engine if needed
                        if self._requires_calculations(context):
                            calc_context = self._create_calculation_context(context, entity_name)
                            calc_code = self.calculation_generator.generate_calculation_engine(calc_context)
                            project_files.append(FileInfo(
                                path=self._get_calculation_path(context, entity_name),
                                content=calc_code.content,
                                file_type="java"
                            ))
                        
                        # Generate event publisher
                        event_context = self._create_event_context(context, entity_name)
                        event_code = self.event_generator.generate_event_publisher(event_context)
                        project_files.append(FileInfo(
                            path=self._get_event_publisher_path(context, entity_name),
                            content=event_code.content,
                            file_type="java"
                        ))
                        
                        # Generate audit service if required
                        if self._requires_audit(context):
                            audit_context = self._create_audit_context(context, entity_name)
                            audit_code = self.audit_generator.generate_audit_service(audit_context)
                            project_files.append(FileInfo(
                                path=self._get_audit_path(context, entity_name),
                                content=audit_code.content,
                                file_type="java"
                            ))
            
            # Generate configuration files
            project_files.extend(self._generate_config_files(context))
            
            return ProjectStructure(
                name=context.project_name or context.entity_name,
                base_package=context.package_name,
                framework=context.framework,
                files=project_files,
                metadata={
                    'generator': 'SpringBootGenerator',
                    'entities_count': len(context.entities or [context.entity_name]),
                    'generated_at': context.created_at.isoformat(),
                    'business_logic_enabled': self._requires_business_logic(context),
                    'enhanced_features': {
                        'dto_generation': True,
                        'repository_enhancement': True,
                        'mapper_generation': True,
                        'validation_generation': True,
                        'workflow_generation': self._requires_business_logic(context),
                        'calculation_engine': self._requires_calculations(context),
                        'event_publishing': True,
                        'audit_trail': self._requires_audit(context)
                    }
                }
            )
            
        except Exception as e:
            raise CodeGenerationError(f"Failed to generate Spring Boot project: {str(e)}")
    
    def _create_application_context(self, base_context: GenerationContext) -> GenerationContext:
        """Create context for main application class."""
        return GenerationContext(
            entity_name=f"{base_context.project_name or base_context.entity_name}Application",
            package_name=base_context.package_name,
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("Application.java"),
            fields=[],
            requirements=["Spring Boot main class with @SpringBootApplication"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements
        )
    
    def _create_entity_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for entity class."""
        return GenerationContext(
            entity_name=entity_name,
            package_name=f"{base_context.package_name}.model",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("Entity.java"),
            fields=base_context.fields,
            requirements=["JPA entity with proper annotations", "Primary key field", "Getters and setters"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements
        )
    
    def _create_repository_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for repository class."""
        return GenerationContext(
            entity_name=f"{entity_name}Repository",
            package_name=f"{base_context.package_name}.repository",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("Repository.java"),
            fields=[],
            requirements=[f"JPA repository for {entity_name} entity", "CRUD operations"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name}
        )
    
    def _create_service_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for service class."""
        return GenerationContext(
            entity_name=f"{entity_name}Service",
            package_name=f"{base_context.package_name}.service",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("Service.java"),
            fields=[],
            requirements=[f"Business logic service for {entity_name}", "Transactional operations", "Exception handling"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name, 'repository_class': f"{entity_name}Repository"}
        )
    
    def _create_controller_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for controller class."""
        return GenerationContext(
            entity_name=f"{entity_name}Controller",
            package_name=f"{base_context.package_name}.controller",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("Controller.java"),
            fields=[],
            requirements=[f"REST controller for {entity_name}", "CRUD endpoints", "Input validation"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name, 'service_class': f"{entity_name}Service"}
        )
    
    def _generate_config_files(self, context: GenerationContext) -> List[FileInfo]:
        """Generate configuration files."""
        config_files = []
        
        # application.properties
        props_content = self._generate_application_properties(context)
        config_files.append(FileInfo(
            path="src/main/resources/application.properties",
            content=props_content,
            file_type="properties"
        ))
        
        # pom.xml
        pom_content = self._generate_pom_xml(context)
        config_files.append(FileInfo(
            path="pom.xml",
            content=pom_content,
            file_type="xml"
        ))
        
        return config_files
    
    def _generate_application_properties(self, context: GenerationContext) -> str:
        """Generate application.properties content."""
        return """# Server configuration
server.port=8080

# Database configuration
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=password

# JPA configuration
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true

# H2 Console (for development)
spring.h2.console.enabled=true
"""
    
    def _generate_pom_xml(self, context: GenerationContext) -> str:
        """Generate pom.xml content."""
        project_name = context.project_name or context.entity_name.lower()
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.0</version>
        <relativePath/>
    </parent>

    <groupId>{context.package_name}</groupId>
    <artifactId>{project_name}</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>{project_name}</name>
    <description>Spring Boot project generated by CodeGenerationAgent</description>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>"""
    
    def _get_template_path(self, template_name: str) -> str:
        """Get template path for given template name."""
        return f"templates/spring_boot/{template_name}"
    
    def _get_application_path(self, context: GenerationContext) -> str:
        """Get path for main application class."""
        package_path = context.package_name.replace('.', '/')
        app_name = f"{context.project_name or context.entity_name}Application"
        return f"src/main/java/{package_path}/{app_name}.java"
    
    def _get_entity_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for entity class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/model/{entity_name}.java"
    
    def _get_repository_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for repository class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/repository/{entity_name}Repository.java"
    
    def _get_service_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for service class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/service/{entity_name}Service.java"
    
    def _get_controller_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for controller class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/controller/{entity_name}Controller.java"
    
    # Enhanced context creation methods
    def _create_request_dto_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for request DTO generation."""
        return GenerationContext(
            entity_name=f"{entity_name}Request",
            package_name=f"{base_context.package_name}.dto",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("RequestDto.java"),
            fields=base_context.fields,
            requirements=["Request DTO with validation", "Jackson annotations", "Swagger documentation"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name, 'dto_type': 'request'}
        )
    
    def _create_response_dto_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for response DTO generation."""
        return GenerationContext(
            entity_name=f"{entity_name}Response",
            package_name=f"{base_context.package_name}.dto",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("ResponseDto.java"),
            fields=base_context.fields,
            requirements=["Response DTO with computed fields", "Jackson annotations", "Swagger documentation"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name, 'dto_type': 'response'}
        )
    
    def _create_enhanced_repository_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for enhanced repository generation."""
        return GenerationContext(
            entity_name=f"{entity_name}Repository",
            package_name=f"{base_context.package_name}.repository",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("Repository.java"),
            fields=base_context.fields,
            requirements=[f"Enhanced JPA repository for {entity_name}", "Custom query methods", "Pagination support"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name}
        )
    
    def _create_mapper_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for mapper generation."""
        return GenerationContext(
            entity_name=f"{entity_name}Mapper",
            package_name=f"{base_context.package_name}.mapper",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("Mapper.java"),
            fields=base_context.fields,
            requirements=["MapStruct mapper", "Entity-DTO conversion", "Bidirectional mapping"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name}
        )
    
    def _create_workflow_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for workflow generation."""
        return GenerationContext(
            entity_name=f"{entity_name}Workflow",
            package_name=f"{base_context.package_name}.workflow",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("WorkflowService.java"),
            fields=base_context.fields,
            requirements=["Business workflow orchestration", "Step-by-step processing", "Error handling"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name}
        )
    
    def _create_calculation_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for calculation engine generation."""
        return GenerationContext(
            entity_name=f"{entity_name}Calculation",
            package_name=f"{base_context.package_name}.calculation",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("CalculationEngine.java"),
            fields=base_context.fields,
            requirements=["Mathematical calculations", "BigDecimal precision", "Caching support"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name}
        )
    
    def _create_event_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for event publisher generation."""
        return GenerationContext(
            entity_name=f"{entity_name}Event",
            package_name=f"{base_context.package_name}.events",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("EventPublisher.java"),
            fields=base_context.fields,
            requirements=["Domain event publishing", "Async processing", "Event correlation"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name}
        )
    
    def _create_audit_context(self, base_context: GenerationContext, entity_name: str) -> GenerationContext:
        """Create context for audit service generation."""
        return GenerationContext(
            entity_name=f"{entity_name}Audit",
            package_name=f"{base_context.package_name}.audit",
            target_language=base_context.target_language,
            framework=base_context.framework,
            template_path=self._get_template_path("AuditService.java"),
            fields=base_context.fields,
            requirements=["Audit trail logging", "Change tracking", "User context capture"],
            use_ai_enhancement=base_context.use_ai_enhancement,
            enhancements=base_context.enhancements,
            additional_context={'entity_class': entity_name}
        )
    
    # Helper methods for business logic detection
    def _requires_business_logic(self, context: GenerationContext) -> bool:
        """Check if context requires business logic components."""
        # Check if any business rules or complex workflows are defined
        additional_context = context.additional_context or {}
        requirements = context.requirements or []
        
        business_indicators = ['workflow', 'business_rule', 'calculation', 'premium', 'risk', 'approval']
        
        for indicator in business_indicators:
            if any(indicator.lower() in req.lower() for req in requirements):
                return True
            
        return additional_context.get('has_business_logic', False)
    
    def _requires_calculations(self, context: GenerationContext) -> bool:
        """Check if context requires calculation engine."""
        requirements = context.requirements or []
        calc_indicators = ['calculation', 'premium', 'tax', 'discount', 'interest', 'formula']
        
        return any(indicator.lower() in req.lower() for req in requirements)
    
    def _requires_audit(self, context: GenerationContext) -> bool:
        """Check if context requires audit trail."""
        additional_context = context.additional_context or {}
        requirements = context.requirements or []
        
        audit_indicators = ['audit', 'track', 'history', 'log', 'change']
        
        for indicator in audit_indicators:
            if any(indicator.lower() in req.lower() for req in requirements):
                return True
                
        return additional_context.get('audit_enabled', True)  # Default to enabled
    
    # Path generation methods for new components
    def _get_request_dto_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for request DTO class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/dto/{entity_name}Request.java"
    
    def _get_response_dto_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for response DTO class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/dto/{entity_name}Response.java"
    
    def _get_mapper_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for mapper class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/mapper/{entity_name}Mapper.java"
    
    def _get_workflow_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for workflow service class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/workflow/{entity_name}WorkflowService.java"
    
    def _get_calculation_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for calculation engine class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/calculation/{entity_name}CalculationEngine.java"
    
    def _get_event_publisher_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for event publisher class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/events/{entity_name}EventPublisher.java"
    
    def _get_audit_path(self, context: GenerationContext, entity_name: str) -> str:
        """Get path for audit service class."""
        package_path = context.package_name.replace('.', '/')
        return f"src/main/java/{package_path}/audit/{entity_name}AuditService.java"
