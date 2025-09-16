/**
 * Enhanced Compilation Handlers for MCP Server
 * Provides TypeScript handlers that can call enhanced Python compilation agents
 */

import { BaseToolHandler } from './BaseToolHandler.js';
import { ServerContext, ToolResult } from '../types/index.js';
import { spawn } from 'child_process';
import path from 'path';

export class EnhancedCompileCodeHandler extends BaseToolHandler {
  /**
   * Enhanced compilation handler with OpenAI analysis and simplified output format.
   * This provides a standardized, simplified format for both UI display and agent consumption.
   */
  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    console.log('[DEBUG] Starting enhanced compilation with OpenAI analysis');
    console.log('[DEBUG] Input args:', JSON.stringify(args, null, 2));
    
    const { projectPath, projectType, buildOptions, enableOpenAI = true, format = 'simplified' } = args;
    
    if (!projectPath) {
      throw new Error('projectPath parameter is required');
    }

    try {
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
        } else {
          commandArgs.push('--disable-ai');
          console.log('[WARN] OpenAI API key not found, AI analysis disabled');
        }
      } else {
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
      const result = await new Promise<string>((resolve, reject) => {
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
          } else {
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
      } catch (parseError) {
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
      
    } catch (error) {
      console.error('[ERROR] Enhanced compilation failed:', error);
      
      // Return error in simplified format
      const errorResult = this.createErrorResult(error instanceof Error ? error.message : String(error), projectPath);
      
      return this.createJsonResult({
        message: "Enhanced Compilation Failed",
        result: errorResult
      });
    }
  }
  
  private createErrorResult(errorMessage: string, projectPath: string): any {
    /**
     * Create standardized error result in simplified format.
     */
    return {
      compilation_status: "failed",
      project_info: {
        path: projectPath,
        type: "unknown",
        build_tool: "unknown",
        compilation_time: 0
      },
      summary: {
        total_issues: 1,
        errors: 1,
        warnings: 0,
        infos: 0,
        hints: 0,
        files_with_issues: 1
      },
      ai_analysis: {
        processed: false,
        summary: null,
        suggestions_available: 0
      },
      issues: [
        {
          id: "error_001",
          severity: "error",
          message: errorMessage,
          location: {
            file_path: projectPath,
            line_number: null,
            column_number: null
          },
          category: "compilation",
          tool: "enhanced_mcp_handler",
          ai_processed: false,
          ai_suggestions: []
        }
      ],
      issues_by_file: {
        [projectPath]: [
          {
            id: "error_001",
            severity: "error",
            message: errorMessage,
            location: {
              file_path: projectPath,
              line_number: null,
              column_number: null
            },
            category: "compilation",
            tool: "enhanced_mcp_handler",
            ai_processed: false,
            ai_suggestions: []
          }
        ]
      },
      metadata: {
        handler: "enhanced_compile_code",
        error: true
      }
    };
  }
}

export class CompilationIssueAnalyzer extends BaseToolHandler {
  /**
   * Handler for analyzing compilation issues with OpenAI.
   * This handler can take raw compilation output and convert it to
   * the standardized format with AI analysis.
   */
  
  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    console.log('[DEBUG] Starting compilation issue analysis');
    console.log('[DEBUG] Input args:', JSON.stringify(args, null, 2));
    
    const { issues = [], projectPath = "", enableOpenAI = true } = args;
    
    if (!issues || !Array.isArray(issues)) {
      return this.createJsonResult({
        message: "No issues to analyze",
        result: this.createEmptyResult()
      });
    }
    
    try {
      // Convert issues to standardized format
      const standardizedIssues = this.convertToStandardizedFormat(issues, projectPath);
      
      // Group issues by file
      const issuesByFile = this.groupIssuesByFile(standardizedIssues);
      
      // Create summary
      const summary = this.createSummary(standardizedIssues);
      
      const result = {
        total_issues: standardizedIssues.length,
        summary: summary,
        issues: standardizedIssues,
        issues_by_file: issuesByFile,
        ai_processed: false,
        project_path: projectPath
      };
      
      console.log('[DEBUG] Issue analysis completed');
      
      return this.createJsonResult({
        message: "Compilation Issue Analysis Result",
        result: result
      });
      
    } catch (error) {
      console.error('[ERROR] Issue analysis failed:', error);
      throw new Error(`Analysis failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  private convertToStandardizedFormat(issues: any[], projectPath: string): any[] {
    /**
     * Convert various issue formats to standardized format.
     */
    return issues.map((issue, index) => {
      // Check if already in new format
      if (issue.location && typeof issue.location === 'object') {
        return issue;
      }
      
      // Convert from legacy format
      return {
        id: issue.id || `issue_${index}`,
        severity: issue.severity || 'error',
        message: issue.message || issue.toString(),
        location: {
          file_path: issue.file_path || issue.filePath || projectPath,
          line_number: issue.line_number || issue.lineNumber || null,
          column_number: issue.column_number || issue.columnNumber || null
        },
        category: issue.category || 'compilation',
        tool: issue.tool || 'unknown',
        ai_processed: false,
        ai_suggestions: [],
        metadata: {
          converted_from_legacy: !issue.location,
          original_suggestion: issue.suggestion
        }
      };
    });
  }
  
  private groupIssuesByFile(issues: any[]): { [key: string]: any[] } {
    /**
     * Group issues by file path.
     */
    const grouped: { [key: string]: any[] } = {};
    
    for (const issue of issues) {
      const filePath = issue.location.file_path;
      if (!grouped[filePath]) {
        grouped[filePath] = [];
      }
      grouped[filePath].push(issue);
    }
    
    return grouped;
  }
  
  private createSummary(issues: any[]): any {
    /**
     * Create summary statistics for issues.
     */
    const errors = issues.filter(i => i.severity === 'error').length;
    const warnings = issues.filter(i => i.severity === 'warning').length;
    const infos = issues.filter(i => i.severity === 'info').length;
    const hints = issues.filter(i => i.severity === 'hint').length;
    
    const uniqueFiles = new Set(issues.map(i => i.location.file_path)).size;
    
    return {
      total_issues: issues.length,
      errors: errors,
      warnings: warnings,
      infos: infos,
      hints: hints,
      files_with_issues: uniqueFiles,
      ai_suggestions_available: issues.filter(i => i.ai_suggestions && i.ai_suggestions.length > 0).length
    };
  }
  
  private createEmptyResult(): any {
    /**
     * Create empty result for no issues.
     */
    return {
      total_issues: 0,
      summary: {
        total_issues: 0,
        errors: 0,
        warnings: 0,
        infos: 0,
        hints: 0,
        files_with_issues: 0,
        ai_suggestions_available: 0
      },
      issues: [],
      issues_by_file: {},
      ai_processed: false
    };
  }
}
