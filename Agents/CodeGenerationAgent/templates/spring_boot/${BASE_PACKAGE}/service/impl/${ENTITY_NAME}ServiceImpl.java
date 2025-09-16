package ${BASE_PACKAGE}.service.impl;

import ${BASE_PACKAGE}.dto.${ENTITY_NAME}Dto;
import ${BASE_PACKAGE}.model.${ENTITY_NAME};
import ${BASE_PACKAGE}.repository.${ENTITY_NAME}Repository;
import ${BASE_PACKAGE}.service.${ENTITY_NAME}Service;
import ${BASE_PACKAGE}.exception.ResourceNotFoundException;
import ${BASE_PACKAGE}.exception.BadRequestException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Optional;

/**
 * Service implementation for ${ENTITY_NAME} operations
 */
@Service
@Transactional
public class ${ENTITY_NAME}ServiceImpl implements ${ENTITY_NAME}Service {

    private static final Logger logger = LoggerFactory.getLogger(${ENTITY_NAME}ServiceImpl.class);

    private final ${ENTITY_NAME}Repository ${ENTITY_NAME_LOWER}Repository;

    @Autowired
    public ${ENTITY_NAME}ServiceImpl(${ENTITY_NAME}Repository ${ENTITY_NAME_LOWER}Repository) {
        this.${ENTITY_NAME_LOWER}Repository = ${ENTITY_NAME_LOWER}Repository;
    }

    @Override
    public ${ENTITY_NAME} create${ENTITY_NAME}(${ENTITY_NAME}Dto ${ENTITY_NAME_LOWER}Dto) {
        logger.info("Creating new ${ENTITY_NAME_LOWER} with name: {}", ${ENTITY_NAME_LOWER}Dto.getName());

        // Check if ${ENTITY_NAME_LOWER} with same name already exists
        if (${ENTITY_NAME_LOWER}Repository.existsByName(${ENTITY_NAME_LOWER}Dto.getName())) {
            throw new BadRequestException("${ENTITY_NAME} with name '" + ${ENTITY_NAME_LOWER}Dto.getName() + "' already exists");
        }

        ${ENTITY_NAME} ${ENTITY_NAME_LOWER} = new ${ENTITY_NAME}();
        ${ENTITY_NAME_LOWER}.setName(${ENTITY_NAME_LOWER}Dto.getName());
        ${ENTITY_NAME_LOWER}.setDescription(${ENTITY_NAME_LOWER}Dto.getDescription());
        ${ENTITY_NAME_LOWER}.setStatus(${ENTITY_NAME_LOWER}Dto.getStatus());

        ${ENTITY_NAME} saved${ENTITY_NAME} = ${ENTITY_NAME_LOWER}Repository.save(${ENTITY_NAME_LOWER});
        logger.info("Successfully created ${ENTITY_NAME_LOWER} with ID: {}", saved${ENTITY_NAME}.getId());

        return saved${ENTITY_NAME};
    }

    @Override
    @Transactional(readOnly = true)
    public List<${ENTITY_NAME}> getAll${ENTITY_NAME_PLURAL}() {
        logger.info("Retrieving all ${ENTITY_NAME_PLURAL_LOWER}");
        return ${ENTITY_NAME_LOWER}Repository.findAll();
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<${ENTITY_NAME}> get${ENTITY_NAME}ById(Long id) {
        logger.info("Retrieving ${ENTITY_NAME_LOWER} with ID: {}", id);
        return ${ENTITY_NAME_LOWER}Repository.findById(id);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<${ENTITY_NAME}> get${ENTITY_NAME}ByName(String name) {
        logger.info("Retrieving ${ENTITY_NAME_LOWER} with name: {}", name);
        return ${ENTITY_NAME_LOWER}Repository.findByName(name);
    }

    @Override
    public ${ENTITY_NAME} update${ENTITY_NAME}(Long id, ${ENTITY_NAME}Dto ${ENTITY_NAME_LOWER}Dto) {
        logger.info("Updating ${ENTITY_NAME_LOWER} with ID: {}", id);

        ${ENTITY_NAME} existing${ENTITY_NAME} = ${ENTITY_NAME_LOWER}Repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("${ENTITY_NAME} not found with ID: " + id));

        // Check if another ${ENTITY_NAME_LOWER} with the same name exists (excluding current one)
        Optional<${ENTITY_NAME}> existingByName = ${ENTITY_NAME_LOWER}Repository.findByName(${ENTITY_NAME_LOWER}Dto.getName());
        if (existingByName.isPresent() && !existingByName.get().getId().equals(id)) {
            throw new BadRequestException("${ENTITY_NAME} with name '" + ${ENTITY_NAME_LOWER}Dto.getName() + "' already exists");
        }

        existing${ENTITY_NAME}.setName(${ENTITY_NAME_LOWER}Dto.getName());
        existing${ENTITY_NAME}.setDescription(${ENTITY_NAME_LOWER}Dto.getDescription());
        existing${ENTITY_NAME}.setStatus(${ENTITY_NAME_LOWER}Dto.getStatus());

        ${ENTITY_NAME} updated${ENTITY_NAME} = ${ENTITY_NAME_LOWER}Repository.save(existing${ENTITY_NAME});
        logger.info("Successfully updated ${ENTITY_NAME_LOWER} with ID: {}", id);

        return updated${ENTITY_NAME};
    }

    @Override
    public boolean delete${ENTITY_NAME}(Long id) {
        logger.info("Deleting ${ENTITY_NAME_LOWER} with ID: {}", id);

        if (!${ENTITY_NAME_LOWER}Repository.existsById(id)) {
            logger.warn("${ENTITY_NAME} with ID {} not found for deletion", id);
            return false;
        }

        ${ENTITY_NAME_LOWER}Repository.deleteById(id);
        logger.info("Successfully deleted ${ENTITY_NAME_LOWER} with ID: {}", id);
        return true;
    }

    @Override
    @Transactional(readOnly = true)
    public List<${ENTITY_NAME}> get${ENTITY_NAME_PLURAL}ByStatus(String status) {
        logger.info("Retrieving ${ENTITY_NAME_PLURAL_LOWER} with status: {}", status);
        return ${ENTITY_NAME_LOWER}Repository.findByStatus(status);
    }

    @Override
    @Transactional(readOnly = true)
    public List<${ENTITY_NAME}> search${ENTITY_NAME_PLURAL}ByName(String namePattern) {
        logger.info("Searching ${ENTITY_NAME_PLURAL_LOWER} with name pattern: {}", namePattern);
        return ${ENTITY_NAME_LOWER}Repository.findByNameContainingIgnoreCase(namePattern);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean exists${ENTITY_NAME}ByName(String name) {
        logger.info("Checking if ${ENTITY_NAME_LOWER} exists with name: {}", name);
        return ${ENTITY_NAME_LOWER}Repository.existsByName(name);
    }

    @Override
    @Transactional(readOnly = true)
    public long count${ENTITY_NAME_PLURAL}ByStatus(String status) {
        logger.info("Counting ${ENTITY_NAME_PLURAL_LOWER} with status: {}", status);
        return ${ENTITY_NAME_LOWER}Repository.countByStatus(status);
    }

    @Override
    @Transactional(readOnly = true)
    public List<${ENTITY_NAME}> getActive${ENTITY_NAME_PLURAL}() {
        logger.info("Retrieving all active ${ENTITY_NAME_PLURAL_LOWER}");
        return ${ENTITY_NAME_LOWER}Repository.findActive${ENTITY_NAME_PLURAL}();
    }
}
