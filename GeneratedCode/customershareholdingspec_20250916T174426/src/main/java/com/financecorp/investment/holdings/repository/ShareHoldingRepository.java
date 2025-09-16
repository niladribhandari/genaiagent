package com.financecorp.investment.holdings.repository;

import com.financecorp.investment.holdings.model.ShareHolding;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * JPA Repository for ShareHolding entity
 */
@Repository
public interface ShareHoldingRepository extends JpaRepository<ShareHolding, UUID> {
    
    /**
     * Find shareholding by name
     */
    Optional<ShareHolding> findByName(String name);
    
    /**
     * Check if shareholding exists by name
     */
    boolean existsByName(String name);
    
    /**
     * Find shareholdings by name containing (case insensitive)
     */
    @Query("SELECT p FROM ShareHolding p WHERE LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<ShareHolding> findByNameContainingIgnoreCase(@Param("name") String name);
    
    /**
     * Find active shareholdings
     */
    @Query("SELECT p FROM ShareHolding p WHERE p.active = true")
    List<ShareHolding> findActiveShareHoldings();
}