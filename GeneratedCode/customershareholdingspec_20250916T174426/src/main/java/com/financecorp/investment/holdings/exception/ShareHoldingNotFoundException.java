package com.financecorp.investment.holdings.exception;

/**
 * Exception thrown when ShareHolding is not found
 */
public class ShareHoldingNotFoundException extends RuntimeException {
    
    public ShareHoldingNotFoundException(String message) {
        super(message);
    }
    
    public ShareHoldingNotFoundException(String message, Throwable cause) {
        super(message, cause);
    }
}