package com.financecorp.investment.holdings.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.financecorp.investment.holdings.dto.ShareHoldingRequest;
import com.financecorp.investment.holdings.dto.ShareHoldingResponse;
import com.financecorp.investment.holdings.service.ShareHoldingService;

@RestController
@RequestMapping("/api/v3/shareholdings")
@Tag(name = "ShareHolding", description = "ShareHolding management APIs")
@RequiredArgsConstructor
public class ShareHoldingController {

    private static final Logger logger = LoggerFactory.getLogger(ShareHoldingController.class);

    private final ShareHoldingService shareholdingService;

    @GetMapping
    @Operation(summary = "Get all shareholdings", description = "Retrieves a paginated list of all shareholdings")
    public ResponseEntity<Page<ShareHoldingResponse>> getAllShareHoldings(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ResponseEntity.ok(shareholdingService.getAllShareHoldings(page, size));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get shareholding by ID", description = "Retrieves a shareholding by their ID")
    public ResponseEntity<ShareHoldingResponse> getShareHoldingById(@PathVariable UUID id) {
        return ResponseEntity.ok(shareholdingService.getShareHoldingById(id));
    }

    @PostMapping
    @Operation(summary = "Create shareholding", description = "Creates a new shareholding")
    public ResponseEntity<ShareHoldingResponse> createShareHolding(
            @RequestBody @Valid ShareHoldingRequest request) {
        ShareHoldingResponse response = shareholdingService.createShareHolding(request);
        return ResponseEntity
            .created(URI.create("/api/v3/shareholdings/" + response.getId()))
            .body(response);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update shareholding", description = "Updates an existing shareholding")
    public ResponseEntity<ShareHoldingResponse> updateShareHolding(
            @PathVariable UUID id,
            @RequestBody @Valid ShareHoldingRequest request) {
        return ResponseEntity.ok(shareholdingService.updateShareHolding(id, request));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete shareholding", description = "Deletes a shareholding")
    public ResponseEntity<Void> deleteShareHolding(@PathVariable UUID id) {
        shareholdingService.deleteShareHolding(id);
        return ResponseEntity.noContent().build();
    }
}