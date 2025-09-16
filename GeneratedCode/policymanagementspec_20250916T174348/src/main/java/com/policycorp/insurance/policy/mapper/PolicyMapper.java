package com.policycorp.insurance.policy.mapper;

import com.policycorp.insurance.policy.dto.PolicyRequest;
import com.policycorp.insurance.policy.dto.PolicyResponse;
import com.policycorp.insurance.policy.model.Policy;
import org.springframework.stereotype.Component;

/**
 * Mapper for Policy entity and DTOs
 */
@Component
public class PolicyMapper {
    
    /**
     * Convert entity to response DTO
     */
    public PolicyResponse toResponse(Policy entity) {
        if (entity == null) {
            return null;
        }
        
        return PolicyResponse.builder()
            .id(entity.getId())
            .name(entity.getName())
            .description(entity.getDescription())
            .active(entity.getActive())
            .createdAt(entity.getCreatedAt())
            .updatedAt(entity.getUpdatedAt())
            .build();
    }
    
    /**
     * Convert request DTO to entity
     */
    public Policy toEntity(PolicyRequest request) {
        if (request == null) {
            return null;
        }
        
        return Policy.builder()
            .name(request.getName())
            .description(request.getDescription())
            .active(request.getActive() != null ? request.getActive() : true)
            .build();
    }
    
    /**
     * Update entity from request DTO
     */
    public void updateEntity(PolicyRequest request, Policy entity) {
        if (request == null || entity == null) {
            return;
        }
        
        if (request.getName() != null) {
            entity.setName(request.getName());
        }
        if (request.getDescription() != null) {
            entity.setDescription(request.getDescription());
        }
        if (request.getActive() != null) {
            entity.setActive(request.getActive());
        }
    }
}