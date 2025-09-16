package ${BASE_PACKAGE}.workflow;

import ${BASE_PACKAGE}.entity.${ENTITY_NAME};
import ${BASE_PACKAGE}.service.${ENTITY_NAME}Service;
import ${BASE_PACKAGE}.dto.${ENTITY_NAME}RequestDto;
import ${BASE_PACKAGE}.dto.${ENTITY_NAME}ResponseDto;
import ${BASE_PACKAGE}.validation.${ENTITY_NAME}Validator;
import ${BASE_PACKAGE}.events.${ENTITY_NAME}EventPublisher;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.HashMap;
import java.util.UUID;

/**
 * Business workflow service for ${ENTITY_NAME}.
 * Orchestrates complex business operations with step-by-step execution.
 */
@Service
@Transactional
public class ${ENTITY_NAME}WorkflowService {

    private static final Logger logger = LoggerFactory.getLogger(${ENTITY_NAME}WorkflowService.class);

    @Autowired
    private ${ENTITY_NAME}Service ${ENTITY_NAME_LOWER}Service;

    @Autowired
    private ${ENTITY_NAME}Validator ${ENTITY_NAME_LOWER}Validator;

    @Autowired
    private ${ENTITY_NAME}EventPublisher eventPublisher;

    /**
     * Execute complete workflow for creating ${ENTITY_NAME}.
     *
     * @param requestDto the request data
     * @return the workflow execution result
     */
    public WorkflowResult<${ENTITY_NAME}ResponseDto> executeCreateWorkflow(${ENTITY_NAME}RequestDto requestDto) {
        String correlationId = UUID.randomUUID().toString();
        WorkflowContext context = new WorkflowContext(correlationId, "CREATE_${ENTITY_NAME_UPPER}", requestDto);
        
        logger.info("Starting create workflow for ${ENTITY_NAME} with correlation ID: {}", correlationId);
        
        try {
            // Step 1: Input Validation
            context = validateInput(context);
            if (context.hasErrors()) {
                return WorkflowResult.failure(context.getErrors());
            }
            
            // Step 2: Business Rule Check
            context = applyBusinessRules(context);
            if (context.hasErrors()) {
                return WorkflowResult.failure(context.getErrors());
            }
            
            // Step 3: Data Processing
            context = processData(context);
            if (context.hasErrors()) {
                return WorkflowResult.failure(context.getErrors());
            }
            
            // Step 4: Persistence Operation
            context = persistEntity(context);
            if (context.hasErrors()) {
                return WorkflowResult.failure(context.getErrors());
            }
            
            // Step 5: Event Publication
            publishEvents(context);
            
            logger.info("Successfully completed create workflow for ${ENTITY_NAME} with correlation ID: {}", correlationId);
            return WorkflowResult.success(context.getResult());
            
        } catch (Exception e) {
            logger.error("Workflow execution failed for correlation ID: " + correlationId, e);
            return WorkflowResult.failure("Workflow execution failed: " + e.getMessage());
        }
    }

    /**
     * Execute complete workflow for updating ${ENTITY_NAME}.
     *
     * @param id the entity ID
     * @param requestDto the request data
     * @return the workflow execution result
     */
    public WorkflowResult<${ENTITY_NAME}ResponseDto> executeUpdateWorkflow(Long id, ${ENTITY_NAME}RequestDto requestDto) {
        String correlationId = UUID.randomUUID().toString();
        WorkflowContext context = new WorkflowContext(correlationId, "UPDATE_${ENTITY_NAME_UPPER}", requestDto);
        context.setEntityId(id);
        
        logger.info("Starting update workflow for ${ENTITY_NAME} ID: {} with correlation ID: {}", id, correlationId);
        
        try {
            // Step 1: Validation
            context = validateInput(context);
            if (context.hasErrors()) {
                return WorkflowResult.failure(context.getErrors());
            }
            
            // Step 2: Load existing entity
            context = loadExistingEntity(context);
            if (context.hasErrors()) {
                return WorkflowResult.failure(context.getErrors());
            }
            
            // Step 3: Business rules
            context = applyBusinessRules(context);
            if (context.hasErrors()) {
                return WorkflowResult.failure(context.getErrors());
            }
            
            // Step 4: Update entity
            context = updateEntity(context);
            if (context.hasErrors()) {
                return WorkflowResult.failure(context.getErrors());
            }
            
            // Step 5: Publish events
            publishEvents(context);
            
            logger.info("Successfully completed update workflow for ${ENTITY_NAME} ID: {} with correlation ID: {}", id, correlationId);
            return WorkflowResult.success(context.getResult());
            
        } catch (Exception e) {
            logger.error("Update workflow execution failed for ID: " + id + ", correlation ID: " + correlationId, e);
            return WorkflowResult.failure("Update workflow execution failed: " + e.getMessage());
        }
    }

