package com.customercorp.customer.mapper;

import com.customercorp.customer.dto.CustomerRequest;
import com.customercorp.customer.dto.CustomerResponse;
import com.customercorp.customer.model.Customer;
import org.springframework.stereotype.Component;

/**
 * Mapper for Customer entity and DTOs
 */
@Component
public class CustomerMapper {
    
    /**
     * Convert entity to response DTO
     */
    public CustomerResponse toResponse(Customer entity) {
        if (entity == null) {
            return null;
        }
        
        return CustomerResponse.builder()
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
    public Customer toEntity(CustomerRequest request) {
        if (request == null) {
            return null;
        }
        
        return Customer.builder()
            .name(request.getName())
            .description(request.getDescription())
            .active(request.getActive() != null ? request.getActive() : true)
            .build();
    }
    
    /**
     * Update entity from request DTO
     */
    public void updateEntity(CustomerRequest request, Customer entity) {
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