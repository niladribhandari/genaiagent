package ${BASE_PACKAGE}.service;

import ${BASE_PACKAGE}.dto.${ENTITY_NAME}Dto;
import ${BASE_PACKAGE}.model.${ENTITY_NAME};

import java.util.List;
import java.util.Optional;

/**
 * Service interface for ${ENTITY_NAME} operations
 */
public interface ${ENTITY_NAME}Service {

    /**
     * Create a new ${ENTITY_NAME_LOWER}
     *
     * @param ${ENTITY_NAME_LOWER}Dto the ${ENTITY_NAME_LOWER} data
     * @return the created ${ENTITY_NAME_LOWER}
     */
    ${ENTITY_NAME} create${ENTITY_NAME}(${ENTITY_NAME}Dto ${ENTITY_NAME_LOWER}Dto);

    /**
     * Get all ${ENTITY_NAME_PLURAL_LOWER}
     *
     * @return list of all ${ENTITY_NAME_PLURAL_LOWER}
     */
    List<${ENTITY_NAME}> getAll${ENTITY_NAME_PLURAL}();

    /**
     * Get ${ENTITY_NAME_LOWER} by ID
     *
     * @param id the ${ENTITY_NAME_LOWER} ID
     * @return Optional containing the ${ENTITY_NAME_LOWER} if found
     */
    Optional<${ENTITY_NAME}> get${ENTITY_NAME}ById(Long id);

    /**
     * Get ${ENTITY_NAME_LOWER} by name
     *
     * @param name the ${ENTITY_NAME_LOWER} name
     * @return Optional containing the ${ENTITY_NAME_LOWER} if found
     */
    Optional<${ENTITY_NAME}> get${ENTITY_NAME}ByName(String name);

    /**
     * Update an existing ${ENTITY_NAME_LOWER}
     *
     * @param id the ${ENTITY_NAME_LOWER} ID to update
     * @param ${ENTITY_NAME_LOWER}Dto the updated ${ENTITY_NAME_LOWER} data
     * @return the updated ${ENTITY_NAME_LOWER}
     */
    ${ENTITY_NAME} update${ENTITY_NAME}(Long id, ${ENTITY_NAME}Dto ${ENTITY_NAME_LOWER}Dto);

    /**
     * Delete a ${ENTITY_NAME_LOWER} by ID
     *
     * @param id the ${ENTITY_NAME_LOWER} ID to delete
     * @return true if deleted successfully, false otherwise
     */
    boolean delete${ENTITY_NAME}(Long id);

    /**
     * Get ${ENTITY_NAME_PLURAL_LOWER} by status
     *
     * @param status the status to filter by
     * @return list of ${ENTITY_NAME_PLURAL_LOWER} with the given status
     */
    List<${ENTITY_NAME}> get${ENTITY_NAME_PLURAL}ByStatus(String status);

    /**
     * Search ${ENTITY_NAME_PLURAL_LOWER} by name pattern
     *
     * @param namePattern the name pattern to search for
     * @return list of matching ${ENTITY_NAME_PLURAL_LOWER}
     */
    List<${ENTITY_NAME}> search${ENTITY_NAME_PLURAL}ByName(String namePattern);

    /**
     * Check if a ${ENTITY_NAME_LOWER} exists with the given name
     *
     * @param name the name to check
     * @return true if exists, false otherwise
     */
    boolean exists${ENTITY_NAME}ByName(String name);

    /**
     * Get count of ${ENTITY_NAME_PLURAL_LOWER} by status
     *
     * @param status the status to count
     * @return number of ${ENTITY_NAME_PLURAL_LOWER} with the given status
     */
    long count${ENTITY_NAME_PLURAL}ByStatus(String status);

    /**
     * Get all active ${ENTITY_NAME_PLURAL_LOWER}
     *
     * @return list of active ${ENTITY_NAME_PLURAL_LOWER}
     */
    List<${ENTITY_NAME}> getActive${ENTITY_NAME_PLURAL}();
}
