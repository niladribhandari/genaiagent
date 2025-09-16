package ${BASE_PACKAGE}.calculation;

import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Business calculation engine for ${ENTITY_NAME}.
 * Provides mathematical calculations with configurable rules and formulas.
 */
@Service
public class ${ENTITY_NAME}CalculationEngine {

    private static final Logger logger = LoggerFactory.getLogger(${ENTITY_NAME}CalculationEngine.class);
    
    private static final int DEFAULT_PRECISION = 2;
    private static final RoundingMode DEFAULT_ROUNDING_MODE = RoundingMode.HALF_UP;
    
    // Cache for calculation results
    private final Map<String, BigDecimal> calculationCache = new ConcurrentHashMap<>();

    /**
     * Calculate total from multiple values.
     *
     * @param values the values to sum
     * @return the total sum
     */
    public BigDecimal calculateTotal(List<BigDecimal> values) {
        logger.debug("Calculating total for {} values", values.size());
        
        validateInputs(values);
        
        String cacheKey = generateCacheKey("TOTAL", values);
        BigDecimal cached = calculationCache.get(cacheKey);
        if (cached != null) {
            logger.debug("Returning cached total calculation result");
            return cached;
        }
        
        BigDecimal total = values.stream()
            .filter(value -> value != null)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .setScale(DEFAULT_PRECISION, DEFAULT_ROUNDING_MODE);
        
        calculationCache.put(cacheKey, total);
        logger.debug("Calculated total: {}", total);
        
        return total;
    }

    /**
     * Calculate average from multiple values.
     *
     * @param values the values to average
     * @return the average value
     */
    public BigDecimal calculateAverage(List<BigDecimal> values) {
        logger.debug("Calculating average for {} values", values.size());
        
        validateInputs(values);
        
        List<BigDecimal> nonNullValues = values.stream()
            .filter(value -> value != null)
            .toList();
        
        if (nonNullValues.isEmpty()) {
            logger.warn("No valid values provided for average calculation");
            return BigDecimal.ZERO;
        }
        
        String cacheKey = generateCacheKey("AVERAGE", values);
        BigDecimal cached = calculationCache.get(cacheKey);
        if (cached != null) {
            logger.debug("Returning cached average calculation result");
            return cached;
        }
        
        BigDecimal sum = calculateTotal(nonNullValues);
        BigDecimal count = BigDecimal.valueOf(nonNullValues.size());
        BigDecimal average = sum.divide(count, DEFAULT_PRECISION, DEFAULT_ROUNDING_MODE);
        
        calculationCache.put(cacheKey, average);
        logger.debug("Calculated average: {}", average);
        
        return average;
    }

    /**
     * Calculate percentage of part from total.
     *
     * @param part the part value
     * @param total the total value
     * @return the percentage
     */
    public BigDecimal calculatePercentage(BigDecimal part, BigDecimal total) {
        logger.debug("Calculating percentage: part={}, total={}", part, total);
        
        if (part == null || total == null) {
            throw new IllegalArgumentException("Part and total values cannot be null");
        }
        
        if (total.compareTo(BigDecimal.ZERO) == 0) {
            throw new IllegalArgumentException("Total value cannot be zero for percentage calculation");
        }
        
        String cacheKey = generateCacheKey("PERCENTAGE", List.of(part, total));
        BigDecimal cached = calculationCache.get(cacheKey);
        if (cached != null) {
            logger.debug("Returning cached percentage calculation result");
            return cached;
        }
        
        BigDecimal hundred = BigDecimal.valueOf(100);
        BigDecimal percentage = part.divide(total, DEFAULT_PRECISION + 2, DEFAULT_ROUNDING_MODE)
            .multiply(hundred)
            .setScale(DEFAULT_PRECISION, DEFAULT_ROUNDING_MODE);
        
        calculationCache.put(cacheKey, percentage);
        logger.debug("Calculated percentage: {}%", percentage);
        
        return percentage;
    }

    /**
     * Calculate tax amount based on amount and tax rate.
     *
     * @param amount the base amount
     * @param taxRate the tax rate percentage
     * @return the tax amount
     */
    public BigDecimal calculateTax(BigDecimal amount, BigDecimal taxRate) {
        logger.debug("Calculating tax: amount={}, taxRate={}%", amount, taxRate);
        
        if (amount == null || taxRate == null) {
            throw new IllegalArgumentException("Amount and tax rate cannot be null");
        }
        
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount cannot be negative");
        }
        
        if (taxRate.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Tax rate cannot be negative");
        }
        
        String cacheKey = generateCacheKey("TAX", List.of(amount, taxRate));
        BigDecimal cached = calculationCache.get(cacheKey);
        if (cached != null) {
            logger.debug("Returning cached tax calculation result");
            return cached;
        }
        
        BigDecimal hundred = BigDecimal.valueOf(100);
        BigDecimal tax = amount.multiply(taxRate)
            .divide(hundred, DEFAULT_PRECISION, DEFAULT_ROUNDING_MODE);
        
        calculationCache.put(cacheKey, tax);
        logger.debug("Calculated tax: {}", tax);
        
