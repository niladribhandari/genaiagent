"""
Demo script for Code Compilation Agent
Shows how to compile different types of projects and handle compilation issues
"""

import asyncio
import os
from pathlib import Path
from src.compilation_agent import (
    CodeCompilationAgent, 
    ProjectType, 
    CompilationStatus,
    compile_java_springboot,
    get_project_info,
    generate_report
)


def demo_java_springboot_compilation():
    """Demo Java Spring Boot compilation."""
    print("🚀 Java Spring Boot Compilation Demo")
    print("=" * 50)
    
    # Example project paths (these would be real project paths in practice)
    example_paths = [
        "./example-projects/spring-boot-api",
        "/path/to/your/springboot/project",
        "~/projects/my-spring-app"
    ]
    
    agent = CodeCompilationAgent(config={
        "verbose": True,
        "timeout": 300
    })
    
    for project_path in example_paths:
        print(f"\n📁 Analyzing project: {project_path}")
        
        # Get project information first
        info = agent.get_project_info(project_path)
        print(f"   Project exists: {info['exists']}")
        print(f"   Project type: {info['project_type']}")
        print(f"   Build files: {', '.join(info['build_files']) if info['build_files'] else 'None found'}")
        print(f"   Source files: {info['source_files_count']}")
        
        if not info['exists']:
            print("   ⚠️  Project path does not exist, skipping...")
            continue
        
        print(f"\n🔨 Starting compilation...")
        
        # Compile the project
        result = agent.compile_project(
            project_path=project_path,
            project_type=ProjectType.JAVA_SPRINGBOOT,
            build_options={
                "goals": ["clean", "compile"],  # Maven goals
                "skip_tests": True,  # Skip tests for faster compilation
                "args": ["-q"]  # Quiet mode
            }
        )
        
        # Print compilation results
        if result.status == CompilationStatus.SUCCESS:
            print("✅ Compilation successful!")
        else:
            print("❌ Compilation failed!")
        
        print(f"   Time taken: {result.compilation_time:.2f} seconds")
        print(f"   Issues found: {len(result.issues)}")
        print(f"   Errors: {len(result.get_errors())}")
        print(f"   Warnings: {len(result.get_warnings())}")
        
        # Show first few issues
        if result.issues:
            print("\n📋 Issues found:")
            for i, issue in enumerate(result.issues[:3], 1):
                severity_emoji = "🔴" if issue.severity == "error" else "🟡"
                print(f"   {i}. {severity_emoji} {issue.message}")
                if issue.file_path:
                    print(f"      📄 {issue.file_path}:{issue.line_number}")
            
            if len(result.issues) > 3:
                print(f"   ... and {len(result.issues) - 3} more issues")
        
        # Generate detailed report
        report = agent.generate_compilation_report(result)
        
        # Save report to file
        report_file = f"compilation_report_{Path(project_path).name}.txt"
        try:
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")
        
        print("\n" + "-" * 50)


def demo_quick_compilation():
    """Demo quick compilation functions."""
    print("\n🎯 Quick Compilation Demo")
    print("=" * 30)
    
    # Example using quick functions
    project_path = "./example-spring-boot-project"
    
    print(f"📁 Quick project info for: {project_path}")
    info = get_project_info(project_path)
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔨 Quick Java Spring Boot compilation...")
    result = compile_java_springboot(
        project_path,
        goals=["clean", "compile"],
        skip_tests=True
    )
    
    print(f"   Status: {result.status.value}")
    print(f"   Issues: {len(result.issues)}")
    
    # Generate and display report
    if result.issues:
        print("\n📋 Quick Report:")
        report = generate_report(result)
        # Show just the summary part
        lines = report.split('\n')
        summary_start = next(i for i, line in enumerate(lines) if line.startswith("SUMMARY:"))
        summary_end = summary_start + 6
        for line in lines[summary_start:summary_end]:
            print(f"   {line}")


def demo_multi_project_compilation():
    """Demo compiling multiple projects with different configurations."""
    print("\n🏗️  Multi-Project Compilation Demo")
    print("=" * 40)
    
    projects = [
        {
            "path": "./project1",
            "type": ProjectType.JAVA_SPRINGBOOT,
            "options": {"goals": ["clean", "compile"], "skip_tests": True}
        },
        {
            "path": "./project2", 
            "type": ProjectType.JAVA_SPRINGBOOT,
            "options": {"goals": ["clean", "test"], "skip_tests": False}
        },
        {
            "path": "./project3",
            "type": ProjectType.JAVA_SPRINGBOOT,
            "options": {"goals": ["clean", "package"], "args": ["-DskipTests"]}
        }
    ]
    
    agent = CodeCompilationAgent(config={"verbose": True})
    results = []
    
    for i, project in enumerate(projects, 1):
        print(f"\n📦 Project {i}: {project['path']}")
        
        result = agent.compile_project(
            project_path=project['path'],
            project_type=project['type'],
            build_options=project['options']
        )
        
        results.append(result)
        
        status_emoji = "✅" if result.status == CompilationStatus.SUCCESS else "❌"
        print(f"   {status_emoji} {result.status.value} ({result.compilation_time:.2f}s)")
        print(f"   Issues: {len(result.issues)} ({len(result.get_errors())} errors)")
    
    # Summary of all projects
    print(f"\n📊 Overall Summary:")
    print(f"   Total projects: {len(results)}")
    print(f"   Successful: {sum(1 for r in results if r.status == CompilationStatus.SUCCESS)}")
    print(f"   Failed: {sum(1 for r in results if r.status == CompilationStatus.FAILED)}")
    print(f"   Total compilation time: {sum(r.compilation_time for r in results):.2f}s")
    print(f"   Total issues: {sum(len(r.issues) for r in results)}")


