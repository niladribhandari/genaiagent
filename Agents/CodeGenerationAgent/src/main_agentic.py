"""
AgenticAI Code Generation - Main Interface
Autonomous code generation system that maintains compatibility with existing CLI.
"""

import asyncio
import argparse
import json
import logging
import os
import sys
import tempfile
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add current directory and parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from agentic.core import AgentOrchestrator, AgentGoal, Priority
from agentic.simple_agents import (
    SimpleConfigurationAgent, SimpleStructureAgent, SimpleTemplateAgent, 
    SimpleCodeGenerationAgent, SimpleValidationAgent
)


class AgenticCodeGenerator:
    """
    Autonomous code generation system using AgenticAI principles.
    Maintains compatibility with existing command-line interface.
    """
    
    def __init__(self):
        """Initialize the agentic code generator."""
        self.logger = logging.getLogger("AgenticCodeGenerator")
        
        # Create orchestrator with configuration
        orchestrator_config = {
            "max_concurrent_goals": 5,
            "timeout_seconds": 300,
            "retry_failed_goals": True,
            "log_level": "INFO"
        }
        self.orchestrator = AgentOrchestrator(orchestrator_config)
        self._setup_agents()
    
    def _setup_agents(self):
        """Initialize and register all specialized agents."""
        # Create specialized agents
        config_agent = SimpleConfigurationAgent()
        structure_agent = SimpleStructureAgent() 
        template_agent = SimpleTemplateAgent()
        codegen_agent = SimpleCodeGenerationAgent()
        validation_agent = SimpleValidationAgent()
        
        # Register agents with orchestrator
        self.orchestrator.register_agent(config_agent)
        self.orchestrator.register_agent(structure_agent)
        self.orchestrator.register_agent(template_agent)
        self.orchestrator.register_agent(codegen_agent)
        self.orchestrator.register_agent(validation_agent)
        
        self.logger.info("AgenticAI Code Generation system initialized with 5 specialized agents")
        
        # Debug: Log agent capabilities
        for agent_id, agent in self.orchestrator.agents.items():
            self.logger.info(f"Registered agent {agent_id}: {agent.name} with capabilities: {agent.capabilities}")
    
    async def generate_code_project(self, spec_path: str, instruction_path: str, 
                                  output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Generate complete code project using autonomous agents.
        
        Args:
            spec_path: Path to API specification file
            instruction_path: Path to instruction template file  
            output_path: Path where generated code will be written
            **kwargs: Additional configuration options
        
        Returns:
            Dict containing generation results and metrics
        """
        self.logger.info("Starting autonomous code generation process")
        
        try:
            # Create master context for all agents
            context = {
                "spec_path": spec_path,
                "instruction_path": instruction_path,
                "output_path": output_path,
                "template_dir": kwargs.get("template_dir", "templates"),
                "verbose": kwargs.get("verbose", False),
                "ai_enhance": kwargs.get("ai_enhance", True)
            }
            
    # Phase 1: Configuration and validation
    logger.info("Starting configuration phase...")
    config_goal = AgentGoal("load_specification", spec_file_path, {"spec_path": spec_file_path})
    instruction_goal = AgentGoal("load_instructions", instruction_path, {"instruction_path": instruction_path})
    compatibility_goal = AgentGoal("validate_compatibility", "compatibility", {})

    config_results = await orchestrator.execute_goals([config_goal, instruction_goal, compatibility_goal])
    
    # Process results
    success_results = []
    failed_results = []
    
    for result in config_results:
        if result.success:
            success_results.append(result.result)
        else:
            failed_results.append(result)
    
    if failed_results:
        logger.error(f"Configuration phase had failures: {failed_results}")
        return {
            "success": False,
            "error": "Configuration phase failed",
            "details": {
                "success": len(success_results) > 0,
                "results": success_results + [{"success": False, "error": r.error, "goal_id": r.goal_id} for r in failed_results],
                "entity_count": 0,
                "framework": "unknown",
                "message": f"Configuration phase completed for {len(success_results)} of {len(config_results)} goals"
            }
        }
    
    # Extract results from config phase  
    spec_data = None
    instruction_data = None
    
    for result in success_results:
        if result.get("spec_data"):
            spec_data = result["spec_data"]
        elif result.get("instruction_data"):
            instruction_data = result["instruction_data"]
    
    if not spec_data:
        logger.error("Failed to load specification data")
        return {"success": False, "error": "Specification loading failed"}
    
    entities = spec_data.get("entities", [])
    framework = instruction_data.get("framework", "unknown") if instruction_data else "unknown"            # Phase 2: Project Structure Setup  
            self.logger.info("Phase 2: Project Structure Setup")
            structure_results = await self._execute_structure_phase(context)
            if not structure_results.get("success"):
                return {"success": False, "error": "Structure phase failed", "details": structure_results}
            
            # Phase 3: Template Processing
            self.logger.info("Phase 3: Template Processing")
            template_results = await self._execute_template_phase(context)
            if not template_results.get("success"):
                return {"success": False, "error": "Template phase failed", "details": template_results}
            
            # Phase 4: AI-Enhanced Code Generation
            self.logger.info("Phase 4: AI-Enhanced Code Generation")
            generation_results = await self._execute_generation_phase(context)
            if not generation_results.get("success"):
                return {"success": False, "error": "Generation phase failed", "details": generation_results}
            
            # Phase 5: Code Validation and Quality Assurance
            self.logger.info("Phase 5: Code Validation")
            validation_results = await self._execute_validation_phase(context)
            
            # Phase 6: File Generation and Output
            self.logger.info("Phase 6: File Generation")
            file_results = await self._execute_file_generation_phase(context)
            if not file_results.get("success"):
                return {"success": False, "error": "File generation phase failed", "details": file_results}
            
            # Compile final results
            final_results = {
                "success": True,
                "message": "Autonomous code generation completed successfully",
                "phases": {
                    "configuration": config_results,
                    "structure": structure_results,
                    "templates": template_results,
                    "generation": generation_results,
                    "validation": validation_results,
                    "files": file_results
                },
                "metrics": {
                    "total_files_generated": file_results.get("files_written", 0),
                    "entities_processed": config_results.get("entity_count", 0),
                    "templates_processed": template_results.get("template_count", 0),
                    "validation_rate": validation_results.get("validation_rate", 0.0),
                    "quality_score": validation_results.get("average_quality_score", 0.0)
                },
                "output_path": output_path
            }
            
            self.logger.info(f"Code generation complete: {final_results['metrics']['total_files_generated']} files generated")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_configuration_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute configuration analysis and loading phase."""
        goals = [
            AgentGoal(
                id="load_specification",
                description="Load and validate API specification file",
                priority=Priority.HIGH,
                success_criteria={},
                context=context
            ),
            AgentGoal(
                id="load_instructions", 
                description="Load and validate instruction template file",
                priority=Priority.HIGH,
                success_criteria={},
                context=context
            )
        ]
        
        # Execute configuration goals
        results = []
        for goal in goals:
            agent_result = await self.orchestrator.execute_goal(goal)
            if agent_result.success:
                result = agent_result.result
            else:
                result = {
                    "success": False, 
                    "error": getattr(agent_result, 'error_message', 'Goal execution failed'),
                    "goal_id": goal.id
                }
            results.append(result)
            
            # Update context with loaded data
            if result.get("success"):
                if "spec_data" in result:
                    context["spec_data"] = result["spec_data"]
                if "instruction_data" in result:
                    context["instruction_data"] = result["instruction_data"]
        
        # Validate compatibility
        compatibility_goal = AgentGoal(
            id="validate_compatibility",
            description="Validate compatibility between specification and instructions",
            priority=Priority.MEDIUM,
            success_criteria={},
            context=context
        )
        
        compatibility_agent_result = await self.orchestrator.execute_goal(compatibility_goal)
        compatibility_result = compatibility_agent_result.result if compatibility_agent_result.success else {"success": False, "error": "Compatibility check failed"}
        results.append(compatibility_result)
        
        # Determine overall success
        success = all(r.get("success", False) for r in results)
        entity_count = len(context.get("spec_data", {}).get("entities", []))
        
        return {
            "success": success,
            "results": results,
            "entity_count": entity_count,
            "framework": context.get("instruction_data", {}).get("framework", "unknown"),
            "message": f"Configuration phase completed for {entity_count} entities"
        }
    
    async def _execute_structure_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute project structure setup phase."""
        structure_goal = AgentGoal(
            id="setup_project_structure",
            description="Create complete project structure",
            priority=Priority.HIGH,
            success_criteria={},
            context=context
        )
        
        agent_result = await self.orchestrator.execute_goal(structure_goal)
        result = agent_result.result if agent_result.success else {"success": False, "error": "Structure setup failed"}
        
        return {
            "success": result.get("success", False),
            "structure_result": result,
            "directories_created": result.get("directory_count", 0),
            "message": f"Structure phase completed with {result.get('directory_count', 0)} directories"
        }
    
    async def _execute_template_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute template processing phase."""
        template_goal = AgentGoal(
            id="process_all_templates",
            description="Process templates for all entities",
            priority=Priority.HIGH,
            success_criteria={},
            context=context
        )
        
        agent_result = await self.orchestrator.execute_goal(template_goal)
        result = agent_result.result if agent_result.success else {"success": False, "error": "Template processing failed"}
        
        if result.get("success"):
            context["processed_templates"] = result.get("processed_templates", {})
        
        return {
            "success": result.get("success", False),
            "template_result": result,
            "template_count": result.get("template_count", 0),
            "message": f"Template phase processed {result.get('template_count', 0)} templates"
        }
    
    async def _execute_generation_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI-enhanced code generation phase."""
        generation_goal = AgentGoal(
            id="ai_enhanced_generation",
            description="Enhance templates with AI-generated code",
            priority=Priority.HIGH,
            success_criteria={},
            context=context
        )
        
        agent_result = await self.orchestrator.execute_goal(generation_goal)
        result = agent_result.result if agent_result.success else {"success": False, "error": "AI generation failed"}
        
        # Debug: Log the result structure
        self.logger.info(f"Generation result keys: {list(result.keys()) if result else 'None'}")
        if result:
            self.logger.info(f"Result type: {type(result)}")
            
            # Check what's inside codegen_agent
            if 'codegen_agent' in result:
                codegen_result = result['codegen_agent']
                self.logger.info(f"Codegen agent result type: {type(codegen_result)}")
                self.logger.info(f"Codegen agent result keys: {list(codegen_result.keys()) if isinstance(codegen_result, dict) else 'Not a dict'}")
                
                # Look for enhanced_templates in the nested result
                if isinstance(codegen_result, dict) and 'enhanced_templates' in codegen_result:
                    self.logger.info(f"Found enhanced templates in codegen_agent: {len(codegen_result['enhanced_templates'])} entities")
            
            if "enhanced_templates" in result:
                self.logger.info(f"Enhanced templates found: {len(result['enhanced_templates'])} entities")
        
        # Extract enhanced templates from the result
        enhanced_templates = {}
        if result.get("enhanced_templates"):
            enhanced_templates = result["enhanced_templates"]
        elif result.get("result") and result["result"].get("enhanced_templates"):
            enhanced_templates = result["result"]["enhanced_templates"]
        elif result.get("codegen_agent") and isinstance(result["codegen_agent"], dict):
            # Check in the codegen_agent nested result
            if result["codegen_agent"].get("enhanced_templates"):
                enhanced_templates = result["codegen_agent"]["enhanced_templates"]
            elif result["codegen_agent"].get("result") and result["codegen_agent"]["result"].get("enhanced_templates"):
                enhanced_templates = result["codegen_agent"]["result"]["enhanced_templates"]
        
        # Fallback to processed templates if no enhanced templates available
        if not enhanced_templates:
            enhanced_templates = context.get("processed_templates", {})
            self.logger.warning("No enhanced templates found, using processed templates as fallback")
        else:
            self.logger.info("Found %d enhanced entities with enhanced templates", len(enhanced_templates))
        
        if enhanced_templates:
            context["enhanced_templates"] = enhanced_templates
        
        return {
            "success": True,  # Consider it successful if we got a result
            "generation_result": result,
            "enhanced_entities": len(enhanced_templates),
            "enhanced_templates": enhanced_templates,
            "message": f"Generation phase enhanced {len(enhanced_templates)} entities"
        }
    
    async def _execute_validation_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code validation and quality assurance phase."""
        validation_goal = AgentGoal(
            id="comprehensive_validation",
            description="Validate generated code and assess quality",
            priority=Priority.MEDIUM,
            success_criteria={},
            context=context
        )
        
        agent_result = await self.orchestrator.execute_goal(validation_goal)
        result = agent_result.result if agent_result.success else {"success": False, "error": "Validation failed"}
        
        return {
            "success": result.get("success", False),
            "validation_result": result,
            "validation_rate": result.get("code_validation", {}).get("validation_rate", 0.0),
            "average_quality_score": result.get("quality_assessment", {}).get("average_quality_score", 0.0),
            "message": "Validation phase completed"
        }
    
    async def _execute_file_generation_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file generation and writing phase."""
        enhanced_templates = context.get("enhanced_templates", {})
        output_path = context.get("output_path")
        
        if not enhanced_templates:
            return {"success": False, "error": "No enhanced templates available for file generation"}
        
        files_written = 0
        generated_files = []
        errors = []
        
        try:
            output_dir = Path(output_path)
            
            for entity_name, entity_templates in enhanced_templates.items():
                for template_name, template_data in entity_templates.items():
                    # Get content (prefer enhanced over original)
                    content = template_data.get("enhanced_content", template_data.get("content", ""))
                    output_file_path = template_data.get("output_path")
                    
                    if not output_file_path or not content:
                        continue
                    
                    # Create full file path
                    full_path = output_dir / output_file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Apply smart import processing to all Java files
                    if output_file_path.endswith('.java'):
                        from agentic.ai_code_agent import EnhancedCodeGenerationAgent, GenerationContext
                        
                        # Get package name from template data
                        package_name = template_data.get("package_name", "com.example.demo")
                        entity_name = template_data.get("entity_name", "Entity")
                        
                        # Create context for import processing
                        file_type = self._determine_file_type(output_file_path)
                        context = GenerationContext(
                            entity_name=entity_name,
                            package_name=package_name,
                            file_type=file_type,
                            language="Java",
                            framework="Spring Boot",
                            template_content=content,
                            spec_data={},
                            instruction_data={},
                            output_path=output_file_path
                        )
                        
                        # Apply smart import enhancement
                        ai_agent = EnhancedCodeGenerationAgent()
                        content = ai_agent._enhance_java_imports(content, context)
                    
                    # Write file
                    try:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        files_written += 1
                        generated_files.append({
                            "entity": entity_name,
                            "template": template_name,
                            "file_path": str(full_path),
                            "size": len(content)
                        })
                        
                        self.logger.debug(f"Generated: {full_path}")
                        
                    except Exception as e:
                        error_msg = f"Failed to write {full_path}: {e}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)
            
            return {
                "success": len(errors) == 0,
                "files_written": files_written,
                "generated_files": generated_files,
                "errors": errors,
                "message": f"Generated {files_written} files with {len(errors)} errors"
            }
            
        except Exception as e:
            return {"success": False, "error": f"File generation failed: {e}"}
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type from file path."""
        file_path = file_path.lower()
        if '/controller/' in file_path or 'controller.java' in file_path:
            return 'controller'
        elif '/service/' in file_path and '/impl/' in file_path:
            return 'service'
        elif '/service/' in file_path:
            return 'service'
        elif '/model/' in file_path or '/entity/' in file_path:
            return 'model'
        elif '/dto/' in file_path:
            return 'dto'
        elif '/repository/' in file_path:
            return 'repository'
        elif '/client/' in file_path:
            return 'client'
        elif '/config/' in file_path:
            return 'config'
        elif '/exception/' in file_path:
            return 'exception'
        elif '/util/' in file_path:
            return 'util'
        else:
            return 'other'


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments():
    """Parse command line arguments maintaining compatibility."""
    parser = argparse.ArgumentParser(
        description="AgenticAI Code Generation - Autonomous code generation system"
    )
    
    parser.add_argument(
        "--spec", "-s",
        dest="spec_path",
        required=True,
        help="Path to API specification file"
    )
    
    parser.add_argument(
        "--instructions", "-i", 
        dest="instruction_path",
        required=True,
        help="Path to instruction template file"
    )
    
    parser.add_argument(
        "--project", "-p",
        dest="output_path", 
        required=True,
        help="Output directory for generated code"
    )
    
    parser.add_argument(
        "--template-dir",
        dest="template_dir",
        default="templates",
        help="Directory containing template files (default: templates)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--no-ai-enhance",
        action="store_true",
        help="Disable AI enhancement (use templates only)"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point for AgenticAI code generation."""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting AgenticAI Code Generation System")
    
    # Validate input files
    if not os.path.exists(args.spec_path):
        logger.error(f"Specification file not found: {args.spec_path}")
        sys.exit(1)
    
    if not os.path.exists(args.instruction_path):
        logger.error(f"Instruction file not found: {args.instruction_path}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_path, exist_ok=True)
    
    try:
        # Initialize AgenticAI system
        generator = AgenticCodeGenerator()
        
        # Execute autonomous code generation
        result = await generator.generate_code_project(
            spec_path=args.spec_path,
            instruction_path=args.instruction_path,
            output_path=args.output_path,
            template_dir=args.template_dir,
            verbose=args.verbose,
            ai_enhance=not args.no_ai_enhance
        )
        
        # Report results
        if result.get("success"):
            metrics = result.get("metrics", {})
            logger.info("=" * 60)
            logger.info("CODE GENERATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"Files Generated: {metrics.get('total_files_generated', 0)}")
            logger.info(f"Entities Processed: {metrics.get('entities_processed', 0)}")
            logger.info(f"Templates Processed: {metrics.get('templates_processed', 0)}")
            logger.info(f"Validation Rate: {metrics.get('validation_rate', 0):.1%}")
            logger.info(f"Quality Score: {metrics.get('quality_score', 0):.2f}")
            logger.info(f"Output Directory: {result.get('output_path')}")
            logger.info("=" * 60)
            
            if args.verbose:
                logger.info("Phase Results:")
                for phase_name, phase_result in result.get("phases", {}).items():
                    logger.info(f"  {phase_name.title()}: {phase_result.get('message', 'Completed')}")
        else:
            logger.error("CODE GENERATION FAILED")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            if args.verbose and "details" in result:
                logger.error(f"Details: {result['details']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Code generation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    # Check if we're being called with JSON arguments (from MCP server)
    if len(sys.argv) > 1 and sys.argv[1].startswith('{'):
        import json
        try:
            # Parse JSON arguments from MCP server
            json_args = json.loads(sys.argv[1])
            
            # Extract required arguments
            if json_args.get('action') == 'generate_project':
                spec_input = json_args.get('specification', '')
                output_path = json_args.get('output_path', '/tmp/generated_code')
                technology = json_args.get('technology', 'java_springboot')
                
                # Check if specification is a file path or inline content
                if os.path.isfile(spec_input):
                    # It's a file path, use it directly
                    temp_spec_path = spec_input
                    print(f"[DEBUG] Using specification file: {temp_spec_path}", file=sys.stderr)
                else:
                    # It's inline content, create a temporary file
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_spec:
                        temp_spec.write(spec_input)
                        temp_spec_path = temp_spec.name
                    print(f"[DEBUG] Created temporary spec file: {temp_spec_path}", file=sys.stderr)
                
                # Debug: validate that the YAML content is valid
                try:
                    with open(temp_spec_path, 'r') as f:
                        test_yaml = yaml.safe_load(f)
                    print(f"[DEBUG] YAML file loaded successfully from: {temp_spec_path}", file=sys.stderr)
                    print(f"[DEBUG] YAML contains keys: {list(test_yaml.keys()) if test_yaml else 'None'}", file=sys.stderr)
                except Exception as yaml_error:
                    print(f"[DEBUG] YAML parsing error: {yaml_error}", file=sys.stderr)
                    print(json.dumps({"success": False, "error": f"Invalid YAML content: {yaml_error}"}))
                    sys.exit(1)
                
                # Find instruction file based on technology
                instruction_files = {
                    'java_springboot': 'java_springboot.yml',
                    'nodejs_express': 'nodejs_express.yml',
                    'dotnet_webapi': 'dotnet_webapi.yml'
                }
                
                # Look for instruction file in parent directory
                instruction_filename = instruction_files.get(technology, 'java_springboot.yml')
                instruction_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'InstructionFiles', instruction_filename)
                
                if not os.path.exists(instruction_path):
                    print(json.dumps({"success": False, "error": f"Instruction file not found: {instruction_path}"}))
                    sys.exit(1)
                
                # Create output directory
                os.makedirs(output_path, exist_ok=True)
                
                # Initialize generator and run
                try:
                    generator = AgenticCodeGenerator()
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(generator.generate_code_project(
                        spec_path=temp_spec_path,
                        instruction_path=instruction_path,
                        output_path=output_path,
                        verbose=True
                    ))
                    
                    # Clean up temp file only if we created one
                    if not os.path.isfile(spec_input):  # Only delete if we created a temporary file
                        try:
                            os.unlink(temp_spec_path)
                        except:
                            pass
                    
                    # Return JSON result
                    print(json.dumps(result))
                    
                except Exception as e:
                    # Clean up temp file only if we created one
                    if not os.path.isfile(spec_input) and 'temp_spec_path' in locals():
                        try:
                            os.unlink(temp_spec_path)
                        except:
                            pass
                    
                    print(json.dumps({"success": False, "error": str(e)}))
                    sys.exit(1)
                    
            else:
                print(json.dumps({"success": False, "error": "Unknown action or missing action parameter"}))
                sys.exit(1)
                
        except json.JSONDecodeError as e:
            print(json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"}))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"success": False, "error": f"Unexpected error: {str(e)}"}))
            sys.exit(1)
    else:
        # Run the async main function (original CLI mode)
        asyncio.run(main())
