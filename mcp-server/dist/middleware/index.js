/**
 * Express middleware for request logging and error handling
 */
/**
 * Request logging middleware
 */
export function requestLogger(req, res, next) {
    const start = Date.now();
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`);
    });
    next();
}
/**
 * Error handling middleware
 */
export function errorHandler(error, req, res, next) {
    console.error('[ERROR]', error);
    if (res.headersSent) {
        return next(error);
    }
    const statusCode = error.statusCode || 500;
    const message = error.message || 'Internal server error';
    res.status(statusCode).json({
        error: {
            message,
            ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
        }
    });
}
/**
 * CORS configuration
 */
export function corsConfig() {
    return {
        origin: process.env.NODE_ENV === 'production'
            ? ['http://localhost:3000', 'http://localhost:3001']
            : true,
        credentials: true,
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allowedHeaders: ['Content-Type', 'Authorization']
    };
}
/**
 * Async route wrapper to handle promise rejections
 */
export function asyncHandler(fn) {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
}
