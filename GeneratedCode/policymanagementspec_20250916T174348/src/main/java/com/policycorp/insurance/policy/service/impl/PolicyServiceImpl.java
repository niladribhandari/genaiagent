package com.policycorp.insurance.policy.service.impl;

import com.policycorp.insurance.policy.dto.PolicyRequest;
import com.policycorp.insurance.policy.dto.PolicyResponse;
import com.policycorp.insurance.policy.model.Policy;
import com.policycorp.insurance.policy.repository.PolicyRepository;
import com.policycorp.insurance.policy.service.PolicyService;
import com.policycorp.insurance.policy.mapper.PolicyMapper;
import com.policycorp.insurance.policy.exception.ResourceNotFoundException;
import com.policycorp.insurance.policy.exception.BadRequestException;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Service implementation for Policy operations
 */
@Service
@RequiredArgsConstructor
@Transactional
public class PolicyServiceImpl implements PolicyService {

    private static final Logger logger = LoggerFactory.getLogger(PolicyServiceImpl.class);

    private final PolicyRepository policyRepository;
    private final PolicyMapper policyMapper;

    @Override
    @Transactional(readOnly = true)
    public Page<PolicyResponse> getAllPolicies(int page, int size) {
        logger.info("Retrieving all policies - page: {}, size: {}", page, size);
        return policyRepository.findAll(PageRequest.of(page, size))
            .map(policyMapper::toResponse);
    }

    @Override
    @Transactional(readOnly = true)
    public PolicyResponse getPolicyById(UUID id) {
        logger.info("Retrieving policy with ID: {}", id);
        return policyRepository.findById(id)
            .map(policyMapper::toResponse)
            .orElseThrow(() -> new ResourceNotFoundException("Policy not found with ID: " + id));
    }

    @Override
    public PolicyResponse createPolicy(PolicyRequest request) {
        logger.info("Creating new policy: {}", request);
        
        if (request.getName() != null && policyRepository.existsByName(request.getName())) {
            throw new BadRequestException("Policy with name '" + request.getName() + "' already exists");
        }

        Policy policy = policyMapper.toEntity(request);
        Policy savedPolicy = policyRepository.save(policy);
        
        logger.info("Successfully created policy with ID: {}", savedPolicy.getId());
        return policyMapper.toResponse(savedPolicy);
    }

    @Override
    public PolicyResponse updatePolicy(UUID id, PolicyRequest request) {
        logger.info("Updating policy with ID: {}", id);

        Policy existingPolicy = policyRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Policy not found with ID: " + id));

        // Check name uniqueness if name is being changed
        if (request.getName() != null && 
            !existingPolicy.getName().equals(request.getName()) &&
            policyRepository.existsByName(request.getName())) {
            throw new BadRequestException("Policy with name '" + request.getName() + "' already exists");
        }

        policyMapper.updateEntity(request, existingPolicy);
        Policy updatedPolicy = policyRepository.save(existingPolicy);
        
        logger.info("Successfully updated policy with ID: {}", id);
        return policyMapper.toResponse(updatedPolicy);
    }

    @Override
    public void deletePolicy(UUID id) {
        logger.info("Deleting policy with ID: {}", id);
        
        if (!policyRepository.existsById(id)) {
            throw new ResourceNotFoundException("Policy not found with ID: " + id);
        }
        
        policyRepository.deleteById(id);
        logger.info("Successfully deleted policy with ID: {}", id);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsPolicyByName(String name) {
        logger.info("Checking if policy exists with name: {}", name);
        return policyRepository.existsByName(name);
    }
}