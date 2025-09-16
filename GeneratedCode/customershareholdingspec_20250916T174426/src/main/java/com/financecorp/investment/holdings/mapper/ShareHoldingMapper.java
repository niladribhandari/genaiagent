package com.financecorp.investment.holdings.mapper;

import com.financecorp.investment.holdings.dto.ShareHoldingRequest;
import com.financecorp.investment.holdings.dto.ShareHoldingResponse;
import com.financecorp.investment.holdings.model.ShareHolding;
import org.springframework.stereotype.Component;

/**
 * Mapper for ShareHolding entity and DTOs
 */
@Component
public class ShareHoldingMapper {
    
    /**
     * Convert entity to response DTO
     */
    public ShareHoldingResponse toResponse(ShareHolding entity) {
        if (entity == null) {
            return null;
        }
        
        return ShareHoldingResponse.builder()
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
    public ShareHolding toEntity(ShareHoldingRequest request) {
        if (request == null) {
            return null;
        }
        
        return ShareHolding.builder()
            .name(request.getName())
            .description(request.getDescription())
            .active(request.getActive() != null ? request.getActive() : true)
            .build();
    }
    
    /**
     * Update entity from request DTO
     */
    public void updateEntity(ShareHoldingRequest request, ShareHolding entity) {
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