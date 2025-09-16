"""
Enhanced AgenticAI Code Generation - Main Interface with Business Intelligence
Intelligent code generation system with business logic awareness and AI integration.
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
from agentic.enhanced_agents import EnhancedConfigurationAgent, IntelligentCodeGenerationAgent
from agentic.simple_agents import SimpleStructureAgent, SimpleValidationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("EnhancedAgenticCodeGenerator")


class EnhancedAgenticCodeGenerator:
    """
    Enhanced autonomous code generation system with business intelligence.
    Uses sophisticated AI and business logic processing for intelligent code generation.
    """
    
    def __init__(self):
        """Initialize the enhanced agentic code generator."""
        self.logger = logging.getLogger("EnhancedAgenticCodeGenerator")
        
        # Create orchestrator with enhanced configuration
        orchestrator_config = {
            "max_concurrent_goals": 8,  # Increased for parallel processing
            "timeout_seconds": 600,     # Increased timeout for AI processing
            "retry_failed_goals": True,
            "log_level": "INFO"
        }
        self.orchestrator = AgentOrchestrator(orchestrator_config)
        self._setup_enhanced_agents()
    
    def _setup_enhanced_agents(self):
        """Initialize and register enhanced specialized agents."""
        try:
            self.logger.info("Setting up enhanced specialized agents...")
            # Import enhanced and simple agents
            from agentic.enhanced_agents import EnhancedConfigurationAgent, IntelligentCodeGenerationAgent
            from agentic.simple_agents import SimpleStructureAgent, SimpleValidationAgent

            # Instantiate agents
            config_agent = EnhancedConfigurationAgent()
            codegen_agent = IntelligentCodeGenerationAgent()
            structure_agent = SimpleStructureAgent()
            validation_agent = SimpleValidationAgent()

            # Register agents with orchestrator
            self.orchestrator.register_agent(config_agent)
            self.orchestrator.register_agent(codegen_agent)
            self.orchestrator.register_agent(structure_agent)
            self.orchestrator.register_agent(validation_agent)

            self.logger.info("Enhanced agents registered successfully")
        except Exception as e:
            self.logger.error(f"Failed to setup enhanced agents: {e}")
            # Fallback to simple agents
            self._setup_fallback_agents()
    
    def _setup_fallback_agents(self):
        """Setup fallback simple agents if enhanced agents fail."""
        self.logger.warning("Setting up fallback simple agents")
        
        from agentic.simple_agents import (
            SimpleConfigurationAgent, SimpleTemplateAgent, SimpleCodeGenerationAgent
        )
        
        config_agent = SimpleConfigurationAgent()
        structure_agent = SimpleStructureAgent()
        template_agent = SimpleTemplateAgent()
        codegen_agent = SimpleCodeGenerationAgent()
        validation_agent = SimpleValidationAgent()
        
        self.orchestrator.register_agent(config_agent)
        self.orchestrator.register_agent(structure_agent)
        self.orchestrator.register_agent(template_agent)
        self.orchestrator.register_agent(codegen_agent)
        self.orchestrator.register_agent(validation_agent)
        
        self.logger.info("Fallback agents registered successfully")
    
    async def generate_code_project(self, spec_path: str, instruction_path: str, 
                                  output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Generate complete code project using enhanced autonomous agents.
        
        Args:
            spec_path: Path to API specification file
            instruction_path: Path to instruction template file  
            output_path: Path where generated code will be written
            **kwargs: Additional configuration options
        
        Returns:
            Dict containing generation results and enhanced metrics
        """
        self.logger.info("Starting enhanced autonomous code generation process")
        self.logger.info(f"Spec: {spec_path}")
        self.logger.info(f"Instructions: {instruction_path}")
        self.logger.info(f"Output: {output_path}")
        
        try:
            # Phase 1: Enhanced Configuration and Analysis
            phase1_result = await self._execute_configuration_phase(
                spec_path, instruction_path
            )
            
            if not phase1_result['success']:
                return phase1_result
            
            # Phase 2: Project Structure Setup
            phase2_result = await self._execute_structure_phase(
                output_path, phase1_result['context']
            )
            
            if not phase2_result['success']:
                return phase2_result
            
            # Phase 3: Intelligent Code Generation
            phase3_result = await self._execute_intelligent_generation_phase(
                {**phase1_result['context'], **phase2_result['context']}
            )
            
            if not phase3_result['success']:
                return phase3_result
            
            # Phase 4: Validation and Quality Assurance
            phase4_result = await self._execute_validation_phase(
                phase3_result['context']
            )
            
            # Compile final results
            final_result = self._compile_final_results(
                phase1_result, phase2_result, phase3_result, phase4_result
            )
            
            self.logger.info("Enhanced autonomous code generation completed successfully")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Enhanced code generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "details": {
                    "phase": "unknown",
                    "message": "Enhanced generation system error"
                }
            }
    
    async def _execute_configuration_phase(self, spec_path: str, instruction_path: str) -> Dict[str, Any]:
        """Execute enhanced configuration and analysis phase."""
        self.logger.info("Phase 1: Enhanced Configuration and Business Analysis")
        
        try:
            # Create configuration goals
            goals = [
                AgentGoal(
                    id="load_specification", 
                    description="spec_loading",
                    priority=Priority.HIGH, 
                    success_criteria={"spec_loaded": True},
                    context={"spec_path": spec_path}
                ),
                AgentGoal(
                    id="load_instructions",
                    description="instruction_loading",
                    priority=Priority.HIGH,
                    success_criteria={"instructions_loaded": True}, 
                    context={"instruction_path": instruction_path}
                ),
            ]
            
            # Execute configuration goals
            results = await self.orchestrator.execute_goals(goals)
            
            # Process results
            spec_data = None
            instruction_data = None
            entities = []
            business_metadata = {}
            
            for result in results:
                if result.success:
                    result_data = result.result
                    if 'spec_data' in result_data:
                        spec_data = result_data['spec_data']
                        entities = result_data.get('entities', [])
                        business_metadata = result_data.get('business_metadata', {})
                    elif 'instruction_data' in result_data:
                        instruction_data = result_data['instruction_data']
                else:
                    self.logger.error(f"Configuration goal failed: {result.goal_id} - {result.error_message}")
            
            if not spec_data or not instruction_data:
                return {
                    "success": False,
                    "error": "Failed to load specification or instruction data",
                    "phase": "configuration"
                }
            
            # Execute compatibility validation
            compatibility_goal = AgentGoal(
                id="validate_compatibility",
                description="compatibility",
                priority=Priority.MEDIUM,
                success_criteria={"compatibility_validated": True},
                context={
                    "spec_data": spec_data,
                    "instruction_data": instruction_data
                }
            )
            
            compatibility_results = await self.orchestrator.execute_goals([compatibility_goal])
            
            # Execute business requirements analysis
            business_analysis_goal = AgentGoal(
                id="analyze_business_requirements",
                description="business_analysis",
                priority=Priority.HIGH,
                success_criteria={"business_analysis_complete": True},
                context={
                    "spec_data": spec_data,
                    "instruction_data": instruction_data
                }
            )
            
            business_results = await self.orchestrator.execute_goals([business_analysis_goal])
            
            # Extract business analysis
            business_analysis = {}
            requires_ai_generation = False
            
            for result in business_results:
                if result.success:
                    business_analysis = result.result.get('business_analysis', {})
                    requires_ai_generation = result.result.get('requires_ai_generation', False)
            
            return {
                "success": True,
                "context": {
                    "spec_data": spec_data,
                    "instruction_data": instruction_data,
                    "entities": entities,
                    "business_metadata": business_metadata,
                    "business_analysis": business_analysis,
                    "requires_ai_generation": requires_ai_generation
                },
                "phase": "configuration",
                "message": f"Configuration completed. Found {len(entities)} entities. AI Required: {requires_ai_generation}"
            }
            
        except Exception as e:
            self.logger.error(f"Configuration phase failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "phase": "configuration"
            }
    
    async def _execute_structure_phase(self, output_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute project structure setup phase."""
        self.logger.info("Phase 2: Project Structure Setup")
        
        try:
            structure_goal = AgentGoal(
                id="setup_project_structure",
                description="structure",
                priority=Priority.HIGH,
                success_criteria={"project_structure_created": True},
                context={
                    "output_path": output_path,
                    "instruction_data": context.get("instruction_data", {})
                }
            )
            
            results = await self.orchestrator.execute_goals([structure_goal])
            
            for result in results:
                if result.success:
                    return {
                        "success": True,
                        "context": {
                            "output_path": output_path,
                            "structure_result": result.result
                        },
                        "phase": "structure",
                        "message": f"Project structure created at {output_path}"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.error_message,
                        "phase": "structure"
                    }
            
            return {
                "success": False,
                "error": "No structure results returned",
                "phase": "structure"
            }
            
        except Exception as e:
            self.logger.error(f"Structure phase failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "phase": "structure"
            }
    
    async def _execute_intelligent_generation_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intelligent code generation phase."""
        self.logger.info("Phase 3: Intelligent Code Generation")
        
        try:
            # Determine generation strategy based on business analysis
            requires_ai = context.get("requires_ai_generation", False)
            business_analysis = context.get("business_analysis", {})
            complexity_score = business_analysis.get("complexity_score", 1)
            
            if complexity_score >= 7 or requires_ai:
                generation_goal_id = "intelligent_generation"
                self.logger.info(f"Using intelligent AI generation (complexity: {complexity_score})")
            elif complexity_score >= 4:
                generation_goal_id = "business_aware_generation"
                self.logger.info(f"Using business-aware generation (complexity: {complexity_score})")
            else:
                generation_goal_id = "pattern_based_generation"
                self.logger.info(f"Using pattern-based generation (complexity: {complexity_score})")
            
            generation_goal = AgentGoal(
                id=generation_goal_id,
                description="code_generation",
                priority=Priority.CRITICAL,
                success_criteria={"code_generated": True},
                context=context
            )
            
            results = await self.orchestrator.execute_goals([generation_goal])
            
            for result in results:
                if result.success:
                    return {
                        "success": True,
                        "context": {
                            **context,
                            "generation_result": result.result
                        },
                        "phase": "generation",
                        "message": f"Code generation completed using {generation_goal_id}"
                    }
                else:
                    self.logger.error(f"Generation failed: {result.error_message}")
                    # Try fallback generation
                    return await self._execute_fallback_generation(context)
            
            return {
                "success": False,
                "error": "No generation results returned",
                "phase": "generation"
            }
            
        except Exception as e:
            self.logger.error(f"Generation phase failed: {e}")
            return await self._execute_fallback_generation(context)
    
    async def _execute_fallback_generation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fallback generation using simple template processing."""
        self.logger.warning("Executing fallback generation")
        
        try:
            # Use simple template processing as fallback
            fallback_goal = AgentGoal(
                id="process_all_templates",
                description="fallback_generation",
                priority=Priority.HIGH,
                success_criteria={"templates_processed": True},
                context=context
            )
            
            results = await self.orchestrator.execute_goals([fallback_goal])
            
            for result in results:
                if result.success:
                    return {
                        "success": True,
                        "context": {
                            **context,
                            "generation_result": result.result
                        },
                        "phase": "generation",
                        "message": "Code generation completed using fallback template processing"
                    }
            
            return {
                "success": False,
                "error": "Even fallback generation failed",
                "phase": "generation"
            }
            
        except Exception as e:
            self.logger.error(f"Fallback generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "phase": "generation"
            }
    
    async def _execute_validation_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation and quality assurance phase."""
        self.logger.info("Phase 4: Validation and Quality Assurance")
        
        try:
            validation_goal = AgentGoal(
                id="comprehensive_validation",
                description="validation",
                priority=Priority.MEDIUM,
                success_criteria={"validation_complete": True},
                context=context
            )
            
            results = await self.orchestrator.execute_goals([validation_goal])
            
            for result in results:
                if result.success:
                    return {
                        "success": True,
                        "context": {
                            **context,
                            "validation_result": result.result
                        },
                        "phase": "validation",
                        "message": "Code validation completed"
                    }
                else:
                    self.logger.warning(f"Validation failed: {result.error_message}")
                    # Continue even if validation fails
                    return {
                        "success": True,  # Don't fail the entire process
                        "context": {
                            **context,
                            "validation_result": {
                                "success": False,
                                "error": result.error_message
                            }
                        },
                        "phase": "validation",
                        "message": "Code validation failed but generation completed"
                    }
            
            return {
                "success": True,
                "context": context,
                "phase": "validation",
                "message": "Validation phase completed with warnings"
            }
            
        except Exception as e:
            self.logger.warning(f"Validation phase error: {e}")
            # Don't fail the entire process for validation errors
            return {
                "success": True,
                "context": context,
                "phase": "validation",
                "message": f"Validation phase completed with error: {str(e)}"
            }
    
    def _compile_final_results(self, phase1: Dict, phase2: Dict, 
                             phase3: Dict, phase4: Dict) -> Dict[str, Any]:
        """Compile final comprehensive results."""
        
        context = phase3.get('context', {})
        generation_result = context.get('generation_result', {})
        validation_result = context.get('validation_result', {})
        
        # Calculate comprehensive statistics
        stats = {
            "entities_processed": len(context.get('entities', [])),
            "generation_approach": self._determine_generation_approach(context),
            "business_analysis": context.get('business_analysis', {}),
            "requires_ai": context.get('requires_ai_generation', False),
            "complexity_score": context.get('business_analysis', {}).get('complexity_score', 1)
        }
        
        # Add generation statistics
        if 'generation_stats' in generation_result:
            stats.update(generation_result['generation_stats'])
        
        # Add validation statistics
        if validation_result and 'code_validation' in validation_result:
            stats['validation'] = validation_result['code_validation']
        
        return {
            "success": True,
            "results": {
                "output_path": context.get('output_path', ''),
                "entities": context.get('entities', []),
                "generated_files": generation_result.get('generated_files', {}),
                "generation_stats": stats,
                "phases_completed": [
                    {"phase": "configuration", "success": phase1['success']},
                    {"phase": "structure", "success": phase2['success']},
                    {"phase": "generation", "success": phase3['success']},
                    {"phase": "validation", "success": phase4['success']}
                ]
            },
            "message": f"Enhanced code generation completed successfully for {stats['entities_processed']} entities"
        }
    
    def _determine_generation_approach(self, context: Dict[str, Any]) -> str:
        """Determine what generation approach was used."""
        if context.get('requires_ai_generation', False):
            return "intelligent_ai_enhanced"
        elif context.get('business_analysis', {}).get('complexity_score', 1) >= 4:
            return "business_aware"
        else:
            return "template_based"


# CLI Interface - Maintains compatibility with existing interface
def create_cli_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser with enhanced options."""
    parser = argparse.ArgumentParser(
        description="Enhanced AgenticAI Code Generator with Business Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_enhanced_agentic.py generate --spec api_spec.yml --instructions java_spring.yml --output ./generated
  python main_enhanced_agentic.py generate --spec api_spec.yml --instructions java_spring.yml --output ./generated --ai-enhanced
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate code from specification')
    generate_parser.add_argument('--spec', required=True, 
                               help='Path to API specification file (YAML)')
    generate_parser.add_argument('--instructions', required=True,
                               help='Path to instruction template file (YAML)')
    generate_parser.add_argument('--output', required=True,
                               help='Output directory for generated code')
    generate_parser.add_argument('--ai-enhanced', action='store_true',
                               help='Force AI-enhanced generation')
    generate_parser.add_argument('--verbose', action='store_true',
                               help='Enable verbose logging')
    
    return parser


async def main():
    """Main CLI entry point with JSON support for MCP integration."""
    # Check if we have JSON input as first argument (MCP mode)
    if len(sys.argv) > 1:
        try:
            # Try to parse first argument as JSON
            json_args = json.loads(sys.argv[1])
            
            # Handle JSON-based execution (from MCP server)
            if json_args.get('action') == 'generate_project':
                logger.info("Starting Enhanced AgenticAI Code Generation (JSON mode)")
                
                # Extract parameters from JSON
                specification = json_args.get('specification', '')
                output_path = json_args.get('output_path', './generated')
                technology = json_args.get('technology', 'java_springboot')
                
                # Create temporary spec file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_spec:
                    temp_spec.write(specification)
                    spec_path = temp_spec.name
                
                # Map technology to instruction file
                instruction_mapping = {
                    'java_springboot': 'java_springboot.yml',
                    'nodejs_express': 'nodejs_express.yml',
                    'dotnet_webapi': 'dotnet_webapi.yml'
                }
                
                instruction_file = instruction_mapping.get(technology, 'java_springboot.yml')
                # Always resolve from Agents/InstructionFiles
                agents_dir = Path(__file__).resolve().parent.parent
                instruction_path = str(agents_dir / 'InstructionFiles' / instruction_file)
                
                if not os.path.exists(instruction_path):
                    logger.error(f"Instruction file not found: {instruction_path}")
                    response = {
                        "success": False,
                        "error": f"Instruction file not found: {instruction_path}"
                    }
                    print(json.dumps(response))
                    return {"success": False, "error": f"Instruction file not found: {instruction_path}"}
                
                # Create output directory
                Path(output_path).mkdir(parents=True, exist_ok=True)
                
                try:
                    # Execute generation
                    generator = EnhancedAgenticCodeGenerator()
                    result = await generator.generate_code_project(spec_path, instruction_path, output_path)
                    
                    # Clean up temp file
                    os.unlink(spec_path)
                    
                    # Print JSON response for MCP server
                    response = {
                        "success": result.get("success", False),
                        "message": "Code generation completed" if result.get("success") else "Code generation failed",
                        "output_path": output_path,
                        "technology": technology
                    }
                    if not result.get("success"):
                        response["error"] = result.get("error", "Unknown error")
                    
                    print(json.dumps(response))
                    return result
                    
                except Exception as e:
                    logger.error(f"Code generation failed: {e}")
                    # Clean up temp file on error
                    if os.path.exists(spec_path):
                        os.unlink(spec_path)
                    
                    # Print JSON response for MCP server
                    response = {
                        "success": False,
                        "error": str(e),
                        "output_path": output_path,
                        "technology": technology
                    }
                    print(json.dumps(response))
                    return {"success": False, "error": str(e)}
            
            else:
                # Print JSON error response for MCP server
                error_response = {
                    "success": False,
                    "error": f"Unknown action: {json_args.get('action')}"
                }
                print(json.dumps(error_response))
                logger.error(f"Unknown JSON action: {json_args.get('action')}")
                return {"success": False, "error": f"Unknown action: {json_args.get('action')}"}
                
        except json.JSONDecodeError:
            # Not JSON, fall through to CLI parsing
            pass
    
    # Handle CLI mode
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Verbose logging enabled")
    
    if args.command == 'generate':
        logger.info("Starting Enhanced AgenticAI Code Generation (CLI mode)")
        
        # Validate input files
        if not os.path.exists(args.spec):
            logger.error(f"Specification file not found: {args.spec}")
            sys.exit(1)
        
        if not os.path.exists(args.instructions):
            logger.error(f"Instructions file not found: {args.instructions}")
            sys.exit(1)
        
        # Create output directory if needed
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize enhanced code generator
            generator = EnhancedAgenticCodeGenerator()
            
            # Generate code using the autonomous method (matches JSON mode)
            result = await generator.generate_autonomous_code(
                spec_file_path=args.spec,
                instruction_path=args.instructions,
                output_path=str(output_path),
                ai_enhance=args.ai_enhanced,
                verbose=args.verbose
            )
            
            # Output results
            if result.get('success'):
                logger.info("✅ Code generation completed successfully!")
                if result.get('results'):
                    stats = result['results'].get('generation_stats', {})
                    logger.info(f"📊 Generated code for {stats.get('entities_processed', 0)} entities")
                    logger.info(f"🧠 Generation approach: {stats.get('generation_approach', 'standard')}")
                    logger.info(f"📈 Complexity score: {stats.get('complexity_score', 0)}")
                    
                    if stats.get('total_files'):
                        logger.info(f"📄 Total files: {stats['total_files']}")
                    if stats.get('ai_enhanced_files'):
                        logger.info(f"🤖 AI-enhanced files: {stats['ai_enhanced_files']}")
                    if stats.get('business_rules_applied'):
                        logger.info(f"📋 Business rules applied: {stats['business_rules_applied']}")
            else:
                logger.error(f"❌ Code generation failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"❌ Code generation failed with exception: {e}")
            sys.exit(1)
        
        # Initialize enhanced code generator
        generator = EnhancedAgenticCodeGenerator()
        
        # Generate code
        result = await generator.generate_code_project(
            spec_path=args.spec,
            instruction_path=args.instructions,
            output_path=str(output_path),
            ai_enhanced=args.ai_enhanced,
            verbose=args.verbose
        )
        
        # Output results
        if result['success']:
            logger.info("✅ Code generation completed successfully!")
            stats = result['results']['generation_stats']
            logger.info(f"📊 Generated code for {stats['entities_processed']} entities")
            logger.info(f"🧠 Generation approach: {stats['generation_approach']}")
            logger.info(f"📈 Complexity score: {stats['complexity_score']}")
            
            if stats.get('total_files'):
                logger.info(f"📄 Total files: {stats['total_files']}")
                if stats.get('ai_enhanced_files'):
                    logger.info(f"🤖 AI-enhanced files: {stats['ai_enhanced_files']}")
                if stats.get('business_rules_applied'):
                    logger.info(f"📋 Business rules applied: {stats['business_rules_applied']}")
            
            logger.info(f"📂 Output location: {result['results']['output_path']}")
        else:
            logger.error("❌ Code generation failed!")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
