package com.policycorp.insurance.policy.repository;

import com.policycorp.insurance.policy.model.Policy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * JPA Repository for Policy entity
 */
@Repository
public interface PolicyRepository extends JpaRepository<Policy, UUID> {
    
    /**
     * Find policy by name
     */
    Optional<Policy> findByName(String name);
    
    /**
     * Check if policy exists by name
     */
    boolean existsByName(String name);
    
    /**
     * Find policies by name containing (case insensitive)
     */
    @Query("SELECT p FROM Policy p WHERE LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<Policy> findByNameContainingIgnoreCase(@Param("name") String name);
    
    /**
     * Find active policies
     */
    @Query("SELECT p FROM Policy p WHERE p.active = true")
    List<Policy> findActivePolicies();
}