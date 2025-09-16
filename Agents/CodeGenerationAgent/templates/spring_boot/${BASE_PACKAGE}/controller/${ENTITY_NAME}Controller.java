package ${BASE_PACKAGE};

import ${BASE_PACKAGE}.dto.${ENTITY_NAME}Request;
import ${BASE_PACKAGE}.dto.${ENTITY_NAME}Response;
import ${BASE_PACKAGE}.service.${ENTITY_NAME}Service;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.net.URI;
import java.util.UUID;

/**
 * This controller class handles all HTTP requests related to ${ENTITY_NAME_LOWER} entities.
 */
@RestController
@RequestMapping("${API_BASE_PATH}/${ENTITY_NAME_PLURAL_LOWER}")
@Tag(name = "${ENTITY_NAME}", description = "${ENTITY_NAME} management APIs")
@RequiredArgsConstructor
public class ${ENTITY_NAME}Controller {

    private final ${ENTITY_NAME}Service ${ENTITY_NAME_LOWER}Service;

    /**
     * Retrieves all ${ENTITY_NAME_PLURAL_LOWER}.
     *
     * @param page the page number to retrieve
     * @param size the number of records per page
     * @return the list of ${ENTITY_NAME_PLURAL_LOWER}
     */
    @GetMapping
    @Operation(summary = "Get all ${ENTITY_NAME_PLURAL_LOWER}", description = "Retrieves a paginated list of all ${ENTITY_NAME_PLURAL_LOWER}")
    public ResponseEntity<Page<${ENTITY_NAME}Response>> getAll${ENTITY_NAME_PLURAL}(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ResponseEntity.ok(${ENTITY_NAME_LOWER}Service.getAll${ENTITY_NAME_PLURAL}(page, size));
    }

    /**
     * Retrieves a ${ENTITY_NAME_LOWER} by their ID.
     *
     * @param id the ID of the ${ENTITY_NAME_LOWER}
     * @return the ${ENTITY_NAME_LOWER} record
     */
    @GetMapping("/{id}")
    @Operation(summary = "Get ${ENTITY_NAME_LOWER} by ID", description = "Retrieves a ${ENTITY_NAME_LOWER} by their ID")
    public ResponseEntity<${ENTITY_NAME}Response> get${ENTITY_NAME}ById(@PathVariable UUID id) {
        return ResponseEntity.ok(${ENTITY_NAME_LOWER}Service.get${ENTITY_NAME}ById(id));
    }

    /**
     * Creates a new ${ENTITY_NAME_LOWER}.
     *
     * @param request the ${ENTITY_NAME_LOWER} record to create
     * @return the created ${ENTITY_NAME_LOWER} record
     */
    @PostMapping
    @Operation(summary = "Create ${ENTITY_NAME_LOWER}", description = "Creates a new ${ENTITY_NAME_LOWER}")
    public ResponseEntity<${ENTITY_NAME}Response> create${ENTITY_NAME}(
            @RequestBody @Valid ${ENTITY_NAME}Request request) {
        ${ENTITY_NAME}Response response = ${ENTITY_NAME_LOWER}Service.create${ENTITY_NAME}(request);
        return ResponseEntity
            .created(URI.create("${API_BASE_PATH}/${ENTITY_NAME_PLURAL_LOWER}/" + response.getId()))
            .body(response);
    }

    /**
     * Updates an existing ${ENTITY_NAME_LOWER}.
     *
     * @param id      the ID of the ${ENTITY_NAME_LOWER} to update
     * @param request the updated ${ENTITY_NAME_LOWER} record
     * @return the updated ${ENTITY_NAME_LOWER} record
     */
    @PutMapping("/{id}")
    @Operation(summary = "Update ${ENTITY_NAME_LOWER}", description = "Updates an existing ${ENTITY_NAME_LOWER}")
    public ResponseEntity<${ENTITY_NAME}Response> update${ENTITY_NAME}(
            @PathVariable UUID id,
            @RequestBody @Valid ${ENTITY_NAME}Request request) {
        return ResponseEntity.ok(${ENTITY_NAME_LOWER}Service.update${ENTITY_NAME}(id, request));
    }

    /**
     * Deletes a ${ENTITY_NAME_LOWER}.
     *
     * @param id the ID of the ${ENTITY_NAME_LOWER} to delete
     * @return a response entity with no content
     */
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete ${ENTITY_NAME_LOWER}", description = "Deletes a ${ENTITY_NAME_LOWER}")
    public ResponseEntity<Void> delete${ENTITY_NAME}(@PathVariable UUID id) {
        ${ENTITY_NAME_LOWER}Service.delete${ENTITY_NAME}(id);
        return ResponseEntity.noContent().build();
    }
}
