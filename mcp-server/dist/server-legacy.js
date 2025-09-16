#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import fs from "fs/promises";
import { existsSync } from "fs";
import path from "path";
import { execSync } from "child_process";
import express from 'express';
import cors from 'cors';
// @ts-ignore
import OpenAI from "openai";
import { AgentOrchestrator } from './agents.js';
import { WorkflowOrchestrationAgent } from './workflow-orchestrator.js';
class DeveloperAssistantServer {
    server; // Make server public
    openai;
    activeWorkflows = new Map();
    pendingApprovals = new Map();
    orchestrator;
    workflowOrchestrator;
    constructor() {
        console.log('[DEBUG] Initializing DeveloperAssistantServer...');
        this.server = new Server({
            name: "developer-assistant",
            version: "1.0.0",
        }, {
            capabilities: {
                tools: {},
            },
        });
        console.log('[DEBUG] Creating AgentOrchestrator...');
        this.orchestrator = new AgentOrchestrator();
        console.log('[DEBUG] AgentOrchestrator created successfully');
        console.log('[DEBUG] Creating WorkflowOrchestrationAgent...');
        this.workflowOrchestrator = new WorkflowOrchestrationAgent();
        console.log('[DEBUG] WorkflowOrchestrationAgent created successfully');
        // Initialize OpenAI client with error handling
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) {
            console.warn('Warning: OPENAI_API_KEY not found. Some AI features may not work.');
            // Create a mock client for testing without API key
            this.openai = new OpenAI({
                apiKey: 'sk-dummy-key-for-testing',
                dangerouslyAllowBrowser: false
            });
        }
        else {
            console.log('[DEBUG] Initializing OpenAI client with API key');
            this.openai = new OpenAI({
                apiKey: apiKey,
            });
        }
        console.log('[DEBUG] Setting up tool handlers...');
        this.setupToolHandlers();
        console.log('[DEBUG] Setting up error handling...');
        this.setupErrorHandling();
        console.log('[DEBUG] DeveloperAssistantServer initialization complete');
    }
    setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return {
                tools: [
                    {
                        name: "analyze_project_structure",
                        description: "Analyze and return the structure of a project directory",
                        inputSchema: {
                            type: "object",
                            properties: {
                                projectPath: {
                                    type: "string",
                                    description: "Path to the project directory",
                                },
                                maxDepth: {
                                    type: "number",
                                    description: "Maximum depth to traverse (default: 3)",
                                    default: 3,
                                },
                            },
                            required: ["projectPath"],
                        },
                    },
                    {
                        name: "generate_code_template",
                        description: "Generate code templates for common patterns",
                        inputSchema: {
                            type: "object",
                            properties: {
                                templateType: {
                                    type: "string",
                                    enum: ["react-component", "express-route", "typescript-class", "test-file", "config-file"],
                                    description: "Type of template to generate",
                                },
                                name: {
                                    type: "string",
                                    description: "Name for the generated code",
                                },
                                options: {
                                    type: "object",
                                    description: "Additional options for template generation",
                                    properties: {
                                        typescript: { type: "boolean" },
                                        styled: { type: "boolean" },
                                        hooks: { type: "boolean" },
                                    },
                                },
                            },
                            required: ["templateType", "name"],
                        },
                    },
                    {
                        name: "analyze_code_quality",
                        description: "Analyze code quality and suggest improvements",
                        inputSchema: {
                            type: "object",
                            properties: {
                                filePath: {
                                    type: "string",
                                    description: "Path to the code file to analyze",
                                },
                                language: {
                                    type: "string",
                                    description: "Programming language (auto-detected if not provided)",
                                },
                            },
                            required: ["filePath"],
                        },
                    },
                    {
                        name: "generate_documentation",
                        description: "Generate documentation for code files",
                        inputSchema: {
                            type: "object",
                            properties: {
                                filePath: {
                                    type: "string",
                                    description: "Path to the code file",
                                },
                                docType: {
                                    type: "string",
                                    enum: ["readme", "api-docs", "inline-comments", "jsdoc"],
                                    description: "Type of documentation to generate",
                                },
                            },
                            required: ["filePath", "docType"],
                        },
                    },
                    {
                        name: "git_workflow_helper",
                        description: "Assist with Git operations and workflow",
                        inputSchema: {
                            type: "object",
                            properties: {
                                action: {
                                    type: "string",
                                    enum: ["status", "suggest-commit-message", "branch-info", "recent-changes"],
                                    description: "Git action to perform",
                                },
                                repositoryPath: {
                                    type: "string",
                                    description: "Path to the Git repository",
                                },
                                files: {
                                    type: "array",
                                    items: { type: "string" },
                                    description: "Specific files for commit message generation",
                                },
                            },
                            required: ["action", "repositoryPath"],
                        },
                    },
                    {
                        name: "summarize_project_functionality",
                        description: "Summarize and describe the main functionality of an existing project. Supports Java, .NET, or Node.js projects.",
                        inputSchema: {
                            type: "object",
                            properties: {
                                projectPath: {
                                    type: "string",
                                    description: "Path to the root of the project to summarize",
                                },
                                language: {
                                    type: "string",
                                    enum: ["java", ".net", "node"],
                                    description: "Project language (java, .net, or node)",
                                },
                            },
                            required: ["projectPath", "language"],
                        },
                    },
                    // Enhanced Agentic Workflow Tools
                    {
                        name: "start_enhanced_workflow",
                        description: "Start enhanced development workflow with advanced orchestration",
                        inputSchema: {
                            type: "object",
                            properties: {
                                requirements: {
                                    type: "string",
                                    description: "Business requirements description"
                                },
                                technology: {
                                    type: "string",
                                    enum: ["java_springboot", "dotnet_api", "nodejs_express", "python_fastapi"],
                                    description: "Target technology stack"
                                },
                                outputPath: {
                                    type: "string",
                                    description: "Base directory for generated project"
                                },
                                templateId: {
                                    type: "string",
                                    description: "Workflow template ID (optional)"
                                },
                                approvalMode: {
                                    type: "string",
                                    enum: ["interactive", "auto_approve", "batch"],
                                    default: "interactive",
                                    description: "Approval handling mode"
                                },
                                config: {
                                    type: "object",
                                    description: "Technology-specific configuration"
                                }
                            },
                            required: ["requirements", "technology", "outputPath"]
                        }
                    },
                    {
                        name: "get_enhanced_workflow_status",
                        description: "Get detailed status of enhanced workflow",
                        inputSchema: {
                            type: "object",
                            properties: {
                                workflowId: {
                                    type: "string",
                                    description: "Enhanced workflow ID"
                                }
                            },
                            required: ["workflowId"]
                        }
                    },
                    {
                        name: "handle_enhanced_approval",
                        description: "Handle approval for enhanced workflow phase",
                        inputSchema: {
                            type: "object",
                            properties: {
                                workflowId: { type: "string" },
                                phaseId: { type: "string" },
                                action: {
                                    type: "string",
                                    enum: ["approve", "modify", "retry", "skip", "cancel"]
                                },
                                modifications: {
                                    type: "object",
                                    description: "Modifications to apply if action is 'modify'"
                                },
                                feedback: {
                                    type: "string",
                                    description: "Feedback for the action"
                                },
                                userId: {
                                    type: "string",
                                    description: "User ID for audit trail"
                                }
                            },
                            required: ["workflowId", "phaseId", "action"]
                        }
                    },
                    {
                        name: "get_enhanced_pending_approvals",
                        description: "Get all pending approval requests with context",
                        inputSchema: {
                            type: "object",
                            properties: {},
                        }
                    },
                    {
                        name: "get_workflow_templates",
                        description: "Get available workflow templates",
                        inputSchema: {
                            type: "object",
                            properties: {
                                technology: {
                                    type: "string",
                                    description: "Filter by technology (optional)"
                                }
                            }
                        }
                    },
                    {
                        name: "start_development_workflow",
                        description: "Start complete end-to-end development workflow with all agents",
                        inputSchema: {
                            type: "object",
                            properties: {
                                requirements: {
                                    type: "string",
                                    description: "Initial business requirements"
                                },
                                technology: {
                                    type: "string",
                                    enum: ["java_springboot", "dotnet_api", "nodejs_express", "python_fastapi"],
                                    description: "Target technology stack"
                                },
                                outputPath: {
                                    type: "string",
                                    description: "Base directory for generated project"
                                },
                                approvalMode: {
                                    type: "string",
                                    enum: ["interactive", "auto_approve", "batch"],
                                    default: "interactive",
                                    description: "How to handle approval gates"
                                },
                                workflowConfig: {
                                    type: "object",
                                    description: "Workflow customization options"
                                }
                            },
                            required: ["requirements", "technology", "outputPath"]
                        }
                    },
                    {
                        name: "get_workflow_status",
                        description: "Get current status of running workflow",
                        inputSchema: {
                            type: "object",
                            properties: {
                                workflowId: {
                                    type: "string",
                                    description: "Workflow ID from start_development_workflow"
                                }
                            },
                            required: ["workflowId"]
                        }
                    },
                    {
                        name: "approve_workflow_phase",
                        description: "Approve or modify a workflow phase result",
                        inputSchema: {
                            type: "object",
                            properties: {
                                workflowId: { type: "string" },
                                phaseId: { type: "string" },
                                action: {
                                    type: "string",
                                    enum: ["approve", "modify", "retry", "skip"]
                                },
                                modifications: {
                                    type: "object",
                                    description: "Modifications to apply if action is 'modify'"
                                },
                                feedback: {
                                    type: "string",
                                    description: "Feedback for retry or modification"
                                }
                            },
                            required: ["workflowId", "phaseId", "action"]
                        }
                    },
                    {
                        name: "get_pending_approvals",
                        description: "Get all pending approval requests",
                        inputSchema: {
                            type: "object",
                            properties: {},
                        }
                    },
                    // Individual Agent Tools
                    {
                        name: "compile_project_with_agent",
                        description: "Compile project using the Code Compilation Agent",
                        inputSchema: {
                            type: "object",
                            properties: {
                                projectPath: {
                                    type: "string",
                                    description: "Path to the project to compile"
                                },
                                projectType: {
                                    type: "string",
                                    enum: ["java_springboot", "dotnet_api", "python_api", "nodejs_api"],
                                    description: "Type of project to compile"
                                },
                                buildOptions: {
                                    type: "object",
                                    description: "Build options and configuration"
                                }
                            },
                            required: ["projectPath"]
                        }
                    },
                    {
                        name: "generate_code_with_agent",
                        description: "Generate code using the Code Generation Agent",
                        inputSchema: {
                            type: "object",
                            properties: {
                                specification: {
                                    type: "object",
                                    description: "API specification or requirements"
                                },
                                outputPath: {
                                    type: "string",
                                    description: "Output directory for generated code"
                                },
                                technology: {
                                    type: "string",
                                    enum: ["java_springboot", "dotnet_api", "nodejs_express", "python_fastapi"],
                                    description: "Target technology stack"
                                }
                            },
                            required: ["specification", "outputPath", "technology"]
                        }
                    },
                    {
                        name: "review_code_with_agent",
                        description: "Review code using the Code Review Agent",
                        inputSchema: {
                            type: "object",
                            properties: {
                                projectPath: {
                                    type: "string",
                                    description: "Path to the project to review"
                                },
                                reviewScope: {
                                    type: "array",
                                    items: {
                                        type: "string",
                                        enum: ["quality", "security", "compliance", "performance"]
                                    },
                                    description: "Scope of the code review"
                                }
                            },
                            required: ["projectPath"]
                        }
                    },
                    {
                        name: "search_github_with_agent",
                        description: "Search GitHub repositories using the GitHub Search Agent",
                        inputSchema: {
                            type: "object",
                            properties: {
                                query: {
                                    type: "string",
                                    description: "Search query for GitHub repositories"
                                },
                                language: {
                                    type: "string",
                                    description: "Programming language filter"
                                },
                                minStars: {
                                    type: "number",
                                    description: "Minimum star count filter",
                                    default: 0
                                }
                            },
                            required: ["query"]
                        }
                    },
                    {
                        name: "search_web_with_agent",
                        description: "Search the web using the Web Search Agent",
                        inputSchema: {
                            type: "object",
                            properties: {
                                query: {
                                    type: "string",
                                    description: "Search query for web search"
                                },
                                context: {
                                    type: "string",
                                    description: "Additional context for the search"
                                }
                            },
                            required: ["query"]
                        }
                    },
                    {
                        name: "generate_api_spec_with_agent",
                        description: "Generate API specification using the API Spec Writer Agent",
                        inputSchema: {
                            type: "object",
                            properties: {
                                requirements: {
                                    type: "string",
                                    description: "Business requirements for the API"
                                },
                                projectName: {
                                    type: "string",
                                    description: "Name of the API project"
                                },
                                technology: {
                                    type: "string",
                                    enum: ["java_springboot", "dotnet_api", "nodejs_express", "python_fastapi"],
                                    description: "Target technology stack"
                                }
                            },
                            required: ["requirements", "projectName", "technology"]
                        }
                    },
                    // Project Management Tools
                    {
                        name: "list_generated_projects",
                        description: "List all generated projects from the generatedCode directory",
                        inputSchema: {
                            type: "object",
                            properties: {},
                        },
                    },
                    {
                        name: "read_file_content",
                        description: "Read the content of a specific file in a generated project",
                        inputSchema: {
                            type: "object",
                            properties: {
                                filePath: {
                                    type: "string",
                                    description: "Full path to the file to read"
                                }
                            },
                            required: ["filePath"]
                        }
                    },
                    {
                        name: "compile_code_with_agent",
                        description: "Compile a generated project using appropriate compilation tools",
                        inputSchema: {
                            type: "object",
                            properties: {
                                projectPath: {
                                    type: "string",
                                    description: "Path to the generated project directory"
                                },
                                technology: {
                                    type: "string",
                                    description: "Technology stack of the project"
                                }
                            },
                            required: ["projectPath", "technology"]
                        }
                    },
                    {
                        name: "review_code_with_agent",
                        description: "Review generated code for quality, security, and best practices",
                        inputSchema: {
                            type: "object",
                            properties: {
                                projectPath: {
                                    type: "string",
                                    description: "Path to the generated project directory"
                                },
                                technology: {
                                    type: "string",
                                    description: "Technology stack of the project"
                                }
                            },
                            required: ["projectPath", "technology"]
                        }
                    },
                ],
            };
        });
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            console.log('[DEBUG] MCP Tool Call Request:', request.params.name);
            console.log('[DEBUG] Request arguments:', JSON.stringify(request.params.arguments, null, 2));
            try {
                const { name, arguments: args } = request.params;
                if (!args || typeof args !== 'object') {
                    console.error('[ERROR] Invalid or missing arguments:', args);
                    throw new Error('Invalid or missing arguments');
                }
                console.log('[DEBUG] Processing tool:', name);
                switch (name) {
                    case "analyze_project_structure":
                        return await this.analyzeProjectStructure(args.projectPath, args.maxDepth || 3);
                    case "generate_code_template":
                        return await this.generateCodeTemplate(args.templateType, args.name, args.options || {});
                    case "analyze_code_quality":
                        return await this.analyzeCodeQuality(args.filePath, args.language);
                    case "generate_documentation":
                        return await this.generateDocumentation(args.filePath, args.docType);
                    case "git_workflow_helper":
                        return await this.gitWorkflowHelper(args.action, args.repositoryPath, args.files);
                    case "summarize_project_functionality":
                        return await this.summarizeProjectFunctionality(args.projectPath, args.language);
                    // Enhanced Agentic Workflow Tools
                    case "start_enhanced_workflow":
                        return await this.startEnhancedWorkflow(args.requirements, args.technology, args.outputPath, {
                            templateId: args.templateId,
                            approvalMode: args.approvalMode || "interactive",
                            config: args.config || {}
                        });
                    case "get_enhanced_workflow_status":
                        return await this.getEnhancedWorkflowStatus(args.workflowId);
                    case "handle_enhanced_approval":
                        return await this.handleEnhancedApproval(args.workflowId, args.phaseId, args.action, {
                            modifications: args.modifications,
                            feedback: args.feedback,
                            userId: args.userId
                        });
                    case "get_enhanced_pending_approvals":
                        return await this.getEnhancedPendingApprovals();
                    case "get_workflow_templates":
                        return await this.getWorkflowTemplates(args.technology);
                    case "start_development_workflow":
                        return await this.startDevelopmentWorkflow(args.requirements, args.technology, args.outputPath, args.approvalMode || "interactive", args.workflowConfig || {});
                    case "get_workflow_status":
                        return await this.getWorkflowStatus(args.workflowId);
                    case "approve_workflow_phase":
                        return await this.approveWorkflowPhase(args.workflowId, args.phaseId, args.action, args.modifications, args.feedback);
                    case "get_pending_approvals":
                        return await this.getPendingApprovals();
                    case "compile_project_with_agent":
                        const compileAgent = this.orchestrator.getAgent('compilation');
                        const compileResult = await compileAgent.compileProject(args.projectPath, args.language, args.buildTool);
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: `Compilation Result:\n${JSON.stringify(compileResult, null, 2)}`,
                                },
                            ],
                        };
                    case "generate_code_with_agent":
                        const genAgent = this.orchestrator.getAgent('generation');
                        const codeGenResult = await genAgent.generateProject(args.apiSpec, args.outputDir, args.framework);
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: `Code Generation Result:\n${JSON.stringify(codeGenResult, null, 2)}`,
                                },
                            ],
                        };
                    case "review_code_with_agent":
                        const reviewAgent = this.orchestrator.getAgent('review');
                        const reviewResult = await reviewAgent.reviewProject(args.filePath, args.criteria || ['quality', 'security']);
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: `Code Review Result:\n${JSON.stringify(reviewResult, null, 2)}`,
                                },
                            ],
                        };
                    case "search_github_with_agent":
                        const githubAgent = this.orchestrator.getAgent('github');
                        const githubResult = await githubAgent.searchCodebase(args.query, args.language, args.type || 'repositories');
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: `GitHub Search Result:\n${JSON.stringify(githubResult, null, 2)}`,
                                },
                            ],
                        };
                    case "search_web_with_agent":
                        const webAgent = this.orchestrator.getAgent('web');
                        const webResult = await webAgent.searchWeb(args.query, args.searchType || "general");
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: `Web Search Result:\n${JSON.stringify(webResult, null, 2)}`,
                                },
                            ],
                        };
                    case "generate_api_spec_with_agent":
                        console.log('[DEBUG] Starting API spec generation with agent');
                        console.log('[DEBUG] Input args:', JSON.stringify(args, null, 2));
                        try {
                            const apiAgent = this.orchestrator.getAgent('apispec');
                            console.log('[DEBUG] Retrieved API agent:', apiAgent ? 'SUCCESS' : 'FAILED');
                            if (!apiAgent) {
                                console.error('[ERROR] API agent not found in orchestrator');
                                throw new Error('API spec agent not available');
                            }
                            console.log('[DEBUG] Calling generateAPISpec with params:', {
                                requirements: args.requirements,
                                outputPath: args.outputPath || 'generated-api',
                                format: args.format || 'openapi'
                            });
                            const apiSpecResult = await apiAgent.generateAPISpec(args.requirements, args.outputPath || 'generated-api', args.format || 'openapi');
                            console.log('[DEBUG] API spec generation completed:', apiSpecResult ? 'SUCCESS' : 'FAILED');
                            console.log('[DEBUG] Result:', JSON.stringify(apiSpecResult, null, 2));
                            return {
                                content: [
                                    {
                                        type: "text",
                                        text: `API Spec Generation Result:\n${JSON.stringify(apiSpecResult, null, 2)}`,
                                    },
                                ],
                            };
                        }
                        catch (agentError) {
                            console.error('[ERROR] API spec generation failed:', agentError);
                            console.error('[ERROR] Stack trace:', agentError instanceof Error ? agentError.stack : 'No stack trace');
                            throw new Error(`API Spec Generation failed: ${agentError instanceof Error ? agentError.message : String(agentError)}`);
                        }
                    // Project Management Tools
                    case "list_generated_projects":
                        return await this.listGeneratedProjects();
                    case "read_file_content":
                        return await this.readFileContent(args.filePath);
                    case "compile_code_with_agent":
                        return await this.compileCodeWithAgent(args.projectPath, args.technology);
                    case "review_code_with_agent":
                        return await this.reviewCodeWithAgent(args.projectPath, args.technology);
                    default:
                        console.error('[ERROR] Unknown tool requested:', name);
                        throw new Error(`Unknown tool: ${name}`);
                }
            }
            catch (error) {
                console.error('[ERROR] Tool execution failed:', error);
                console.error('[ERROR] Error type:', typeof error);
                console.error('[ERROR] Error details:', error instanceof Error ? error.message : String(error));
                console.error('[ERROR] Stack trace:', error instanceof Error ? error.stack : 'No stack trace');
                return {
                    content: [
                        {
                            type: "text",
                            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
                        },
                    ],
                };
            }
        });
    }
    // Remove duplicate public handler methods and SDK-internal handler access
    // Only keep these public methods:
    async handleListTools() {
        return await this.listToolsHandler();
    }
    async handleCallTool(name, args) {
        return await this.callToolHandler(name, args);
    }
    async listToolsHandler() {
        // Replicate the logic from setupToolHandlers for listing tools
        return {
            tools: [
                {
                    name: "analyze_project_structure",
                    description: "Analyze and return the structure of a project directory",
                    inputSchema: {
                        type: "object",
                        properties: {
                            projectPath: {
                                type: "string",
                                description: "Path to the project directory",
                            },
                            maxDepth: {
                                type: "number",
                                description: "Maximum depth to traverse (default: 3)",
                                default: 3,
                            },
                        },
                        required: ["projectPath"],
                    },
                },
                {
                    name: "generate_code_template",
                    description: "Generate code templates for common patterns",
                    inputSchema: {
                        type: "object",
                        properties: {
                            templateType: {
                                type: "string",
                                enum: ["react-component", "express-route", "typescript-class", "test-file", "config-file"],
                                description: "Type of template to generate",
                            },
                            name: {
                                type: "string",
                                description: "Name for the generated code",
                            },
                            options: {
                                type: "object",
                                description: "Additional options for template generation",
                                properties: {
                                    typescript: { type: "boolean" },
                                    styled: { type: "boolean" },
                                    hooks: { type: "boolean" },
                                },
                            },
                        },
                        required: ["templateType", "name"],
                    },
                },
                {
                    name: "analyze_code_quality",
                    description: "Analyze code quality and suggest improvements",
                    inputSchema: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "Path to the code file to analyze",
                            },
                            language: {
                                type: "string",
                                description: "Programming language (auto-detected if not provided)",
                            },
                        },
                        required: ["filePath"],
                    },
                },
                {
                    name: "generate_documentation",
                    description: "Generate documentation for code files",
                    inputSchema: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "Path to the code file",
                            },
                            docType: {
                                type: "string",
                                enum: ["readme", "api-docs", "inline-comments", "jsdoc"],
                                description: "Type of documentation to generate",
                            },
                        },
                        required: ["filePath", "docType"],
                    },
                },
                {
                    name: "git_workflow_helper",
                    description: "Assist with Git operations and workflow",
                    inputSchema: {
                        type: "object",
                        properties: {
                            action: {
                                type: "string",
                                enum: ["status", "suggest-commit-message", "branch-info", "recent-changes"],
                                description: "Git action to perform",
                            },
                            repositoryPath: {
                                type: "string",
                                description: "Path to the Git repository",
                            },
                            files: {
                                type: "array",
                                items: { type: "string" },
                                description: "Specific files for commit message generation",
                            },
                        },
                        required: ["action", "repositoryPath"],
                    },
                },
                {
                    name: "summarize_project_functionality",
                    description: "Summarize and describe the main functionality of an existing project. Supports Java, .NET, or Node.js projects.",
                    inputSchema: {
                        type: "object",
                        properties: {
                            projectPath: {
                                type: "string",
                                description: "Path to the root of the project to summarize",
                            },
                            language: {
                                type: "string",
                                enum: ["java", ".net", "node"],
                                description: "Project language (java, .net, or node)",
                            },
                        },
                        required: ["projectPath", "language"],
                    },
                },
                // Enhanced Agentic Workflow Tools
                {
                    name: "start_enhanced_workflow",
                    description: "Start enhanced development workflow with advanced orchestration",
                    inputSchema: {
                        type: "object",
                        properties: {
                            requirements: {
                                type: "string",
                                description: "Business requirements description"
                            },
                            technology: {
                                type: "string",
                                enum: ["java_springboot", "dotnet_api", "nodejs_express", "python_fastapi"],
                                description: "Target technology stack"
                            },
                            outputPath: {
                                type: "string",
                                description: "Base directory for generated project"
                            },
                            templateId: {
                                type: "string",
                                description: "Workflow template ID (optional)"
                            },
                            approvalMode: {
                                type: "string",
                                enum: ["interactive", "auto_approve", "batch"],
                                default: "interactive",
                                description: "Approval handling mode"
                            },
                            config: {
                                type: "object",
                                description: "Technology-specific configuration"
                            }
                        },
                        required: ["requirements", "technology", "outputPath"]
                    }
                },
                {
                    name: "generate_api_spec_with_agent",
                    description: "Generate API specification using the API Spec Writer Agent",
                    inputSchema: {
                        type: "object",
                        properties: {
                            requirements: {
                                type: "string",
                                description: "Business requirements for the API"
                            },
                            projectName: {
                                type: "string",
                                description: "Name of the API project"
                            },
                            technology: {
                                type: "string",
                                enum: ["java_springboot", "dotnet_api", "nodejs_express", "python_fastapi"],
                                description: "Target technology stack"
                            }
                        },
                        required: ["requirements", "projectName", "technology"]
                    }
                },
            ],
        };
    }
    async callToolHandler(name, args) {
        // Replicate the switch logic from setupToolHandlers
        if (!args || typeof args !== 'object') {
            throw new Error('Invalid or missing arguments');
        }
        switch (name) {
            case "analyze_project_structure":
                return await this.analyzeProjectStructure(args.projectPath, args.maxDepth || 3);
            case "generate_code_template":
                return await this.generateCodeTemplate(args.templateType, args.name, args.options || {});
            case "analyze_code_quality":
                return await this.analyzeCodeQuality(args.filePath, args.language);
            case "generate_documentation":
                return await this.generateDocumentation(args.filePath, args.docType);
            case "git_workflow_helper":
                return await this.gitWorkflowHelper(args.action, args.repositoryPath, args.files);
            case "summarize_project_functionality":
                return await this.summarizeProjectFunctionality(args.projectPath, args.language);
            case "generate_api_spec_with_agent":
                console.log('[DEBUG] Starting API spec generation with agent');
                console.log('[DEBUG] Input args:', JSON.stringify(args, null, 2));
                try {
                    const apiAgent = this.orchestrator.getAgent('apispec');
                    console.log('[DEBUG] Retrieved API agent:', apiAgent ? 'SUCCESS' : 'FAILED');
                    if (!apiAgent) {
                        console.error('[ERROR] API agent not found in orchestrator');
                        throw new Error('API spec agent not available');
                    }
                    console.log('[DEBUG] Calling generateAPISpec with params:', {
                        requirements: args.requirements,
                        outputPath: args.outputPath || 'generated-api',
                        format: args.format || 'openapi'
                    });
                    const apiSpecResult = await apiAgent.generateAPISpec(args.requirements, args.outputPath || 'generated-api', args.format || 'openapi');
                    console.log('[DEBUG] API spec generation completed:', apiSpecResult ? 'SUCCESS' : 'FAILED');
                    console.log('[DEBUG] Result:', JSON.stringify(apiSpecResult, null, 2));
                    return {
                        content: [
                            {
                                type: "text",
                                text: `API Spec Generation Result:\n${JSON.stringify(apiSpecResult, null, 2)}`,
                            },
                        ],
                    };
                }
                catch (agentError) {
                    console.error('[ERROR] API spec generation failed:', agentError);
                    console.error('[ERROR] Stack trace:', agentError instanceof Error ? agentError.stack : 'No stack trace');
                    throw new Error(`API Spec Generation failed: ${agentError instanceof Error ? agentError.message : String(agentError)}`);
                }
            case "generate_code_with_agent":
                console.log('[DEBUG] Starting code generation with agent');
                const genAgent = this.orchestrator.getAgent('generation');
                console.log('[DEBUG] Retrieved generation agent:', genAgent ? 'SUCCESS' : 'FAILED');
                if (!genAgent) {
                    console.error('[ERROR] Generation agent not found in orchestrator');
                    throw new Error('Code generation agent not available');
                }
                const codeGenResult = await genAgent.generateProject(args.apiSpec, args.outputDir, args.framework);
                console.log('[DEBUG] Code generation completed:', codeGenResult ? 'SUCCESS' : 'FAILED');
                return {
                    content: [
                        {
                            type: "text",
                            text: `Code Generation Result:\n${JSON.stringify(codeGenResult, null, 2)}`,
                        },
                    ],
                };
            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    }
    async analyzeProjectStructure(projectPath, maxDepth) {
        try {
            const structure = await this.buildProjectStructure(projectPath, 0, maxDepth);
            const stats = await this.getProjectStats(projectPath);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            structure,
                            stats,
                            analysis: {
                                totalFiles: stats.fileCount,
                                totalDirectories: stats.dirCount,
                                languages: stats.languages,
                                recommendations: this.getProjectRecommendations(structure, stats),
                            },
                        }, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            throw new Error(`Failed to analyze project structure: ${error}`);
        }
    }
    async buildProjectStructure(dirPath, currentDepth, maxDepth) {
        const stats = await fs.stat(dirPath);
        const name = path.basename(dirPath);
        if (stats.isFile()) {
            return {
                name,
                type: 'file',
                path: dirPath,
                size: stats.size,
                lastModified: stats.mtime,
            };
        }
        const structure = {
            name,
            type: 'directory',
            path: dirPath,
            children: [],
        };
        if (currentDepth < maxDepth) {
            try {
                const entries = await fs.readdir(dirPath);
                const filteredEntries = entries.filter(entry => !entry.startsWith('.') || ['.gitignore', '.env.example'].includes(entry));
                for (const entry of filteredEntries) {
                    const fullPath = path.join(dirPath, entry);
                    try {
                        const childStructure = await this.buildProjectStructure(fullPath, currentDepth + 1, maxDepth);
                        structure.children.push(childStructure);
                    }
                    catch (error) {
                        // Skip inaccessible files/directories
                    }
                }
            }
            catch (error) {
                // Directory not accessible
            }
        }
        return structure;
    }
    async getProjectStats(projectPath) {
        let fileCount = 0;
        let dirCount = 0;
        const languages = new Set();
        const traverse = async (currentPath) => {
            try {
                const entries = await fs.readdir(currentPath, { withFileTypes: true });
                for (const entry of entries) {
                    if (entry.name.startsWith('.') && !entry.name.includes('git'))
                        continue;
                    const fullPath = path.join(currentPath, entry.name);
                    if (entry.isDirectory()) {
                        dirCount++;
                        await traverse(fullPath);
                    }
                    else {
                        fileCount++;
                        const ext = path.extname(entry.name).toLowerCase();
                        if (ext)
                            languages.add(ext);
                    }
                }
            }
            catch (error) {
                // Skip inaccessible directories
            }
        };
        await traverse(projectPath);
        return {
            fileCount,
            dirCount,
            languages: Array.from(languages),
        };
    }
    getProjectRecommendations(structure, stats) {
        const recommendations = [];
        // Check for common project files
        const hasPackageJson = this.findFile(structure, 'package.json');
        const hasReadme = this.findFile(structure, 'README.md') || this.findFile(structure, 'readme.md');
        const hasGitignore = this.findFile(structure, '.gitignore');
        if (!hasReadme)
            recommendations.push("Consider adding a README.md file for project documentation");
        if (!hasGitignore)
            recommendations.push("Consider adding a .gitignore file");
        if (hasPackageJson && !this.findFile(structure, 'package-lock.json') && !this.findFile(structure, 'yarn.lock')) {
            recommendations.push("Consider using a lock file (package-lock.json or yarn.lock) for dependency management");
        }
        if (stats.fileCount > 50 && !this.findFile(structure, 'tsconfig.json') && stats.languages.includes('.js')) {
            recommendations.push("Consider migrating to TypeScript for better type safety in larger projects");
        }
        return recommendations;
    }
    findFile(structure, fileName) {
        if (structure.type === 'file' && structure.name === fileName)
            return true;
        if (structure.children) {
            return structure.children.some(child => this.findFile(child, fileName));
        }
        return false;
    }
    async generateCodeTemplate(templateType, name, options) {
        const templates = {
            'react-component': this.generateReactComponent(name, options),
            'express-route': this.generateExpressRoute(name, options),
            'typescript-class': this.generateTypescriptClass(name, options),
            'test-file': this.generateTestFile(name, options),
            'config-file': this.generateConfigFile(name, options),
        };
        const template = templates[templateType];
        return {
            content: [
                {
                    type: "text",
                    text: JSON.stringify({
                        templateType,
                        name,
                        code: template,
                        suggestedFileName: this.getSuggestedFileName(templateType, name),
                    }, null, 2),
                },
            ],
        };
    }
    generateReactComponent(name, options) {
        const isTypeScript = options.typescript || false;
        const useHooks = options.hooks !== false;
        const styled = options.styled || false;
        const ext = isTypeScript ? 'tsx' : 'jsx';
        const typeAnnotations = isTypeScript ? ': React.FC' : '';
        return `import React${useHooks ? ', { useState, useEffect }' : ''} from 'react';
${styled ? "import styled from 'styled-components';" : ''}

${isTypeScript ? `interface ${name}Props {
  // Add your props here
}` : ''}

${styled ? `const StyledContainer = styled.div\`
  padding: 1rem;
  border-radius: 8px;
\`;` : ''}

