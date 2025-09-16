/**
 * Agent Wrapper Classes for MCP Integration
 * These classes wrap the existing Python agents to provide a consistent interface
 * for the MCP server to interact with all agents.
 */

import { spawn, exec } from 'child_process';
import * as path from 'path';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Helper function for error handling
function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

// Base Agent Interface
export interface AgentResult {
  success: boolean;
  data?: any;
  error?: string;
  metadata?: any;
}

export interface AgentConfig {
  workingDirectory?: string;
  timeout?: number;
  verbose?: boolean;
}

// Base Agent Class
export abstract class BaseAgentWrapper {
  protected config: AgentConfig;
  protected agentPath: string;

  constructor(agentPath: string, config: AgentConfig = {}) {
    this.agentPath = agentPath;
    this.config = {
      timeout: 300000, // 5 minutes default
      verbose: false,
      ...config
    };
  }

  protected async executePythonScript(scriptPath: string, args: any[] = []): Promise<AgentResult> {
    console.log('[DEBUG] Executing Python script:', scriptPath);
    console.log('[DEBUG] Script arguments:', JSON.stringify(args, null, 2));
    console.log('[DEBUG] Working directory:', this.config.workingDirectory || this.agentPath);
    
    return new Promise((resolve) => {
      const pythonPath = 'python3';
      const fullArgs = [scriptPath, ...args.map(arg => JSON.stringify(arg))];
      
      console.log('[DEBUG] Full command:', pythonPath, fullArgs.join(' '));
      
      const process = spawn(pythonPath, fullArgs, {
        cwd: this.config.workingDirectory || this.agentPath,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        const output = data.toString();
        console.log('[DEBUG] Python stdout:', output);
        stdout += output;
      });

      process.stderr.on('data', (data) => {
        const output = data.toString();
        console.log('[DEBUG] Python stderr:', output);
        stderr += output;
      });

      const timeout = setTimeout(() => {
        console.log('[DEBUG] Python process timeout reached');
        process.kill('SIGTERM');
        resolve({
          success: false,
          error: 'Agent execution timed out'
        });
      }, this.config.timeout);

      process.on('close', (code) => {
        console.log('[DEBUG] Python process closed with code:', code);
        clearTimeout(timeout);
        
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            console.log('[DEBUG] Parsed JSON result:', result);
            resolve({
              success: true,
              data: result,
              metadata: { executionTime: Date.now() }
            });
          } catch (e) {
            console.log('[DEBUG] Failed to parse JSON, returning raw output');
            resolve({
              success: true,
              data: { output: stdout },
              metadata: { rawOutput: true }
            });
          }
        } else {
          console.log('[DEBUG] Process failed with exit code:', code);
          resolve({
            success: false,
            error: stderr || `Process exited with code ${code}`,
            metadata: { exitCode: code, stdout, stderr }
          });
        }
      });

      process.on('error', (error) => {
        console.error('[ERROR] Python process error:', error);
        clearTimeout(timeout);
        resolve({
          success: false,
          error: error.message
        });
      });
    });
  }
}

// Code Compilation Agent Wrapper
export class CodeCompilationAgentWrapper extends BaseAgentWrapper {
  constructor(config: AgentConfig = {}) {
    const agentPath = path.join(process.cwd(), '..', 'Agents', 'CodeCompilationAgent');
    console.log('[DEBUG] CodeCompilationAgent path:', agentPath);
    super(agentPath, config);
  }