    private WorkflowContext validateInput(WorkflowContext context) {
        logger.debug("Executing input validation step for correlation ID: {}", context.getCorrelationId());
        
        try {
            ${ENTITY_NAME}RequestDto requestDto = (${ENTITY_NAME}RequestDto) context.getInputData();
            ${ENTITY_NAME_LOWER}Validator.validateRequest(requestDto);
            
            context.addStepResult("INPUT_VALIDATION", "PASSED");
            logger.debug("Input validation passed for correlation ID: {}", context.getCorrelationId());
            
        } catch (Exception e) {
            context.addError("INPUT_VALIDATION", "Input validation failed: " + e.getMessage());
            logger.warn("Input validation failed for correlation ID: {}", context.getCorrelationId(), e);
        }
        
        return context;
    }

    private WorkflowContext applyBusinessRules(WorkflowContext context) {
        logger.debug("Executing business rules step for correlation ID: {}", context.getCorrelationId());
        
        try {
            // Apply business-specific rules here
            // Example: Check business constraints, validate against external systems, etc.
            
            context.addStepResult("BUSINESS_RULES", "PASSED");
            logger.debug("Business rules validation passed for correlation ID: {}", context.getCorrelationId());
            
        } catch (Exception e) {
            context.addError("BUSINESS_RULES", "Business rules validation failed: " + e.getMessage());
            logger.warn("Business rules validation failed for correlation ID: {}", context.getCorrelationId(), e);
        }
        
        return context;
    }

    private WorkflowContext processData(WorkflowContext context) {
        logger.debug("Executing data processing step for correlation ID: {}", context.getCorrelationId());
        
        try {
            // Process and transform data as needed
            ${ENTITY_NAME}RequestDto requestDto = (${ENTITY_NAME}RequestDto) context.getInputData();
            
            // Add processing timestamp
            context.addMetadata("processed_at", LocalDateTime.now());
            
            context.addStepResult("DATA_PROCESSING", "COMPLETED");
            logger.debug("Data processing completed for correlation ID: {}", context.getCorrelationId());
            
        } catch (Exception e) {
            context.addError("DATA_PROCESSING", "Data processing failed: " + e.getMessage());
            logger.warn("Data processing failed for correlation ID: {}", context.getCorrelationId(), e);
        }
        
        return context;
    }

    private WorkflowContext persistEntity(WorkflowContext context) {
        logger.debug("Executing persistence step for correlation ID: {}", context.getCorrelationId());
        
        try {
            ${ENTITY_NAME}RequestDto requestDto = (${ENTITY_NAME}RequestDto) context.getInputData();
            ${ENTITY_NAME}ResponseDto result = ${ENTITY_NAME_LOWER}Service.create${ENTITY_NAME}(requestDto);
            
            context.setResult(result);
            context.addStepResult("PERSISTENCE", "COMPLETED");
            logger.debug("Entity persistence completed for correlation ID: {}", context.getCorrelationId());
            
        } catch (Exception e) {
            context.addError("PERSISTENCE", "Entity persistence failed: " + e.getMessage());
            logger.error("Entity persistence failed for correlation ID: {}", context.getCorrelationId(), e);
        }
        
        return context;
    }

    private WorkflowContext loadExistingEntity(WorkflowContext context) {
        logger.debug("Loading existing entity for correlation ID: {}", context.getCorrelationId());
        
        try {
            Long entityId = context.getEntityId();
            ${ENTITY_NAME}ResponseDto existing = ${ENTITY_NAME_LOWER}Service.get${ENTITY_NAME}ById(entityId);
            
            context.setExistingEntity(existing);
            context.addStepResult("LOAD_EXISTING", "COMPLETED");
            logger.debug("Existing entity loaded for correlation ID: {}", context.getCorrelationId());
            
        } catch (Exception e) {
            context.addError("LOAD_EXISTING", "Failed to load existing entity: " + e.getMessage());
            logger.error("Failed to load existing entity for correlation ID: {}", context.getCorrelationId(), e);
        }
        
        return context;
    }

