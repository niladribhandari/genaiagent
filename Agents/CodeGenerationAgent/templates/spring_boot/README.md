# ${PROJECT_NAME}

## Description
${PROJECT_DESCRIPTION}

## Prerequisites
- Java 17 or higher
- Maven 3.8+
- Docker and Docker Compose (optional)

## Getting Started

### Local Development
1. Clone the repository
```bash
git clone ${REPOSITORY_URL}
cd ${PROJECT_NAME}
```

2. Set up the database
```bash
# Using Docker
docker-compose up db -d

# Or use your local PostgreSQL instance
# Create a database named ${DATABASE_NAME}
```

3. Configure application
- Copy `src/main/resources/application.yml` to `src/main/resources/application-dev.yml`
- Update the database configuration in `application-dev.yml`

4. Run the application
```bash
# Using Maven
mvn spring-boot:run -Dspring.profiles.active=dev

# Or using Docker Compose
docker-compose up
```

## API Documentation
- Swagger UI: http://localhost:8080/api/v1/swagger-ui.html
- OpenAPI Spec: http://localhost:8080/api/v1/api-docs

## Testing
```bash
# Run unit tests
mvn test

# Run integration tests
mvn verify
```

## Building
```bash
# Create JAR file
mvn clean package

# Build Docker image
docker build -t ${PROJECT_NAME}:latest .
```

## Project Structure
```
src
├── main
│   ├── java/com/${COMPANY_NAME}/${PROJECT_NAME}
│   │   ├── adapter            # Adapters (REST Controllers, JPA Repositories)
│   │   ├── application        # Application services and ports
│   │   ├── domain            # Domain model and business logic
│   │   └── infrastructure    # Infrastructure configuration
│   └── resources
│       ├── db/migration      # Flyway database migrations
│       └── application.yml   # Application configuration
└── test
    └── java                 # Test files
```

## Contributing
1. Create a feature branch
2. Commit your changes
3. Push to the branch
4. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details
