package com.financecorp.investment.holdings.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Response DTO for ShareHolding operations
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ShareHoldingResponse {

    private UUID id;
    private String name;
    private String description;
    private Boolean active;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}