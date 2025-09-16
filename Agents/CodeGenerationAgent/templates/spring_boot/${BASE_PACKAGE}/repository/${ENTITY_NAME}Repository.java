package ${BASE_PACKAGE}.repository;

import ${BASE_PACKAGE}.model.${ENTITY_NAME};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for ${ENTITY_NAME} entity
 */
@Repository
public interface ${ENTITY_NAME}Repository extends JpaRepository<${ENTITY_NAME}, Long> {

    /**
     * Find ${ENTITY_NAME_LOWER} by name
     *
     * @param name the name to search for
     * @return Optional containing the ${ENTITY_NAME_LOWER} if found
     */
    Optional<${ENTITY_NAME}> findByName(String name);

    /**
     * Find all ${ENTITY_NAME_PLURAL_LOWER} by status
     *
     * @param status the status to filter by
     * @return List of ${ENTITY_NAME_PLURAL_LOWER} with the given status
     */
    List<${ENTITY_NAME}> findByStatus(String status);

    /**
     * Find ${ENTITY_NAME_PLURAL_LOWER} by name containing (case-insensitive)
     *
     * @param name the name pattern to search for
     * @return List of ${ENTITY_NAME_PLURAL_LOWER} matching the pattern
     */
    List<${ENTITY_NAME}> findByNameContainingIgnoreCase(String name);

    /**
     * Check if a ${ENTITY_NAME_LOWER} exists with the given name
     *
     * @param name the name to check
     * @return true if exists, false otherwise
     */
    boolean existsByName(String name);

    /**
     * Count ${ENTITY_NAME_PLURAL_LOWER} by status
     *
     * @param status the status to count
     * @return number of ${ENTITY_NAME_PLURAL_LOWER} with the given status
     */
    long countByStatus(String status);

    /**
     * Custom query to find active ${ENTITY_NAME_PLURAL_LOWER}
     *
     * @return List of active ${ENTITY_NAME_PLURAL_LOWER}
     */
    @Query("SELECT e FROM ${ENTITY_NAME} e WHERE e.status = 'ACTIVE'")
    List<${ENTITY_NAME}> findActive${ENTITY_NAME_PLURAL}();

    /**
     * Custom query to find ${ENTITY_NAME_PLURAL_LOWER} by name and status
     *
     * @param name the name to search for
     * @param status the status to filter by
     * @return List of matching ${ENTITY_NAME_PLURAL_LOWER}
     */
    @Query("SELECT e FROM ${ENTITY_NAME} e WHERE e.name LIKE %:name% AND e.status = :status")
    List<${ENTITY_NAME}> findByNameLikeAndStatus(@Param("name") String name, @Param("status") String status);
}
