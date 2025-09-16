#!/usr/bin/env node
/**
 * Modular Developer Assistant MCP Server
 * Refactored for maintainability, testability, and scalability
 */
import dotenv from 'dotenv';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import express from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs/promises';
// @ts-ignore
import OpenAI from "openai";
// Load environment variables from .env file
dotenv.config();
// Import modular components
import { AgentOrchestrator } from './agents.js';
import { WorkflowOrchestrationAgent } from './workflow-orchestrator.js';
import { requestLogger, errorHandler, corsConfig, asyncHandler } from './middleware/index.js';
import { ListGeneratedProjectsHandler, ReadFileContentHandler, AnalyzeProjectStructureHandler, CompileCodeWithAgentHandler, ReviewCodeWithAgentHandler, GenerateCodeWithAgentHandler, GenerateApiSpecWithAgentHandler, FixCompilationIssuesWithAgentHandler, CreateWorkflowHandler, ListWorkflowsHandler, GetWorkflowHandler, ApproveWorkflowPhaseHandler, GetPendingApprovalsHandler } from './handlers/index.js';
import { EnhancedCompileCodeHandler, CompilationIssueAnalyzer } from './handlers/EnhancedCompilationHandlers.js';
export class DeveloperAssistantServer {
    server;
    app;
    context;
    config;
    toolHandlers = new Map();
    constructor(config = {}) {
        // Initialize configuration
        this.config = {
            port: 3001,
            corsEnabled: true,
            ...config
        };
        console.log('[DEBUG] Initializing DeveloperAssistantServer...');
        // Initialize MCP server
        this.server = new Server({
            name: "developer-assistant",
            version: "1.0.0",
        }, {
            capabilities: {
                tools: {},
            },
        });
        // Initialize context
        this.context = this.initializeContext();
        // Initialize Express app
        this.app = this.createExpressApp();
        // Initialize tool handlers
        this.initializeToolHandlers();
        // Setup MCP server handlers
        this.setupMCPHandlers();
        // Setup Express routes
        this.setupExpressRoutes();
        console.log('[DEBUG] DeveloperAssistantServer initialization complete');
    }
    /**
     * Initialize server context
     */
    initializeContext() {
        console.log('[DEBUG] Creating AgentOrchestrator...');
        const orchestrator = new AgentOrchestrator();
        console.log('[DEBUG] AgentOrchestrator created successfully');
        console.log('[DEBUG] Creating WorkflowOrchestrationAgent...');
        const workflowOrchestrator = new WorkflowOrchestrationAgent();
        console.log('[DEBUG] WorkflowOrchestrationAgent created successfully');
        const context = {
            orchestrator,
            workflowOrchestrator,
            activeWorkflows: new Map(),
            pendingApprovals: new Map()
        };
        // Initialize OpenAI if API key is available
        const openaiApiKey = this.config.openaiApiKey || process.env.OPENAI_API_KEY;
        if (openaiApiKey) {
            try {
                context.openai = new OpenAI({
                    apiKey: openaiApiKey,
                });
                console.log(`[INFO] OpenAI client initialized successfully`);
                console.log(`[INFO] OpenAI API Key: ${openaiApiKey.substring(0, 12)}...${openaiApiKey.substring(openaiApiKey.length - 4)} (${openaiApiKey.length} chars)`);
                console.log(`[INFO] OpenAI features are ENABLED`);
            }
            catch (error) {
                console.warn('[WARN] Failed to initialize OpenAI client:', error);
                console.log(`[WARN] OpenAI API Key was present but initialization failed`);
            }
        }
        else {
            console.log('[WARN] OPENAI_API_KEY not found in environment variables or config.');
            console.log('[WARN] AI features may not work properly without OpenAI API key.');
            console.log('[INFO] Available environment variables starting with OPENAI:', Object.keys(process.env).filter(key => key.startsWith('OPENAI')));
        }
        return context;
    }
    /**
     * Initialize tool handlers
     */
    initializeToolHandlers() {
        console.log('[DEBUG] Setting up tool handlers...');
        // Project handlers
        this.toolHandlers.set('list_generated_projects', new ListGeneratedProjectsHandler(this.context));
        this.toolHandlers.set('read_file_content', new ReadFileContentHandler(this.context));
        this.toolHandlers.set('analyze_project_structure', new AnalyzeProjectStructureHandler(this.context));
        // Agent handlers
        this.toolHandlers.set('compile_code_with_agent', new CompileCodeWithAgentHandler(this.context));
        this.toolHandlers.set('enhanced_compile_code', new EnhancedCompileCodeHandler(this.context));
        this.toolHandlers.set('analyze_compilation_issues', new CompilationIssueAnalyzer(this.context));
        this.toolHandlers.set('review_code_with_agent', new ReviewCodeWithAgentHandler(this.context));
        this.toolHandlers.set('generate_code_with_agent', new GenerateCodeWithAgentHandler(this.context));
        this.toolHandlers.set('generate_api_spec_with_agent', new GenerateApiSpecWithAgentHandler(this.context));
        this.toolHandlers.set('fix_compilation_issues_with_agent', new FixCompilationIssuesWithAgentHandler(this.context));
        // Workflow handlers
        this.toolHandlers.set('create_workflow', new CreateWorkflowHandler(this.context));
        this.toolHandlers.set('list_workflows', new ListWorkflowsHandler(this.context));
        this.toolHandlers.set('get_workflow', new GetWorkflowHandler(this.context));
        this.toolHandlers.set('approve_workflow_phase', new ApproveWorkflowPhaseHandler(this.context));
        this.toolHandlers.set('get_pending_approvals', new GetPendingApprovalsHandler(this.context));
        console.log(`[DEBUG] Initialized ${this.toolHandlers.size} tool handlers`);
    }
    /**
     * Create Express application
     */
    createExpressApp() {
        const app = express();
        // Middleware
        if (this.config.corsEnabled) {
            app.use(cors(corsConfig()));
        }
        app.use(express.json({ limit: '50mb' }));
        app.use(express.urlencoded({ extended: true, limit: '50mb' }));
        app.use(requestLogger);
        return app;
    }
    /**
     * Setup MCP server handlers
     */
    setupMCPHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: this.getToolDefinitions(),
        }));
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            console.log(`[DEBUG] Call tool endpoint called with: ${JSON.stringify({ name, arguments: args })}`);
            try {
                const handler = this.toolHandlers.get(name);
                if (!handler) {
                    throw new Error(`Unknown tool: ${name}`);
                }
                const result = await handler.handle(args, this.context);
                return result;
            }
            catch (error) {
                console.error('[ERROR] Call tool error:', error);
                throw error;
            }
        });
    }
    /**
     * Setup Express routes
     */
    setupExpressRoutes() {
        // Health check
        this.app.get('/', asyncHandler(async (req, res) => {
            console.log('[DEBUG] Health check endpoint called');
            res.json({
                status: 'running',
                message: 'Developer Assistant MCP Server is running',
                timestamp: new Date().toISOString(),
                tools: Array.from(this.toolHandlers.keys())
            });
        }));
        // Health endpoint
        this.app.get('/health', asyncHandler(async (req, res) => {
            console.log('[DEBUG] Health endpoint called');
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                version: '2.0.0',
                uptime: process.uptime(),
                toolCount: this.toolHandlers.size
            });
        }));
        // List available tools
        this.app.get('/tools', asyncHandler(async (req, res) => {
            console.log('[DEBUG] List tools endpoint called');
            res.json({
                tools: this.getToolDefinitions()
            });
        }));
        // Alternative tools list endpoint for compatibility
        this.app.get('/tools/list', asyncHandler(async (req, res) => {
            console.log('[DEBUG] Tools list endpoint called');
            res.json({
                tools: this.getToolDefinitions()
            });
        }));
        // Call tool endpoint
        this.app.post('/call-tool', asyncHandler(async (req, res) => {
            const { name, arguments: args } = req.body;
            console.log(`[DEBUG] Call tool endpoint called with: ${JSON.stringify({ name, arguments: args })}`);
            const handler = this.toolHandlers.get(name);
            if (!handler) {
                return res.status(400).json({ error: `Unknown tool: ${name}` });
            }
            const result = await handler.handle(args, this.context);
            res.json(result);
        }));
        // Alternative call tool endpoint for compatibility
        this.app.post('/tools/call', asyncHandler(async (req, res) => {
            const { name, arguments: args } = req.body;
            console.log(`[DEBUG] Tools call endpoint called with: ${JSON.stringify({ name, arguments: args })}`);
            const handler = this.toolHandlers.get(name);
            if (!handler) {
                return res.status(400).json({ error: `Unknown tool: ${name}` });
            }
            const result = await handler.handle(args, this.context);
            res.json(result);
        }));
        // List saved API specifications
        this.app.get('/specs/list', asyncHandler(async (req, res) => {
            console.log('[DEBUG] List specs endpoint called');
            try {
                const specsDir = path.join(process.cwd(), '..', 'Agents', 'API-requirements', 'specs');
                const files = await fs.readdir(specsDir);
                const specs = [];
                for (const file of files) {
                    if (file.endsWith('.yml') || file.endsWith('.yaml')) {
                        const filePath = path.join(specsDir, file);
                        const stats = await fs.stat(filePath);
                        try {
                            // Read the first few lines to extract metadata
                            const content = await fs.readFile(filePath, 'utf8');
                            const lines = content.split('\n').slice(0, 20); // First 20 lines should contain metadata
                            let apiName = file.replace(/\.(yml|yaml)$/, '');
                            let technology = 'unknown';
                            let endpoints = 0;
                            // Try to extract metadata from the YAML content
                            for (const line of lines) {
                                if (line.includes('api_name:')) {
                                    apiName = line.split('api_name:')[1]?.trim().replace(/['"]/g, '') || apiName;
                                }
                                if (line.includes('framework:')) {
                                    technology = line.split('framework:')[1]?.trim().replace(/['"]/g, '') || technology;
                                }
                                if (line.includes('endpoints:') && line.includes('[')) {
                                    // Count endpoints in the array
                                    const endpointsMatch = content.match(/endpoints:\s*\[([\s\S]*?)\]/);
                                    if (endpointsMatch) {
                                        const endpointsContent = endpointsMatch[1];
                                        endpoints = (endpointsContent.match(/path:/g) || []).length;
                                    }
                                }
                            }
                            specs.push({
                                id: file,
                                name: apiName,
                                technology,
                                endpoints,
                                createdAt: stats.mtime,
                                fileName: file
                            });
                        }
                        catch (readError) {
                            console.error(`[ERROR] Failed to read spec file ${file}:`, readError);
                        }
                    }
                }
                // Sort by creation date, newest first
                specs.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
                res.json({ success: true, specs });
            }
            catch (error) {
                console.error('[ERROR] List specs error:', error);
                res.status(500).json({
                    success: false,
                    error: error instanceof Error ? error.message : String(error)
                });
            }
        }));
        // Get individual API specification
        this.app.get('/specs/:fileName', asyncHandler(async (req, res) => {
            console.log('[DEBUG] Get individual spec endpoint called for:', req.params.fileName);
            try {
                const { fileName } = req.params;
                const specsDir = path.join(process.cwd(), '..', 'Agents', 'API-requirements', 'specs');
                const filePath = path.join(specsDir, fileName);
                // Check if file exists
                try {
                    await fs.access(filePath);
                }
                catch {
                    return res.status(404).json({ success: false, error: 'Specification not found' });
                }
                const content = await fs.readFile(filePath, 'utf8');
                const stats = await fs.stat(filePath);
                res.json({
                    success: true,
                    spec: {
                        fileName,
                        content,
                        lastModified: stats.mtime,
                        size: stats.size
                    }
                });
            }
            catch (error) {
                console.error('[ERROR] Get spec error:', error);
                res.status(500).json({
                    success: false,
                    error: error instanceof Error ? error.message : String(error)
                });
            }
        }));
        // Error handling middleware (must be last)
        this.app.use(errorHandler);
    }
    /**
     * Get tool definitions
     */
    getToolDefinitions() {
        return [
            {
                name: "list_generated_projects",
                description: "List all generated projects with their structure and statistics",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
            {
                name: "read_file_content",
                description: "Read the content of a specific file",
                inputSchema: {
                    type: "object",
                    properties: {
                        filePath: {
                            type: "string",
                            description: "Path to the file to read",
                        },
                    },
                    required: ["filePath"],
                },
            },
            {
                name: "analyze_project_structure",
                description: "Analyze the structure of a project directory",
                inputSchema: {
                    type: "object",
                    properties: {
                        projectPath: {
                            type: "string",
                            description: "Path to the project directory to analyze",
                        },
                        maxDepth: {
                            type: "number",
                            description: "Maximum depth to traverse (default: 10)",
                            default: 10,
                        },
                    },
                    required: ["projectPath"],
                },
            },
            {
                name: "compile_code_with_agent",
                description: "Compile a project using the compilation agent",
                inputSchema: {
                    type: "object",
                    properties: {
                        projectPath: {
                            type: "string",
                            description: "Path to the project to compile",
                        },
                        projectType: {
                            type: "string",
                            description: "Type of project (java, typescript, etc.)",
                        },
                        buildOptions: {
                            type: "object",
                            description: "Additional build options",
                        },
                    },
                    required: ["projectPath"],
                },
            },
            {
                name: "enhanced_compile_code",
                description: "Enhanced compilation with OpenAI analysis and simplified output format for UI display and agent consumption",
                inputSchema: {
                    type: "object",
                    properties: {
                        projectPath: {
                            type: "string",
                            description: "Path to the project to compile",
                        },
                        projectType: {
                            type: "string",
                            description: "Type of project (java_springboot, dotnet_api, python_api, nodejs_api)",
                        },
                        buildOptions: {
                            type: "object",
                            description: "Build configuration options",
                            properties: {
                                goals: {
                                    type: "array",
                                    items: { type: "string" },
                                    description: "Build goals/targets to execute"
                                },
                                skipTests: {
                                    type: "boolean",
                                    description: "Whether to skip test execution"
                                },
                                timeout: {
                                    type: "number",
                                    description: "Compilation timeout in seconds"
                                }
                            }
                        },
                        enableOpenAI: {
                            type: "boolean",
                            description: "Enable OpenAI-powered issue analysis and suggestions",
                            default: true
                        },
                        format: {
                            type: "string",
                            description: "Output format",
                            enum: ["simplified", "detailed"],
                            default: "simplified"
                        }
                    },
                    required: ["projectPath"],
                },
            },
            {
                name: "analyze_compilation_issues",
                description: "Analyze compilation issues and convert to standardized format with AI suggestions",
                inputSchema: {
                    type: "object",
                    properties: {
                        issues: {
                            type: "array",
                            description: "Array of compilation issues to analyze",
                            items: {
                                type: "object",
                                properties: {
                                    severity: {
                                        type: "string",
                                        enum: ["error", "warning", "info", "hint"],
                                        description: "Issue severity level"
                                    },
                                    message: {
                                        type: "string",
                                        description: "Issue description or error message"
                                    },
                                    file_path: {
                                        type: "string",
                                        description: "Path to file containing the issue"
                                    },
                                    line_number: {
                                        type: "number",
                                        description: "Line number where issue occurs"
                                    },
                                    column_number: {
                                        type: "number",
                                        description: "Column number where issue occurs"
                                    }
                                }
                            }
                        },
                        projectPath: {
                            type: "string",
                            description: "Path to the project for context"
                        },
                        enableOpenAI: {
                            type: "boolean",
                            description: "Enable OpenAI-powered analysis and suggestions",
                            default: true
                        }
                    },
                    required: ["issues"],
                },
            },
            {
                name: "review_code_with_agent",
                description: "Review code using the code review agent",
                inputSchema: {
                    type: "object",
                    properties: {
                        projectPath: {
                            type: "string",
                            description: "Path to the project to review",
                        },
                        filePath: {
                            type: "string",
                            description: "Path to specific file to review",
                        },
                        reviewType: {
                            type: "string",
                            description: "Type of review (quality, security, performance)",
                            default: "quality",
                        },
                    },
                },
            },
            {
                name: "generate_code_with_agent",
                description: "Generate code using the code generation agent",
                inputSchema: {
                    type: "object",
                    properties: {
                        apiSpec: {
                            type: "object",
                            description: "API specification or requirements",
                        },
                        outputDir: {
                            type: "string",
                            description: "Output directory for generated code",
                        },
                        framework: {
                            type: "string",
                            description: "Target framework/technology",
                        },
                    },
                    required: ["apiSpec", "outputDir"],
                },
            },
            {
                name: "generate_api_spec_with_agent",
                description: "Generate API specification using the API spec agent",
                inputSchema: {
                    type: "object",
                    properties: {
                        requirements: {
                            type: "string",
                            description: "Requirements for the API specification",
                        },
                        outputPath: {
                            type: "string",
                            description: "Output path for the specification",
                            default: "generated-api",
                        },
                        format: {
                            type: "string",
                            description: "Format of the specification (openapi, swagger)",
                            default: "openapi",
                        },
                    },
                    required: ["requirements"],
                },
            },
            {
                name: "fix_compilation_issues_with_agent",
                description: "Fix compilation issues using AI-powered fix compilation agent",
                inputSchema: {
                    type: "object",
                    properties: {
                        projectPath: {
                            type: "string",
                            description: "Path to the project with compilation issues",
                        },
                        errors: {
                            type: "array",
                            description: "Array of compilation errors to fix",
                            items: {
                                type: "object",
                                properties: {
                                    message: {
                                        type: "string",
                                        description: "Error message",
                                    },
                                    file_path: {
                                        type: "string",
                                        description: "Path to file with error",
                                    },
                                    line_number: {
                                        type: "number",
                                        description: "Line number of error",
                                    },
                                    column_number: {
                                        type: "number",
                                        description: "Column number of error",
                                    },
                                    severity: {
                                        type: "string",
                                        enum: ["error", "warning"],
                                        description: "Severity of the issue",
                                    },
                                },
                            },
                        },
                        buildTool: {
                            type: "string",
                            description: "Build tool used (maven, gradle)",
                            default: "maven",
                        },
                    },
                    required: ["projectPath", "errors"],
                },
            },
            {
                name: "create_workflow",
                description: "Create a new development workflow",
                inputSchema: {
                    type: "object",
                    properties: {
                        requirements: {
                            type: "string",
                            description: "Project requirements",
                        },
                        technology: {
                            type: "string",
                            description: "Target technology stack",
                        },
                        outputPath: {
                            type: "string",
                            description: "Output path for the project",
                        },
                        approvalMode: {
                            type: "string",
                            enum: ["interactive", "auto_approve", "batch"],
                            default: "interactive",
                        },
                        workflowConfig: {
                            type: "object",
                            description: "Additional workflow configuration",
                        },
                    },
                    required: ["requirements", "technology", "outputPath"],
                },
            },
            {
                name: "list_workflows",
                description: "List all active workflows",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
            {
                name: "get_workflow",
                description: "Get details of a specific workflow",
                inputSchema: {
                    type: "object",
                    properties: {
                        workflowId: {
                            type: "string",
                            description: "ID of the workflow to retrieve",
                        },
                    },
                    required: ["workflowId"],
                },
            },
            {
                name: "approve_workflow_phase",
                description: "Approve or reject a workflow phase",
                inputSchema: {
                    type: "object",
                    properties: {
                        approvalId: {
                            type: "string",
                            description: "ID of the approval request",
                        },
                        response: {
                            type: "string",
                            enum: ["approve", "reject", "modify"],
                            description: "Approval response",
                        },
                        feedback: {
                            type: "string",
                            description: "Optional feedback for the approval",
                        },
                    },
                    required: ["approvalId", "response"],
                },
            },
            {
                name: "get_pending_approvals",
                description: "Get all pending approval requests",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
        ];
    }
    /**
     * Start the server
     */
    async start() {
        return new Promise((resolve, reject) => {
            try {
                const httpServer = this.app.listen(this.config.port, () => {
                    console.log(`Developer Assistant MCP server running on http://localhost:${this.config.port}`);
                    resolve();
                });
                httpServer.on('error', (error) => {
                    console.error('[ERROR] Failed to start server:', error);
                    reject(error);
                });
                // Handle graceful shutdown
                process.on('SIGINT', () => {
                    console.log('\n[INFO] Gracefully shutting down...');
                    httpServer.close(() => {
                        console.log('[INFO] Server closed');
                        process.exit(0);
                    });
                });
            }
            catch (error) {
                console.error('[ERROR] Server initialization failed:', error);
                reject(error);
            }
        });
    }
    /**
     * Stop the server
     */
    async stop() {
        // Implementation for graceful shutdown
        console.log('[INFO] Server stopped');
    }
}
// Start the server if this file is run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    // Log environment status before server initialization
    console.log('[INFO] =================================================');
    console.log('[INFO] Developer Assistant MCP Server Starting...');
    console.log('[INFO] =================================================');
    console.log('[INFO] Environment Check:');
    console.log(`[INFO] NODE_ENV: ${process.env.NODE_ENV || 'not set'}`);
    console.log(`[INFO] PORT: ${process.env.PORT || '3001 (default)'}`);
    // Check for OpenAI API key
    const apiKey = process.env.OPENAI_API_KEY;
    if (apiKey) {
        console.log(`[INFO] OPENAI_API_KEY: Found (${apiKey.substring(0, 12)}...${apiKey.substring(apiKey.length - 4)}, ${apiKey.length} chars)`);
    }
    else {
        console.log('[WARN] OPENAI_API_KEY: Not found in environment');
    }
    console.log('[INFO] =================================================');
    const config = {
        port: parseInt(process.env.PORT || '3001'),
        openaiApiKey: process.env.OPENAI_API_KEY
    };
    const server = new DeveloperAssistantServer(config);
    server.start().catch((error) => {
        console.error('[ERROR] Failed to start server:', error);
        process.exit(1);
    });
}
export default DeveloperAssistantServer;
