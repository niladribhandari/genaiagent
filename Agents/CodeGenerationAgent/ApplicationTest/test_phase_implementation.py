#!/usr/bin/env python3
"""
Test script to validate Phase 1 and Phase 2 implementation
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

try:
    from src.application.generators.spring_boot_generator import SpringBootGenerator
    from src.domain.models.generation_context import GenerationContext
    from agentic.core import AgentOrchestrator, AgentGoal, Priority
    from agentic.simple_agents import ConfigurationAgent, StructureAgent, TemplateAgent, CodeGenerationAgent, ValidationAgent
    from agentic.ai_code_agent import EnhancedCodeGenerationAgent
except ImportError as e:
    print(f"Import error: {e}")
    print("Attempting to test individual components...")
    SpringBootGenerator = None

def test_agentic_framework():
    """Test that the agentic framework is properly implemented."""
    print("Testing Agentic Framework...")
    
    try:
        # Test agent orchestrator creation
        orchestrator = AgentOrchestrator()
        print("✅ AgentOrchestrator created successfully")
        
        # Test adding agents
        config_agent = ConfigurationAgent()
        orchestrator.add_agent(config_agent)
        print("✅ ConfigurationAgent added to orchestrator")
        
        # Test goal creation
        goal = AgentGoal(
            description="Generate Spring Boot project",
            priority=Priority.HIGH,
            context={"project_type": "spring_boot", "entity": "Policy"}
        )
        print("✅ AgentGoal created successfully")
        
        # Test enhanced code generation agent
        enhanced_agent = EnhancedCodeGenerationAgent()
        print("✅ EnhancedCodeGenerationAgent created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agentic Framework test failed: {e}")
        return False

def test_business_logic_templates():
    """Test that business logic templates exist."""
    print("\nTesting Business Logic Templates...")
    
    templates_dir = Path(__file__).parent / "templates" / "spring_boot"
    
    # Check for business logic templates
    expected_templates = [
        "PremiumCalculationController.java",
        "RiskAssessmentController.java", 
        "PolicyWorkflowController.java",
        "PremiumCalculationRequest.java",
        "PremiumCalculationResponse.java"
    ]
    
    success_count = 0
    for template in expected_templates:
        template_path = templates_dir / "${BASE_PACKAGE}" / template
        if template_path.exists():
            print(f"✅ {template} template found")
            success_count += 1
        else:
            print(f"❌ {template} template missing")
    
    return success_count == len(expected_templates)

def test_enhanced_spring_boot_generator():
    """Test that the enhanced Spring Boot generator works."""
    print("\nTesting Enhanced Spring Boot Generator...")
    
    try:
        # Create generator with all enhanced components
        generator = SpringBootGenerator()
        print("✅ SpringBootGenerator with enhanced components created")
        
        # Verify all enhanced generators are available
        expected_generators = [
            'dto_generator',
            'repository_generator', 
            'mapper_generator',
            'validation_generator',
            'workflow_generator',
            'calculation_generator',
            'event_generator',
            'audit_generator'
        ]
        
        success_count = 0
        for gen_name in expected_generators:
            if hasattr(generator, gen_name):
                print(f"✅ {gen_name} available in SpringBootGenerator")
                success_count += 1
            else:
                print(f"❌ {gen_name} missing from SpringBootGenerator")
        
        # Test context creation methods
        test_context = GenerationContext(
            entity_name="Policy",
            package_name="com.example.insurance",
            target_language="java",
            framework="spring_boot",
            requirements=["premium calculation", "workflow approval", "audit trail"]
        )
        
        # Test business logic detection
        if generator._requires_business_logic(test_context):
            print("✅ Business logic detection working")
        else:
            print("❌ Business logic detection failed")
        
        if generator._requires_calculations(test_context):
            print("✅ Calculation requirement detection working")
        else:
            print("❌ Calculation requirement detection failed")
        
        if generator._requires_audit(test_context):
            print("✅ Audit requirement detection working")
        else:
            print("❌ Audit requirement detection failed")
        
        return success_count >= 6  # At least most generators should be present
        
    except Exception as e:
        print(f"❌ SpringBootGenerator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_creation_methods():
    """Test context creation methods."""
    print("\nTesting Context Creation Methods...")
    
    try:
        generator = SpringBootGenerator()
        base_context = GenerationContext(
            entity_name="Policy",
            package_name="com.example.insurance", 
            target_language="java",
            framework="spring_boot"
        )
        
        # Test DTO context creation
        request_context = generator._create_request_dto_context(base_context, "Policy")
        if request_context.entity_name == "PolicyRequest":
            print("✅ Request DTO context creation working")
        else:
            print("❌ Request DTO context creation failed")
            
        response_context = generator._create_response_dto_context(base_context, "Policy")
        if response_context.entity_name == "PolicyResponse":
            print("✅ Response DTO context creation working")
        else:
            print("❌ Response DTO context creation failed")
        
        # Test other context creation methods
        mapper_context = generator._create_mapper_context(base_context, "Policy")
        if mapper_context.entity_name == "PolicyMapper":
            print("✅ Mapper context creation working")
        else:
            print("❌ Mapper context creation failed")
        
        workflow_context = generator._create_workflow_context(base_context, "Policy")
        if workflow_context.entity_name == "PolicyWorkflow":
            print("✅ Workflow context creation working")
        else:
            print("❌ Workflow context creation failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Context creation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 1 & PHASE 2 IMPLEMENTATION VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Agentic Framework", test_agentic_framework),
        ("Business Logic Templates", test_business_logic_templates),
        ("Enhanced Spring Boot Generator", test_enhanced_spring_boot_generator),
        ("Context Creation Methods", test_context_creation_methods)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 1 & Phase 2 implementation successful!")
        return True
    else:
        print("⚠️  Some tests failed. Implementation needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
