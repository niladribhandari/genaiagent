package com.customercorp.customer.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/**
 * Configuration for Customer service
 */
@Configuration
public class CustomerConfig {
    
    /**
     * RestTemplate bean for HTTP client operations
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}