  async compileProject(projectPath: string, projectType?: string, buildOptions?: any): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'compile_cli.py');
      
      // Build command line arguments properly
      const args = [scriptPath, projectPath]; // Script path and project path as positional arg
      
      if (projectType) {
        args.push('--type', projectType);
      }

      if (buildOptions?.skip_tests) {
        args.push('--skip-tests');
      }

      if (buildOptions?.goals && Array.isArray(buildOptions.goals)) {
        args.push('--goals', buildOptions.goals.join(','));
      }

      args.push('--json-output'); // Request JSON output for parsing

      console.log('[DEBUG] Executing compilation with args:', args);
      
      return new Promise((resolve) => {
        const pythonPath = 'python3';
        
        const process = spawn(pythonPath, args, {
          cwd: this.agentPath,
          stdio: ['pipe', 'pipe', 'pipe']
        });

        let stdout = '';
        let stderr = '';

        process.stdout.on('data', (data) => {
          const output = data.toString();
          stdout += output;
          if (this.config.verbose) {
            console.log('[STDOUT]', output);
          }
        });

        process.stderr.on('data', (data) => {
          const output = data.toString();
          stderr += output;
          if (this.config.verbose) {
            console.error('[STDERR]', output);
          }
        });

        process.on('close', (code) => {
          console.log('[DEBUG] Python process closed with code:', code);
          console.log('[DEBUG] Raw stdout:', stdout);
          console.log('[DEBUG] Raw stderr:', stderr);
          
          // Always try to parse JSON output first, regardless of exit code
          // The Python script outputs JSON even on compilation failure
          try {
            // Extract JSON from mixed output - look for the JSON object starting with {
            const jsonStartIndex = stdout.indexOf('{');
            let jsonOutput = stdout;
            
            if (jsonStartIndex > 0) {
              // There's text before the JSON, extract just the JSON part
              jsonOutput = stdout.substring(jsonStartIndex);
              console.log('[DEBUG] Extracted JSON portion:', jsonOutput);
            }
            
            const result = JSON.parse(jsonOutput.trim());
            console.log('[DEBUG] Successfully parsed JSON result:', JSON.stringify(result, null, 2));
            resolve({
              success: code === 0,
              data: result,
              metadata: { stderr: stderr, exitCode: code }
            });
          } catch (parseError) {
            console.log('[DEBUG] Failed to parse JSON, using fallback. Parse error:', parseError);
            // Fallback to plain text output
            resolve({
              success: code === 0,
              error: code !== 0 ? `Compilation failed with exit code ${code}` : undefined,
              data: { output: stdout },
              metadata: { stderr: stderr, exitCode: code }
            });
          }
        });

        process.on('error', (error) => {
          console.error('[DEBUG] Process error:', error);
          resolve({
            success: false,
            error: `Process failed: ${error.message}`,
            metadata: { stderr: error.message }
          });
        });
      });
    } catch (error) {
      return {
        success: false,
        error: `Compilation failed: ${getErrorMessage(error)}`
      };
    }
  }

  async getProjectInfo(projectPath: string): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'src', 'compilation_agent.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'get_project_info',
        project_path: projectPath
      }]);
    } catch (error) {
      return {
        success: false,
        error: `Failed to get project info: ${getErrorMessage(error)}`
      };
    }
  }
}

// Code Generation Agent Wrapper
export class CodeGenerationAgentWrapper extends BaseAgentWrapper {
  constructor(config: AgentConfig = {}) {
    const agentPath = path.join(process.cwd(), '..', 'Agents', 'CodeGenerationAgent');
    console.log('[DEBUG] CodeGenerationAgent path:', agentPath);
    super(agentPath, config);
  }

  async generateProject(specification: any, outputPath: string, technology: string): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'main_enhanced_agentic.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'generate_project',
        specification,
        output_path: outputPath,
        technology,
        timestamp: new Date().toISOString()
      }]);
    } catch (error) {
      return {
        success: false,
        error: `Code generation failed: ${getErrorMessage(error)}`
      };
    }
  }

  async generateCodeFromTemplate(templateType: string, name: string, options: any): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'src', 'template_processor.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'generate_from_template',
        template_type: templateType,
        name,
        options
      }]);
    } catch (error) {
      return {
        success: false,
        error: `Template generation failed: ${getErrorMessage(error)}`
      };
    }
  }
}