    private WorkflowContext updateEntity(WorkflowContext context) {
        logger.debug("Executing entity update step for correlation ID: {}", context.getCorrelationId());
        
        try {
            Long entityId = context.getEntityId();
            ${ENTITY_NAME}RequestDto requestDto = (${ENTITY_NAME}RequestDto) context.getInputData();
            ${ENTITY_NAME}ResponseDto result = ${ENTITY_NAME_LOWER}Service.update${ENTITY_NAME}(entityId, requestDto);
            
            context.setResult(result);
            context.addStepResult("UPDATE_ENTITY", "COMPLETED");
            logger.debug("Entity update completed for correlation ID: {}", context.getCorrelationId());
            
        } catch (Exception e) {
            context.addError("UPDATE_ENTITY", "Entity update failed: " + e.getMessage());
            logger.error("Entity update failed for correlation ID: {}", context.getCorrelationId(), e);
        }
        
        return context;
    }

    private void publishEvents(WorkflowContext context) {
        try {
            ${ENTITY_NAME}ResponseDto result = context.getResult();
            if (result != null) {
                String operationType = context.getOperationType();
                eventPublisher.publishWorkflowCompleted(result.getId(), operationType, context.getCorrelationId());
                logger.debug("Events published for correlation ID: {}", context.getCorrelationId());
            }
        } catch (Exception e) {
            // Event publication failures should not fail the workflow
            logger.warn("Failed to publish events for correlation ID: {}", context.getCorrelationId(), e);
        }
    }

    /**
     * Workflow context for maintaining state across steps.
     */
    public static class WorkflowContext {
        private final String correlationId;
        private final String operationType;
        private final Object inputData;
        private Long entityId;
        private Object existingEntity;
        private Object result;
        private final Map<String, String> stepResults = new HashMap<>();
        private final Map<String, String> errors = new HashMap<>();
        private final Map<String, Object> metadata = new HashMap<>();

        public WorkflowContext(String correlationId, String operationType, Object inputData) {
            this.correlationId = correlationId;
            this.operationType = operationType;
            this.inputData = inputData;
        }

        // Getters and setters
        public String getCorrelationId() { return correlationId; }
        public String getOperationType() { return operationType; }
        public Object getInputData() { return inputData; }
        public Long getEntityId() { return entityId; }
        public void setEntityId(Long entityId) { this.entityId = entityId; }
        public Object getExistingEntity() { return existingEntity; }
        public void setExistingEntity(Object existingEntity) { this.existingEntity = existingEntity; }
        public ${ENTITY_NAME}ResponseDto getResult() { return (${ENTITY_NAME}ResponseDto) result; }
        public void setResult(Object result) { this.result = result; }
        
        public void addStepResult(String step, String result) { stepResults.put(step, result); }
        public void addError(String step, String error) { errors.put(step, error); }
        public void addMetadata(String key, Object value) { metadata.put(key, value); }
        
        public boolean hasErrors() { return !errors.isEmpty(); }
        public Map<String, String> getErrors() { return errors; }
        public Map<String, String> getStepResults() { return stepResults; }
        public Map<String, Object> getMetadata() { return metadata; }
    }

    /**
     * Workflow execution result.
     */
    public static class WorkflowResult<T> {
        private final boolean success;
        private final T data;
        private final Map<String, String> errors;

        private WorkflowResult(boolean success, T data, Map<String, String> errors) {
            this.success = success;
            this.data = data;
            this.errors = errors;
        }

        public static <T> WorkflowResult<T> success(T data) {
            return new WorkflowResult<>(true, data, null);
        }

        public static <T> WorkflowResult<T> failure(Map<String, String> errors) {
            return new WorkflowResult<>(false, null, errors);
        }

        public static <T> WorkflowResult<T> failure(String error) {
            Map<String, String> errors = new HashMap<>();
            errors.put("GENERAL", error);
            return new WorkflowResult<>(false, null, errors);
        }

        public boolean isSuccess() { return success; }
        public T getData() { return data; }
        public Map<String, String> getErrors() { return errors; }
    }
}
