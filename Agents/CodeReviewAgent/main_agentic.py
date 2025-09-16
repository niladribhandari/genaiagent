#!/usr/bin/env python3
"""
Enhanced AgenticAI Code Review System
Autonomous intelligent agents for comprehensive code analysis
"""

import argparse
import json
import sys
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import existing components for backward compatibility
try:
    from core.review_engine import ReviewEngine
    from core.report_generator import ReportGenerator
    from models.review_result import ReviewResult
    from utils.logger_config import LoggerConfig
except ImportError:
    # Fallback imports
    ReviewEngine = None
    ReportGenerator = None
    ReviewResult = None
    LoggerConfig = None

# Import new AgenticAI components
from agentic.core import AgentOrchestrator, AgentGoal, Priority
from agentic.review_agents import (
    FileDiscoveryAgent, CodeQualityAgent, SecurityAnalysisAgent,
    ComplianceAgent, ReportGenerationAgent
)


class AgenticReviewSystem:
    """Main AgenticAI Review System orchestrating autonomous agents."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.logger = logging.getLogger(__name__)
        self.orchestrator = AgentOrchestrator(self.config)
        self._initialize_agents()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration for the agentic system."""
        return {
            "max_complexity": 10,
            "max_nesting_depth": 4,
            "enable_security_analysis": True,
            "enable_compliance_check": True,
            "report_formats": ["json", "html"],
            "parallel_processing": True,
            "agent_timeout": 300,  # 5 minutes
            "learning_enabled": True
        }
    
    def _initialize_agents(self):
        """Initialize all specialized agents."""
        # File Discovery Agent
        file_discovery_agent = FileDiscoveryAgent("file_discovery_agent", self.config)
        self.orchestrator.register_agent(file_discovery_agent)
        
        # Code Quality Agent  
        code_quality_agent = CodeQualityAgent("code_quality_agent", self.config)
        self.orchestrator.register_agent(code_quality_agent)
        
        # Security Analysis Agent
        security_agent = SecurityAnalysisAgent("security_analysis_agent", self.config)
        self.orchestrator.register_agent(security_agent)
        
        # Compliance Agent
        compliance_agent = ComplianceAgent("compliance_agent", self.config)
        self.orchestrator.register_agent(compliance_agent)
        
        # Report Generation Agent
        report_agent = ReportGenerationAgent("report_generation_agent", self.config)
        self.orchestrator.register_agent(report_agent)
        
        self.logger.info("All agents initialized successfully")
    
    async def analyze_project(self, project_path: str, instruction_file: Optional[str] = None, 
                             api_spec_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive project analysis using autonomous agents.
        
        Args:
            project_path: Path to the project to analyze
            instruction_file: Optional instruction file for context
            api_spec_file: Optional API specification file
            
        Returns:
            Comprehensive analysis results from all agents
        """
        try:
            self.logger.info(f"Starting AgenticAI analysis of project: {project_path}")
            
            # Prepare analysis context
            context = await self._prepare_analysis_context(
                project_path, instruction_file, api_spec_file
            )
            
            # Define the main analysis goal
            main_goal = AgentGoal(
                goal_id="comprehensive_code_review",
                description="Perform comprehensive code review using autonomous agents",
                priority=Priority.CRITICAL,
                context=context
            )
            
            # Execute autonomous analysis workflow
            results = await self.orchestrator.execute_goal(main_goal)
            
            self.logger.info("AgenticAI analysis completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"AgenticAI analysis failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _prepare_analysis_context(self, project_path: str, 
                                       instruction_file: Optional[str],
                                       api_spec_file: Optional[str]) -> Dict[str, Any]:
        """Prepare comprehensive analysis context."""
        context = {
            "project_path": project_path,
            "analysis_mode": "agentic",
            "timestamp": "2025-08-14T22:00:00Z"  # Would use actual timestamp
        }
        
        # Load instruction context if provided
        if instruction_file:
            try:
                instruction_context = await self._load_instruction_context(instruction_file)
                context["instruction_context"] = instruction_context
                self.logger.info(f"Loaded instruction context from {instruction_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load instruction file {instruction_file}: {e}")
        
        # Load API specification context if provided
        if api_spec_file:
            try:
                api_context = await self._load_api_context(api_spec_file)
                context["api_context"] = api_context
                self.logger.info(f"Loaded API context from {api_spec_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load API spec file {api_spec_file}: {e}")
        
        return context
    
    async def _load_instruction_context(self, instruction_file: str) -> Dict[str, Any]:
        """Load and parse instruction file for analysis context."""
        instruction_path = Path(instruction_file)
        
        if not instruction_path.exists():
            raise FileNotFoundError(f"Instruction file not found: {instruction_file}")
        
        context = {"source_file": str(instruction_path)}
        
        try:
            with open(instruction_path, 'r', encoding='utf-8') as f:
                if instruction_path.suffix.lower() in ['.yaml', '.yml']:
                    import yaml
                    content = yaml.safe_load(f)
                    context.update(content)
                elif instruction_path.suffix.lower() == '.json':
                    content = json.load(f)
                    context.update(content)
                else:
                    # Plain text instruction file
                    content = f.read()
                    context["instructions"] = content
                    
                    # Extract structured information from text
                    context.update(self._parse_text_instructions(content))
        
        except Exception as e:
            self.logger.error(f"Error parsing instruction file: {e}")
            raise
        
        return context
    
    async def _load_api_context(self, api_spec_file: str) -> Dict[str, Any]:
        """Load and parse API specification file."""
        api_path = Path(api_spec_file)
        
        if not api_path.exists():
            raise FileNotFoundError(f"API spec file not found: {api_spec_file}")
        
        context = {"source_file": str(api_path)}
        
        try:
            with open(api_path, 'r', encoding='utf-8') as f:
                if api_path.suffix.lower() in ['.yaml', '.yml']:
                    import yaml
                    content = yaml.safe_load(f)
                    context.update(content)
                elif api_path.suffix.lower() == '.json':
                    content = json.load(f)
                    context.update(content)
                else:
                    # Other formats
                    content = f.read()
                    context["raw_content"] = content
        
        except Exception as e:
            self.logger.error(f"Error parsing API spec file: {e}")
            raise
        
        return context
    
    def _parse_text_instructions(self, content: str) -> Dict[str, Any]:
        """Parse structured information from text instructions."""
        parsed = {
            "required_components": [],
            "naming_conventions": {},
            "architectural_patterns": [],
            "constraints": []
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if line.lower().startswith('required components:'):
                current_section = 'required_components'
            elif line.lower().startswith('naming conventions:'):
                current_section = 'naming_conventions'
            elif line.lower().startswith('architectural patterns:'):
                current_section = 'architectural_patterns'
            elif line.lower().startswith('constraints:'):
                current_section = 'constraints'
            elif line.startswith('- ') and current_section:
                # List item
                item = line[2:].strip()
                if current_section in ['required_components', 'architectural_patterns', 'constraints']:
                    parsed[current_section].append(item)
        
        return parsed


async def run_agentic_analysis(project_path: str, instruction_file: Optional[str] = None,
                              api_spec_file: Optional[str] = None, 
                              output_file: Optional[str] = None,
                              output_format: str = "json") -> Dict[str, Any]:
    """Run the complete AgenticAI analysis workflow."""
    
    # Initialize the agentic review system
    review_system = AgenticReviewSystem()
    
    # Perform analysis
    results = await review_system.analyze_project(
        project_path=project_path,
        instruction_file=instruction_file,
        api_spec_file=api_spec_file
    )
    
    # Generate output file if specified
    if output_file:
        try:
            output_path = Path(output_file)
            
            if output_format.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, default=str)
            elif output_format.lower() == "html":
                # Generate HTML report
                html_content = generate_html_report(results)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            print(f"Analysis results saved to: {output_file}")
            
        except Exception as e:
            print(f"Error saving results to file: {e}")
    
    return results


def generate_html_report(results: Dict[str, Any]) -> str:
    """Generate HTML report from analysis results."""
    
    # Extract key metrics
    executive_summary = results.get("comprehensive_report", {}).get("executive_summary", {})
    total_files = executive_summary.get("total_files_analyzed", 0)
    total_issues = executive_summary.get("total_issues_found", 0)
    quality_score = executive_summary.get("overall_quality_score", 0.0)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AgenticAI Code Review Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .metric {{ text-align: center; padding: 10px; }}
            .metric h3 {{ margin: 0; color: #333; }}
            .metric p {{ margin: 5px 0; font-size: 24px; font-weight: bold; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007cba; }}
            .agent-result {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; }}
            .high-priority {{ border-left-color: #d32f2f; }}
            .medium-priority {{ border-left-color: #f57c00; }}
            .low-priority {{ border-left-color: #388e3c; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>AgenticAI Code Review Report</h1>
            <p>Autonomous intelligent analysis by specialized agents</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <h3>Files Analyzed</h3>
                <p>{total_files}</p>
            </div>
            <div class="metric">
                <h3>Issues Found</h3>
                <p>{total_issues}</p>
            </div>
            <div class="metric">
                <h3>Quality Score</h3>
                <p>{quality_score:.2f}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Agent Analysis Results</h2>
            {_generate_agent_results_html(results)}
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            {_generate_recommendations_html(results)}
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <pre>{json.dumps(executive_summary, indent=2)}</pre>
        </div>
    </body>
    </html>
    """
    
    return html_content


def _generate_agent_results_html(results: Dict[str, Any]) -> str:
    """Generate HTML for agent results section."""
    agent_results = results.get("comprehensive_report", {}).get("agent_analyses", {})
    
    html_parts = []
    for agent_id, agent_result in agent_results.items():
        html_parts.append(f"""
        <div class="agent-result">
            <h3>{agent_id.replace('_', ' ').title()}</h3>
            <pre>{json.dumps(agent_result, indent=2)}</pre>
        </div>
        """)
    
    return ''.join(html_parts)


def _generate_recommendations_html(results: Dict[str, Any]) -> str:
    """Generate HTML for recommendations section."""
    recommendations = results.get("comprehensive_report", {}).get("recommendations", [])
    
    if not recommendations:
        return "<p>No specific recommendations generated.</p>"
    
    html_parts = ["<ul>"]
    for rec in recommendations:
        priority_class = rec.get("priority", "medium").lower() + "-priority"
        html_parts.append(f"""
        <li class="{priority_class}">
            <strong>{rec.get('title', 'Recommendation')}</strong>: 
            {rec.get('description', 'No description')}
        </li>
        """)
    html_parts.append("</ul>")
    
    return ''.join(html_parts)


def run_legacy_analysis(project_path: str, config_file: Optional[str] = None,
                       output_file: Optional[str] = None) -> None:
    """Run legacy analysis for backward compatibility."""
    logger = logging.getLogger(__name__)
    logger.info("Running in legacy mode")
    
    # Load configuration
    config = {}
    if config_file:
        with open(config_file, 'r') as f:
            config = json.load(f)
    
    engine = ReviewEngine(config)
    result = engine.review_project(project_path)
    
    # Generate report using existing generator
    generator = ReportGenerator()
    output_file = output_file or "legacy_review_report.json"
    generator.generate_report(result, output_file)
    
    print(f"Legacy analysis completed. Report saved to {output_file}")


def parse_arguments():
    """Parse command line arguments for both legacy and agentic modes."""
    parser = argparse.ArgumentParser(
        description="AgenticAI Code Review System - Autonomous intelligent code analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # AgenticAI mode with autonomous agents
  python main_agentic.py -p /path/to/project -i instructions.yml -s api_spec.yml
  
  # Legacy mode for backward compatibility
  python main_agentic.py --legacy /path/to/project
  
  # Generate HTML report
  python main_agentic.py -p /path/to/project -o report.html --format html
        """
    )
    
    # New AgenticAI arguments
    parser.add_argument('-p', '--project-path', type=str, 
                       help='Path to the project directory to analyze')
    parser.add_argument('-i', '--instruction-file', type=str,
                       help='Path to instruction file (YAML/JSON)')
    parser.add_argument('-s', '--api-spec-file', type=str,
                       help='Path to API specification file (YAML/JSON)')
    parser.add_argument('-o', '--output-file', type=str,
                       help='Output file for analysis results')
    parser.add_argument('--format', choices=['json', 'html'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    # Legacy mode support
    parser.add_argument('--legacy', type=str, metavar='PROJECT_PATH',
                       help='Run in legacy mode (backward compatibility)')
    
    return parser.parse_args()


async def main():
    """Main entry point for the AgenticAI Review System."""
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    LoggerConfig.setup_logging(level=log_level, console_output=True)
    logger = logging.getLogger(__name__)
    
    try:
        if args.legacy:
            # Legacy mode for backward compatibility
            logger.info("Running in legacy mode")
            
            # Validate project path
            if not Path(args.legacy).exists():
                print(f"Error: Project path does not exist: {args.legacy}")
                sys.exit(1)
            
            run_legacy_analysis(
                project_path=args.legacy,
                config_file=args.config,
                output_file=args.output_file
            )
            
        else:
            # AgenticAI mode
            if not args.project_path:
                print("Error: Project path is required for AgenticAI mode")
                print("Use -p/--project-path to specify the project directory")
                sys.exit(1)
            
            logger.info("Running in AgenticAI mode with autonomous agents")
            
            # Validate project path
            if not Path(args.project_path).exists():
                print(f"Error: Project path does not exist: {args.project_path}")
                sys.exit(1)
            
            # Run AgenticAI analysis
            results = await run_agentic_analysis(
                project_path=args.project_path,
                instruction_file=args.instruction_file,
                api_spec_file=args.api_spec_file,
                output_file=args.output_file,
                output_format=args.format
            )
            
            # Display summary
            if "error" not in results:
                exec_summary = results.get("comprehensive_report", {}).get("executive_summary", {})
                print("\nAgenticAI Analysis Summary:")
                print(f"Files Analyzed: {exec_summary.get('total_files_analyzed', 0)}")
                print(f"Issues Found: {exec_summary.get('total_issues_found', 0)}")
                print(f"Quality Score: {exec_summary.get('overall_quality_score', 0.0):.2f}")
                print(f"Critical Issues: {exec_summary.get('critical_issues', 0)}")
            else:
                print(f"Analysis failed: {results['error']}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print("\nAnalysis interrupted.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
