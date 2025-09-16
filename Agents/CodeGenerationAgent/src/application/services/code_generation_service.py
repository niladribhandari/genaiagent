"""Code generation service."""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Use absolute imports to avoid relative import issues
try:
    from core.interfaces import CodeGenerator
    from core.exceptions import CodeGenerationError
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode
    from infrastructure.template_engine import TemplateEngine
    from infrastructure.ai_provider import OpenAIProvider
    from infrastructure.import_manager import ImportManager
except ImportError:
    # Fallback for testing environments
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.append(src_dir)
    
    from core.interfaces import CodeGenerator
    from core.exceptions import CodeGenerationError
    from domain.models.generation_context import GenerationContext
    from domain.models.code_models import GeneratedCode
    from infrastructure.template_engine import TemplateEngine
    from infrastructure.ai_provider import OpenAIProvider
    from infrastructure.import_manager import ImportManager


class CodeGenerationService(CodeGenerator):
    """Main code generation service orchestrating the generation process."""
    
    def __init__(self, 
                 template_engine: TemplateEngine,
                 ai_provider: OpenAIProvider,
                 import_manager: ImportManager):
        self.template_engine = template_engine
        self.ai_provider = ai_provider
        self.import_manager = import_manager
        self.logger = logging.getLogger(__name__)
    
    def generate(self, context: GenerationContext) -> GeneratedCode:
        """Generate code using template and AI enhancement."""
        try:
            self.logger.info(f"Starting code generation for {context.entity_name}")
            
            # Step 1: Generate base code from template
            base_code = self._generate_from_template(context)
            
            # Step 2: Enhance with AI if requested
            if context.use_ai_enhancement:
                enhanced_code = self._enhance_with_ai(base_code, context)
            else:
                enhanced_code = base_code
            
            # Step 3: Process imports
            final_code = self._process_imports(enhanced_code, context)
            
            # Step 4: Create result
            result = GeneratedCode(
                content=final_code,
                language=context.target_language,
                framework=context.framework,
                metadata={
                    'template_used': context.template_path,
                    'ai_enhanced': context.use_ai_enhancement,
                    'entity_name': context.entity_name,
                    'package_name': context.package_name
                }
            )
            
            self.logger.info(f"Code generation completed for {context.entity_name}")
            return result
            
        except Exception as e:
            raise CodeGenerationError(f"Failed to generate code: {str(e)}")
    
    def _generate_from_template(self, context: GenerationContext) -> str:
        """Generate base code from template."""
        if not context.template_path or not Path(context.template_path).exists():
            raise CodeGenerationError(f"Template not found: {context.template_path}")
        
        # Prepare template context
        template_context = self._build_template_context(context)
        
        # Process template
        return self.template_engine.process_template_file(
            context.template_path, 
            template_context
        )
    
    def _enhance_with_ai(self, code: str, context: GenerationContext) -> str:
        """Enhance code using AI provider."""
        try:
            # Generate enhanced version
            enhanced_result = self.ai_provider.generate_code(context)
            
            # If AI generation fails, fall back to template code
            if enhanced_result.content:
                return enhanced_result.content
            else:
                self.logger.warning("AI enhancement failed, using template code")
                return code
                
        except Exception as e:
            self.logger.warning(f"AI enhancement failed: {str(e)}, using template code")
            return code
    
    def _process_imports(self, code: str, context: GenerationContext) -> str:
        """Process and organize imports."""
        try:
            # Detect required imports
            required_imports = self.import_manager.detect_imports(
                code, 
                context.target_language
            )
            
            # Add missing imports
            return self.import_manager.add_missing_imports(code, required_imports)
            
        except Exception as e:
            self.logger.warning(f"Import processing failed: {str(e)}")
            return code
    
    def _build_template_context(self, context: GenerationContext) -> Dict[str, Any]:
        """Build context dictionary for template processing."""
        template_context = {
            'entity_name': context.entity_name,
            'package_name': context.package_name,
            'class_name': self._to_class_name(context.entity_name),
            'variable_name': self._to_variable_name(context.entity_name),
            'fields': [
                {
                    'name': field.name,
                    'type': field.type,
                    'getter_name': f"get{self._to_class_name(field.name)}",
                    'setter_name': f"set{self._to_class_name(field.name)}",
                    'variable_name': self._to_variable_name(field.name)
                }
                for field in context.fields
            ],
            'framework': context.framework,
            'target_language': context.target_language
        }
        
        # Add any additional context
        if context.additional_context:
            template_context.update(context.additional_context)
        
        return template_context
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to ClassName format."""
        return ''.join(word.capitalize() for word in name.replace('_', ' ').split())
    
    def _to_variable_name(self, name: str) -> str:
        """Convert name to variableName format."""
        words = name.replace('_', ' ').split()
        if not words:
            return name
        
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