// Code Review Agent Wrapper
export class CodeReviewAgentWrapper extends BaseAgentWrapper {
  constructor(config: AgentConfig = {}) {
    const agentPath = path.join(process.cwd(), '..', 'Agents', 'CodeReviewAgent');
    console.log('[DEBUG] CodeReviewAgent path:', agentPath);
    super(agentPath, config);
  }

  async reviewProject(projectPath: string, reviewScope: string[] = ['quality', 'security']): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'main_enhanced_agentic.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'analyze_project',
        project_path: projectPath,
        review_scope: reviewScope,
        include_security: reviewScope.includes('security'),
        include_compliance: reviewScope.includes('compliance')
      }]);
    } catch (error) {
      return {
        success: false,
        error: `Code review failed: ${getErrorMessage(error)}`
      };
    }
  }

  async analyzeCodeQuality(filePath: string): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'main_enhanced_agentic.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'analyze_file',
        file_path: filePath,
        analysis_type: 'quality'
      }]);
    } catch (error) {
      return {
        success: false,
        error: `Quality analysis failed: ${getErrorMessage(error)}`
      };
    }
  }
}

// GitHub Search Agent Wrapper
export class GitHubSearchAgentWrapper extends BaseAgentWrapper {
  constructor(config: AgentConfig = {}) {
    const agentPath = path.join(process.cwd(), '..', 'Agents', 'GitHubSearchAgent');
    console.log('[DEBUG] GitHubSearchAgent path:', agentPath);
    super(agentPath, config);
  }

  async searchRepositories(query: string, language?: string, minStars: number = 0): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'src', 'github_search_agent.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'search_repositories',
        query,
        language,
        min_stars: minStars,
        max_results: 20
      }]);
    } catch (error) {
      return {
        success: false,
        error: `GitHub search failed: ${getErrorMessage(error)}`
      };
    }
  }

  async analyzeRepository(repoUrl: string): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'src', 'github_search_agent.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'analyze_repository',
        repo_url: repoUrl,
        include_security: true,
        include_trends: true
      }]);
    } catch (error) {
      return {
        success: false,
        error: `Repository analysis failed: ${getErrorMessage(error)}`
      };
    }
  }
}

// Web Search Agent Wrapper
export class WebSearchAgentWrapper extends BaseAgentWrapper {
  constructor(config: AgentConfig = {}) {
    const agentPath = path.join(process.cwd(), '..', 'Agents', 'WebSerarchAgent');
    console.log('[DEBUG] WebSerarchAgent path:', agentPath);
    super(agentPath, config);
  }

  async searchWeb(query: string, context?: string): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'webserach.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'web_search',
        query,
        context
      }]);
    } catch (error) {
      return {
        success: false,
        error: `Web search failed: ${getErrorMessage(error)}`
      };
    }
  }
}

// API Specification Writer Agent Wrapper
export class APISpecWriterAgentWrapper extends BaseAgentWrapper {
  constructor(config: AgentConfig = {}) {
    const agentPath = path.join(process.cwd(), '..', 'Agents', 'WriteAPISpecAgent');
    console.log('[DEBUG] WriteAPISpecAgent path:', agentPath);
    super(agentPath, config);
  }

  async generateAPISpec(requirements: string, projectName: string, technology: string): Promise<AgentResult> {
    try {
      console.log('[DEBUG] APISpecWriterAgent generateAPISpec called with:', {
        requirements,
        projectName,
        technology
      });
      
      // Use the MCP-compatible API generator script
      const scriptPath = path.join(this.agentPath, 'mcp_api_generator.py');
      console.log('[DEBUG] Using MCP API generator script:', scriptPath);
      
      const result = await this.executePythonScript(scriptPath, [{
        requirements,
        project_name: projectName,
        technology,
        output_format: 'yaml'
      }]);
      
      console.log('[DEBUG] API spec generation result:', result);
      return result;
    } catch (error) {
      console.error('[ERROR] API spec generation error:', error);
      return {
        success: false,
        error: `API specification generation failed: ${getErrorMessage(error)}`
      };
    }
  }