def demo_error_handling():
    """Demo error handling scenarios."""
    print("\n🚨 Error Handling Demo")
    print("=" * 25)
    
    agent = CodeCompilationAgent()
    
    # Test cases for different error scenarios
    error_cases = [
        {
            "name": "Non-existent project",
            "path": "/path/that/does/not/exist",
            "expected": "Project path does not exist"
        },
        {
            "name": "Empty directory",
            "path": "./empty-directory",
            "expected": "No build files found"
        },
        {
            "name": "Invalid project structure",
            "path": "./invalid-project",
            "expected": "Invalid project structure"
        }
    ]
    
    for case in error_cases:
        print(f"\n🧪 Testing: {case['name']}")
        print(f"   Path: {case['path']}")
        
        result = agent.compile_project(case['path'])
        
        print(f"   Status: {result.status.value}")
        print(f"   Issues: {len(result.issues)}")
        
        if result.issues:
            print(f"   First error: {result.issues[0].message}")


def demo_maven_vs_gradle():
    """Demo compilation differences between Maven and Gradle projects."""
    print("\n⚖️  Maven vs Gradle Demo")
    print("=" * 30)
    
    projects = [
        {"path": "./maven-project", "tool": "Maven"},
        {"path": "./gradle-project", "tool": "Gradle"}
    ]
    
    agent = CodeCompilationAgent(config={"verbose": True})
    
    for project in projects:
        print(f"\n🔧 {project['tool']} Project: {project['path']}")
        
        result = agent.compile_project(project['path'])
        
        print(f"   Status: {result.status.value}")
        print(f"   Build tool: {result.metadata.get('build_tool', 'Unknown')}")
        print(f"   Time: {result.compilation_time:.2f}s")
        print(f"   Issues: {len(result.issues)}")
        
        if result.build_logs:
            # Show first few lines of build logs
            log_lines = result.build_logs.split('\n')[:5]
            print(f"   Build logs preview:")
            for line in log_lines:
                if line.strip():
                    print(f"     {line}")


def create_sample_projects():
    """Create sample project structures for testing."""
    print("\n🏗️  Creating Sample Projects")
    print("=" * 30)
    
    # Create a simple Maven project structure
    maven_project = Path("./sample-maven-project")
    maven_project.mkdir(exist_ok=True)
    
    # Create pom.xml
    pom_content = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>sample-spring-boot-api</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.0</version>
        <relativePath/>
    </parent>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>"""
    
    (maven_project / "pom.xml").write_text(pom_content)
    
    # Create source directory and sample Java file
    src_dir = maven_project / "src" / "main" / "java" / "com" / "example"
    src_dir.mkdir(parents=True, exist_ok=True)
    
    java_content = """package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class SampleApplication {
    public static void main(String[] args) {
        SpringApplication.run(SampleApplication.class, args);
    }
}

@RestController
class HelloController {
    @GetMapping("/hello")
    public String hello() {
        return "Hello, World!";
    }
}"""
    
    (src_dir / "SampleApplication.java").write_text(java_content)
    
    print(f"✅ Created sample Maven project at: {maven_project}")
    
    return str(maven_project)


def main():
    """Main demo function."""
    print("🎯 Code Compilation Agent Demo")
    print("=" * 60)
    print("This demo shows how to use the Code Compilation Agent")
    print("to compile Java Spring Boot projects and handle issues.")
    print("=" * 60)
    
    # Create sample project for testing
    sample_project = create_sample_projects()
    
    # Run different demo scenarios
    demo_java_springboot_compilation()
    demo_quick_compilation()
    demo_multi_project_compilation()
    demo_error_handling()
    demo_maven_vs_gradle()
    
    print(f"\n🎉 Demo completed!")
    print(f"Sample project created at: {sample_project}")
    print("You can test the compilation agent with your own Java Spring Boot projects.")
    print("\nUsage example:")
    print("  from src.compilation_agent import compile_java_springboot")
    print("  result = compile_java_springboot('/path/to/your/project')")
    print("  print(result.status, len(result.issues))")


if __name__ == "__main__":
    main()
