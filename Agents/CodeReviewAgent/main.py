"""
Code Review Agent - Main Entry Point

This module provides the main entry point for the code review agent.
It orchestrates the review process and generates     # Setup logging
    level = "DEBUG" if args.verbose else "INFO"
    LoggerConfig.setup_logging(level=level, console_output=True)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Code Review Agent...")
    
    # Determine source directory
    source_path = None
    review_context = {}
    
    if args.project_path:
        # New mode: Review generated code with context
        source_path = Path(args.project_path)
        logger.info(f"Project path: {args.project_path}")
        
        # Store instruction file context
        if args.instruction_file:
            instruction_path = Path(args.instruction_file)
            if instruction_path.exists():
                review_context['instruction_file'] = str(instruction_path)
                logger.info(f"Instruction file: {args.instruction_file}")
            else:
                logger.warning(f"Instruction file not found: {args.instruction_file}")
        
        # Store API spec context  
        if args.api_spec:
            api_spec_path = Path(args.api_spec)
            if api_spec_path.exists():
                review_context['api_spec'] = str(api_spec_path)
                logger.info(f"API specification: {args.api_spec}")
            else:
                logger.warning(f"API specification not found: {args.api_spec}")
                
    elif args.source:
        # Legacy mode: Direct source directory
        source_path = Path(args.source)
        logger.info(f"Source directory (legacy mode): {args.source}")
    else:
        logger.error("Either --project-path (-p) or --source must be specified")
        sys.exit(1)
    
    logger.info(f"Output format: {args.format}")
    logger.info(f"Minimum severity: {args.severity}")
    
    # Validate source path
    if not source_path.exists():
        logger.error(f"Source path does not exist: {source_path}")
        sys.exit(1)ports.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .core.review_engine import ReviewEngine
from .core.report_generator import ReportGenerator
from .models.review_result import ReviewResult
from .utils.file_scanner import FileScanner
from .utils.logger_config import LoggerConfig


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Code Review Agent - Automated code quality analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # New workflow mode (recommended):
    %(prog)s -i InstructionFiles/java_springboot.yml -s API-requirements/policy_management_spec.yml -p policy-generation
    %(prog)s -i InstructionFiles/nodejs_express.yml -s API-requirements/customer_update_spec.yml -p customer-service --format html
    
    # Legacy mode:
    %(prog)s --source /path/to/generated/code --output review_report.json
    %(prog)s --source /path/to/code --format html --output report.html --verbose
        """
    )
    
    parser.add_argument(
        "--source",
        help="Path to the source code directory to review (legacy mode)"
    )
    
    parser.add_argument(
        "-i", "--instruction-file",
        help="Path to instruction file (e.g., InstructionFiles/java_springboot.yml)"
    )
    
    parser.add_argument(
        "-s", "--api-spec",
        dest="api_spec",
        help="Path to API requirements specification (e.g., API-requirements/policy_management_spec.yml)"
    )
    
    parser.add_argument(
        "-p", "--project-path",
        help="Path to generated source code project directory (e.g., policy-generation)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="review_report.json",
        help="Output file for the review report (default: review_report.json)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "html", "markdown", "text"],
        default="json",
        help="Output format for the report (default: json)"
    )
    
    parser.add_argument(
        "-r", "--rules",
        help="Path to custom review rules configuration file"
    )
    
    parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Minimum severity level to report (default: medium)"
    )
    
    parser.add_argument(
        "--language",
        choices=["java", "python", "javascript", "typescript", "auto"],
        default="auto",
        help="Primary programming language to analyze (default: auto-detect)"
    )
    
    parser.add_argument(
        "--include-patterns",
        nargs="+",
        default=["*.java", "*.py", "*.js", "*.ts", "*.xml", "*.yml", "*.yaml"],
        help="File patterns to include in review"
    )
    
    parser.add_argument(
        "--exclude-patterns",
        nargs="+",
        default=["*.class", "*.jar", "node_modules/*", ".git/*", "target/*"],
        help="File patterns to exclude from review"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    
    return parser.parse_args()


def load_configuration(config_path: Optional[str]) -> Dict:
    """Load configuration from file if provided."""
    default_config = {
        "review_categories": [
            "code_quality",
            "security",
            "performance", 
            "maintainability",
            "documentation",
            "testing",
            "architecture"
        ],
        "rules": {
            "java": {
                "enforce_naming_conventions": True,
                "check_exception_handling": True,
                "verify_dependency_injection": True,
                "validate_annotations": True,
                "check_thread_safety": True
            },
            "python": {
                "enforce_pep8": True,
                "check_type_hints": True,
                "validate_docstrings": True,
                "check_security_patterns": True
            }
        }
    }
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            logging.warning(f"Failed to load config from {config_path}: {e}")
    
    return default_config


def main():
    """Main entry point for the code review agent."""
    args = parse_arguments()
    
    # Setup logging
    level = "DEBUG" if args.verbose else "INFO"
    LoggerConfig.setup_logging(level=level, console_output=True)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Code Review Agent...")
    
    # Determine source directory
    source_path = None
    review_context = {}
    
    if args.project_path:
        # New mode: Review generated code with context
        source_path = Path(args.project_path)
        logger.info(f"Project path: {args.project_path}")
        
        # Store instruction file context
        if args.instruction_file:
            instruction_path = Path(args.instruction_file)
            if instruction_path.exists():
                review_context['instruction_file'] = str(instruction_path)
                logger.info(f"Instruction file: {args.instruction_file}")
            else:
                logger.warning(f"Instruction file not found: {args.instruction_file}")
        
        # Store API spec context  
        if args.api_spec:
            api_spec_path = Path(args.api_spec)
            if api_spec_path.exists():
                review_context['api_spec'] = str(api_spec_path)
                logger.info(f"API specification: {args.api_spec}")
            else:
                logger.warning(f"API specification not found: {args.api_spec}")
                
    elif args.source:
        # Legacy mode: Direct source directory
        source_path = Path(args.source)
        logger.info(f"Source directory (legacy mode): {args.source}")
    else:
        logger.error("Either --project-path (-p) or --source must be specified")
        sys.exit(1)
    
    logger.info(f"Output format: {args.format}")
    logger.info(f"Minimum severity: {args.severity}")
    
    try:
        # Validate source directory
        if not source_path.exists():
            logger.error(f"Source directory does not exist: {source_path}")
            sys.exit(1)
        
        if not source_path.is_dir():
            logger.error(f"Source path is not a directory: {source_path}")
            sys.exit(1)
        
        # Load configuration
        config = load_configuration(args.config)
        
        # Add review context to config
        config['review_context'] = review_context
        
        # Initialize file scanner
        scanner_config = {}
        if args.include_patterns:
            scanner_config['include_patterns'] = args.include_patterns
        if args.exclude_patterns:
            scanner_config['ignore_patterns'] = (scanner_config.get('ignore_patterns', []) + 
                                                 args.exclude_patterns)
        if args.language != 'auto':
            scanner_config['languages'] = [args.language]
        
        scanner = FileScanner(scanner_config)
        
        # Scan for files to review
        logger.info("Scanning for files to review...")
        files_to_review = scanner.scan_directory(source_path)
        logger.info(f"Found {len(files_to_review)} files to review")
        
        if not files_to_review:
            logger.warning("No files found to review")
            sys.exit(0)
        
        # Initialize review engine
        review_engine = ReviewEngine(
            config=config,
            language=args.language,
            severity_threshold=args.severity
        )
        
        # Perform code review
        logger.info("Starting code review process...")
        review_results = review_engine.review_files(files_to_review)
        
        # Generate report
        logger.info("Generating review report...")
        report_generator = ReportGenerator(format=args.format)
        
        # Get summary and add review context
        summary_stats = review_engine.get_summary_statistics()
        summary_stats.review_context = review_context
        
        report_generator.generate_report(
            review_results=review_results,
            output_path=args.output,
            summary_stats=summary_stats
        )
        
        logger.info(f"Review completed. Report saved to: {args.output}")
        
        # Exit with appropriate code
        critical_issues = sum(1 for result in review_results 
                            if result.has_critical_issues())
        if critical_issues > 0:
            logger.warning(f"Found {critical_issues} files with critical issues")
            sys.exit(2)
        
        logger.info("Code review completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Review process interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Unexpected error during review: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
