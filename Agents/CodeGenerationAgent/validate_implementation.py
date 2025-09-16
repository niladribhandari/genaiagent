#!/usr/bin/env python3
"""
Simple validation test to check if Phase 1 and Phase 2 files exist
"""

import os
from pathlib import Path

def check_agentic_framework():
    """Check if agentic framework files exist."""
    print("🔍 Checking Agentic Framework Files...")
    
    agentic_dir = Path(__file__).parent / "agentic"
    expected_files = [
        "__init__.py",
        "core.py", 
        "simple_agents.py",
        "ai_code_agent.py"
    ]
    
    success = True
    for file_name in expected_files:
        file_path = agentic_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")
            success = False
    
    return success

def check_business_logic_templates():
    """Check if business logic templates exist."""
    print("\n🔍 Checking Business Logic Templates...")
    
    templates_base = Path(__file__).parent / "templates" / "spring_boot" / "${BASE_PACKAGE}"
    expected_templates = [
        ("controller/PremiumCalculationController.java", "Controller"),
        ("controller/RiskAssessmentController.java", "Controller"), 
        ("controller/${ENTITY_NAME}WorkflowController.java", "Workflow Controller"),
        ("dto/PremiumCalculationRequest.java", "Request DTO"),
        ("dto/PremiumCalculationResponse.java", "Response DTO")
    ]
    
    success = True
    for template_path, description in expected_templates:
        full_path = templates_base / template_path
        if full_path.exists():
            print(f"✅ {description} ({template_path}) exists")
        else:
            print(f"❌ {description} ({template_path}) missing")
            success = False
    
    return success

def check_enhanced_generator():
    """Check if enhanced Spring Boot generator exists with new methods."""
    print("\n🔍 Checking Enhanced Spring Boot Generator...")
    
    generator_path = Path(__file__).parent / "src" / "application" / "generators" / "spring_boot_generator.py"
    
    if not generator_path.exists():
        print("❌ SpringBootGenerator file missing")
        return False
    
    # Check if enhanced methods exist in the generator
    content = generator_path.read_text()
    
    expected_methods = [
        "_requires_business_logic",
        "_requires_calculations", 
        "_requires_audit",
        "_create_request_dto_context",
        "_create_response_dto_context",
        "_create_mapper_context",
        "_create_workflow_context",
        "_create_calculation_context",
        "_create_event_context",
        "_create_audit_context"
    ]
    
    success = True
    for method in expected_methods:
        if f"def {method}" in content:
            print(f"✅ {method} method exists")
        else:
            print(f"❌ {method} method missing")
            success = False
    
    return success

def check_file_contents():
    """Check content quality of key files."""
    print("\n🔍 Checking File Content Quality...")
    
    files_to_check = [
        ("agentic/core.py", ["class BaseAgent", "class AgentOrchestrator", "class AgentGoal"]),
        ("agentic/simple_agents.py", ["class SimpleConfigurationAgent", "class SimpleStructureAgent", "class SimpleTemplateAgent"]),
        ("agentic/ai_code_agent.py", ["class EnhancedCodeGenerationAgent"]),
        ("templates/spring_boot/${BASE_PACKAGE}/controller/PremiumCalculationController.java", ["@RestController", "PremiumCalculationRequest", "@PostMapping"]),
        ("templates/spring_boot/${BASE_PACKAGE}/dto/PremiumCalculationRequest.java", ["BigDecimal", "@NotNull", "@Valid"])
    ]
    
    success = True
    for file_path, expected_content in files_to_check:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            content = full_path.read_text()
            missing_content = []
            for expected in expected_content:
                if expected not in content:
                    missing_content.append(expected)
            
            if missing_content:
                print(f"❌ {file_path}: Missing content - {', '.join(missing_content)}")
                success = False
            else:
                print(f"✅ {file_path}: Content quality OK")
        else:
            print(f"❌ {file_path}: File missing")
            success = False
    
    return success

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("PHASE 1 & PHASE 2 IMPLEMENTATION FILE VALIDATION")
    print("=" * 60)
    
    checks = [
        ("Agentic Framework Files", check_agentic_framework),
        ("Business Logic Templates", check_business_logic_templates),
        ("Enhanced Generator Methods", check_enhanced_generator),
        ("File Content Quality", check_file_contents)
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY") 
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<30} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL VALIDATIONS PASSED! Implementation files are in place!")
        return True
    else:
        print("⚠️  Some validations failed. Please check the missing files/content.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
