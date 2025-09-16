/**
 * Common server types and interfaces
 */

import { AgentOrchestrator } from '../agents.js';
import { WorkflowOrchestrationAgent } from '../workflow-orchestrator.js';
import { Workflow, ApprovalRequest } from './workflow.js';

export interface ServerConfig {
  port: number;
  corsEnabled: boolean;
  openaiApiKey?: string;
  workflowStoragePath?: string;
}

export interface ServerContext {
  orchestrator: AgentOrchestrator;
  workflowOrchestrator: WorkflowOrchestrationAgent;
  activeWorkflows: Map<string, Workflow>;
  pendingApprovals: Map<string, ApprovalRequest>;
  openai?: any;
}

export interface ToolResult {
  content: Array<{
    type: string;
    text: string;
  }>;
}

export interface FileSystemEntry {
  name: string;
  path: string;
  isDirectory: boolean;
  size?: number;
  lastModified?: Date;
}

export interface CompilationError {
  file: string;
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface CompilationResult {
  success: boolean;
  errors?: CompilationError[];
  warnings?: CompilationError[];
  output?: string;
}
