"""
Fixed imports for testing - resolving relative import issues
"""

import sys
import os

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')

# Add all necessary paths
sys.path.insert(0, src_dir)
sys.path.insert(0, os.path.join(src_dir, 'domain'))
sys.path.insert(0, os.path.join(src_dir, 'domain', 'models'))
sys.path.insert(0, os.path.join(src_dir, 'domain', 'services'))
sys.path.insert(0, os.path.join(src_dir, 'infrastructure'))

# Test individual imports
try:
    from infrastructure.error_handling import ProductionError, ErrorHandler
    print("✅ Infrastructure imports successful")
    
    # Test error handler
    handler = ErrorHandler()
    error = handler.handle_error(Exception("Test"))
    print(f"✅ Error handler working: {error.message}")
    
except Exception as e:
    print(f"❌ Infrastructure import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    import domain.models.generation_context
    print("✅ Domain models import successful")
except Exception as e:
    print(f"❌ Domain models import failed: {e}")

try:
    import domain.services.business_logic_processor
    print("✅ Business logic processor import successful")
except Exception as e:
    print(f"❌ Business logic processor import failed: {e}")

try:
    import domain.services.prompt_builder
    print("✅ Prompt builder import successful")
except Exception as e:
    print(f"❌ Prompt builder import failed: {e}")
