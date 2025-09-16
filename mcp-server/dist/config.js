/**
 * Server configuration
 */
export const defaultConfig = {
    server: {
        port: parseInt(process.env.PORT || '3001'),
        host: process.env.HOST || 'localhost',
        corsEnabled: process.env.NODE_ENV !== 'production'
    },
    agents: {
        timeout: 300000, // 5 minutes
        workingDirectory: process.env.AGENTS_DIR || '../Agents'
    },
    workflow: {
        storagePath: process.env.WORKFLOW_STORAGE_PATH || './workflows',
        defaultApprovalMode: process.env.DEFAULT_APPROVAL_MODE || 'interactive'
    },
    projects: {
        generatedCodePath: process.env.GENERATED_CODE_PATH || '../GeneratedCode'
    },
    logging: {
        level: process.env.LOG_LEVEL || 'debug',
        enableRequestLogging: process.env.ENABLE_REQUEST_LOGGING === 'true'
    },
    openai: {
        apiKey: process.env.OPENAI_API_KEY,
        model: process.env.OPENAI_MODEL || 'gpt-4'
    }
};
export function loadConfig() {
    // In a production environment, you might load this from a file
    // or environment variables, with validation
    return defaultConfig;
}
