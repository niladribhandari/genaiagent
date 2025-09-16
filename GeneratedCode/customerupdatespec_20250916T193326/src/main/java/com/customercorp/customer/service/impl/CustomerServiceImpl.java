package com.customercorp.customer.service.impl;

import com.customercorp.customer.dto.CustomerRequest;
import com.customercorp.customer.dto.CustomerResponse;
import com.customercorp.customer.model.Customer;
import com.customercorp.customer.repository.CustomerRepository;
import com.customercorp.customer.service.CustomerService;
import com.customercorp.customer.mapper.CustomerMapper;
import com.customercorp.customer.exception.ResourceNotFoundException;
import com.customercorp.customer.exception.BadRequestException;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Service implementation for Customer operations
 */
@Service
@RequiredArgsConstructor
@Transactional
public class CustomerServiceImpl implements CustomerService {

    private static final Logger logger = LoggerFactory.getLogger(CustomerServiceImpl.class);

    private final CustomerRepository customerRepository;
    private final CustomerMapper customerMapper;

    @Override
    @Transactional(readOnly = true)
    public Page<CustomerResponse> getAllCustomers(int page, int size) {
        logger.info("Retrieving all customers - page: {}, size: {}", page, size);
        return customerRepository.findAll(PageRequest.of(page, size))
            .map(customerMapper::toResponse);
    }

    @Override
    @Transactional(readOnly = true)
    public CustomerResponse getCustomerById(UUID id) {
        logger.info("Retrieving customer with ID: {}", id);
        return customerRepository.findById(id)
            .map(customerMapper::toResponse)
            .orElseThrow(() -> new ResourceNotFoundException("Customer not found with ID: " + id));
    }

    @Override
    public CustomerResponse createCustomer(CustomerRequest request) {
        logger.info("Creating new customer: {}", request);
        
        if (request.getName() != null && customerRepository.existsByName(request.getName())) {
            throw new BadRequestException("Customer with name '" + request.getName() + "' already exists");
        }

        Customer customer = customerMapper.toEntity(request);
        Customer savedCustomer = customerRepository.save(customer);
        
        logger.info("Successfully created customer with ID: {}", savedCustomer.getId());
        return customerMapper.toResponse(savedCustomer);
    }

    @Override
    public CustomerResponse updateCustomer(UUID id, CustomerRequest request) {
        logger.info("Updating customer with ID: {}", id);

        Customer existingCustomer = customerRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Customer not found with ID: " + id));

        // Check name uniqueness if name is being changed
        if (request.getName() != null && 
            !existingCustomer.getName().equals(request.getName()) &&
            customerRepository.existsByName(request.getName())) {
            throw new BadRequestException("Customer with name '" + request.getName() + "' already exists");
        }

        customerMapper.updateEntity(request, existingCustomer);
        Customer updatedCustomer = customerRepository.save(existingCustomer);
        
        logger.info("Successfully updated customer with ID: {}", id);
        return customerMapper.toResponse(updatedCustomer);
    }

    @Override
    public void deleteCustomer(UUID id) {
        logger.info("Deleting customer with ID: {}", id);
        
        if (!customerRepository.existsById(id)) {
            throw new ResourceNotFoundException("Customer not found with ID: " + id);
        }
        
        customerRepository.deleteById(id);
        logger.info("Successfully deleted customer with ID: {}", id);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsCustomerByName(String name) {
        logger.info("Checking if customer exists with name: {}", name);
        return customerRepository.existsByName(name);
    }
}