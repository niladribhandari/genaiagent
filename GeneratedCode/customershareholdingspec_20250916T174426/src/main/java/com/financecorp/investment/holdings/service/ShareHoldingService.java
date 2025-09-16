package com.financecorp.investment.holdings.service;

import com.financecorp.investment.holdings.dto.ShareHoldingRequest;
import com.financecorp.investment.holdings.dto.ShareHoldingResponse;
import org.springframework.data.domain.Page;
import java.util.UUID;

/**
 * Service interface for ShareHolding operations
 */
public interface ShareHoldingService {
    
    /**
     * Get all shareholdings with pagination
     */
    Page<ShareHoldingResponse> getAllShareHoldings(int page, int size);
    
    /**
     * Get shareholding by ID
     */
    ShareHoldingResponse getShareHoldingById(UUID id);
    
    /**
     * Create new shareholding
     */
    ShareHoldingResponse createShareHolding(ShareHoldingRequest request);
    
    /**
     * Update existing shareholding
     */
    ShareHoldingResponse updateShareHolding(UUID id, ShareHoldingRequest request);
    
    /**
     * Delete shareholding by ID
     */
    void deleteShareHolding(UUID id);
    
    /**
     * Check if shareholding exists by name
     */
    boolean existsShareHoldingByName(String name);
}