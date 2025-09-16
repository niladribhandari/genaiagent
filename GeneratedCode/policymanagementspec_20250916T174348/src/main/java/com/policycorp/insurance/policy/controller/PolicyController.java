package com.policycorp.insurance.policy.controller;

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

import com.policycorp.insurance.policy.dto.PolicyRequest;
import com.policycorp.insurance.policy.dto.PolicyResponse;
import com.policycorp.insurance.policy.service.PolicyService;

@RestController
@RequestMapping("/api/v1/policies")
@Tag(name = "Policy", description = "Policy management APIs")
@RequiredArgsConstructor
public class PolicyController {

    private static final Logger logger = LoggerFactory.getLogger(PolicyController.class);

    private final PolicyService policyService;

    @GetMapping
    @Operation(summary = "Get all policies", description = "Retrieves a paginated list of all policies")
    public ResponseEntity<Page<PolicyResponse>> getAllPolicies(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ResponseEntity.ok(policyService.getAllPolicies(page, size));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get policy by ID", description = "Retrieves a policy by their ID")
    public ResponseEntity<PolicyResponse> getPolicyById(@PathVariable UUID id) {
        return ResponseEntity.ok(policyService.getPolicyById(id));
    }

    @PostMapping
    @Operation(summary = "Create policy", description = "Creates a new policy")
    public ResponseEntity<PolicyResponse> createPolicy(
            @RequestBody @Valid PolicyRequest request) {
        PolicyResponse response = policyService.createPolicy(request);
        return ResponseEntity
            .created(URI.create("/api/v1/policies/" + response.getId()))
            .body(response);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update policy", description = "Updates an existing policy")
    public ResponseEntity<PolicyResponse> updatePolicy(
            @PathVariable UUID id,
            @RequestBody @Valid PolicyRequest request) {
        return ResponseEntity.ok(policyService.updatePolicy(id, request));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete policy", description = "Deletes a policy")
    public ResponseEntity<Void> deletePolicy(@PathVariable UUID id) {
        policyService.deletePolicy(id);
        return ResponseEntity.noContent().build();
    }
}