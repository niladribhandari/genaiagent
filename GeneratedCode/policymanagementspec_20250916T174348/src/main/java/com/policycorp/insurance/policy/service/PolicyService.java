package com.policycorp.insurance.policy.service;

import com.policycorp.insurance.policy.dto.PolicyRequest;
import com.policycorp.insurance.policy.dto.PolicyResponse;
import org.springframework.data.domain.Page;
import java.util.UUID;

/**
 * Service interface for Policy operations
 */
public interface PolicyService {
    
    /**
     * Get all policies with pagination
     */
    Page<PolicyResponse> getAllPolicies(int page, int size);
    
    /**
     * Get policy by ID
     */
    PolicyResponse getPolicyById(UUID id);
    
    /**
     * Create new policy
     */
    PolicyResponse createPolicy(PolicyRequest request);
    
    /**
     * Update existing policy
     */
    PolicyResponse updatePolicy(UUID id, PolicyRequest request);
    
    /**
     * Delete policy by ID
     */
    void deletePolicy(UUID id);
    
    /**
     * Check if policy exists by name
     */
    boolean existsPolicyByName(String name);
}