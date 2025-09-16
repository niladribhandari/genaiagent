/**
 * Workflow-related tool handlers
 */

import { BaseToolHandler } from './BaseToolHandler.js';
import { ServerContext, ToolResult } from '../types/index.js';
import { WorkflowService } from '../services/index.js';
import { WorkflowRequest } from '../types/index.js';

export class CreateWorkflowHandler extends BaseToolHandler {
  private workflowService: WorkflowService;

  constructor(context: ServerContext) {
    super(context);
    this.workflowService = new WorkflowService();
  }

  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    const workflowRequest: WorkflowRequest = {
      requirements: args.requirements,
      technology: args.technology,
      outputPath: args.outputPath,
      approvalMode: args.approvalMode || 'interactive',
      workflowConfig: args.workflowConfig
    };

    const workflow = this.workflowService.createWorkflow(workflowRequest);
    return this.createJsonResult({
      message: "Workflow created successfully",
      workflow
    });
  }
}

export class ListWorkflowsHandler extends BaseToolHandler {
  private workflowService: WorkflowService;

  constructor(context: ServerContext) {
    super(context);
    this.workflowService = new WorkflowService();
  }

  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    const workflows = this.workflowService.listWorkflows();
    return this.createJsonResult({
      workflows,
      totalWorkflows: workflows.length
    });
  }
}

export class GetWorkflowHandler extends BaseToolHandler {
  private workflowService: WorkflowService;

  constructor(context: ServerContext) {
    super(context);
    this.workflowService = new WorkflowService();
  }

  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    const { workflowId } = args;
    if (!workflowId) {
      throw new Error('workflowId parameter is required');
    }

    const workflow = this.workflowService.getWorkflow(workflowId);
    if (!workflow) {
      throw new Error(`Workflow with ID ${workflowId} not found`);
    }

    return this.createJsonResult({ workflow });
  }
}

export class ApproveWorkflowPhaseHandler extends BaseToolHandler {
  private workflowService: WorkflowService;

  constructor(context: ServerContext) {
    super(context);
    this.workflowService = new WorkflowService();
  }

  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    const { approvalId, response, feedback } = args;
    if (!approvalId || !response) {
      throw new Error('approvalId and response parameters are required');
    }

    const success = this.workflowService.processApproval(approvalId, response, feedback);
    if (!success) {
      throw new Error(`Approval with ID ${approvalId} not found`);
    }

    return this.createJsonResult({
      message: "Approval processed successfully",
      approvalId,
      response
    });
  }
}

export class GetPendingApprovalsHandler extends BaseToolHandler {
  private workflowService: WorkflowService;

  constructor(context: ServerContext) {
    super(context);
    this.workflowService = new WorkflowService();
  }

  async handle(args: any, context: ServerContext): Promise<ToolResult> {
    const approvals = this.workflowService.getPendingApprovals();
    return this.createJsonResult({
      pendingApprovals: approvals,
      totalPending: approvals.length
    });
  }
}
