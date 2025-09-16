#!/usr/bin/env python3
"""Test Runner for Enhanced CodeGenerationAgent - ApplicationTest Suite"""

import sys
import os
import subprocess
import logging
from pathlib import Path

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.append(src_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("TestRunner")

def run_test(test_file):
    """Run a single test file."""
    logger.info(f"🧪 Running {test_file}")
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, 
                              cwd=current_dir)
        if result.returncode == 0:
            logger.info(f"✅ {test_file} PASSED")
            return True
        else:
            logger.error(f"❌ {test_file} FAILED")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ {test_file} ERROR: {e}")
        return False

def main():
    """Run all test files."""
    logger.info("🚀 Starting Enhanced CodeGenerationAgent Test Suite")
    logger.info("=" * 60)
    
    # Test files in order of complexity
    test_files = [
        "test_phase3_direct.py",           # Component tests
        "test_context_enrichment.py",     # Context enrichment tests
        "test_phase3_integration.py",     # Main integration test
    ]
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        test_path = os.path.join(current_dir, test_file)
        if os.path.exists(test_path):
            if run_test(test_file):
                passed += 1
            else:
                failed += 1
        else:
            logger.warning(f"⚠️  Test file {test_file} not found")
    
    logger.info("-" * 60)
    logger.info(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All tests PASSED! Enhanced system is ready for production.")
    else:
        logger.error(f"💥 {failed} test(s) FAILED. Please check the issues above.")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