const ${name}${typeAnnotations} = (${isTypeScript ? `props: ${name}Props` : 'props'}) => {
  ${useHooks ? 'const [state, setState] = useState(null);' : ''}
  
  ${useHooks ? `useEffect(() => {
    // Component initialization
  }, []);` : ''}

  return (
    ${styled ? '<StyledContainer>' : '<div>'}
      <h2>${name} Component</h2>
      {/* Your component content here */}
    ${styled ? '</StyledContainer>' : '</div>'}
  );
};

export default ${name};`;
    }
    generateExpressRoute(name, options) {
        return `import express from 'express';
import { Request, Response } from 'express';

const router = express.Router();

// GET /${name.toLowerCase()}
router.get('/', async (req: Request, res: Response) => {
  try {
    // Your GET logic here
    res.json({ message: '${name} GET endpoint' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /${name.toLowerCase()}
router.post('/', async (req: Request, res: Response) => {
  try {
    const data = req.body;
    // Your POST logic here
    res.status(201).json({ message: '${name} created successfully', data });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /${name.toLowerCase()}/:id
router.put('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const data = req.body;
    // Your PUT logic here
    res.json({ message: \`${name} \${id} updated successfully\`, data });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// DELETE /${name.toLowerCase()}/:id
router.delete('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    // Your DELETE logic here
    res.json({ message: \`${name} \${id} deleted successfully\` });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;`;
    }
    generateTypescriptClass(name, options) {
        return `export class ${name} {
  private _id: string;
  private _createdAt: Date;

  constructor(id?: string) {
    this._id = id || this.generateId();
    this._createdAt = new Date();
  }

  public get id(): string {
    return this._id;
  }

  public get createdAt(): Date {
    return this._createdAt;
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  // Add your methods here
  public toString(): string {
    return \`${name} {\${this._id}}\`;
  }
}`;
    }
    generateTestFile(name, options) {
        return `import { describe, it, expect, beforeEach, afterEach } from 'vitest';
// import { ${name} } from './${name}';

describe('${name}', () => {
  beforeEach(() => {
    // Setup before each test
  });

  afterEach(() => {
    // Cleanup after each test
  });

  it('should create an instance', () => {
    // const instance = new ${name}();
    // expect(instance).toBeDefined();
  });

  it('should handle basic functionality', () => {
    // Add your test cases here
    expect(true).toBe(true);
  });

  it('should handle edge cases', () => {
    // Add edge case tests here
    expect(true).toBe(true);
  });
});`;
    }
    generateConfigFile(name, options) {
        return `export const ${name}Config = {
  development: {
    apiUrl: 'http://localhost:3000/api',
    debug: true,
    logLevel: 'debug',
  },
  production: {
    apiUrl: process.env.API_URL || 'https://api.example.com',
    debug: false,
    logLevel: 'error',
  },
  test: {
    apiUrl: 'http://localhost:3001/api',
    debug: false,
    logLevel: 'silent',
  },
};

export const getConfig = () => {
  const env = process.env.NODE_ENV || 'development';
  return ${name}Config[env as keyof typeof ${name}Config];
};`;
    }
    getSuggestedFileName(templateType, name) {
        const fileNameMap = {
            'react-component': `${name}.tsx`,
            'express-route': `${name.toLowerCase()}.routes.ts`,
            'typescript-class': `${name}.ts`,
            'test-file': `${name}.test.ts`,
            'config-file': `${name.toLowerCase()}.config.ts`,
        };
        return fileNameMap[templateType] || `${name}.ts`;
    }
    async analyzeCodeQuality(filePath, language) {
        try {
            const code = await fs.readFile(filePath, 'utf-8');
            const detectedLanguage = language || this.detectLanguage(filePath);
            const analysis = this.performCodeAnalysis(code, detectedLanguage);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            filePath,
                            language: detectedLanguage,
                            analysis,
                        }, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            throw new Error(`Failed to analyze code quality: ${error}`);
        }
    }
    detectLanguage(filePath) {
        const ext = path.extname(filePath).toLowerCase();
        const languageMap = {
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.py': 'python',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
        };
        return languageMap[ext] || 'unknown';
    }
    performCodeAnalysis(code, language) {
        const lines = code.split('\n');
        const analysis = {
            lineCount: lines.length,
            characterCount: code.length,
            complexity: this.calculateComplexity(code),
            suggestions: [],
            metrics: {
                functionCount: 0,
                classCount: 0,
                commentLines: 0,
                emptyLines: 0,
            },
        };
        // Count various metrics
        lines.forEach(line => {
            const trimmed = line.trim();
            if (!trimmed)
                analysis.metrics.emptyLines++;
            if (trimmed.startsWith('//') || trimmed.startsWith('/*')) {
                analysis.metrics.commentLines++;
            }
            if (trimmed.includes('function ') || trimmed.includes('const ') && trimmed.includes('=>')) {
                analysis.metrics.functionCount++;
            }
            if (trimmed.includes('class ')) {
                analysis.metrics.classCount++;
            }
        });
        // Generate suggestions
        if (analysis.lineCount > 200) {
            analysis.suggestions.push("Consider breaking this file into smaller modules");
        }
        if (analysis.metrics.commentLines / analysis.lineCount < 0.1) {
            analysis.suggestions.push("Consider adding more comments for better code documentation");
        }
        if (analysis.complexity > 10) {
            analysis.suggestions.push("High cyclomatic complexity detected - consider refactoring");
        }
        return analysis;
    }
    calculateComplexity(code) {
        // Simple complexity calculation based on control structures
        const complexityPatterns = [
            /if\s*\(/g,
            /else\s*if/g,
            /while\s*\(/g,
            /for\s*\(/g,
            /catch\s*\(/g,
            /case\s+/g,
            /&&/g,
            /\|\|/g,
        ];
        let complexity = 1; // Base complexity
        complexityPatterns.forEach(pattern => {
            const matches = code.match(pattern);
            if (matches)
                complexity += matches.length;
        });
        return complexity;
    }
    async generateDocumentation(filePath, docType) {
        try {
            const code = await fs.readFile(filePath, 'utf-8');
            const language = this.detectLanguage(filePath);
            const documentation = this.createDocumentation(code, docType, language, filePath);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            filePath,
                            docType,
                            documentation,
                        }, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            throw new Error(`Failed to generate documentation: ${error}`);
        }
    }
    createDocumentation(code, docType, language, filePath) {
        const fileName = path.basename(filePath);
        switch (docType) {
            case 'readme':
                return this.generateReadme(fileName, code, language);
            case 'api-docs':
                return this.generateApiDocs(code, language);
            case 'inline-comments':
                return this.generateInlineComments(code, language);
            case 'jsdoc':
                return this.generateJSDoc(code);
            default:
                return 'Unknown documentation type';
        }
    }
    generateReadme(fileName, code, language) {
        return `# ${fileName}

## Description
This ${language} file contains [brief description of functionality].

## Usage
\`\`\`${language}
// Example usage here
\`\`\`

## Functions/Classes
${this.extractFunctionsAndClasses(code)}

## Installation
\`\`\`bash
npm install
\`\`\`

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
[License information]
`;
    }
    generateApiDocs(code, language) {
        const functions = this.extractFunctions(code);
        let docs = '# API Documentation\n\n';
        functions.forEach(func => {
            docs += `## ${func.name}\n`;
            docs += `**Description:** ${func.description || 'No description provided'}\n\n`;
            docs += `**Parameters:**\n`;
            docs += func.parameters.length ?
                func.parameters.map(p => `- \`${p}\`: Description\n`).join('') :
                '- None\n';
            docs += '\n**Returns:** Description of return value\n\n';
            docs += '**Example:**\n```javascript\n// Usage example\n```\n\n';
        });
        return docs;
    }
    generateInlineComments(code, language) {
        const lines = code.split('\n');
        return lines.map(line => {
            const trimmed = line.trim();
            if (trimmed.includes('function ') || trimmed.includes('const ') && trimmed.includes('=>')) {
                return line + ' // TODO: Add function description';
            }
            if (trimmed.includes('class ')) {
                return line + ' // TODO: Add class description';
            }
            return line;
        }).join('\n');
    }
    generateJSDoc(code) {
        const functions = this.extractFunctions(code);
        let documented = code;
        functions.forEach(func => {
            const jsdoc = `/**
 * ${func.description || 'Description of function'}
 * ${func.parameters.map(p => `@param {type} ${p} - Description of ${p}`).join('\n * ')}
 * @returns {type} Description of return value
 */
`;
            documented = documented.replace(func.signature, jsdoc + func.signature);
        });
        return documented;
    }
    extractFunctionsAndClasses(code) {
        const functions = this.extractFunctions(code);
        const classes = this.extractClasses(code);
        let result = '';
        if (functions.length) {
            result += '### Functions\n';
            functions.forEach(func => {
                result += `- \`${func.name}\`: ${func.description || 'No description'}\n`;
            });
        }
        if (classes.length) {
            result += '\n### Classes\n';
            classes.forEach(cls => {
                result += `- \`${cls}\`: Class description\n`;
            });
        }
        return result || 'No functions or classes found.';
    }
    extractFunctions(code) {
        const functionRegex = /(?:function\s+(\w+)|const\s+(\w+)\s*=.*?=>)/g;
        const functions = [];
        let match;
        while ((match = functionRegex.exec(code)) !== null) {
            const name = match[1] || match[2];
            const signature = match[0];
            const parameters = this.extractParameters(signature);
            functions.push({
                name,
                signature,
                parameters,
                description: null,
            });
        }
        return functions;
    }
    extractClasses(code) {
        const classRegex = /class\s+(\w+)/g;
        const classes = [];
        let match;
        while ((match = classRegex.exec(code)) !== null) {
            classes.push(match[1]);
        }
        return classes;
    }
    extractParameters(signature) {
        const paramMatch = signature.match(/\(([^)]*)\)/);
        if (!paramMatch)
            return [];
        return paramMatch[1]
            .split(',')
            .map(p => p.trim().split(/[:\s=]/)[0])
            .filter(p => p.length > 0);
    }
    async gitWorkflowHelper(action, repositoryPath, files) {
        try {
            let result;
            switch (action) {
                case 'status':
                    result = this.getGitStatus(repositoryPath);
                    break;
                case 'suggest-commit-message':
                    result = await this.suggestCommitMessage(repositoryPath, files);
                    break;
                case 'branch-info':
                    result = this.getBranchInfo(repositoryPath);
                    break;
                case 'recent-changes':
                    result = this.getRecentChanges(repositoryPath);
                    break;
                default:
                    throw new Error(`Unknown git action: ${action}`);
            }
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(result, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            throw new Error(`Git workflow helper failed: ${error}`);
        }
    }
    getGitStatus(repositoryPath) {
        try {
            const status = execSync('git status --porcelain', {
                cwd: repositoryPath,
                encoding: 'utf-8'
            });
            const files = status.trim().split('\n').filter(line => line.trim());
            const parsed = files.map(line => ({
                status: line.slice(0, 2),
                file: line.slice(3),
            }));
            return {
                action: 'status',
                clean: files.length === 0,
                files: parsed,
                summary: {
                    modified: parsed.filter(f => f.status.includes('M')).length,
                    added: parsed.filter(f => f.status.includes('A')).length,
                    deleted: parsed.filter(f => f.status.includes('D')).length,
                    untracked: parsed.filter(f => f.status.includes('??')).length,
                },
            };
        }
        catch (error) {
            throw new Error(`Failed to get git status: ${error}`);
        }
    }
    async suggestCommitMessage(repositoryPath, files) {
        try {
            const diff = execSync('git diff --staged', {
                cwd: repositoryPath,
                encoding: 'utf-8'
            });
            if (!diff.trim()) {
                return {
                    action: 'suggest-commit-message',
                    message: 'No staged changes found',
                    suggestions: [],
                };
            }
            const suggestions = this.analyzeChangesForCommitMessage(diff, files);
            return {
                action: 'suggest-commit-message',
                suggestions,
                conventional: this.generateConventionalCommits(suggestions),
            };
        }
        catch (error) {
            throw new Error(`Failed to suggest commit message: ${error}`);
        }
    }
    analyzeChangesForCommitMessage(diff, files) {
        const suggestions = [];
        // Analyze the diff for common patterns
        if (diff.includes('function ') || diff.includes('const ') && diff.includes('=>')) {
            suggestions.push('Add new function implementation');
        }
        if (diff.includes('import ') || diff.includes('require(')) {
            suggestions.push('Update dependencies and imports');
        }
        if (diff.includes('test(') || diff.includes('describe(')) {
            suggestions.push('Add/update test cases');
        }
        if (diff.includes('README') || diff.includes('documentation')) {
            suggestions.push('Update documentation');
        }
        if (diff.includes('fix') || diff.includes('bug')) {
            suggestions.push('Fix bug in implementation');
        }
        // If no specific patterns found, provide generic suggestions
        if (suggestions.length === 0) {
            suggestions.push('Update implementation');
            suggestions.push('Refactor code structure');
            suggestions.push('Improve functionality');
        }
        return suggestions;
    }
    generateConventionalCommits(suggestions) {
        return suggestions.map(suggestion => {
            if (suggestion.toLowerCase().includes('fix') || suggestion.toLowerCase().includes('bug')) {
                return `fix: ${suggestion.toLowerCase()}`;
            }
            if (suggestion.toLowerCase().includes('test')) {
                return `test: ${suggestion.toLowerCase()}`;
            }
            if (suggestion.toLowerCase().includes('doc')) {
                return `docs: ${suggestion.toLowerCase()}`;
            }
            if (suggestion.toLowerCase().includes('refactor')) {
                return `refactor: ${suggestion.toLowerCase()}`;
            }
            return `feat: ${suggestion.toLowerCase()}`;
        });
    }
    getBranchInfo(repositoryPath) {
        try {
            const currentBranch = execSync('git branch --show-current', {
                cwd: repositoryPath,
                encoding: 'utf-8'
            }).trim();
            const branches = execSync('git branch -a', {
                cwd: repositoryPath,
                encoding: 'utf-8'
            }).trim().split('\n').map(b => b.replace(/^\*?\s*/, ''));
            const remoteBranches = branches.filter(b => b.startsWith('remotes/'));
            const localBranches = branches.filter(b => !b.startsWith('remotes/'));
            return {
                action: 'branch-info',
                current: currentBranch,
                local: localBranches,
                remote: remoteBranches,
                total: branches.length,
            };
        }
        catch (error) {
            throw new Error(`Failed to get branch info: ${error}`);
        }
    }
    getRecentChanges(repositoryPath) {
        try {
            const log = execSync('git log --oneline -10', {
                cwd: repositoryPath,
                encoding: 'utf-8'
            });
            const commits = log.trim().split('\n').map(line => {
                const [hash, ...messageParts] = line.split(' ');
                return {
                    hash: hash,
                    message: messageParts.join(' '),
                };
            });
            return {
                action: 'recent-changes',
                commits,
                count: commits.length,
            };
        }
        catch (error) {
            throw new Error(`Failed to get recent changes: ${error}`);
        }
    }
    setupErrorHandling() {
        this.server.onerror = (error) => {
            console.error("[MCP Error]", error);
        };
        process.on("SIGINT", async () => {
            await this.server.close();
            process.exit(0);
        });
    }
    async summarizeWithOpenAI(prompt) {
        try {
            const completion = await this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [
                    { role: "system", content: "You are an expert software architect. Summarize the following project, focusing on both technical and business functionality. Extract business logic and main features from code comments and structure." },
                    { role: "user", content: prompt }
                ],
                max_tokens: 800,
                temperature: 0.3,
            });
            return completion.choices[0]?.message?.content || "(No summary generated)";
        }
        catch (e) {
            return `OpenAI summarization failed: ${e}`;
        }
    }
    async summarizeProjectFunctionality(projectPath, language) {
        try {
            // Gather metadata, README, and code samples as before
            let meta = "";
            let codeSamples = "";
            let readme = "";
            switch (language) {
                case "node":
                    try {
                        const pkgPath = path.join(projectPath, "package.json");
                        meta = await fs.readFile(pkgPath, "utf-8");
                    }
                    catch { }
                    break;
                case "java":
                    try {
                        const pomPath = path.join(projectPath, "pom.xml");
                        meta = await fs.readFile(pomPath, "utf-8");
                    }
                    catch { }
                    break;
                case ".net":
                    try {
                        const files = await fs.readdir(projectPath);
                        const csproj = files.find(f => f.endsWith('.csproj'));
                        if (csproj)
                            meta = await fs.readFile(path.join(projectPath, csproj), "utf-8");
                    }
                    catch { }
                    break;
            }
            try {
                readme = await fs.readFile(path.join(projectPath, "README.md"), "utf-8");
            }
            catch { }
            // Collect up to 3 code samples
            let files = [];
            async function walk(dir) {
                let entries = [];
                try {
                    entries = await fs.readdir(dir, { withFileTypes: true });
                }
                catch {
                    return;
                }
                for (const entry of entries) {
                    const fullPath = path.join(dir, entry.name);
                    if (entry.isDirectory() && !entry.name.startsWith('.'))
                        await walk(fullPath);
                    else if (entry.isFile() && [".js", ".ts", ".tsx", ".java", ".cs"].some(ext => entry.name.endsWith(ext)))
                        files.push(fullPath);
                }
            }
            await walk(projectPath);
            for (const file of files.slice(0, 3)) {
                try {
                    const code = await fs.readFile(file, "utf-8");
                    codeSamples += `\nFile: ${path.relative(projectPath, file)}\n\n${code.substring(0, 1200)}\n`;
                }
                catch { }
            }
            // Compose prompt
            const prompt = `Project metadata:\n${meta}\n\nREADME:\n${readme}\n\nCode samples:\n${codeSamples}`;
            const summary = await this.summarizeWithOpenAI(prompt);
            return {
                content: [
                    {
                        type: "text",
                        text: summary,
                    },
                ],
            };
        }
        catch (error) {
            throw new Error(`Failed to summarize project functionality: ${error}`);
        }
    }
    // Enhanced Agentic Workflow Methods
    async startEnhancedWorkflow(requirements, technology, outputPath, options = {}) {
        try {
            const result = await this.workflowOrchestrator.startWorkflow(requirements, technology, outputPath, {
                approvalMode: options.approvalMode || 'interactive',
                templateId: options.templateId,
                config: options.config
            });
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            workflowId: result.workflowId,
                            status: result.workflow.status,
                            currentPhase: result.workflow.currentPhase,
                            progress: result.workflow.progress,
                            message: "Enhanced development workflow started successfully",
                            phases: result.workflow.phases.map(p => ({
                                id: p.id,
                                name: p.name,
                                description: p.description,
                                status: p.status,
                                dependencies: p.dependencies
                            }))
                        }, null, 2)
                    }
                ]
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: error instanceof Error ? error.message : String(error)
                        }, null, 2)
                    }
                ]
            };
        }
    }
    async getEnhancedWorkflowStatus(workflowId) {
        try {
            const workflow = await this.workflowOrchestrator.getWorkflowStatus(workflowId);
            if (!workflow) {
                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify({ error: "Enhanced workflow not found" }, null, 2)
                        }
                    ]
                };
            }
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            workflowId: workflow.id,
                            status: workflow.status,
                            currentPhase: workflow.currentPhase,
                            progress: workflow.progress,
                            phases: workflow.phases.map(p => ({
                                id: p.id,
                                name: p.name,
                                description: p.description,
                                status: p.status,
                                startTime: p.startTime,
                                endTime: p.endTime,
                                retryCount: p.retryCount,
                                error: p.error,
                                dependencies: p.dependencies
                            })),
                            artifacts: workflow.artifacts,
                            createdAt: workflow.createdAt,
                            updatedAt: workflow.updatedAt,
                            estimatedCompletion: this.estimateCompletion(workflow)
                        }, null, 2)
                    }
                ]
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            error: error instanceof Error ? error.message : String(error)
                        }, null, 2)
                    }
                ]
            };
        }
    }
    async handleEnhancedApproval(workflowId, phaseId, action, options = {}) {
        try {
            const result = await this.workflowOrchestrator.handleApproval(workflowId, phaseId, action, options);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            success: result.success,
                            message: result.message,
                            workflowId,
                            phaseId,
                            action,
                            timestamp: new Date().toISOString()
                        }, null, 2)
                    }
                ]
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: error instanceof Error ? error.message : String(error)
                        }, null, 2)
                    }
                ]
            };
        }
    }
    async getEnhancedPendingApprovals() {
        try {
            const approvals = this.workflowOrchestrator.getPendingApprovals();
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            pendingApprovals: approvals.map(approval => ({
                                workflowId: approval.workflowId,
                                phaseId: approval.phaseId,
                                phaseName: approval.phaseName,
                                phaseDescription: approval.phaseDescription,
                                result: approval.result,
                                artifacts: approval.artifacts,
                                nextPhase: approval.nextPhase,
                                options: approval.options,
                                context: approval.context
                            })),
                            count: approvals.length
                        }, null, 2)
                    }
                ]
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            error: error instanceof Error ? error.message : String(error)
                        }, null, 2)
                    }
                ]
            };
        }
    }
    async getWorkflowTemplates(technology) {
        try {
            const templates = this.workflowOrchestrator.getWorkflowTemplates();
            const filteredTemplates = technology
                ? templates.filter(t => t.technology === technology)
                : templates;
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            templates: filteredTemplates.map(template => ({
                                id: template.id,
                                name: template.name,
                                description: template.description,
                                technology: template.technology,
                                phases: template.phases.map(p => ({
                                    id: p.id,
                                    name: p.name,
                                    description: p.description,
                                    dependencies: p.dependencies,
                                    approvalRequired: p.approvalRequired
                                })),
                                defaultConfig: template.defaultConfig
                            })),
                            count: filteredTemplates.length
                        }, null, 2)
                    }
                ]
            };
        }
        catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            error: error instanceof Error ? error.message : String(error)
                        }, null, 2)
                    }
                ]
            };
        }
    }
    estimateCompletion(workflow) {
        const remainingPhases = workflow.phases.filter(p => p.status === 'pending').length;
        const avgPhaseTime = 5; // 5 minutes average
        const estimatedMinutes = remainingPhases * avgPhaseTime;
        if (estimatedMinutes < 60) {
            return `${estimatedMinutes} minutes`;
        }
        else {
            const hours = Math.floor(estimatedMinutes / 60);
            const minutes = estimatedMinutes % 60;
            return `${hours}h ${minutes}m`;
        }
    }
    async startDevelopmentWorkflow(requirements, technology, outputPath, approvalMode = "interactive", workflowConfig = {}) {
        const workflowId = `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const workflow = {
            id: workflowId,
            requirements,
            technology,
            outputPath,
            approvalMode,
            config: workflowConfig,
            status: "running",
            currentPhase: "specification",
            phases: [
                {
                    id: "specification",
                    name: "API Specification",
                    status: "pending",
                    dependencies: [],
                    result: null,
                    timestamp: new Date()
                },
                {
                    id: "code_generation",
                    name: "Code Generation",
                    status: "pending",
                    dependencies: ["specification"],
                    result: null,
                    timestamp: new Date()
                },
                {
                    id: "code_review",
                    name: "Code Review",
                    status: "pending",
                    dependencies: ["code_generation"],
                    result: null,
                    timestamp: new Date()
                },
                {
                    id: "compilation",
                    name: "Compilation & Validation",
                    status: "pending",
                    dependencies: ["code_review"],
                    result: null,
                    timestamp: new Date()
                },
                {
                    id: "deployment",
                    name: "Deployment",
                    status: "pending",
                    dependencies: ["compilation"],
                    result: null,
                    timestamp: new Date()
                }
            ],
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.activeWorkflows.set(workflowId, workflow);
        // Start the first phase
        try {
            await this.executeWorkflowPhase(workflow, "specification");
        }
        catch (error) {
            workflow.status = "failed";
            workflow.error = error instanceof Error ? error.message : String(error);
        }
        return {
            content: [
                {
                    type: "text",
                    text: JSON.stringify({
                        workflowId,
                        status: workflow.status,
                        currentPhase: workflow.currentPhase,
                        message: "Development workflow started successfully"
                    }, null, 2)
                }
            ]
        };
    }
    async getWorkflowStatus(workflowId) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow) {
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({ error: "Workflow not found" }, null, 2)
                    }
                ]
            };
        }
        return {
            content: [
                {
                    type: "text",
                    text: JSON.stringify({
                        workflowId,
                        status: workflow.status,
                        currentPhase: workflow.currentPhase,
                        phases: workflow.phases.map(p => ({
                            id: p.id,
                            name: p.name,
                            status: p.status,
                            timestamp: p.timestamp
                        })),
                        error: workflow.error || null
                    }, null, 2)
                }
            ]
        };
    }
    async approveWorkflowPhase(workflowId, phaseId, action, modifications, feedback) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow) {
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({ error: "Workflow not found" }, null, 2)
                    }
                ]
            };
        }
        const phase = workflow.phases.find(p => p.id === phaseId);
        if (!phase) {
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({ error: "Phase not found" }, null, 2)
                    }
                ]
            };
        }
        // Remove from pending approvals
        this.pendingApprovals.delete(`${workflowId}:${phaseId}`);
        switch (action) {
            case "approve":
                phase.status = "completed";
                await this.proceedToNextPhase(workflow);
                break;
            case "modify":
                if (modifications) {
                    phase.result = { ...phase.result, ...modifications };
                }
                phase.status = "completed";
                await this.proceedToNextPhase(workflow);
                break;
            case "retry":
                phase.status = "pending";
                await this.executeWorkflowPhase(workflow, phaseId);
                break;
            case "skip":
                phase.status = "skipped";
                await this.proceedToNextPhase(workflow);
                break;
        }
        return {
            content: [
                {
                    type: "text",
                    text: JSON.stringify({
                        workflowId,
                        phaseId,
                        action,
                        status: phase.status,
                        message: `Phase ${action} successful`
                    }, null, 2)
                }
            ]
        };
    }
    async getPendingApprovals() {
        const approvals = Array.from(this.pendingApprovals.entries()).map(([key, approval]) => ({
            key,
            ...approval
        }));
        return {
            content: [
                {
                    type: "text",
                    text: JSON.stringify({ pendingApprovals: approvals }, null, 2)
                }
            ]
        };
    }
    async executeWorkflowPhase(workflow, phaseId) {
        const phase = workflow.phases.find(p => p.id === phaseId);
        if (!phase)
            return;
        phase.status = "running";
        workflow.currentPhase = phaseId;
        workflow.updatedAt = new Date();
        try {
            // Use the agent orchestrator to execute the phase with real agents
            const input = {
                requirements: workflow.requirements,
                technology: workflow.technology,
                outputPath: workflow.outputPath,
                projectPath: workflow.outputPath,
                projectName: `Generated-${workflow.technology}-Project`,
                specification: phase.id === 'specification' ? null : this.getPhaseResult(workflow, 'specification'),
                reviewScope: ['quality', 'security', 'compliance'],
                buildOptions: {}
            };
            const agentResult = await this.orchestrator.executeWorkflowPhase(phaseId, input);
            if (agentResult.success) {
                phase.result = agentResult.data;
            }
            else {
                throw new Error(agentResult.error || 'Unknown agent error');
            }
            if (workflow.approvalMode === "interactive") {
                phase.status = "waiting_approval";
                this.pendingApprovals.set(`${workflow.id}:${phaseId}`, {
                    workflowId: workflow.id,
                    phaseId,
                    phaseName: phase.name,
                    result: phase.result,
                    timestamp: new Date(),
                    options: ["approve", "modify", "retry", "skip"]
                });
            }
            else {
                phase.status = "completed";
                await this.proceedToNextPhase(workflow);
            }
        }
        catch (error) {
            phase.status = "failed";
            phase.error = error instanceof Error ? error.message : String(error);
            workflow.status = "failed";
            workflow.error = phase.error;
        }
    }
    getPhaseResult(workflow, phaseId) {
        const phase = workflow.phases.find(p => p.id === phaseId);
        return phase?.result || null;
    }
    async proceedToNextPhase(workflow) {
        const currentPhaseIndex = workflow.phases.findIndex(p => p.id === workflow.currentPhase);
        if (currentPhaseIndex < workflow.phases.length - 1) {
            const nextPhase = workflow.phases[currentPhaseIndex + 1];
            await this.executeWorkflowPhase(workflow, nextPhase.id);
        }
        else {
            workflow.status = "completed";
            workflow.updatedAt = new Date();
        }
    }
    async executeSpecificationPhase(workflow) {
        // Simulate API specification generation
        return {
            specification: {
                title: `${workflow.technology} API`,
                version: "1.0.0",
                description: `Generated from requirements: ${workflow.requirements}`,
                endpoints: [
                    { path: "/api/health", method: "GET", description: "Health check endpoint" },
                    { path: "/api/data", method: "GET", description: "Get data endpoint" },
                    { path: "/api/data", method: "POST", description: "Create data endpoint" }
                ]
            },
            message: "API specification generated successfully"
        };
    }
    async executeCodeGenerationPhase(workflow) {
        // Simulate code generation
        return {
            generatedFiles: [
                `${workflow.outputPath}/src/main/Application.java`,
                `${workflow.outputPath}/src/main/Controller.java`,
                `${workflow.outputPath}/pom.xml`
            ],
            message: "Code generation completed successfully"
        };
    }
    async executeCodeReviewPhase(workflow) {
        // Simulate code review
        return {
            reviewScore: 8.5,
            issues: [
                { severity: "minor", description: "Consider adding input validation" },
                { severity: "suggestion", description: "Add more comprehensive error handling" }
            ],
            message: "Code review completed successfully"
        };
    }
    async executeCompilationPhase(workflow) {
        // Simulate compilation
        return {
            compilationResult: "success",
            warnings: 2,
            errors: 0,
            message: "Compilation completed successfully"
        };
    }
    async executeDeploymentPhase(workflow) {
        // Simulate deployment
        return {
            deploymentUrl: `http://localhost:8080`,
            status: "deployed",
            message: "Application deployed successfully"
        };
    }
    // Project Management Methods
    async listGeneratedProjects() {
        try {
            const generatedCodeDir = path.join(process.cwd(), '..', 'Agents', 'CodeGenerationAgent', 'generated_examples');
            // Check if directory exists
            try {
                await fs.access(generatedCodeDir);
            }
            catch {
                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify({ success: true, projects: [] }, null, 2),
                        },
                    ],
                };
            }
            const entries = await fs.readdir(generatedCodeDir, { withFileTypes: true });
            const projects = [];
            for (const entry of entries) {
                if (entry.isDirectory()) {
                    const projectPath = path.join(generatedCodeDir, entry.name);
                    try {
                        const stats = await fs.stat(projectPath);
                        // Analyze project structure to get file count and technology
                        const projectStructure = await this.analyzeProjectDirectory(projectPath);
                        projects.push({
                            name: entry.name,
                            path: projectPath,
                            createdAt: stats.birthtime,
                            technology: this.detectProjectTechnology(projectPath),
                            status: 'generated',
                            fileCount: projectStructure.fileCount,
                            size: this.formatFileSize(projectStructure.totalSize),
                            lastAction: 'Generated'
                        });
                    }
                    catch (err) {
                        console.error(`Error analyzing project ${entry.name}:`, err);
                    }
                }
            }
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({ success: true, projects }, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            console.error('[ERROR] List generated projects failed:', error);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: error instanceof Error ? error.message : String(error)
                        }, null, 2),
                    },
                ],
            };
        }
    }
    async readFileContent(filePath) {
        try {
            const content = await fs.readFile(filePath, 'utf8');
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({ success: true, content }, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            console.error('[ERROR] Read file content failed:', error);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: error instanceof Error ? error.message : String(error)
                        }, null, 2),
                    },
                ],
            };
        }
    }
    async compileCodeWithAgent(projectPath, technology) {
        try {
            const compilationAgent = this.orchestrator.getAgent('compilation');
            if (!compilationAgent || typeof compilationAgent.compileProject !== 'function') {
                throw new Error('Compilation agent not available');
            }
            const result = await compilationAgent.compileProject(projectPath, technology, {} // buildOptions
            );
            // Helper functions to extract info from error messages
            const extractFileNameFromMessage = (message) => {
                const fileMatch = message.match(/\/([^\/]+\.java):\[/);
                return fileMatch ? fileMatch[1] : null;
            };
            const extractLineFromMessage = (message) => {
                const lineMatch = message.match(/:?\[(\d+),\d+\]/);
                return lineMatch ? parseInt(lineMatch[1], 10) : null;
            };
            const extractColumnFromMessage = (message) => {
                const columnMatch = message.match(/:?\[\d+,(\d+)\]/);
                return columnMatch ? parseInt(columnMatch[1], 10) : null;
            };
            const cleanErrorMessage = (message) => {
                // Remove file path and line info from the beginning if it exists
                return message.replace(/^.*?\.java:\[\d+,\d+\]\s*/, '').trim();
            };
            // Transform the agent result for the UI
            let transformedResult;
            if (result.data) {
                // Extract the compilation data from the nested structure
                const compilationData = result.data;
                if (compilationData.issues && Array.isArray(compilationData.issues)) {
                    // Transform error format to match UI expectations
                    const transformedErrors = compilationData.issues
                        .filter((issue) => issue.severity === 'error') // Only show errors for now
                        .map((issue) => ({
                        file: issue.file_path || extractFileNameFromMessage(issue.message) || 'Unknown file',
                        line: issue.line_number || extractLineFromMessage(issue.message) || 0,
                        column: issue.column_number || extractColumnFromMessage(issue.message) || 0,
                        message: cleanErrorMessage(issue.message) || '',
                        severity: issue.severity === 'error' ? 'error' : 'warning'
                    }));
                    transformedResult = {
                        success: compilationData.summary?.build_successful === true,
                        errors: transformedErrors,
                        output: `Compilation ${compilationData.summary?.build_successful ? 'successful' : 'failed'} - ${transformedErrors.length} errors found`
                    };
                }
                else if (compilationData.errors && Array.isArray(compilationData.errors)) {
                    // Fallback to old format if still using 'errors' field
                    const transformedErrors = compilationData.errors.map((error) => ({
                        file: error.file_path || '',
                        line: error.line_number || 0,
                        column: error.column_number || 0,
                        message: error.message || '',
                        severity: error.severity === 'error' ? 'error' : 'warning'
                    }));
                    transformedResult = {
                        success: compilationData.metadata?.return_code === 0,
                        errors: transformedErrors,
                        output: transformedErrors.length > 0 ?
                            `Compilation failed with ${transformedErrors.length} errors/warnings` :
                            'Compilation completed'
                    };
                }
                else {
                    // Fallback for other data formats
                    transformedResult = {
                        success: result.success,
                        errors: [],
                        output: result.data.output || 'Compilation completed'
                    };
                }
            }
            else {
                // Handle failure case
                transformedResult = {
                    success: false,
                    errors: [],
                    output: result.error || 'Compilation failed'
                };
            }
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(transformedResult, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            console.error('[ERROR] Code compilation failed:', error);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            errors: [],
                            output: `Error during compilation process: ${error instanceof Error ? error.message : String(error)}`
                        }, null, 2),
                    },
                ],
            };
        }
    }
    async reviewCodeWithAgent(projectPath, technology) {
        try {
            const reviewAgent = this.orchestrator.getAgent('review');
            if (!reviewAgent || typeof reviewAgent.reviewProject !== 'function') {
                throw new Error('Review agent not available');
            }
            const result = await reviewAgent.reviewProject(projectPath, ['quality', 'security', 'compliance', 'performance']);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(result, null, 2),
                    },
                ],
            };
        }
        catch (error) {
            console.error('[ERROR] Code review failed:', error);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: error instanceof Error ? error.message : String(error)
                        }, null, 2),
                    },
                ],
            };
        }
    }
    // Helper methods for project management
    async analyzeProjectDirectory(projectPath) {
        let fileCount = 0;
        let totalSize = 0;
        const analyzeRecursive = async (dirPath) => {
            const entries = await fs.readdir(dirPath, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry.name);
                if (entry.isDirectory()) {
                    // Skip node_modules, .git, and other build directories
                    if (!['node_modules', '.git', 'target', 'build', 'dist', '.next'].includes(entry.name)) {
                        await analyzeRecursive(fullPath);
                    }
                }
                else {
                    fileCount++;
                    const stats = await fs.stat(fullPath);
                    totalSize += stats.size;
                }
            }
        };
        await analyzeRecursive(projectPath);
        return { fileCount, totalSize };
    }
    detectProjectTechnology(projectPath) {
        try {
            // Check for Spring Boot (Java)
            if (existsSync(path.join(projectPath, 'pom.xml')) ||
                existsSync(path.join(projectPath, 'build.gradle'))) {
                return 'Java Spring Boot';
            }
            // Check for .NET
            if (existsSync(path.join(projectPath, '*.csproj'))) {
                return '.NET Web API';
            }
            // Check for Node.js
            if (existsSync(path.join(projectPath, 'package.json'))) {
                return 'Node.js Express';
            }
            // Check for Python
            if (existsSync(path.join(projectPath, 'requirements.txt')) ||
                existsSync(path.join(projectPath, 'pyproject.toml'))) {
                return 'Python FastAPI';
            }
            return 'Unknown';
        }
        catch {
            return 'Unknown';
        }
    }
    formatFileSize(bytes) {
        if (bytes === 0)
            return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}
