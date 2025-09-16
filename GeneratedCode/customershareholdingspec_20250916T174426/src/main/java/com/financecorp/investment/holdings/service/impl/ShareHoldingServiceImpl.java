package com.financecorp.investment.holdings.service.impl;

import com.financecorp.investment.holdings.dto.ShareHoldingRequest;
import com.financecorp.investment.holdings.dto.ShareHoldingResponse;
import com.financecorp.investment.holdings.model.ShareHolding;
import com.financecorp.investment.holdings.repository.ShareHoldingRepository;
import com.financecorp.investment.holdings.service.ShareHoldingService;
import com.financecorp.investment.holdings.mapper.ShareHoldingMapper;
import com.financecorp.investment.holdings.exception.ResourceNotFoundException;
import com.financecorp.investment.holdings.exception.BadRequestException;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Service implementation for ShareHolding operations
 */
@Service
@RequiredArgsConstructor
@Transactional
public class ShareHoldingServiceImpl implements ShareHoldingService {

    private static final Logger logger = LoggerFactory.getLogger(ShareHoldingServiceImpl.class);

    private final ShareHoldingRepository shareholdingRepository;
    private final ShareHoldingMapper shareholdingMapper;

    @Override
    @Transactional(readOnly = true)
    public Page<ShareHoldingResponse> getAllShareHoldings(int page, int size) {
        logger.info("Retrieving all shareholdings - page: {}, size: {}", page, size);
        return shareholdingRepository.findAll(PageRequest.of(page, size))
            .map(shareholdingMapper::toResponse);
    }

    @Override
    @Transactional(readOnly = true)
    public ShareHoldingResponse getShareHoldingById(UUID id) {
        logger.info("Retrieving shareholding with ID: {}", id);
        return shareholdingRepository.findById(id)
            .map(shareholdingMapper::toResponse)
            .orElseThrow(() -> new ResourceNotFoundException("ShareHolding not found with ID: " + id));
    }

    @Override
    public ShareHoldingResponse createShareHolding(ShareHoldingRequest request) {
        logger.info("Creating new shareholding: {}", request);
        
        if (request.getName() != null && shareholdingRepository.existsByName(request.getName())) {
            throw new BadRequestException("ShareHolding with name '" + request.getName() + "' already exists");
        }

        ShareHolding shareholding = shareholdingMapper.toEntity(request);
        ShareHolding savedShareHolding = shareholdingRepository.save(shareholding);
        
        logger.info("Successfully created shareholding with ID: {}", savedShareHolding.getId());
        return shareholdingMapper.toResponse(savedShareHolding);
    }

    @Override
    public ShareHoldingResponse updateShareHolding(UUID id, ShareHoldingRequest request) {
        logger.info("Updating shareholding with ID: {}", id);

        ShareHolding existingShareHolding = shareholdingRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("ShareHolding not found with ID: " + id));

        // Check name uniqueness if name is being changed
        if (request.getName() != null && 
            !existingShareHolding.getName().equals(request.getName()) &&
            shareholdingRepository.existsByName(request.getName())) {
            throw new BadRequestException("ShareHolding with name '" + request.getName() + "' already exists");
        }

        shareholdingMapper.updateEntity(request, existingShareHolding);
        ShareHolding updatedShareHolding = shareholdingRepository.save(existingShareHolding);
        
        logger.info("Successfully updated shareholding with ID: {}", id);
        return shareholdingMapper.toResponse(updatedShareHolding);
    }

    @Override
    public void deleteShareHolding(UUID id) {
        logger.info("Deleting shareholding with ID: {}", id);
        
        if (!shareholdingRepository.existsById(id)) {
            throw new ResourceNotFoundException("ShareHolding not found with ID: " + id);
        }
        
        shareholdingRepository.deleteById(id);
        logger.info("Successfully deleted shareholding with ID: {}", id);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsShareHoldingByName(String name) {
        logger.info("Checking if shareholding exists with name: {}", name);
        return shareholdingRepository.existsByName(name);
    }
}