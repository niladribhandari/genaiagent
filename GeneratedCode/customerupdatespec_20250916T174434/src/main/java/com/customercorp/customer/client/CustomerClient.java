package com.customercorp.customer.client;

import com.customercorp.customer.dto.CustomerRequest;
import com.customercorp.customer.dto.CustomerResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.RestClientException;

import java.util.List;
import java.util.UUID;

/**
 * HTTP Client for Customer external service integration
 */
@Component
public class CustomerClient {
    
    private static final Logger logger = LoggerFactory.getLogger(CustomerClient.class);
    
    private final RestTemplate restTemplate;
    private final String baseUrl;
    
    public CustomerClient(RestTemplate restTemplate, 
                              @Value("${external.customer.service.url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }
    
    /**
     * Fetch customer from external service
     */
    public CustomerResponse fetchCustomer(UUID externalId) {
        try {
            logger.info("Fetching customer from external service: {}", externalId);
            
            String url = baseUrl + "/customers/" + externalId;
            ResponseEntity<CustomerResponse> response = restTemplate.getForEntity(
                url, CustomerResponse.class);
            
            logger.info("Successfully fetched customer: {}", externalId);
            return response.getBody();
            
        } catch (RestClientException e) {
            logger.error("Failed to fetch customer {}: {}", externalId, e.getMessage());
            throw new RuntimeException("External service error", e);
        }
    }
    
    /**
     * Sync customer with external service
     */
    public void syncCustomer(CustomerRequest request, UUID externalId) {
        try {
            logger.info("Syncing customer with external service: {}", externalId);
            
            String url = baseUrl + "/customers/" + externalId;
            restTemplate.put(url, request);
            
            logger.info("Successfully synced customer: {}", externalId);
            
        } catch (RestClientException e) {
            logger.error("Failed to sync customer {}: {}", externalId, e.getMessage());
            throw new RuntimeException("External service sync error", e);
        }
    }
}