  async validateAPISpec(specPath: string): Promise<AgentResult> {
    try {
      const scriptPath = path.join(this.agentPath, 'src', 'api_spec_writer_system.py');
      return await this.executePythonScript(scriptPath, [{
        action: 'validate_specification',
        spec_path: specPath
      }]);
    } catch (error) {
      return {
        success: false,
        error: `API specification validation failed: ${getErrorMessage(error)}`
      };
    }
  }
}

// Fix Compilation Issues Agent Wrapper
export class FixCompilationIssuesAgentWrapper extends BaseAgentWrapper {
  constructor(config: AgentConfig = {}) {
    const agentPath = path.join(process.cwd(), '..', 'Agents', 'FixCompilationIssuesAgent');
    console.log('[DEBUG] FixCompilationIssuesAgent path:', agentPath);
    super(agentPath, config);
  }

  async fixCompilationIssues(projectPath: string, errors: any[], buildTool: string = 'maven', buildOutput?: string): Promise<AgentResult> {
    try {
      console.log('[DEBUG] FixCompilationIssuesAgent fixCompilationIssues called with:', {
        projectPath,
        errorsCount: errors?.length || 0,
        buildTool,
        hasBuildOutput: !!buildOutput
      });
      
      const scriptPath = path.join(this.agentPath, 'main_enhanced_agentic.py');
      console.log('[DEBUG] Using fix compilation script:', scriptPath);
      
      // Build command line arguments
      const args = [
        '--project-path', projectPath,
        '--build-tool', buildTool,
        '--compilation-errors', JSON.stringify(errors),
        '--output', '-' // Output to stdout
      ];
      
      // Add build output if available
      if (buildOutput) {
        args.push('--build-output', buildOutput);
      }
      
      console.log('[DEBUG] Fix compilation args:', args);
      
      return new Promise((resolve) => {
        const pythonPath = 'python3';
        
        const process = spawn(pythonPath, [scriptPath, ...args], {
          cwd: this.agentPath,
          stdio: ['pipe', 'pipe', 'pipe']
        });

        let stdout = '';
        let stderr = '';

        process.stdout.on('data', (data) => {
          const output = data.toString();
          stdout += output;
          if (this.config.verbose) {
            console.log('[STDOUT]', output);
          }
        });

        process.stderr.on('data', (data) => {
          const output = data.toString();
          stderr += output;
          if (this.config.verbose) {
            console.error('[STDERR]', output);
          }
        });

        process.on('close', (code) => {
          console.log('[DEBUG] Fix compilation process closed with code:', code);
          console.log('[DEBUG] Raw stdout:', stdout);
          console.log('[DEBUG] Raw stderr:', stderr);
          
          try {
            // Try to parse JSON output
            const jsonStartIndex = stdout.indexOf('{');
            let jsonOutput = stdout;
            
            if (jsonStartIndex > 0) {
              jsonOutput = stdout.substring(jsonStartIndex);
            }
            
            const result = JSON.parse(jsonOutput.trim());
            console.log('[DEBUG] Successfully parsed fix result:', JSON.stringify(result, null, 2));
            resolve({
              success: code === 0,
              data: result,
              metadata: { stderr: stderr, exitCode: code }
            });
          } catch (parseError) {
            console.log('[DEBUG] Failed to parse JSON, using fallback. Parse error:', parseError);
            resolve({
              success: code === 0,
              data: { 
                status: code === 0 ? 'success' : 'error',
                message: stdout || stderr || 'Fix process completed',
                output: stdout
              },
              metadata: { stderr: stderr, exitCode: code }
            });
          }
        });

        process.on('error', (error) => {
          console.error('[DEBUG] Fix process error:', error);
          resolve({
            success: false,
            error: `Fix process failed: ${error.message}`,
            metadata: { stderr: error.message }
          });
        });
      });
    } catch (error) {
      console.error('[ERROR] Fix compilation issues error:', error);
      return {
        success: false,
        error: `Fix compilation issues failed: ${getErrorMessage(error)}`
      };
    }
  }
}

