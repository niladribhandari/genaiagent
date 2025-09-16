#!/usr/bin/env python3
"""Simple test for context enrichment service without init imports"""

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

logger = logging.getLogger("ContextEnrichmentTest")

def test_context_enrichment_directly():
    """Test context enrichment service directly without going through problematic imports."""
    logger.info("Testing Context Enrichment Service Directly")
    
    try:
        # Import each component directly
        import importlib.util
        
        # Import the service module directly
        service_path = os.path.join(src_dir, 'application', 'services', 'context_enrichment_service.py')
        spec = importlib.util.spec_from_file_location("context_enrichment_service", service_path)
        service_module = importlib.util.module_from_spec(spec)
        
        # Bypass the __init__ import by setting path first
        sys.modules['context_enrichment_service'] = service_module
        spec.loader.exec_module(service_module)
        
        # Get the class
        ContextEnrichmentService = service_module.ContextEnrichmentService
        
        # Import domain models directly
        from domain.models.generation_context import GenerationContext
        
        # Create service
        service = ContextEnrichmentService(ai_provider=None)
        
        # Test context enrichment
        test_context = GenerationContext(
            file_type="controller",
            entity_name="Policy",
            package_name="com.example.policy",
            language="java", 
            framework="springboot",
            template_content="",
            spec_data={'paths': {'/policies': {'post': {'summary': 'Create policy'}}}},
            instruction_data={},
            output_path=""
        )
        
        enriched = service.enrich_context(test_context)
        logger.info(f"Context enrichment completed: {len(enriched.business_rules)} business rules added")
        
        logger.info("✅ Context enrichment service working directly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Context enrichment service failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Starting Context Enrichment Service Test")
    
    if test_context_enrichment_directly():
        logger.info("🎉 Context Enrichment Service test passed!")
        sys.exit(0)
    else:
        logger.error("❌ Context Enrichment Service test failed")
        sys.exit(1)