console.log('[DEBUG] Creating Express app...');
const app = express();
console.log('[DEBUG] Setting up middleware...');
app.use(cors());
app.use(express.json());
console.log('[DEBUG] Creating server instance...');
const serverInstance = new DeveloperAssistantServer();
console.log('[DEBUG] Server instance created successfully');
// Health check endpoint
app.get('/health', (req, res) => {
    console.log('[DEBUG] Health check endpoint called');
    res.status(200).json({ status: 'ok' });
});
// List tools endpoint
app.get('/tools/list', async (req, res) => {
    console.log('[DEBUG] List tools endpoint called');
    try {
        const result = await serverInstance.handleListTools();
        res.json(result);
    }
    catch (error) {
        console.error('[ERROR] List tools error:', error);
        res.status(500).json({ error: error instanceof Error ? error.message : String(error) });
    }
});
// Call tool endpoint
app.post('/tools/call', async (req, res) => {
    console.log('[DEBUG] Call tool endpoint called with:', req.body);
    try {
        const { name, arguments: args } = req.body;
        const result = await serverInstance.handleCallTool(name, args);
        res.json(result);
    }
    catch (error) {
        console.error('[ERROR] Call tool error:', error);
        res.status(500).json({ error: error instanceof Error ? error.message : String(error) });
    }
});
// List saved API specifications
app.get('/specs/list', async (req, res) => {
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
});
// Define the individual spec handler separately
const getSpecHandler = async (req, res) => {
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
            return res.status(404).json({
                success: false,
                error: 'Specification file not found'
            });
        }
        const content = await fs.readFile(filePath, 'utf8');
        res.json({ success: true, content });
    }
    catch (error) {
        console.error('[ERROR] Get spec error:', error);
        res.status(500).json({
            success: false,
            error: error instanceof Error ? error.message : String(error)
        });
    }
};
// Register the endpoint
app.get('/specs/:fileName', getSpecHandler);
const PORT = 3001;
console.log('[DEBUG] Starting Express server on port', PORT);
app.listen(PORT, () => {
    console.log(`Developer Assistant MCP server running on http://localhost:${PORT}`);
}).on('error', (error) => {
    console.error('[ERROR] Failed to start Express server:', error);
    process.exit(1);
});
