/**
 * Workflow-related tool handlers
 */
import { BaseToolHandler } from './BaseToolHandler.js';
import { WorkflowService } from '../services/index.js';
export class CreateWorkflowHandler extends BaseToolHandler {
    workflowService;
    constructor(context) {
        super(context);
        this.workflowService = new WorkflowService();
    }
    async handle(args, context) {
        const workflowRequest = {
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
    workflowService;
    constructor(context) {
        super(context);
        this.workflowService = new WorkflowService();
    }
    async handle(args, context) {
        const workflows = this.workflowService.listWorkflows();
        return this.createJsonResult({
            workflows,
            totalWorkflows: workflows.length
        });
    }
}
export class GetWorkflowHandler extends BaseToolHandler {
    workflowService;
    constructor(context) {
        super(context);
        this.workflowService = new WorkflowService();
    }
    async handle(args, context) {
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
    workflowService;
    constructor(context) {
        super(context);
        this.workflowService = new WorkflowService();
    }
    async handle(args, context) {
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
    workflowService;
    constructor(context) {
        super(context);
        this.workflowService = new WorkflowService();
    }
    async handle(args, context) {
        const approvals = this.workflowService.getPendingApprovals();
        return this.createJsonResult({
            pendingApprovals: approvals,
            totalPending: approvals.length
        });
    }
}
