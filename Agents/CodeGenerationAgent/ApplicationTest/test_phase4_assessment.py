#!/usr/bin/env python3
"""Phase 4 System Assessment - Analyze current system for optimization opportunities"""

import sys
import os
import time
import psutil
import logging
from pathlib import Path
from typing import Dict, List, Any

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

logger = logging.getLogger("Phase4Assessment")

class SystemAssessment:
    """Assess current system for Phase 4 optimization opportunities."""
    
    def __init__(self):
        self.metrics = {}
        self.recommendations = []
        
    def assess_performance_baseline(self):
        """Establish performance baseline for Phase 4 improvements."""
        logger.info("🔍 Assessing Performance Baseline")
        
        # Memory usage
        process = psutil.Process()
        self.metrics['memory_mb'] = process.memory_info().rss / 1024 / 1024
        
        # Import time assessment
        start_time = time.time()
        try:
            from domain.models.generation_context import GenerationContext
            from domain.services.business_logic_processor import BusinessLogicProcessor
            from domain.services.prompt_builder import AdvancedPromptBuilder
            import_time = time.time() - start_time
            self.metrics['import_time_ms'] = import_time * 1000
            logger.info(f"  📊 Core imports: {import_time * 1000:.2f}ms")
        except Exception as e:
            logger.error(f"  ❌ Import assessment failed: {e}")
            
        # Component initialization time
        start_time = time.time()
        try:
            processor = BusinessLogicProcessor()
            prompt_builder = AdvancedPromptBuilder()
            init_time = time.time() - start_time
            self.metrics['init_time_ms'] = init_time * 1000
            logger.info(f"  📊 Component initialization: {init_time * 1000:.2f}ms")
        except Exception as e:
            logger.error(f"  ❌ Initialization assessment failed: {e}")
            
        logger.info(f"  📊 Memory usage: {self.metrics.get('memory_mb', 0):.2f}MB")
        
    def assess_scalability_bottlenecks(self):
        """Identify potential scalability bottlenecks."""
        logger.info("🔍 Assessing Scalability Bottlenecks")
        
        bottlenecks = []
        
        # Check for synchronous operations
        src_path = Path(project_root) / 'src'
        if src_path.exists():
            python_files = list(src_path.rglob("*.py"))
            logger.info(f"  📊 Total Python files: {len(python_files)}")
            
            # Look for potential blocking operations
            blocking_patterns = ['requests.get', 'requests.post', 'time.sleep', 'input(']
            for pattern in blocking_patterns:
                count = 0
                for file_path in python_files:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        count += content.count(pattern)
                    except:
                        continue
                if count > 0:
                    bottlenecks.append(f"{pattern}: {count} occurrences")
                    
        if bottlenecks:
            logger.warning("  ⚠️  Potential blocking operations found:")
            for bottleneck in bottlenecks:
                logger.warning(f"    - {bottleneck}")
                self.recommendations.append(f"Optimize blocking operation: {bottleneck}")
        else:
            logger.info("  ✅ No obvious blocking operations detected")
            
    def assess_caching_opportunities(self):
        """Identify caching opportunities."""
        logger.info("🔍 Assessing Caching Opportunities")
        
        caching_opportunities = [
            "API specification parsing (expensive YAML/JSON parsing)",
            "Business rule extraction (complex pattern matching)",
            "Prompt template compilation (string processing)",
            "AI model responses (for similar inputs)",
            "Integration pattern detection (regex-heavy operations)",
            "Code template processing (file I/O operations)"
        ]
        
        logger.info("  💡 Identified caching opportunities:")
        for opportunity in caching_opportunities:
            logger.info(f"    - {opportunity}")
            self.recommendations.append(f"Implement caching for: {opportunity}")
            
    def assess_error_handling(self):
        """Assess current error handling robustness."""
        logger.info("🔍 Assessing Error Handling")
        
        # Look for try/except patterns
        src_path = Path(project_root) / 'src'
        if src_path.exists():
            python_files = list(src_path.rglob("*.py"))
            
            total_functions = 0
            error_handled_functions = 0
            
            for file_path in python_files:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Count function definitions
                    total_functions += content.count('def ')
                    
                    # Count try/except blocks
                    error_handled_functions += content.count('try:')
                    
                except:
                    continue
                    
            if total_functions > 0:
                error_coverage = (error_handled_functions / total_functions) * 100
                self.metrics['error_coverage_percent'] = error_coverage
                logger.info(f"  📊 Error handling coverage: {error_coverage:.1f}%")
                
                if error_coverage < 80:
                    self.recommendations.append("Improve error handling coverage")
                    logger.warning("  ⚠️  Error handling coverage below 80%")
                else:
                    logger.info("  ✅ Good error handling coverage")
                    
    def assess_monitoring_capabilities(self):
        """Assess current monitoring and observability."""
        logger.info("🔍 Assessing Monitoring Capabilities")
        
        monitoring_features = {
            "Structured logging": False,
            "Performance metrics": False,
            "Health checks": False,
            "Error tracking": False,
            "Usage analytics": False
        }
        
        # Check for logging usage
        src_path = Path(project_root) / 'src'
        if src_path.exists():
            python_files = list(src_path.rglob("*.py"))
            
            for file_path in python_files:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    if 'logger.' in content or 'logging.' in content:
                        monitoring_features["Structured logging"] = True
                    if 'time.time()' in content or 'perf_counter' in content:
                        monitoring_features["Performance metrics"] = True
                    if '/health' in content or 'health_check' in content:
                        monitoring_features["Health checks"] = True
                        
                except:
                    continue
                    
        logger.info("  📊 Current monitoring capabilities:")
        for feature, available in monitoring_features.items():
            status = "✅" if available else "❌"
            logger.info(f"    {status} {feature}")
            if not available:
                self.recommendations.append(f"Implement {feature}")
                
    def assess_security_posture(self):
        """Assess current security implementation."""
        logger.info("🔍 Assessing Security Posture")
        
        security_checks = {
            "Input validation": False,
            "API key management": False,
            "SQL injection protection": False,
            "XSS protection": False,
            "Rate limiting": False,
            "Authentication": False
        }
        
        src_path = Path(project_root) / 'src'
        if src_path.exists():
            python_files = list(src_path.rglob("*.py"))
            
            for file_path in python_files:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    if 'validate' in content.lower() or 'sanitize' in content.lower():
                        security_checks["Input validation"] = True
                    if 'api_key' in content.lower() or 'OPENAI_API_KEY' in content:
                        security_checks["API key management"] = True
                    if 'sqlalchemy' in content or 'prepared' in content:
                        security_checks["SQL injection protection"] = True
                        
                except:
                    continue
                    
        logger.info("  🔒 Current security posture:")
        for check, implemented in security_checks.items():
            status = "✅" if implemented else "❌"
            logger.info(f"    {status} {check}")
            if not implemented:
                self.recommendations.append(f"Implement {check}")
                
    def generate_phase4_recommendations(self):
        """Generate comprehensive Phase 4 recommendations."""
        logger.info("🎯 Generating Phase 4 Recommendations")
        
        # Performance recommendations
        if self.metrics.get('import_time_ms', 0) > 100:
            self.recommendations.append("Optimize import times with lazy loading")
            
        if self.metrics.get('memory_mb', 0) > 100:
            self.recommendations.append("Implement memory optimization strategies")
            
        # Priority recommendations
        priority_recommendations = [
            "🚀 HIGH PRIORITY:",
            "- Implement Redis caching layer for expensive operations",
            "- Add comprehensive performance monitoring",
            "- Implement circuit breaker pattern for AI API calls",
            "- Add input validation and security middleware",
            "",
            "🔧 MEDIUM PRIORITY:",
            "- Implement async/await for I/O operations", 
            "- Add health check endpoints",
            "- Implement structured logging with correlation IDs",
            "- Add rate limiting for API endpoints",
            "",
            "📈 OPTIMIZATION OPPORTUNITIES:",
            "- Batch processing for multiple code generations",
            "- Template compilation caching",
            "- AI response caching for similar inputs",
            "- Parallel processing for independent operations"
        ]
        
        logger.info("📋 Phase 4 Implementation Priorities:")
        for rec in priority_recommendations:
            logger.info(f"  {rec}")
            
        return self.recommendations
        
    def run_full_assessment(self):
        """Run complete system assessment for Phase 4 planning."""
        logger.info("🚀 Starting Phase 4 System Assessment")
        logger.info("=" * 60)
        
        try:
            self.assess_performance_baseline()
            self.assess_scalability_bottlenecks()
            self.assess_caching_opportunities()
            self.assess_error_handling()
            self.assess_monitoring_capabilities()
            self.assess_security_posture()
            
            recommendations = self.generate_phase4_recommendations()
            
            logger.info("=" * 60)
            logger.info(f"📊 Assessment Complete: {len(recommendations)} recommendations generated")
            logger.info("🎯 Ready to proceed with Phase 4 implementation!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Assessment failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main assessment function."""
    assessor = SystemAssessment()
    success = assessor.run_full_assessment()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
