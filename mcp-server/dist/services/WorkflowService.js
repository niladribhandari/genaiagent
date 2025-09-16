/**
 * Workflow management service
 */
import { generateId } from '../utils/index.js';
export class WorkflowService {
    activeWorkflows = new Map();
    pendingApprovals = new Map();
    /**
     * Create a new workflow
     */
    createWorkflow(request) {
        const id = generateId();
        const workflow = {
            id,
            status: 'running',
            createdAt: new Date(),
            updatedAt: new Date(),
            requirements: request.requirements,
            technology: request.technology,
            outputPath: request.outputPath,
            approvalMode: request.approvalMode || 'interactive',
            config: request.workflowConfig || {},
            phases: this.createDefaultPhases(request.technology)
        };
        this.activeWorkflows.set(id, workflow);
        return workflow;
    }
    /**
     * Get workflow by ID
     */
    getWorkflow(id) {
        return this.activeWorkflows.get(id);
    }
    /**
     * List all workflows
     */
    listWorkflows() {
        return Array.from(this.activeWorkflows.values());
    }
    /**
     * Update workflow status
     */
    updateWorkflow(id, updates) {
        const workflow = this.activeWorkflows.get(id);
        if (!workflow)
            return undefined;
        Object.assign(workflow, updates, { updatedAt: new Date() });
        this.activeWorkflows.set(id, workflow);
        return workflow;
    }
    /**
     * Delete workflow
     */
    deleteWorkflow(id) {
        return this.activeWorkflows.delete(id);
    }
    /**
     * Create approval request
     */
    createApprovalRequest(workflowId, phaseId, phaseName, result) {
        const id = generateId();
        const approval = {
            id,
            workflowId,
            phaseId,
            phaseName,
            result,
            timestamp: new Date(),
            options: ['approve', 'reject', 'modify']
        };
        this.pendingApprovals.set(id, approval);
        return approval;
    }
    /**
     * Get pending approvals
     */
    getPendingApprovals() {
        return Array.from(this.pendingApprovals.values());
    }
    /**
     * Process approval response
     */
    processApproval(approvalId, response, feedback) {
        const approval = this.pendingApprovals.get(approvalId);
        if (!approval)
            return false;
        // Update workflow based on approval response
        const workflow = this.getWorkflow(approval.workflowId);
        if (workflow) {
            const phase = workflow.phases.find(p => p.id === approval.phaseId);
            if (phase) {
                switch (response) {
                    case 'approve':
                        phase.status = 'completed';
                        break;
                    case 'reject':
                        phase.status = 'failed';
                        phase.error = feedback || 'Rejected by user';
                        break;
                    case 'modify':
                        phase.status = 'pending';
                        // Allow phase to be re-run with modifications
                        break;
                }
                this.updateWorkflow(workflow.id, workflow);
            }
        }
        this.pendingApprovals.delete(approvalId);
        return true;
    }
    /**
     * Create default phases based on technology
     */
    createDefaultPhases(technology) {
        const commonPhases = [
            {
                id: 'api_specification',
                name: 'API Specification',
                agent: 'apispec',
                method: 'generateAPISpec',
                dependencies: [],
                approvalRequired: true,
                status: 'pending'
            },
            {
                id: 'code_generation',
                name: 'Code Generation',
                agent: 'generation',
                method: 'generateProject',
                dependencies: ['api_specification'],
                approvalRequired: true,
                status: 'pending'
            },
            {
                id: 'code_compilation',
                name: 'Code Compilation',
                agent: 'compilation',
                method: 'compileProject',
                dependencies: ['code_generation'],
                approvalRequired: false,
                status: 'pending'
            },
            {
                id: 'code_review',
                name: 'Code Review',
                agent: 'review',
                method: 'reviewCode',
                dependencies: ['code_compilation'],
                approvalRequired: true,
                status: 'pending'
            }
        ];
        // Technology-specific customizations could be added here
        return commonPhases;
    }
}
