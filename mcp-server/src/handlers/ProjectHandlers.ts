/**
 * Project-related tool handlers
 */

import { BaseToolHandler } from './BaseToolHandler.js';
import { ServerContext, ToolResult } from '../types/index.js';
import { ProjectService } from '../services/index.js';

export class ListGeneratedProjectsHandler extends BaseToolHandler {
  private projectService: ProjectService;

  constructor(context: ServerContext) {
    super(context);
    this.projectService = new ProjectService('/Users/niladrib/WorkingFolder/genaiagent/GeneratedCode');
  }

  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    return await this.projectService.listGeneratedProjects();
  }
}

export class ReadFileContentHandler extends BaseToolHandler {
  private projectService: ProjectService;

  constructor(context: ServerContext) {
    super(context);
    this.projectService = new ProjectService('/Users/niladrib/WorkingFolder/genaiagent/GeneratedCode');
  }

  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    const { filePath } = args;
    if (!filePath) {
      throw new Error('filePath parameter is required');
    }
    return await this.projectService.readFileContent(filePath);
  }
}

export class AnalyzeProjectStructureHandler extends BaseToolHandler {
  private projectService: ProjectService;

  constructor(context: ServerContext) {
    super(context);
    this.projectService = new ProjectService('/Users/niladrib/WorkingFolder/genaiagent/GeneratedCode');
  }

  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    const { projectPath, maxDepth = 10 } = args;
    if (!projectPath) {
      throw new Error('projectPath parameter is required');
    }
    return await this.projectService.analyzeProjectStructure(projectPath, maxDepth);
  }
}
