/**
 * Agent-related tool handlers
 */
import { BaseToolHandler } from './BaseToolHandler.js';
import { transformCompilationError } from '../utils/index.js';
export class CompileCodeWithAgentHandler extends BaseToolHandler {
    async handle(args, context) {
        console.log('[DEBUG] Starting compilation with agent');
        const compileAgent = context.orchestrator.getAgent('compilation');
        console.log('[DEBUG] Retrieved compilation agent:', compileAgent ? 'SUCCESS' : 'FAILED');
        if (!compileAgent) {
            console.error('[ERROR] Compilation agent not found in orchestrator');
            throw new Error('Code compilation agent not available');
        }
        const { projectPath } = args;
        if (!projectPath) {
            throw new Error('projectPath parameter is required');
        }
        const compileResult = await compileAgent.compileProject(projectPath);
        console.log('[DEBUG] Compilation completed:', compileResult ? 'SUCCESS' : 'FAILED');
        // Transform compilation errors if present
        if (compileResult && compileResult.data && compileResult.data.issues && Array.isArray(compileResult.data.issues)) {
            compileResult.data.issues = compileResult.data.issues.map((issue) => {
                if (typeof issue === 'string') {
                    return transformCompilationError(issue);
                }
                return issue;
            });
        }
        else if (compileResult && compileResult.data && compileResult.data.errors && Array.isArray(compileResult.data.errors)) {
            compileResult.data.errors = compileResult.data.errors.map((error) => {
                if (typeof error === 'string') {
                    return transformCompilationError(error);
                }
                return error;
            });
        }
        return this.createJsonResult({
            message: "Compilation Result",
            result: compileResult
        });
    }
}
export class ReviewCodeWithAgentHandler extends BaseToolHandler {
    async handle(args, context) {
        console.log('[DEBUG] Starting code review with agent');
        const reviewAgent = context.orchestrator.getAgent('review');
        console.log('[DEBUG] Retrieved review agent:', reviewAgent ? 'SUCCESS' : 'FAILED');
        if (!reviewAgent) {
            console.error('[ERROR] Review agent not found in orchestrator');
            throw new Error('Code review agent not available');
        }
        const { filePath, projectPath, reviewType } = args;
        const targetPath = filePath || projectPath;
        if (!targetPath) {
            throw new Error('filePath or projectPath parameter is required');
        }
        const reviewResult = await reviewAgent.reviewProject(targetPath, reviewType ? [reviewType] : ['quality', 'security']);
        console.log('[DEBUG] Code review completed:', reviewResult ? 'SUCCESS' : 'FAILED');
        return this.createJsonResult({
            message: "Code Review Result",
            result: reviewResult
        });
    }
}
export class GenerateCodeWithAgentHandler extends BaseToolHandler {
    async handle(args, context) {
        console.log('[DEBUG] Starting code generation with agent');
        const genAgent = context.orchestrator.getAgent('generation');
        console.log('[DEBUG] Retrieved generation agent:', genAgent ? 'SUCCESS' : 'FAILED');
        if (!genAgent) {
            console.error('[ERROR] Generation agent not found in orchestrator');
            throw new Error('Code generation agent not available');
        }
        const { apiSpec, outputDir, framework } = args;
        if (!apiSpec || !outputDir) {
            throw new Error('apiSpec and outputDir parameters are required');
        }
        const codeGenResult = await genAgent.generateProject(apiSpec, outputDir, framework);
        console.log('[DEBUG] Code generation completed:', codeGenResult ? 'SUCCESS' : 'FAILED');
        return this.createJsonResult({
            message: "Code Generation Result",
            result: codeGenResult
        });
    }
}
export class GenerateApiSpecWithAgentHandler extends BaseToolHandler {
    async handle(args, context) {
        console.log('[DEBUG] Starting API spec generation with agent');
        console.log('[DEBUG] Input args:', JSON.stringify(args, null, 2));
        const apiAgent = context.orchestrator.getAgent('apispec');
        console.log('[DEBUG] Retrieved API agent:', apiAgent ? 'SUCCESS' : 'FAILED');
        if (!apiAgent) {
            console.error('[ERROR] API agent not found in orchestrator');
            throw new Error('API spec agent not available');
        }
        const { requirements, outputPath = 'generated-api', format = 'openapi' } = args;
        if (!requirements) {
            throw new Error('requirements parameter is required');
        }
        console.log('[DEBUG] Calling generateAPISpec with params:', {
            requirements,
            outputPath,
            format
        });
        try {
            const apiSpecResult = await apiAgent.generateAPISpec(requirements, outputPath, format);
            console.log('[DEBUG] API spec generation completed:', apiSpecResult ? 'SUCCESS' : 'FAILED');
            console.log('[DEBUG] Result:', JSON.stringify(apiSpecResult, null, 2));
            return this.createJsonResult({
                message: "API Spec Generation Result",
                result: apiSpecResult
            });
        }
        catch (agentError) {
            console.error('[ERROR] API spec generation failed:', agentError);
            console.error('[ERROR] Stack trace:', agentError instanceof Error ? agentError.stack : 'No stack trace');
            throw new Error(`API Spec Generation failed: ${agentError instanceof Error ? agentError.message : String(agentError)}`);
        }
    }
}
export class FixCompilationIssuesWithAgentHandler extends BaseToolHandler {
    async handle(args, context) {
        console.log('[DEBUG] Starting fix compilation issues with agent');
        console.log('[DEBUG] Input args:', JSON.stringify(args, null, 2));
        const fixAgent = context.orchestrator.getAgent('fixcompilation');
        console.log('[DEBUG] Retrieved fix compilation agent:', fixAgent ? 'SUCCESS' : 'FAILED');
        if (!fixAgent) {
            console.error('[ERROR] Fix compilation agent not found in orchestrator');
            throw new Error('Fix compilation issues agent not available');
        }
        const { projectPath, errors, buildTool = 'maven', buildOutput } = args;
        if (!projectPath) {
            throw new Error('projectPath parameter is required');
        }
        // Allow empty errors array - the agent can analyze build output or scan project files
        const compilationErrors = errors || [];
        console.log('[DEBUG] Calling fixCompilationIssues with params:', {
            projectPath,
            errorsCount: compilationErrors.length,
            buildTool,
            hasBuildOutput: !!buildOutput
        });
        try {
            const fixResult = await fixAgent.fixCompilationIssues(projectPath, compilationErrors, buildTool, buildOutput);
            console.log('[DEBUG] Fix compilation issues completed:', fixResult ? 'SUCCESS' : 'FAILED');
            console.log('[DEBUG] Result:', JSON.stringify(fixResult, null, 2));
            return this.createJsonResult({
                message: "Fix Compilation Issues Result",
                result: fixResult
            });
        }
        catch (agentError) {
            console.error('[ERROR] Fix compilation issues failed:', agentError);
            console.error('[ERROR] Stack trace:', agentError instanceof Error ? agentError.stack : 'No stack trace');
            throw new Error(`Fix compilation issues failed: ${agentError instanceof Error ? agentError.message : String(agentError)}`);
        }
    }
}
export class EnhancedCompileCodeHandler extends BaseToolHandler {
    /**
     * Enhanced compilation handler with OpenAI analysis and simplified output format.
     * This provides a standardized, simplified format for both UI display and agent consumption.
     */
    async handle(args, context) {
        console.log('[DEBUG] Starting enhanced compilation with OpenAI analysis');
        console.log('[DEBUG] Input args:', JSON.stringify(args, null, 2));
        const { projectPath, projectType, buildOptions, enableOpenAI = true, format = 'simplified' } = args;
        if (!projectPath) {
            throw new Error('projectPath parameter is required');
        }
        try {
            // Try to use the enhanced Python compilation agent if available
            const { spawn } = await import('child_process');
            const path = await import('path');
            // Path to the enhanced compilation agent
            const agentPath = path.join(__dirname, '../../..', 'Agents', 'CodeCompilationAgent', 'compile_cli.py');
            console.log('[DEBUG] Using enhanced compilation agent at:', agentPath);
            // Prepare command arguments
            const command = 'python3';
            const commandArgs = [
                agentPath,
                projectPath,
                '--json-output',
                '--format', format
            ];
            if (projectType) {
                commandArgs.push('--type', projectType);
            }
            if (enableOpenAI) {
                // Check for OpenAI API key
                const openaiKey = process.env.OPENAI_API_KEY ||
                    (context.openai ? context.openai.apiKey : null);
                if (openaiKey) {
                    commandArgs.push('--openai-key', openaiKey);
                    console.log('[DEBUG] OpenAI analysis enabled');
                }
                else {
                    commandArgs.push('--disable-ai');
                    console.log('[WARN] OpenAI API key not found, AI analysis disabled');
                }
            }
            else {
                commandArgs.push('--disable-ai');
            }
            if (buildOptions) {
                if (buildOptions.goals && Array.isArray(buildOptions.goals)) {
                    commandArgs.push('--goals', buildOptions.goals.join(','));
                }
                if (buildOptions.skipTests) {
                    commandArgs.push('--skip-tests');
                }
                if (buildOptions.timeout) {
                    commandArgs.push('--timeout', buildOptions.timeout.toString());
                }
            }
            console.log('[DEBUG] Executing command:', command, commandArgs.join(' '));
            // Execute the enhanced compilation agent
            const result = await new Promise((resolve, reject) => {
                const process = spawn(command, commandArgs, {
                    stdio: ['pipe', 'pipe', 'pipe'],
                    cwd: path.dirname(agentPath)
                });
                let stdout = '';
                let stderr = '';
                process.stdout.on('data', (data) => {
                    stdout += data.toString();
                });
                process.stderr.on('data', (data) => {
                    stderr += data.toString();
                });
                process.on('close', (code) => {
                    if (code === 0 || code === 1) { // 0 = success, 1 = compilation failed (but agent worked)
                        resolve(stdout);
                    }
                    else {
                        reject(new Error(`Enhanced compilation agent failed with code ${code}: ${stderr}`));
                    }
                });
                process.on('error', (error) => {
                    reject(new Error(`Failed to execute enhanced compilation agent: ${error.message}`));
                });
            });
            console.log('[DEBUG] Enhanced compilation completed successfully');
            // Parse the JSON result
            let compilationResult;
            try {
                compilationResult = JSON.parse(result);
            }
            catch (parseError) {
                console.error('[ERROR] Failed to parse compilation result as JSON:', parseError);
                console.log('[DEBUG] Raw result:', result);
                // Fallback to text result
                return this.createTextResult(result);
            }
            console.log('[DEBUG] Parsed compilation result:', JSON.stringify(compilationResult, null, 2));
            return this.createJsonResult({
                message: "Enhanced Compilation Result with AI Analysis",
                result: compilationResult
            });
        }
        catch (error) {
            console.error('[ERROR] Enhanced compilation failed:', error);
            // Fallback to the original compilation agent
            console.log('[DEBUG] Falling back to original compilation agent');
            const compileAgent = context.orchestrator.getAgent('compilation');
            if (!compileAgent) {
                throw new Error('Both enhanced and original compilation agents are unavailable');
            }
            const compileResult = await compileAgent.compileProject(projectPath);
            // Transform to simplified format if requested
            if (format === 'simplified' && compileResult && compileResult.data) {
                const simplifiedResult = this.transformToSimplifiedFormat(compileResult.data, projectPath);
                return this.createJsonResult({
                    message: "Compilation Result (Fallback)",
                    result: simplifiedResult
                });
            }
            return this.createJsonResult({
                message: "Compilation Result (Fallback)",
                result: compileResult
            });
        }
    }
    transformToSimplifiedFormat(originalResult, projectPath) {
        /**
         * Transform original compilation result to simplified format for consistency.
         */
        const issues = originalResult.issues || originalResult.errors || [];
        const transformedIssues = issues.map((issue, index) => ({
            id: issue.id || `issue_${index}`,
            severity: issue.severity || 'error',
            message: issue.message || issue.toString(),
            location: {
                file_path: issue.file_path || issue.filePath || projectPath,
                line_number: issue.line_number || issue.lineNumber || null,
                column_number: issue.column_number || issue.columnNumber || null
            },
            category: issue.category || 'compilation',
            tool: issue.tool || 'fallback',
            ai_processed: false,
            ai_suggestions: []
        }));
        const errorCount = transformedIssues.filter((i) => i.severity === 'error').length;
        const warningCount = transformedIssues.filter((i) => i.severity === 'warning').length;
        return {
            compilation_status: originalResult.status || (errorCount > 0 ? 'failed' : 'success'),
            project_info: {
                path: projectPath,
                type: originalResult.project_type || 'unknown',
                build_tool: originalResult.build_tool || 'unknown',
                compilation_time: originalResult.compilation_time || 0
            },
            summary: {
                total_issues: transformedIssues.length,
                errors: errorCount,
                warnings: warningCount,
                infos: 0,
                hints: 0,
                files_with_issues: new Set(transformedIssues.map((i) => i.location.file_path)).size
            },
            ai_analysis: {
                processed: false,
                summary: null,
                suggestions_available: 0
            },
            issues: transformedIssues,
            issues_by_file: this.groupIssuesByFile(transformedIssues),
            metadata: {
                handler: 'enhanced_compile_code_fallback',
                original_format: true
            }
        };
    }
    groupIssuesByFile(issues) {
        const grouped = {};
        for (const issue of issues) {
            const filePath = issue.location.file_path;
            if (!grouped[filePath]) {
                grouped[filePath] = [];
            }
            grouped[filePath].push(issue);
        }
        return grouped;
    }
}
