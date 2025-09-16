"""Template processing service."""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List

try:
    from src.core.interfaces import TemplateProcessor
    from src.core.exceptions import TemplateProcessingError, FileSystemError
    from src.domain.models.generation_context import GenerationContext
except ImportError:
    from core.interfaces import TemplateProcessor
    from core.exceptions import TemplateProcessingError, FileSystemError
    from domain.models.generation_context import GenerationContext


class TemplateEngine(TemplateProcessor):
    """Implementation of template processing functionality."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.template_cache: Dict[str, str] = {}
    
    def load_template(self, template_path: str) -> str:
        """Load template from file with caching."""
        if template_path in self.template_cache:
            return self.template_cache[template_path]
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.template_cache[template_path] = content
            self.logger.debug(f"Loaded template: {template_path}")
            return content
            
        except FileNotFoundError:
            raise FileSystemError(f"Template file not found: {template_path}")
        except IOError as e:
            raise FileSystemError(f"Error reading template {template_path}: {str(e)}")
    
    def process_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """Process template with context variables."""
        try:
            # Replace simple variables: {{variable}}
            result = self._replace_simple_variables(template_content, context)
            
            # Process conditional blocks: {{#if condition}}...{{/if}}
            result = self._process_conditionals(result, context)
            
            # Process loops: {{#each items}}...{{/each}}
            result = self._process_loops(result, context)
            
            return result
            
        except Exception as e:
            raise TemplateProcessingError(f"Error processing template: {str(e)}")
    
    def process_template_file(self, template_path: str, context: Dict[str, Any]) -> str:
        """Load and process template file."""
        template_content = self.load_template(template_path)
        return self.process_template(template_content, context)
    
    def get_template_variables(self, template_content: str) -> List[str]:
        """Extract all variables used in template."""
        # Find simple variables: {{variable}}
        simple_vars = re.findall(r'\{\{([^#/\s}]+)\}\}', template_content)
        
        # Find conditional variables: {{#if condition}}
        conditional_vars = re.findall(r'\{\{#if\s+([^}]+)\}\}', template_content)
        
        # Find loop variables: {{#each items}}
        loop_vars = re.findall(r'\{\{#each\s+([^}]+)\}\}', template_content)
        
        # Combine and deduplicate
        all_vars = set(simple_vars + conditional_vars + loop_vars)
        return list(all_vars)
    
    def _replace_simple_variables(self, content: str, context: Dict[str, Any]) -> str:
        """Replace {{variable}} with context values."""
        def replace_var(match):
            var_name = match.group(1).strip()
            value = self._get_nested_value(context, var_name)
            return str(value) if value is not None else f"{{{{{var_name}}}}}"
        
        return re.sub(r'\{\{([^#/\s}]+)\}\}', replace_var, content)
    
    def _process_conditionals(self, content: str, context: Dict[str, Any]) -> str:
        """Process {{#if condition}}...{{/if}} blocks."""
        pattern = r'\{\{#if\s+([^}]+)\}\}(.*?)\{\{/if\}\}'
        
        def replace_conditional(match):
            condition = match.group(1).strip()
            block_content = match.group(2)
            
            if self._evaluate_condition(condition, context):
                return self.process_template(block_content, context)
            else:
                return ""
        
        return re.sub(pattern, replace_conditional, content, flags=re.DOTALL)
    
    def _process_loops(self, content: str, context: Dict[str, Any]) -> str:
        """Process {{#each items}}...{{/each}} blocks."""
        pattern = r'\{\{#each\s+([^}]+)\}\}(.*?)\{\{/each\}\}'
        
        def replace_loop(match):
            items_name = match.group(1).strip()
            block_content = match.group(2)
            
            items = self._get_nested_value(context, items_name)
            if not isinstance(items, (list, tuple)):
                return ""
            
            results = []
            for item in items:
                loop_context = context.copy()
                loop_context['this'] = item
                processed_block = self.process_template(block_content, loop_context)
                results.append(processed_block)
            
            return ''.join(results)
        
        return re.sub(pattern, replace_loop, content, flags=re.DOTALL)
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        if '.' not in key:
            return data.get(key)
        
        keys = key.split('.')
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        
        return value
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate conditional expression."""
        condition = condition.strip()
        
        # Simple existence check
        if not any(op in condition for op in ['==', '!=', '>', '<', '>=', '<=']):
            value = self._get_nested_value(context, condition)
            return bool(value)
        
        # Simple equality/inequality checks
        if '==' in condition:
            left, right = condition.split('==', 1)
            left_val = self._get_nested_value(context, left.strip())
            right_val = right.strip().strip('"\'')
            return str(left_val) == right_val
        
        if '!=' in condition:
            left, right = condition.split('!=', 1)
            left_val = self._get_nested_value(context, left.strip())
            right_val = right.strip().strip('"\'')
            return str(left_val) != right_val
        
        # Default to false for complex conditions
        return False
    
    def process(self, template: str, variables: Dict[str, Any]) -> str:
        """Process template with provided variables (TemplateProcessor interface)."""
        return self.process_template(template, variables)
    
    def supports_framework(self, framework: str) -> bool:
        """Check if this processor supports the given framework."""
        # This template engine supports all frameworks with basic templating
        return True
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self.template_cache.clear()
        self.logger.debug("Template cache cleared")
