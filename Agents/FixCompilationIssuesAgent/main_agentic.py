#!/usr/bin/env python3
"""
Fix Compilation Issues Agent - Main Entry Point

This agent analyzes compilation errors and automatically fixes them using AI.
Follows the Agent Best Practices pattern.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic.fix_compilation_agent import FixCompilationIssuesAgent

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('fix_compilation_issues.log')
        ]
    )

def main():
    """Main entry point for the Fix Compilation Issues Agent"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(
        description="Fix Compilation Issues Agent - Automatically fix compilation errors"
    )
    parser.add_argument(
        "--project-path",
        required=True,
        help="Path to the project with compilation issues"
    )
    parser.add_argument(
        "--compilation-errors",
        help="JSON file containing compilation errors or JSON string"
    )
    parser.add_argument(
        "--build-output",
        help="Raw build output from compilation for analysis when structured errors aren't available"
    )
    parser.add_argument(
        "--build-tool",
        default="maven",
        choices=["maven", "gradle"],
        help="Build tool used (default: maven)"
    )
    parser.add_argument(
        "--backup-dir",
        help="Directory to store backups (default: project_path/backups)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes"
    )
    parser.add_argument(
        "--output",
        help="Output file for results (default: stdout)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize the agent
        logger.info("Initializing Fix Compilation Issues Agent...")
        agent = FixCompilationIssuesAgent()
        
        # Parse compilation errors
        errors = []
        if args.compilation_errors:
            if os.path.isfile(args.compilation_errors):
                with open(args.compilation_errors, 'r') as f:
                    errors = json.load(f)
            else:
                try:
                    errors = json.loads(args.compilation_errors)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON format for compilation errors")
                    return 1
        
        # Run the agent
        logger.info(f"Fixing compilation issues in: {args.project_path}")
        result = agent.fix_compilation_issues(
            project_path=args.project_path,
            errors=errors,
            build_tool=args.build_tool,
            backup_dir=args.backup_dir,
            dry_run=args.dry_run,
            build_output=args.build_output
        )
        
        # Output results
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "project_path": args.project_path,
            "result": result
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            logger.info(f"Results written to: {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
        
        logger.info("Fix Compilation Issues Agent completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error running Fix Compilation Issues Agent: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
