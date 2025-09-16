package ${BASE_PACKAGE}.client;

import ${BASE_PACKAGE}.dto.*;
import ${BASE_PACKAGE}.exception.*;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.github.resilience4j.ratelimiter.annotation.RateLimiter;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Duration;
import java.util.*;
import java.util.stream.Collectors;
import java.math.BigDecimal;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * ${CLIENT_DESCRIPTION}
 * 
 * ${CLIENT_FEATURES}
 * 
 * Configuration:
 * - Base URL: ${CLIENT_BASE_URL_CONFIG}
 * - Timeout: ${CLIENT_TIMEOUT}ms
 * - Rate Limit: ${CLIENT_RATE_LIMIT}
 * - Retry Policy: ${CLIENT_RETRY_POLICY}
 */
@Component
public class ${CLIENT_NAME}Client {

    private static final Logger logger = LoggerFactory.getLogger(${CLIENT_NAME}Client.class);

    private final WebClient webClient;
    
    @Value("${${CLIENT_CONFIG_PREFIX}.api.base-url}")
    private String baseUrl;
    
    @Value("${${CLIENT_CONFIG_PREFIX}.api.key}")
    private String apiKey;
    
    @Value("${${CLIENT_CONFIG_PREFIX}.api.timeout:${DEFAULT_TIMEOUT}}")
    private long timeoutMs;
    
    ${CLIENT_CONSTANTS}

    public ${CLIENT_NAME}Client(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder
            .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(${MAX_MEMORY_SIZE}))
            .build();
    }

${CLIENT_METHODS}

${FALLBACK_METHODS}
}
