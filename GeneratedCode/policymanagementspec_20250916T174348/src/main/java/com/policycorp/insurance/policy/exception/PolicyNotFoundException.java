package com.policycorp.insurance.policy.exception;

/**
 * Exception thrown when Policy is not found
 */
public class PolicyNotFoundException extends RuntimeException {
    
    public PolicyNotFoundException(String message) {
        super(message);
    }
    
    public PolicyNotFoundException(String message, Throwable cause) {
        super(message, cause);
    }
}