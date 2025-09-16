package com.customercorp.customer.repository;

import com.customercorp.customer.model.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * JPA Repository for Customer entity
 */
@Repository
public interface CustomerRepository extends JpaRepository<Customer, UUID> {
    
    /**
     * Find customer by name
     */
    Optional<Customer> findByName(String name);
    
    /**
     * Check if customer exists by name
     */
    boolean existsByName(String name);
    
    /**
     * Find customers by name containing (case insensitive)
     */
    @Query("SELECT p FROM Customer p WHERE LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<Customer> findByNameContainingIgnoreCase(@Param("name") String name);
    
    /**
     * Find active customers
     */
    @Query("SELECT p FROM Customer p WHERE p.active = true")
    List<Customer> findActiveCustomers();
}