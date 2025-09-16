package com.policycorp.insurance.policy.client;

import com.policycorp.insurance.policy.dto.PolicyRequest;
import com.policycorp.insurance.policy.dto.PolicyResponse;
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
 * HTTP Client for Policy external service integration
 */
@Component
public class PolicyClient {
    
    private static final Logger logger = LoggerFactory.getLogger(PolicyClient.class);
    
    private final RestTemplate restTemplate;
    private final String baseUrl;
    
    public PolicyClient(RestTemplate restTemplate, 
                              @Value("${external.policy.service.url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }
    
    /**
     * Fetch policy from external service
     */
    public PolicyResponse fetchPolicy(UUID externalId) {
        try {
            logger.info("Fetching policy from external service: {}", externalId);
            
            String url = baseUrl + "/policies/" + externalId;
            ResponseEntity<PolicyResponse> response = restTemplate.getForEntity(
                url, PolicyResponse.class);
            
            logger.info("Successfully fetched policy: {}", externalId);
            return response.getBody();
            
        } catch (RestClientException e) {
            logger.error("Failed to fetch policy {}: {}", externalId, e.getMessage());
            throw new RuntimeException("External service error", e);
        }
    }
    
    /**
     * Sync policy with external service
     */
    public void syncPolicy(PolicyRequest request, UUID externalId) {
        try {
            logger.info("Syncing policy with external service: {}", externalId);
            
            String url = baseUrl + "/policies/" + externalId;
            restTemplate.put(url, request);
            
            logger.info("Successfully synced policy: {}", externalId);
            
        } catch (RestClientException e) {
            logger.error("Failed to sync policy {}: {}", externalId, e.getMessage());
            throw new RuntimeException("External service sync error", e);
        }
    }
}