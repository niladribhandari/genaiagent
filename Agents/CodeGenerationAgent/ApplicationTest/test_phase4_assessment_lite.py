#!/usr/bin/env python3
"""Phase 4 System Assessment - Analyze current system for optimization opportunities (No external deps)"""

import sys
import os
import time
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
            
        # Code generation performance test
        start_time = time.time()
        try:
            context = GenerationContext(
                file_type="controller",
                entity_name="TestEntity",
                package_name="com.test",
                language="java",
                framework="springboot",
                template_content="",
                spec_data={'paths': {'/test': {'get': {'summary': 'Test endpoint'}}}},
                instruction_data={},
                output_path=""
            )
            
            insights = processor.analyze_context(context)
            prompt = prompt_builder.build_prompt(context)
            
            generation_time = time.time() - start_time
            self.metrics['generation_time_ms'] = generation_time * 1000
            logger.info(f"  📊 Business logic processing: {generation_time * 1000:.2f}ms")
            logger.info(f"  📊 Generated {len(insights.business_rules)} business rules")
            logger.info(f"  📊 Generated prompt length: {len(prompt)} characters")
            
        except Exception as e:
            logger.error(f"  ❌ Generation assessment failed: {e}")
        
    def assess_code_structure(self):
        """Assess current code structure and quality."""
        logger.info("🔍 Assessing Code Structure")
        
        src_path = Path(project_root) / 'src'
        if src_path.exists():
            python_files = list(src_path.rglob("*.py"))
            logger.info(f"  📊 Total Python files: {len(python_files)}")
            
            total_lines = 0
            total_functions = 0
            total_classes = 0
            
            for file_path in python_files:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    total_lines += len(lines)
                    total_functions += content.count('def ')
                    total_classes += content.count('class ')
                except:
                    continue
                    
            self.metrics['total_lines'] = total_lines
            self.metrics['total_functions'] = total_functions
            self.metrics['total_classes'] = total_classes
            
            logger.info(f"  📊 Total lines of code: {total_lines}")
            logger.info(f"  📊 Total functions: {total_functions}")
            logger.info(f"  📊 Total classes: {total_classes}")
            
            if total_lines > 10000:
                self.recommendations.append("Consider code splitting for maintainability")
                
    def assess_scalability_bottlenecks(self):
        """Identify potential scalability bottlenecks."""
        logger.info("🔍 Assessing Scalability Bottlenecks")
        
        bottlenecks = []
        
        # Check for synchronous operations
        src_path = Path(project_root) / 'src'
        if src_path.exists():
            python_files = list(src_path.rglob("*.py"))
            
            # Look for potential blocking operations
            blocking_patterns = {
                'requests.get': 'Synchronous HTTP requests',
                'requests.post': 'Synchronous HTTP requests', 
                'time.sleep': 'Blocking sleep operations',
                'input(': 'Blocking input operations',
                'open(': 'Synchronous file operations'
            }
            
            for pattern, description in blocking_patterns.items():
                count = 0
                for file_path in python_files:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        count += content.count(pattern)
                    except:
                        continue
                if count > 0:
                    bottlenecks.append(f"{description}: {count} occurrences")
                    
        if bottlenecks:
            logger.warning("  ⚠️  Potential scalability bottlenecks found:")
            for bottleneck in bottlenecks:
                logger.warning(f"    - {bottleneck}")
                self.recommendations.append(f"Optimize: {bottleneck}")
        else:
            logger.info("  ✅ No obvious scalability bottlenecks detected")
            
    def assess_caching_opportunities(self):
        """Identify caching opportunities."""
        logger.info("🔍 Assessing Caching Opportunities")
        
        caching_opportunities = [
            "🎯 HIGH IMPACT:",
            "- API specification parsing (YAML/JSON processing)",
            "- Business rule extraction (complex regex operations)", 
            "- Prompt template compilation (string processing)",
            "- AI model responses (for similar inputs)",
            "",
            "🔧 MEDIUM IMPACT:",
            "- Integration pattern detection (pattern matching)",
            "- Code template processing (file I/O)",
            "- Validation rule compilation",
            "- Import dependency resolution"
        ]
        
        logger.info("  💡 Identified caching opportunities:")
        for opportunity in caching_opportunities:
            logger.info(f"    {opportunity}")
            
        self.recommendations.extend([
            "Implement Redis caching layer",
            "Add in-memory caching for frequently accessed data",
            "Cache compiled templates and patterns"
        ])
            
    def assess_error_handling(self):
        """Assess current error handling robustness."""
        logger.info("🔍 Assessing Error Handling Coverage")
        
        src_path = Path(project_root) / 'src'
        if src_path.exists():
            python_files = list(src_path.rglob("*.py"))
            
            total_functions = 0
            error_handled_functions = 0
            exception_types = set()
            
            for file_path in python_files:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Count function definitions
                    total_functions += content.count('def ')
                    
                    # Count try/except blocks
                    try_blocks = content.count('try:')
                    error_handled_functions += try_blocks
                    
                    # Find exception types
                    import re
                    exceptions = re.findall(r'except (\w+)', content)
                    exception_types.update(exceptions)
                    
                except:
                    continue
                    
            if total_functions > 0:
                error_coverage = (error_handled_functions / total_functions) * 100
                self.metrics['error_coverage_percent'] = error_coverage
                logger.info(f"  📊 Error handling coverage: {error_coverage:.1f}%")
                logger.info(f"  📊 Unique exception types handled: {len(exception_types)}")
                
                if error_coverage < 60:
                    self.recommendations.append("🚨 CRITICAL: Improve error handling coverage")
                    logger.warning("  ⚠️  Error handling coverage critically low")
                elif error_coverage < 80:
                    self.recommendations.append("Improve error handling coverage")
                    logger.warning("  ⚠️  Error handling coverage below optimal")
                else:
                    logger.info("  ✅ Good error handling coverage")
                    
    def assess_monitoring_capabilities(self):
        """Assess current monitoring and observability."""
        logger.info("🔍 Assessing Monitoring & Observability")
        
        monitoring_features = {
            "Structured logging": False,
            "Performance metrics": False,
            "Health checks": False,
            "Error tracking": False,
            "Usage analytics": False,
            "Request tracing": False
        }
        
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
                    if 'correlation_id' in content or 'trace_id' in content:
                        monitoring_features["Request tracing"] = True
                        
                except:
                    continue
                    
        logger.info("  📊 Current monitoring capabilities:")
        missing_count = 0
        for feature, available in monitoring_features.items():
            status = "✅" if available else "❌"
            logger.info(f"    {status} {feature}")
            if not available:
                missing_count += 1
                
        if missing_count > 3:
            self.recommendations.append("🚨 CRITICAL: Implement comprehensive monitoring")
        elif missing_count > 1:
            self.recommendations.append("Enhance monitoring capabilities")
                
    def assess_security_posture(self):
        """Assess current security implementation."""
        logger.info("🔍 Assessing Security Posture")
        
        security_checks = {
            "Input validation": False,
            "API key management": False,
            "Rate limiting": False,
            "Authentication": False,
            "Authorization": False,
            "Audit logging": False
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
                    if 'rate_limit' in content.lower():
                        security_checks["Rate limiting"] = True
                    if 'auth' in content.lower():
                        security_checks["Authentication"] = True
                        
                except:
                    continue
                    
        logger.info("  🔒 Current security posture:")
        security_gaps = 0
        for check, implemented in security_checks.items():
            status = "✅" if implemented else "❌"
            logger.info(f"    {status} {check}")
            if not implemented:
                security_gaps += 1
                
        if security_gaps > 3:
            self.recommendations.append("🚨 CRITICAL: Implement comprehensive security measures")
        elif security_gaps > 1:
            self.recommendations.append("Enhance security implementation")
                
    def generate_phase4_roadmap(self):
        """Generate comprehensive Phase 4 roadmap."""
        logger.info("🗺️  Generating Phase 4 Implementation Roadmap")
        
        # Analyze metrics for prioritization
        priorities = []
        
        if self.metrics.get('generation_time_ms', 0) > 500:
            priorities.append("🚀 HIGH: Optimize code generation performance")
            
        if self.metrics.get('error_coverage_percent', 0) < 60:
            priorities.append("🚨 CRITICAL: Improve error handling")
            
        if self.metrics.get('import_time_ms', 0) > 100:
            priorities.append("🔧 MEDIUM: Optimize import performance")
        
        roadmap = [
            "",
            "🎯 PHASE 4 IMPLEMENTATION ROADMAP",
            "=" * 50,
            "",
            "📅 STAGE 4.1: Production Infrastructure (Week 1-2)",
            "- ✅ Performance baseline established",
            "- 🔧 Implement Redis caching layer",
            "- 🔧 Add comprehensive error handling",
            "- 🔧 Implement circuit breaker pattern",
            "- 🔧 Add performance monitoring",
            "",
            "📅 STAGE 4.2: Advanced AI Integration (Week 3-4)",
            "- 🔧 Multi-model AI provider support",
            "- 🔧 Vector embeddings for intelligent matching",
            "- 🔧 Response caching and optimization",
            "- 🔧 Context memory persistence",
            "",
            "📅 STAGE 4.3: User Experience (Week 5-6)",
            "- 🔧 Interactive CLI with rich UI",
            "- 🔧 Web interface development",
            "- 🔧 API endpoints with documentation",
            "- 🔧 Real-time progress indicators",
            "",
            "📅 STAGE 4.4: Enterprise Features (Week 7-8)",
            "- 🔧 Multi-tenant architecture",
            "- 🔧 Team collaboration features",
            "- 🔧 Analytics dashboard",
            "- 🔧 Governance and compliance tools",
            "",
            "🎯 IMMEDIATE PRIORITIES:",
        ]
        
        # Add prioritized recommendations
        for priority in priorities:
            roadmap.append(f"   {priority}")
            
        # Add general recommendations
        roadmap.extend([
            "",
            "📋 OPTIMIZATION OPPORTUNITIES:",
            f"   - Current generation time: {self.metrics.get('generation_time_ms', 0):.2f}ms",
            f"   - Error handling coverage: {self.metrics.get('error_coverage_percent', 0):.1f}%",
            f"   - Code base size: {self.metrics.get('total_lines', 0)} lines",
            "",
            "🚀 SUCCESS TARGETS:",
            "   - Sub-100ms generation time for common operations",
            "   - 95%+ error handling coverage",
            "   - 99.9% uptime with monitoring",
            "   - Enterprise-ready security posture",
        ])
        
        for line in roadmap:
            logger.info(line)
            
        return roadmap
        
    def run_full_assessment(self):
        """Run complete system assessment for Phase 4 planning."""
        logger.info("🚀 PHASE 4: PRODUCTION OPTIMIZATION & ADVANCED FEATURES")
        logger.info("🔍 Starting Comprehensive System Assessment")
        logger.info("=" * 60)
        
        try:
            self.assess_performance_baseline()
            self.assess_code_structure()
            self.assess_scalability_bottlenecks() 
            self.assess_caching_opportunities()
            self.assess_error_handling()
            self.assess_monitoring_capabilities()
            self.assess_security_posture()
            
            roadmap = self.generate_phase4_roadmap()
            
            logger.info("=" * 60)
            logger.info(f"📊 Assessment Complete!")
            logger.info(f"📋 Generated {len(self.recommendations)} optimization recommendations")
            logger.info("🎯 Phase 4 roadmap created - ready for implementation!")
            
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