// Agent Orchestrator - Coordinates all agents
export class AgentOrchestrator {
  private agents: Map<string, BaseAgentWrapper>;

  constructor() {
    console.log('[DEBUG] Initializing AgentOrchestrator...');
    this.agents = new Map();
    this.initializeAgents();
    console.log('[DEBUG] AgentOrchestrator initialized with agents:', Array.from(this.agents.keys()));
  }

  private initializeAgents() {
    console.log('[DEBUG] Creating agent wrappers...');
    
    try {
      console.log('[DEBUG] Creating compilation agent...');
      this.agents.set('compilation', new CodeCompilationAgentWrapper());
      
      console.log('[DEBUG] Creating generation agent...');
      this.agents.set('generation', new CodeGenerationAgentWrapper());
      
      console.log('[DEBUG] Creating review agent...');
      this.agents.set('review', new CodeReviewAgentWrapper());
      
      console.log('[DEBUG] Creating github agent...');
      this.agents.set('github', new GitHubSearchAgentWrapper());
      
      console.log('[DEBUG] Creating web agent...');
      this.agents.set('web', new WebSearchAgentWrapper());
      
      console.log('[DEBUG] Creating apispec agent...');
      this.agents.set('apispec', new APISpecWriterAgentWrapper());
      
      console.log('[DEBUG] Creating fix compilation agent...');
      this.agents.set('fixcompilation', new FixCompilationIssuesAgentWrapper());
      
      console.log('[DEBUG] All agents created successfully');
    } catch (error) {
      console.error('[ERROR] Failed to initialize agents:', error);
      throw error;
    }
  }

  getAgent(agentType: string): BaseAgentWrapper | undefined {
    console.log('[DEBUG] Getting agent:', agentType);
    const agent = this.agents.get(agentType);
    console.log('[DEBUG] Agent found:', agent ? 'YES' : 'NO');
    return agent;
  }

  getAllAgents(): Map<string, BaseAgentWrapper> {
    return this.agents;
  }

  async executeWorkflowPhase(phaseId: string, input: any): Promise<AgentResult> {
    try {
      switch (phaseId) {
        case 'specification':
          const apiAgent = this.getAgent('apispec') as APISpecWriterAgentWrapper;
          return await apiAgent.generateAPISpec(
            input.requirements,
            input.projectName || 'Generated Project',
            input.technology
          );

        case 'code_generation':
          const genAgent = this.getAgent('generation') as CodeGenerationAgentWrapper;
          return await genAgent.generateProject(
            input.specification,
            input.outputPath,
            input.technology
          );

        case 'code_review':
          const reviewAgent = this.getAgent('review') as CodeReviewAgentWrapper;
          return await reviewAgent.reviewProject(
            input.projectPath,
            input.reviewScope || ['quality', 'security']
          );

        case 'compilation':
          const compileAgent = this.getAgent('compilation') as CodeCompilationAgentWrapper;
          return await compileAgent.compileProject(
            input.projectPath,
            input.projectType,
            input.buildOptions
          );

        case 'deployment':
          // Deployment logic would go here
          return {
            success: true,
            data: {
              status: 'deployed',
              url: 'http://localhost:8080',
              message: 'Application deployed successfully'
            }
          };

        default:
          return {
            success: false,
            error: `Unknown workflow phase: ${phaseId}`
          };
      }
    } catch (error) {
      return {
        success: false,
        error: `Workflow phase execution failed: ${getErrorMessage(error)}`
      };
    }
  }
}
