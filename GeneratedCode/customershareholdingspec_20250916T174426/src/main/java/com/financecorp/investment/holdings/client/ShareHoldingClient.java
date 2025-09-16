package com.financecorp.investment.holdings.client;

import com.financecorp.investment.holdings.dto.ShareHoldingRequest;
import com.financecorp.investment.holdings.dto.ShareHoldingResponse;
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
 * HTTP Client for ShareHolding external service integration
 */
@Component
public class ShareHoldingClient {
    
    private static final Logger logger = LoggerFactory.getLogger(ShareHoldingClient.class);
    
    private final RestTemplate restTemplate;
    private final String baseUrl;
    
    public ShareHoldingClient(RestTemplate restTemplate, 
                              @Value("${external.shareholding.service.url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }
    
    /**
     * Fetch shareholding from external service
     */
    public ShareHoldingResponse fetchShareHolding(UUID externalId) {
        try {
            logger.info("Fetching shareholding from external service: {}", externalId);
            
            String url = baseUrl + "/shareholdings/" + externalId;
            ResponseEntity<ShareHoldingResponse> response = restTemplate.getForEntity(
                url, ShareHoldingResponse.class);
            
            logger.info("Successfully fetched shareholding: {}", externalId);
            return response.getBody();
            
        } catch (RestClientException e) {
            logger.error("Failed to fetch shareholding {}: {}", externalId, e.getMessage());
            throw new RuntimeException("External service error", e);
        }
    }
    
    /**
     * Sync shareholding with external service
     */
    public void syncShareHolding(ShareHoldingRequest request, UUID externalId) {
        try {
            logger.info("Syncing shareholding with external service: {}", externalId);
            
            String url = baseUrl + "/shareholdings/" + externalId;
            restTemplate.put(url, request);
            
            logger.info("Successfully synced shareholding: {}", externalId);
            
        } catch (RestClientException e) {
            logger.error("Failed to sync shareholding {}: {}", externalId, e.getMessage());
            throw new RuntimeException("External service sync error", e);
        }
    }
}