        return tax;
    }

    /**
     * Calculate discount amount based on amount and discount rate.
     *
     * @param amount the base amount
     * @param discountRate the discount rate percentage
     * @return the discount amount
     */
    public BigDecimal calculateDiscount(BigDecimal amount, BigDecimal discountRate) {
        logger.debug("Calculating discount: amount={}, discountRate={}%", amount, discountRate);
        
        if (amount == null || discountRate == null) {
            throw new IllegalArgumentException("Amount and discount rate cannot be null");
        }
        
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount cannot be negative");
        }
        
        if (discountRate.compareTo(BigDecimal.ZERO) < 0 || discountRate.compareTo(BigDecimal.valueOf(100)) > 0) {
            throw new IllegalArgumentException("Discount rate must be between 0 and 100");
        }
        
        String cacheKey = generateCacheKey("DISCOUNT", List.of(amount, discountRate));
        BigDecimal cached = calculationCache.get(cacheKey);
        if (cached != null) {
            logger.debug("Returning cached discount calculation result");
            return cached;
        }
        
        BigDecimal hundred = BigDecimal.valueOf(100);
        BigDecimal discount = amount.multiply(discountRate)
            .divide(hundred, DEFAULT_PRECISION, DEFAULT_ROUNDING_MODE);
        
        calculationCache.put(cacheKey, discount);
        logger.debug("Calculated discount: {}", discount);
        
        return discount;
    }

    /**
     * Calculate compound interest.
     *
     * @param principal the principal amount
     * @param rate the annual interest rate (as percentage)
     * @param time the time period in years
     * @param compoundFrequency the number of times interest is compounded per year
     * @return the compound interest amount
     */
    public BigDecimal calculateCompoundInterest(BigDecimal principal, BigDecimal rate, 
                                              BigDecimal time, int compoundFrequency) {
        logger.debug("Calculating compound interest: principal={}, rate={}%, time={} years, frequency={}",
                    principal, rate, time, compoundFrequency);
        
        if (principal == null || rate == null || time == null) {
            throw new IllegalArgumentException("Principal, rate, and time cannot be null");
        }
        
        if (principal.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Principal must be positive");
        }
        
        if (compoundFrequency <= 0) {
            throw new IllegalArgumentException("Compound frequency must be positive");
        }
        
        // Formula: A = P(1 + r/n)^(nt)
        BigDecimal hundred = BigDecimal.valueOf(100);
        BigDecimal n = BigDecimal.valueOf(compoundFrequency);
        
        BigDecimal rateDecimal = rate.divide(hundred, DEFAULT_PRECISION + 4, DEFAULT_ROUNDING_MODE);
        BigDecimal rateDividedByN = rateDecimal.divide(n, DEFAULT_PRECISION + 4, DEFAULT_ROUNDING_MODE);
        BigDecimal onePlusRate = BigDecimal.ONE.add(rateDividedByN);
        
        // Calculate exponent (n * t)
        BigDecimal exponent = n.multiply(time);
        
        // For simplicity, we'll approximate the power calculation
        // In a real implementation, you might want to use a more sophisticated approach
        BigDecimal amount = principal.multiply(
            approximatePower(onePlusRate, exponent.intValue())
        ).setScale(DEFAULT_PRECISION, DEFAULT_ROUNDING_MODE);
        
        BigDecimal interest = amount.subtract(principal);
        
        logger.debug("Calculated compound interest: {}", interest);
        return interest;
    }

    /**
     * Clear calculation cache.
     */
    public void clearCache() {
        calculationCache.clear();
        logger.debug("Calculation cache cleared");
    }

    /**
     * Get cache statistics.
     *
     * @return cache statistics
     */
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("cache_size", calculationCache.size());
        stats.put("cached_entries", calculationCache.keySet());
        return stats;
    }

    private void validateInputs(List<BigDecimal> values) {
        if (values == null || values.isEmpty()) {
            throw new IllegalArgumentException("Values list cannot be null or empty");
        }
    }

    private String generateCacheKey(String operation, List<BigDecimal> values) {
        StringBuilder key = new StringBuilder(operation);
        for (BigDecimal value : values) {
            key.append("_").append(value != null ? value.toString() : "NULL");
        }
        return key.toString();
    }

    private BigDecimal approximatePower(BigDecimal base, int exponent) {
        if (exponent == 0) {
            return BigDecimal.ONE;
        }
        
        BigDecimal result = BigDecimal.ONE;
        BigDecimal currentBase = base;
        int currentExponent = Math.abs(exponent);
        
        while (currentExponent > 0) {
            if (currentExponent % 2 == 1) {
                result = result.multiply(currentBase);
            }
            currentBase = currentBase.multiply(currentBase);
            currentExponent /= 2;
        }
        
        if (exponent < 0) {
            result = BigDecimal.ONE.divide(result, DEFAULT_PRECISION + 4, DEFAULT_ROUNDING_MODE);
        }
        
        return result.setScale(DEFAULT_PRECISION + 2, DEFAULT_ROUNDING_MODE);
    }
}
