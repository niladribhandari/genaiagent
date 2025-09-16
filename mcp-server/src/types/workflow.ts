/**
 * Workflow-related type definitions
 */

export interface WorkflowRequest {
  requirements: string;
  technology: string;
  outputPath: string;
  approvalMode?: 'interactive' | 'auto_approve' | 'batch';
  workflowConfig?: any;
}

export interface WorkflowPhase {
  id: string;
  name: string;
  agent?: string;
  method?: string;
  input?: any;
  dependencies: string[];
  condition?: string;
  approvalRequired?: boolean;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'waiting_approval' | 'skipped';
  result?: any;
  error?: string;
  timestamp?: Date;
}

export interface Workflow {
  id: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  createdAt: Date;
  updatedAt: Date;
  requirements: string;
  technology: string;
  outputPath: string;
  approvalMode: string;
  config: any;
  currentPhase?: string;
  phases: WorkflowPhase[];
  error?: string;
}

export interface ApprovalRequest {
  id?: string;
  workflowId: string;
  phaseId: string;
  phaseName: string;
  agentOutput?: any;
  result?: any;
  nextPhase?: string;
  timestamp: Date;
  options: string[];
}

export interface ProjectStructure {
  name: string;
  type: 'file' | 'directory';
  path: string;
  children?: ProjectStructure[];
  size?: number;
  lastModified?: Date;
}

export interface ErrorTransformResult {
  file?: string;
  line?: number;
  column?: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
}
