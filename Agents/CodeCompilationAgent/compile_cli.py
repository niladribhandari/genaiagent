#!/usr/bin/env python3
"""
Command Line Interface for Code Compilation Agent
Usage: python compile_cli.py [OPTIONS] PROJECT_PATH
"""

import argparse
import sys
import json
import asyncio
from pathlib import Path
from src.compilation_agent import (
    CodeCompilationAgent, 
    ProjectType, 
    CompilationStatus,
    get_project_info
)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Enhanced Code Compilation Agent - Compile Java Spring Boot, .NET, Python, and Node.js projects with AI analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compile Java Spring Boot project with AI analysis
  python compile_cli.py /path/to/springboot/project
  
  # Compile with specific options and OpenAI API key
  python compile_cli.py /path/to/project --type java_springboot --skip-tests --openai-key sk-...
  
  # Get project information only
  python compile_cli.py /path/to/project --info-only
  
  # Generate simplified JSON output for agents
  python compile_cli.py /path/to/project --json-output --format simplified
        """
    )
    
    # Required arguments
    parser.add_argument(
        "project_path",
        help="Path to the project directory to compile"
    )
    
    # Optional arguments
    parser.add_argument(
        "--type", "-t",
        choices=["java_springboot", "dotnet_api", "python_api", "nodejs_api"],
        help="Project type (auto-detected if not specified)"
    )
    
    parser.add_argument(
        "--goals", "-g",
        help="Comma-separated list of build goals/tasks (e.g., 'clean,compile,test')"
    )
    
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests during compilation"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Compilation timeout in seconds (default: 300)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-essential output"
    )
    
    parser.add_argument(
        "--info-only",
        action="store_true",
        help="Show project information only, don't compile"
    )
    
    parser.add_argument(
        "--report", "-r",
        help="Save detailed compilation report to file"
    )
    
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--format",
        choices=["standard", "simplified"],
        default="standard",
        help="Output format (simplified for agent consumption)"
    )
    
    parser.add_argument(
        "--openai-key",
        help="OpenAI API key for AI analysis (uses OPENAI_API_KEY env var if not provided)"
    )
    
    parser.add_argument(
        "--disable-ai",
        action="store_true",
        help="Disable OpenAI analysis"
    )
    
    parser.add_argument(
        "--build-args",
        help="Additional build arguments (space-separated)"
    )
    
    args = parser.parse_args()
    
    # Run the async main function
    asyncio.run(main_async(args))


async def main_async(args):
    """Async main function to handle OpenAI integration."""
    # Validate project path
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    # Configure agent
    config = {
        "verbose": args.verbose and not args.quiet,
        "timeout": args.timeout,
        "enable_openai": not args.disable_ai
    }
    
    # Add OpenAI API key if provided
    if args.openai_key:
        config["openai_api_key"] = args.openai_key
    
    agent = CodeCompilationAgent(config=config)
    
    # Show project information
    if not args.quiet:
        print(f"🔍 Analyzing project: {project_path}")
    
    info = agent.get_project_info(str(project_path))
    
    if args.info_only:
        print_project_info(info, args.json_output)
        return
    
    if not args.quiet:
        print(f"   Project type: {info['project_type']}")
        print(f"   Build files: {', '.join(info['build_files']) if info['build_files'] else 'None'}")
        print(f"   Source files: {info['source_files_count']}")
        if config["enable_openai"]:
            print("   🤖 AI analysis: Enabled")
    
    # Determine project type
    project_type = None
    if args.type:
        type_mapping = {
            "java_springboot": ProjectType.JAVA_SPRINGBOOT,
            "dotnet_api": ProjectType.DOTNET_API,
            "python_api": ProjectType.PYTHON_API,
            "nodejs_api": ProjectType.NODEJS_API
        }
        project_type = type_mapping[args.type]
    
    # Prepare build options
    build_options = {}
    
    if args.goals:
        goals = [goal.strip() for goal in args.goals.split(',')]
        if project_type == ProjectType.JAVA_SPRINGBOOT:
            build_options["goals"] = goals
        else:
            build_options["tasks"] = goals
    
    if args.skip_tests:
        build_options["skip_tests"] = True
    
    if args.build_args:
        build_options["args"] = args.build_args.split()
    
    # Start compilation
    if not args.quiet:
        print(f"\n🔨 Starting compilation...")
    
    try:
        result = await agent.compile_project(
            project_path=str(project_path),
            project_type=project_type,
            build_options=build_options
        )
        
        # Handle results
        if args.json_output:
            if args.format == "simplified":
                print(json.dumps(result.to_simplified_format(), indent=2))
            else:
                print_json_results(result)
        else:
            print_results(result, args.quiet)
        
        # Save report if requested
        if args.report:
            try:
                report = agent.generate_compilation_report(result)
                with open(args.report, 'w') as f:
                    f.write(report)
                if not args.quiet:
                    print(f"\n📄 Detailed report saved to: {args.report}")
            except Exception as e:
                print(f"⚠️  Warning: Could not save report: {e}")
        
        # Exit with appropriate code
        if result.status == CompilationStatus.SUCCESS:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Compilation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"❌ Compilation failed with exception: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


def print_project_info(info: dict, json_output: bool = False):
    """Print project information."""
    if json_output:
        print(json.dumps(info, indent=2))
    else:
        print("\n📋 Project Information:")
        print(f"   Path: {info['project_path']}")
        print(f"   Type: {info['project_type']}")
        print(f"   Exists: {info['exists']}")
        print(f"   Build files: {', '.join(info['build_files']) if info['build_files'] else 'None'}")
        print(f"   Source files: {info['source_files_count']}")
        print(f"   Estimated build time: {info['estimated_build_time']}")


def print_results(result, quiet: bool = False):
    """Print compilation results in human-readable format."""
    if result.status == CompilationStatus.SUCCESS:
        print("✅ Compilation successful!")
    elif result.status == CompilationStatus.FAILED:
        print("❌ Compilation failed!")
    elif result.status == CompilationStatus.WARNING:
        print("⚠️  Compilation completed with warnings!")
    
    if not quiet:
        print(f"   Time taken: {result.compilation_time:.2f} seconds")
        
        # Use enhanced summary if available
        if result.issues_summary:
            summary = result.issues_summary
            print(f"   Total issues: {summary.total_issues}")
            print(f"   Errors: {summary.errors}")
            print(f"   Warnings: {summary.warnings}")
            print(f"   Files with issues: {summary.files_with_issues}")
            
            if result.openai_processed:
                print(f"   🤖 AI suggestions: {summary.ai_suggestions_available}")
        else:
            # Fallback to basic summary
            errors = result.get_errors()
            warnings = result.get_warnings()
            print(f"   Total issues: {len(result.issues)}")
            print(f"   Errors: {len(errors)}")
            print(f"   Warnings: {len(warnings)}")
        
        if result.output_path:
            print(f"   Output: {result.output_path}")
    
    # Show errors with enhanced format
    errors = result.get_errors()
    if errors:
        print(f"\n🔴 Errors ({len(errors)}):")
        for i, error in enumerate(errors[:5], 1):  # Show first 5 errors
            print(f"   {i}. {error.message}")
            location_str = f"      📄 {error.get_short_location()}"
            if error.location.line_number:
                location_str += f":{error.location.line_number}"
                if error.location.column_number:
                    location_str += f":{error.location.column_number}"
            print(location_str)
            
            # Show AI suggestion if available
            if error.has_ai_suggestions():
                best_suggestion = error.get_best_suggestion()
                print(f"      🤖 AI Suggestion: {best_suggestion.description}")
                if best_suggestion.confidence > 0.7:
                    print(f"         (Confidence: {best_suggestion.confidence:.1%})")
            elif error.metadata.get("suggestion"):
                print(f"      💡 {error.metadata['suggestion']}")
        
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more errors")
    
    # Show warnings with enhanced format
    warnings = result.get_warnings()
    if warnings and not quiet:
        print(f"\n🟡 Warnings ({len(warnings)}):")
        for i, warning in enumerate(warnings[:3], 1):  # Show first 3 warnings
            print(f"   {i}. {warning.message}")
            location_str = f"      📄 {warning.get_short_location()}"
            if warning.location.line_number:
                location_str += f":{warning.location.line_number}"
            print(location_str)
        
        if len(warnings) > 3:
            print(f"   ... and {len(warnings) - 3} more warnings")
    
    # Show AI summary if available
    if result.ai_summary and not quiet:
        print(f"\n🤖 AI Analysis Summary:")
        print(f"   {result.ai_summary}")


def print_json_results(result):
    """Print compilation results in JSON format."""
    # Use the simplified format for JSON output
    json_result = result.to_simplified_format()
    print(json.dumps(json_result, indent=2))


if __name__ == "__main__":
    main()
