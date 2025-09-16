package com.customercorp.customer.service;

import com.customercorp.customer.dto.CustomerRequest;
import com.customercorp.customer.dto.CustomerResponse;
import org.springframework.data.domain.Page;
import java.util.UUID;

/**
 * Service interface for Customer operations
 */
public interface CustomerService {
    
    /**
     * Get all customers with pagination
     */
    Page<CustomerResponse> getAllCustomers(int page, int size);
    
    /**
     * Get customer by ID
     */
    CustomerResponse getCustomerById(UUID id);
    
    /**
     * Create new customer
     */
    CustomerResponse createCustomer(CustomerRequest request);
    
    /**
     * Update existing customer
     */
    CustomerResponse updateCustomer(UUID id, CustomerRequest request);
    
    /**
     * Delete customer by ID
     */
    void deleteCustomer(UUID id);
    
    /**
     * Check if customer exists by name
     */
    boolean existsCustomerByName(String name);
}