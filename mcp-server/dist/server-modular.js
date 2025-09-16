#!/usr/bin/env node
/**
 * Modular Developer Assistant MCP Server
 * Refactored for maintainability, testability, and scalability
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import express from 'express';
import cors from 'cors';
// @ts-ignore
import OpenAI from "openai";
// Import modular components
import { AgentOrchestrator } from './agents.js';
import { WorkflowOrchestrationAgent } from './workflow-orchestrator.js';
import { requestLogger, errorHandler, corsConfig, asyncHandler } from './middleware/index.js';
import { ListGeneratedProjectsHandler, ReadFileContentHandler, AnalyzeProjectStructureHandler, CompileCodeWithAgentHandler, ReviewCodeWithAgentHandler, GenerateCodeWithAgentHandler, GenerateApiSpecWithAgentHandler, CreateWorkflowHandler, ListWorkflowsHandler, GetWorkflowHandler, ApproveWorkflowPhaseHandler, GetPendingApprovalsHandler } from './handlers/index.js';
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
        if (this.config.openaiApiKey || process.env.OPENAI_API_KEY) {
            try {
                context.openai = new OpenAI({
                    apiKey: this.config.openaiApiKey || process.env.OPENAI_API_KEY,
                });
                console.log('[DEBUG] OpenAI client initialized');
            }
            catch (error) {
                console.warn('[WARN] Failed to initialize OpenAI client:', error);
            }
        }
        else {
            console.log('[WARN] OPENAI_API_KEY not found. Some AI features may not work.');
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
        this.toolHandlers.set('review_code_with_agent', new ReviewCodeWithAgentHandler(this.context));
        this.toolHandlers.set('generate_code_with_agent', new GenerateCodeWithAgentHandler(this.context));
        this.toolHandlers.set('generate_api_spec_with_agent', new GenerateApiSpecWithAgentHandler(this.context));
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
        // List available tools
        this.app.get('/tools', asyncHandler(async (req, res) => {
            console.log('[DEBUG] List tools endpoint called');
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
