import { AgentOrchestrator } from './agents.js';
import fs from 'fs/promises';
import path from 'path';
/**
 * Enhanced Workflow Orchestration Agent
 * Manages complex development workflows with approval gates, dependency management,
 * and intelligent routing between agents.
 */
export class WorkflowOrchestrationAgent {
    orchestrator;
    activeWorkflows = new Map();
    pendingApprovals = new Map();
    workflowTemplates = new Map();
    workflowStorage;
    constructor(workflowStoragePath = './workflows') {
        this.orchestrator = new AgentOrchestrator();
        this.workflowStorage = workflowStoragePath;
        this.initializeTemplates();
        this.ensureStorageExists();
    }
    async ensureStorageExists() {
        try {
            await fs.access(this.workflowStorage);
        }
        catch {
            await fs.mkdir(this.workflowStorage, { recursive: true });
        }
    }
    initializeTemplates() {
        // Default workflow templates for different technology stacks
        const javaSpringBootTemplate = {
            id: 'java_springboot_standard',
            name: 'Java Spring Boot Standard',
            description: 'Complete Java Spring Boot application development workflow',
            technology: 'java_springboot',
            phases: [
                {
                    id: 'api_specification',
                    name: 'API Specification',
                    description: 'Generate OpenAPI specification based on requirements',
                    agent: 'apispec',
                    method: 'generateAPISpec',
                    dependencies: [],
                    approvalRequired: true,
                    timeout: 300000,
                    retryCount: 3
                },
                {
                    id: 'code_generation',
                    name: 'Code Generation',
                    description: 'Generate Spring Boot application code',
                    agent: 'generation',
                    method: 'generateProject',
                    dependencies: ['api_specification'],
                    approvalRequired: true,
                    timeout: 600000,
                    retryCount: 2
                },
                {
                    id: 'code_review',
                    name: 'Code Review',
                    description: 'Automated code quality and security review',
                    agent: 'review',
                    method: 'reviewProject',
                    dependencies: ['code_generation'],
                    approvalRequired: false,
                    timeout: 300000,
                    retryCount: 1
                },
                {
                    id: 'compilation',
                    name: 'Compilation & Testing',
                    description: 'Compile and test the generated application',
                    agent: 'compilation',
                    method: 'compileProject',
                    dependencies: ['code_generation'],
                    approvalRequired: false,
                    timeout: 900000,
                    retryCount: 2
                },
                {
                    id: 'deployment_prep',
                    name: 'Deployment Preparation',
                    description: 'Prepare application for deployment',
                    agent: 'deployment',
                    method: 'prepareDeployment',
                    dependencies: ['compilation'],
                    approvalRequired: true,
                    timeout: 300000,
                    retryCount: 1
                }
            ],
            defaultConfig: {
                javaVersion: '17',
                springBootVersion: '3.2.0',
                packageName: 'com.generated.app',
                buildTool: 'maven'
            }
        };
        // Add more templates for other technologies
        const nodeExpressTemplate = {
            id: 'nodejs_express_standard',
            name: 'Node.js Express Standard',
            description: 'Complete Node.js Express application development workflow',
            technology: 'nodejs_express',
            phases: [
                {
                    id: 'api_specification',
                    name: 'API Specification',
                    description: 'Generate OpenAPI specification based on requirements',
                    agent: 'apispec',
                    method: 'generateAPISpec',
                    dependencies: [],
                    approvalRequired: true,
                    timeout: 300000,
                    retryCount: 3
                },
                {
                    id: 'code_generation',
                    name: 'Code Generation',
                    description: 'Generate Express.js application code',
                    agent: 'generation',
                    method: 'generateProject',
                    dependencies: ['api_specification'],
                    approvalRequired: true,
                    timeout: 600000,
                    retryCount: 2
                },
                {
                    id: 'code_review',
                    name: 'Code Review',
                    description: 'Automated code quality and security review',
                    agent: 'review',
                    method: 'reviewProject',
                    dependencies: ['code_generation'],
                    approvalRequired: false,
                    timeout: 300000,
                    retryCount: 1
                },
                {
                    id: 'testing',
                    name: 'Testing & Linting',
                    description: 'Run tests and linting',
                    agent: 'compilation',
                    method: 'testProject',
                    dependencies: ['code_generation'],
                    approvalRequired: false,
                    timeout: 600000,
                    retryCount: 2
                }
            ],
            defaultConfig: {
                nodeVersion: '18',
                expressVersion: '4.18.0',
                typescript: true,
                packageManager: 'npm'
            }
        };
        this.workflowTemplates.set(javaSpringBootTemplate.id, javaSpringBootTemplate);
        this.workflowTemplates.set(nodeExpressTemplate.id, nodeExpressTemplate);
    }
    /**
     * Start a new workflow based on requirements and technology
     */
    async startWorkflow(requirements, technology, outputPath, options = {}) {
        const workflowId = `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        // Select appropriate template
        const templateId = options.templateId || this.selectTemplate(technology);
        const template = this.workflowTemplates.get(templateId);
        if (!template) {
            throw new Error(`No template found for technology: ${technology}`);
        }
        // Create workflow phases from template
        const phases = (options.customPhases || template.phases).map(phaseTemplate => ({
            id: phaseTemplate.id,
            name: phaseTemplate.name,
            description: phaseTemplate.description,
            agent: phaseTemplate.agent,
            method: phaseTemplate.method,
            dependencies: phaseTemplate.dependencies,
            condition: phaseTemplate.condition,
            approvalRequired: phaseTemplate.approvalRequired,
            status: 'pending',
            retryCount: 0,
            maxRetries: phaseTemplate.retryCount || 3,
            metadata: {
                timeout: phaseTemplate.timeout || 300000,
                defaultParams: phaseTemplate.defaultParams
            }
        }));
        const workflow = {
            id: workflowId,
            templateId,
            status: 'running',
            createdAt: new Date(),
            updatedAt: new Date(),
            startedAt: new Date(),
            requirements,
            technology,
            outputPath,
            approvalMode: options.approvalMode || 'interactive',
            config: { ...template.defaultConfig, ...options.config },
            currentPhase: phases[0]?.id,
            phases,
            progress: {
                totalPhases: phases.length,
                completedPhases: 0,
                percentage: 0
            },
            artifacts: [],
            auditLog: [{
                    id: `audit_${Date.now()}`,
                    timestamp: new Date(),
                    action: 'workflow_started',
                    details: { requirements, technology, outputPath, templateId }
                }]
        };
        this.activeWorkflows.set(workflowId, workflow);
        await this.persistWorkflow(workflow);
        // Start first phase
        await this.executeNextPhase(workflowId);
        return { workflowId, workflow };
    }
    /**
     * Get workflow status and progress
     */
    async getWorkflowStatus(workflowId) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (workflow) {
            return workflow;
        }
        // Try to load from storage
        return await this.loadWorkflow(workflowId);
    }
    /**
     * Handle approval for a workflow phase
     */
    async handleApproval(workflowId, phaseId, action, options = {}) {
        const workflow = await this.getWorkflowStatus(workflowId);
        if (!workflow) {
            return { success: false, message: 'Workflow not found' };
        }
        const phase = workflow.phases.find(p => p.id === phaseId);
        if (!phase) {
            return { success: false, message: 'Phase not found' };
        }
        // Add audit entry
        workflow.auditLog.push({
            id: `audit_${Date.now()}`,
            timestamp: new Date(),
            action: `approval_${action}`,
            phaseId,
            userId: options.userId,
            details: { action, modifications: options.modifications, feedback: options.feedback }
        });
        // Remove from pending approvals
        this.pendingApprovals.delete(`${workflowId}:${phaseId}`);
        switch (action) {
            case 'approve':
                phase.status = 'completed';
                phase.endTime = new Date();
                this.updateProgress(workflow);
                await this.executeNextPhase(workflowId);
                break;
            case 'modify':
                if (options.modifications) {
                    phase.result = { ...phase.result, ...options.modifications };
                }
                phase.status = 'completed';
                phase.endTime = new Date();
                this.updateProgress(workflow);
                await this.executeNextPhase(workflowId);
                break;
            case 'retry':
                phase.status = 'pending';
                phase.error = undefined;
                phase.retryCount = 0;
                await this.executePhase(workflowId, phaseId);
                break;
            case 'skip':
                phase.status = 'skipped';
                phase.endTime = new Date();
                this.updateProgress(workflow);
                await this.executeNextPhase(workflowId);
                break;
            case 'cancel':
                workflow.status = 'cancelled';
                workflow.completedAt = new Date();
                break;
        }
        workflow.updatedAt = new Date();
        await this.persistWorkflow(workflow);
        return { success: true, message: `Phase ${action} successful` };
    }
    /**
     * Get all pending approvals
     */
    getPendingApprovals() {
        return Array.from(this.pendingApprovals.values());
    }
    /**
     * Get available workflow templates
     */
    getWorkflowTemplates() {
        return Array.from(this.workflowTemplates.values());
    }
    selectTemplate(technology) {
        const templateMap = {
            'java_springboot': 'java_springboot_standard',
            'nodejs_express': 'nodejs_express_standard',
            'dotnet_api': 'dotnet_standard', // Would need to be implemented
            'python_fastapi': 'python_fastapi_standard' // Would need to be implemented
        };
        return templateMap[technology] || 'java_springboot_standard';
    }
    async executeNextPhase(workflowId) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow)
            return;
        const nextPhase = this.findNextPhase(workflow);
        if (!nextPhase) {
            // Workflow completed
            workflow.status = 'completed';
            workflow.completedAt = new Date();
            workflow.currentPhase = undefined;
            workflow.updatedAt = new Date();
            await this.persistWorkflow(workflow);
            return;
        }
        await this.executePhase(workflowId, nextPhase.id);
    }
    findNextPhase(workflow) {
        return workflow.phases.find(phase => {
            if (phase.status !== 'pending')
                return false;
            // Check dependencies
            const dependenciesMet = phase.dependencies.every(depId => {
                const depPhase = workflow.phases.find(p => p.id === depId);
                return depPhase && depPhase.status === 'completed';
            });
            return dependenciesMet;
        }) || null;
    }
    async executePhase(workflowId, phaseId) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow)
            return;
        const phase = workflow.phases.find(p => p.id === phaseId);
        if (!phase)
            return;
        phase.status = 'running';
        phase.startTime = new Date();
        workflow.currentPhase = phaseId;
        workflow.updatedAt = new Date();
        try {
            // Prepare input for the agent
            const input = this.preparePhaseInput(workflow, phase);
            // Execute the agent
            const result = await this.orchestrator.executeWorkflowPhase(phaseId, input);
            if (result.success) {
                phase.result = result.data;
                // Create artifacts if applicable
                if (result.data && result.data.files) {
                    for (const file of result.data.files) {
                        workflow.artifacts.push({
                            id: `artifact_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                            type: this.determineArtifactType(file.path),
                            name: path.basename(file.path),
                            path: file.path,
                            phaseId: phase.id,
                            size: file.size,
                            createdAt: new Date(),
                            metadata: file.metadata
                        });
                    }
                }
                if (phase.approvalRequired && workflow.approvalMode === 'interactive') {
                    phase.status = 'waiting_approval';
                    this.createApprovalRequest(workflow, phase);
                }
                else {
                    phase.status = 'completed';
                    phase.endTime = new Date();
                    this.updateProgress(workflow);
                    await this.executeNextPhase(workflowId);
                }
            }
            else {
                throw new Error(result.error || 'Phase execution failed');
            }
        }
        catch (error) {
            phase.status = 'failed';
            phase.error = error instanceof Error ? error.message : String(error);
            phase.endTime = new Date();
            if (phase.retryCount < phase.maxRetries) {
                phase.retryCount++;
                setTimeout(() => this.executePhase(workflowId, phaseId), 5000); // Retry after 5 seconds
            }
            else {
                workflow.status = 'failed';
                workflow.error = `Phase ${phase.name} failed: ${phase.error}`;
            }
        }
        workflow.updatedAt = new Date();
        await this.persistWorkflow(workflow);
    }
    preparePhaseInput(workflow, phase) {
        const baseInput = {
            workflowId: workflow.id,
            phaseId: phase.id,
            requirements: workflow.requirements,
            technology: workflow.technology,
            outputPath: workflow.outputPath,
            projectName: `Generated-${workflow.technology}-Project`,
            config: workflow.config
        };
        // Add results from dependency phases
        const dependencyResults = {};
        phase.dependencies.forEach(depId => {
            const depPhase = workflow.phases.find(p => p.id === depId);
            if (depPhase && depPhase.result) {
                dependencyResults[depId] = depPhase.result;
            }
        });
        return {
            ...baseInput,
            dependencies: dependencyResults,
            previousPhases: workflow.phases.filter(p => p.status === 'completed'),
            ...phase.metadata?.defaultParams
        };
    }
    createApprovalRequest(workflow, phase) {
        const approvalId = `${workflow.id}:${phase.id}`;
        const context = {
            workflowId: workflow.id,
            phaseId: phase.id,
            phaseName: phase.name,
            phaseDescription: phase.description,
            result: phase.result,
            artifacts: workflow.artifacts.filter(a => a.phaseId === phase.id),
            nextPhase: this.findNextPhase(workflow)?.name,
            options: [
                {
                    id: 'approve',
                    label: 'Approve & Continue',
                    action: 'approve',
                    description: 'Accept the results and proceed to the next phase'
                },
                {
                    id: 'modify',
                    label: 'Modify & Continue',
                    action: 'modify',
                    description: 'Make changes to the results before proceeding',
                    requiresInput: true
                },
                {
                    id: 'retry',
                    label: 'Retry Phase',
                    action: 'retry',
                    description: 'Re-execute this phase'
                },
                {
                    id: 'skip',
                    label: 'Skip Phase',
                    action: 'skip',
                    description: 'Skip this phase and continue'
                }
            ],
            context: {
                previousPhases: workflow.phases.filter(p => p.status === 'completed'),
                dependencies: this.preparePhaseInput(workflow, phase).dependencies,
                estimatedTime: this.estimateRemainingTime(workflow)
            }
        };
        this.pendingApprovals.set(approvalId, context);
    }
    updateProgress(workflow) {
        const completedPhases = workflow.phases.filter(p => p.status === 'completed' || p.status === 'skipped').length;
        workflow.progress = {
            totalPhases: workflow.phases.length,
            completedPhases,
            percentage: Math.round((completedPhases / workflow.phases.length) * 100)
        };
    }
    estimateRemainingTime(workflow) {
        const remainingPhases = workflow.phases.filter(p => p.status === 'pending').length;
        const avgPhaseTime = 300000; // 5 minutes default
        return remainingPhases * avgPhaseTime;
    }
    determineArtifactType(filePath) {
        const ext = path.extname(filePath).toLowerCase();
        const filename = path.basename(filePath).toLowerCase();
        if (filename.includes('spec') || filename.includes('api') || ext === '.yaml' || ext === '.yml') {
            return 'specification';
        }
        if (filename.includes('report') || filename.includes('review') || ext === '.md') {
            return 'report';
        }
        if (filename.includes('config') || filename.includes('properties') || ext === '.json' || ext === '.xml') {
            return 'configuration';
        }
        return 'file';
    }
    async persistWorkflow(workflow) {
        try {
            const filePath = path.join(this.workflowStorage, `${workflow.id}.json`);
            await fs.writeFile(filePath, JSON.stringify(workflow, null, 2));
        }
        catch (error) {
            console.error('Failed to persist workflow:', error);
        }
    }
    async loadWorkflow(workflowId) {
        try {
            const filePath = path.join(this.workflowStorage, `${workflowId}.json`);
            const data = await fs.readFile(filePath, 'utf-8');
            const workflow = JSON.parse(data);
            // Convert date strings back to Date objects
            workflow.createdAt = new Date(workflow.createdAt);
            workflow.updatedAt = new Date(workflow.updatedAt);
            if (workflow.startedAt)
                workflow.startedAt = new Date(workflow.startedAt);
            if (workflow.completedAt)
                workflow.completedAt = new Date(workflow.completedAt);
            workflow.phases.forEach(phase => {
                if (phase.timestamp)
                    phase.timestamp = new Date(phase.timestamp);
                if (phase.startTime)
                    phase.startTime = new Date(phase.startTime);
                if (phase.endTime)
                    phase.endTime = new Date(phase.endTime);
            });
            this.activeWorkflows.set(workflowId, workflow);
            return workflow;
        }
        catch (error) {
            return null;
        }
    }
}
