#!/usr/bin/env python3
"""Simple test script for Phase 3 - Testing Enhanced System"""

import sys
import os
import logging

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.append(src_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Phase3Test")

def test_domain_services():
    """Test domain services from Phase 1."""
    logger.info("Testing Phase 1 - Domain Services")
    
    try:
        from domain.services.business_logic_processor import BusinessLogicProcessor
        from domain.services.prompt_builder import AdvancedPromptBuilder
        from domain.services.integration_pattern_processor import IntegrationPatternProcessor
        
        processor = BusinessLogicProcessor()
        prompt_builder = AdvancedPromptBuilder()
        integration_processor = IntegrationPatternProcessor()
        
        logger.info("✅ Domain services loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Domain services failed: {e}")
        return False

def test_application_services():
    """Test application services from Phase 2."""
    logger.info("Testing Phase 2 - Application Services")
    
    try:
        from application.services.context_enrichment_service import ContextEnrichmentService
        
        service = ContextEnrichmentService()
        logger.info("✅ Application services loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Application services failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_infrastructure_services():
    """Test infrastructure services."""
    logger.info("Testing Infrastructure Services")
    
    try:
        from infrastructure.template_engine import TemplateEngine
        from infrastructure.import_manager import ImportManager
        
        template_engine = TemplateEngine()
        import_manager = ImportManager()
        
        logger.info("✅ Infrastructure services loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Infrastructure services failed: {e}")
        return False

def test_ai_provider():
    """Test AI provider with fallback."""
    logger.info("Testing AI Provider")
    
    try:
        from infrastructure.ai_provider import EnhancedOpenAIProvider
        
        # Test without API key (should still initialize)
        ai_provider = EnhancedOpenAIProvider(api_key=None, use_langchain=False)
        
        logger.info("✅ AI provider loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ AI provider failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_domain_models():
    """Test domain models."""
    logger.info("Testing Domain Models")
    
    try:
        from domain.models.generation_context import GenerationContext, BusinessRule
        from domain.models.code_models import GeneratedCode
        
        # Test creating a basic context
        context = GenerationContext(
            file_type="controller",
            entity_name="Policy",
            package_name="com.example.policy",
            language="java",
            framework="springboot", 
            template_content="",
            spec_data={},
            instruction_data={},
            output_path=""
        )
        
        logger.info("✅ Domain models loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Domain models failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Starting Phase 3 Component Testing")
    
    tests = [
        test_domain_models,
        test_infrastructure_services,
        test_domain_services,
        test_ai_provider,
        test_application_services
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            failed += 1
    
    logger.info(f"Phase 3 Testing Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All components ready for Phase 3 integration testing!")
    else:
        logger.warning(f"⚠️ {failed} component(s) need fixing before integration testing")
        
    sys.exit(0 if failed == 0 else 1)
