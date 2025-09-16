#!/usr/bin/env python3
"""
Import Test Script
Tests the fixed import system for CodeGenerationAgent
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test all critical imports"""
    results = []
    
    # Test core imports
    try:
        from core.interfaces import CodeGenerator
        from core.exceptions import CodeGenerationError
        results.append("✅ SUCCESS: Core interfaces and exceptions")
    except Exception as e:
        results.append(f"❌ FAILED: Core imports: {e}")
    
    # Test domain models
    try:
        from domain.models.generation_context import GenerationContext
        from domain.models.code_models import GeneratedCode
        results.append("✅ SUCCESS: Domain models")
    except Exception as e:
        results.append(f"❌ FAILED: Domain models: {e}")
    
    # Test domain services
    try:
        from domain.services.business_logic_processor import BusinessLogicProcessor
        from domain.services.prompt_builder import AdvancedPromptBuilder
        results.append("✅ SUCCESS: Domain services")
    except Exception as e:
        results.append(f"❌ FAILED: Domain services: {e}")
    
    # Test infrastructure
    try:
        from infrastructure.template_engine import TemplateEngine
        from infrastructure.ai_provider import EnhancedOpenAIProvider
        from infrastructure.import_manager import ImportManager
        results.append("✅ SUCCESS: Infrastructure")
    except Exception as e:
        results.append(f"❌ FAILED: Infrastructure: {e}")
    
    # Test application services
    try:
        from application.services.enhanced_code_generation_service import EnhancedCodeGenerationService
        from application.services.context_enrichment_service import ContextEnrichmentService
        results.append("✅ SUCCESS: Application services")
    except Exception as e:
        results.append(f"❌ FAILED: Application services: {e}")
    
    # Test generators
    try:
        from application.generators.dto_generator import DTOGenerator
        from application.generators.workflow_generator import WorkflowGenerator
        results.append("✅ SUCCESS: Generators")
    except Exception as e:
        results.append(f"❌ FAILED: Generators: {e}")
    
    return results

if __name__ == "__main__":
    print("🧪 TESTING IMPORT SYSTEM FIXES")
    print("=" * 50)
    
    results = test_imports()
    for result in results:
        print(result)
    
    print("=" * 50)
    success_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 ALL IMPORTS WORKING! ({success_count}/{total_count})")
        sys.exit(0)
    else:
        print(f"⚠️  SOME IMPORTS FAILED ({success_count}/{total_count})")
        sys.exit(1)
