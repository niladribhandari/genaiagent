"""Enhanced AI provider service with LangChain integration for sophisticated code generation."""

import json
import logging
import requests
import os
import sys
from typing import Dict, Any, List, Optional, Union
from dataclasses import asdict
import asyncio

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from src.core.interfaces import AIProvider
    from src.core.exceptions import AIProviderError
    from src.domain.models.generation_context import GenerationContext
    from src.domain.models.code_models import GeneratedCode
    from src.domain.services.prompt_builder import AdvancedPromptBuilder
except ImportError:
    try:
        from core.interfaces import AIProvider
        from core.exceptions import AIProviderError
        from domain.models.generation_context import GenerationContext
        from domain.models.code_models import GeneratedCode
        from domain.services.prompt_builder import AdvancedPromptBuilder
    except ImportError:
        # Fallback classes
        class AIProvider:
            pass
        class AIProviderError(Exception):
            pass

# LangChain imports with fallback
try:
    from langchain_community.llms import OpenAI
    from langchain_community.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.callbacks.manager import CallbackManager
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        # Fallback to old imports if community package not available
        from langchain.llms import OpenAI
        from langchain.chat_models import ChatOpenAI
        from langchain.schema import HumanMessage, SystemMessage, AIMessage
        from langchain.callbacks.base import BaseCallbackHandler
        from langchain.callbacks.manager import CallbackManager
        from langchain.memory import ConversationBufferWindowMemory
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        from langchain_core.runnables import RunnablePassthrough
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        logging.warning("LangChain not available. Falling back to direct API calls.")


logger = logging.getLogger(__name__)


class CodeGenerationCallbackHandler(BaseCallbackHandler if LANGCHAIN_AVAILABLE else object):
    """Custom callback handler for code generation monitoring."""
    
    def __init__(self):
        self.generations = []
        self.errors = []
        self.token_usage = {}
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts running."""
        logger.info(f"Starting LLM generation with {len(prompts)} prompt(s)")
        
    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM ends running."""
        if hasattr(response, 'llm_output') and response.llm_output:
            self.token_usage = response.llm_output.get('token_usage', {})
        logger.info(f"LLM generation completed. Token usage: {self.token_usage}")
        
    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs) -> None:
        """Called when LLM errors."""
        self.errors.append(str(error))
        logger.error(f"LLM error: {error}")


class EnhancedOpenAIProvider(AIProvider):
    """Enhanced OpenAI provider with LangChain integration and sophisticated prompting."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4", use_langchain: bool = True):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.logger = logging.getLogger(__name__)
        
        # Initialize LangChain components if available
        if self.use_langchain:
            self._initialize_langchain()
        
        # Initialize advanced prompt builder
        self.prompt_builder = AdvancedPromptBuilder()
        
        # Initialize conversation memory for context
        if self.use_langchain:
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                k=5,  # Keep last 5 exchanges
                return_messages=True
            )
    
    def _initialize_langchain(self):
        """Initialize LangChain components."""
        try:
            if not self.api_key:
                raise AIProviderError("OpenAI API key not provided")
            
            # Initialize callback handler
            self.callback_handler = CodeGenerationCallbackHandler()
            callback_manager = CallbackManager([self.callback_handler])
            
            # Initialize Chat model
            self.chat_model = ChatOpenAI(
                openai_api_key=self.api_key,
                model_name=self.model,
                temperature=0.1,  # Low temperature for consistent code generation
                max_tokens=4000,
                callback_manager=callback_manager,
                verbose=True
            )
            
            # Initialize standard LLM for simple tasks
            self.llm = OpenAI(
                openai_api_key=self.api_key,
                model_name="gpt-3.5-turbo-instruct",
                temperature=0.1,
                max_tokens=2000,
                callback_manager=callback_manager
            )
            
            logger.info(f"Initialized LangChain with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Error initializing LangChain: {e}")
            self.use_langchain = False
            
    def generate_code(self, context: GenerationContext) -> GeneratedCode:
        """Generate code using enhanced AI with sophisticated prompting."""
        try:
            if self.use_langchain:
                return self._generate_code_with_langchain(context)
            else:
                return self._generate_code_direct(context)
                
        except Exception as e:
            raise AIProviderError(f"Error generating code: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if AI provider is available."""
        return self.api_key is not None
    
    def _generate_code_with_langchain(self, context: GenerationContext) -> GeneratedCode:
        """Generate code using LangChain with advanced prompting."""
        try:
            # Build sophisticated prompt using AdvancedPromptBuilder
            enhanced_prompt = self.prompt_builder.build_prompt(context)
            
            # Create system message for code generation context
            system_message = SystemMessage(
                content="""You are an expert software architect and developer with deep knowledge of enterprise patterns, 
                best practices, and modern frameworks. You generate production-ready, well-structured code that follows 
                SOLID principles, includes proper error handling, comprehensive validation, and enterprise-grade patterns.
                
                Always generate complete, compilable code with:
                1. Proper imports and package declarations
                2. Comprehensive business logic implementation
                3. Robust error handling and validation
                4. Enterprise patterns (Circuit breaker, Retry, etc.) where needed
                5. Proper documentation and comments
                6. Performance optimizations
                7. Security considerations
                8. Testable, maintainable structure"""
            )
            
            # Create human message with the enhanced prompt
            human_message = HumanMessage(content=enhanced_prompt)
            
            # Generate code using chat model
            messages = [system_message, human_message]
            
            # Add conversation history if available
            if hasattr(self, 'memory') and self.memory.chat_memory.messages:
                # Insert memory messages before the current human message
                memory_messages = self.memory.chat_memory.messages[-4:]  # Last 2 exchanges
                messages = [system_message] + memory_messages + [human_message]
            
            response = self.chat_model(messages)
            
            # Extract generated code
            generated_content = self._extract_code_from_langchain_response(response)
            
            # Save to memory for context
            if hasattr(self, 'memory'):
                self.memory.save_context(
                    {"input": f"Generate {context.file_type} for {context.entity_name}"},
                    {"output": generated_content[:500] + "..." if len(generated_content) > 500 else generated_content}
                )
            
            # Get token usage from callback
            token_usage = {}
            if hasattr(self, 'callback_handler'):
                token_usage = self.callback_handler.token_usage
            
            return GeneratedCode(
                content=generated_content,
                language=context.language,
                framework=context.framework,
                metadata={
                    'model': self.model,
                    'approach': 'langchain_enhanced',
                    'prompt_tokens': token_usage.get('prompt_tokens', 0),
                    'completion_tokens': token_usage.get('completion_tokens', 0),
                    'total_tokens': token_usage.get('total_tokens', 0),
                    'complexity_score': getattr(context, 'complexity_score', 0),
                    'business_rules_count': len(context.business_rules) if context.business_rules else 0,
                    'integration_patterns_count': len(context.integration_patterns) if context.integration_patterns else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Error in LangChain code generation: {e}")
            # Fallback to direct API call
            return self._generate_code_direct(context)
    
    def _generate_code_direct(self, context: GenerationContext) -> GeneratedCode:
        """Generate code using direct API call as fallback."""
        try:
            prompt = self.prompt_builder.build_prompt(context)
            response = self._call_api(prompt)
            
            generated_content = self._extract_code_from_response(response)
            
            return GeneratedCode(
                content=generated_content,
                language=context.language,
                framework=context.framework,
                metadata={
                    'model': self.model,
                    'approach': 'direct_api',
                    'prompt_tokens': response.get('usage', {}).get('prompt_tokens'),
                    'completion_tokens': response.get('usage', {}).get('completion_tokens')
                }
            )
            
        except Exception as e:
            raise AIProviderError(f"Error in direct API code generation: {str(e)}")
    
    def enhance_code(self, code: str, enhancement_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Enhance existing code with sophisticated AI analysis."""
        try:
            if self.use_langchain:
                return self._enhance_code_with_langchain(code, enhancement_type, context or {})
            else:
                return self._enhance_code_direct(code, enhancement_type, context or {})
                
        except Exception as e:
            raise AIProviderError(f"Error enhancing code: {str(e)}")
    
    def _enhance_code_with_langchain(self, code: str, enhancement_type: str, context: Dict[str, Any]) -> str:
        """Enhance code using LangChain with context-aware prompting."""
        
        enhancement_prompts = {
            "business_logic": """Enhance this code by implementing comprehensive business logic and rules:
            
Original Code:
{code}

Context: {context}

Add sophisticated business rule processing, validation logic, and enterprise patterns. 
Ensure the code handles complex business scenarios, implements proper validation,
and includes comprehensive error handling for business rule violations.""",

            "integration_patterns": """Enhance this code with enterprise integration patterns:
            
Original Code:
{code}

Context: {context}

Add circuit breaker patterns, retry logic, external service integration,
resilience patterns, and comprehensive error handling for distributed systems.
Include proper logging, monitoring, and observability.""",

            "error_handling": """Add comprehensive enterprise-grade error handling:
            
Original Code:  
{code}

Context: {context}

Implement proper exception hierarchies, custom exceptions, global error handling,
logging strategies, and recovery mechanisms. Include circuit breakers for external calls.""",

            "performance": """Optimize this code for enterprise performance:
            
Original Code:
{code}

Context: {context}

Add caching strategies, async processing where appropriate, connection pooling,
resource management, and performance monitoring. Optimize for scalability.""",

            "security": """Enhance this code with enterprise security patterns:
            
Original Code:
{code}

Context: {context}

Add input validation, sanitization, authentication checks, authorization logic,
secure coding practices, and protection against common vulnerabilities."""
        }
        
        prompt_template = enhancement_prompts.get(enhancement_type, enhancement_prompts["business_logic"])
        
        # Format prompt with code and context
        formatted_prompt = prompt_template.format(
            code=code,
            context=json.dumps(context, indent=2)
        )
        
        # Create messages
        system_message = SystemMessage(
            content="You are an expert software architect specializing in enterprise code enhancement. "
                   "Generate production-ready, well-structured code improvements that follow best practices."
        )
        human_message = HumanMessage(content=formatted_prompt)
        
        # Generate enhanced code
        response = self.chat_model([system_message, human_message])
        return self._extract_code_from_langchain_response(response)
    
    def _enhance_code_direct(self, code: str, enhancement_type: str, context: Dict[str, Any]) -> str:
        """Enhance code using direct API call."""
        prompt = self._build_enhancement_prompt(code, enhancement_type, context)
        response = self._call_api(prompt)
        return self._extract_code_from_response(response)
    
    def validate_code(self, code: str, language: str, context: Optional[GenerationContext] = None) -> Dict[str, Any]:
        """Validate code quality with sophisticated analysis."""
        try:
            if self.use_langchain:
                return self._validate_code_with_langchain(code, language, context)
            else:
                return self._validate_code_direct(code, language)
                
        except Exception as e:
            raise AIProviderError(f"Error validating code: {str(e)}")
    
    def _validate_code_with_langchain(self, code: str, language: str, context: Optional[GenerationContext] = None) -> Dict[str, Any]:
        """Validate code using LangChain with comprehensive analysis."""
        
        validation_prompt = f"""
        Perform a comprehensive enterprise-grade analysis of this {language} code:
        
        Code to analyze:
        ```{language}
        {code}
        ```
        
        Context: {json.dumps(asdict(context), indent=2) if context else 'No additional context'}
        
        Provide a detailed analysis covering:
        1. Code structure and organization (0-10)
        2. Business logic implementation quality (0-10)
        3. Error handling and resilience patterns (0-10)
        4. Security considerations (0-10)
        5. Performance and scalability (0-10)
        6. Maintainability and testability (0-10)
        7. Enterprise patterns usage (0-10)
        8. Framework best practices (0-10)
        
        Identify:
        - Critical issues that must be fixed
        - Potential improvements
        - Security vulnerabilities
        - Performance bottlenecks
        - Missing enterprise patterns
        - Code smells and anti-patterns
        
        Format response as valid JSON:
        {{
            "overall_score": 8.5,
            "category_scores": {{
                "structure": 9,
                "business_logic": 8,
                "error_handling": 7,
                "security": 8,
                "performance": 9,
                "maintainability": 8,
                "enterprise_patterns": 7,
                "best_practices": 8
            }},
            "critical_issues": ["issue1", "issue2"],
            "improvements": ["improvement1", "improvement2"],
            "security_issues": ["security_issue1"],
            "performance_issues": ["perf_issue1"],
            "missing_patterns": ["pattern1", "pattern2"],
            "strengths": ["strength1", "strength2"],
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        system_message = SystemMessage(
            content="You are a senior software architect and code review expert with deep knowledge of "
                   "enterprise patterns, security best practices, and performance optimization."
        )
        human_message = HumanMessage(content=validation_prompt)
        
        response = self.chat_model([system_message, human_message])
        return self._parse_validation_response(response.content)
    
    def _validate_code_direct(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code using direct API call."""
        prompt = self._build_validation_prompt(code, language)
        response = self._call_api(prompt)
        return self._parse_validation_response(response['choices'][0]['message']['content'])
    
    def _extract_code_from_langchain_response(self, response) -> str:
        """Extract code content from LangChain response."""
        try:
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Remove code block markers if present
            if '```' in content:
                lines = content.split('\n')
                code_lines = []
                in_code_block = False
                
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        code_lines.append(line)
                
                if code_lines:
                    content = '\n'.join(code_lines)
            
            return content.strip()
            
        except Exception as e:
            raise AIProviderError(f"Error extracting code from LangChain response: {str(e)}")
    
    def analyze_business_requirements(self, spec_data: Dict[str, Any], instruction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business requirements using AI to extract patterns and rules."""
        try:
            analysis_prompt = f"""
            Analyze these API specifications and instructions to extract business requirements:
            
            API Specification:
            {json.dumps(spec_data, indent=2)}
            
            Instructions:
            {json.dumps(instruction_data, indent=2)}
            
            Extract and identify:
            1. Business rules and validation requirements
            2. Integration patterns needed
            3. Complexity factors
            4. Performance requirements
            5. Security considerations
            6. Enterprise patterns required
            
            Format as JSON:
            {{
                "business_rules": [
                    {{"name": "rule_name", "description": "rule_desc", "category": "validation|calculation|workflow"}},
                ],
                "integration_patterns": [
                    {{"type": "circuit_breaker|retry|caching", "reason": "why_needed"}},
                ],
                "complexity_score": 1-10,
                "performance_requirements": ["req1", "req2"],
                "security_considerations": ["consideration1"],
                "enterprise_patterns": ["pattern1", "pattern2"]
            }}
            """
            
            if self.use_langchain:
                system_message = SystemMessage(
                    content="You are a business analyst and software architect expert at extracting "
                           "business requirements from technical specifications."
                )
                human_message = HumanMessage(content=analysis_prompt)
                response = self.chat_model([system_message, human_message])
                return self._parse_json_response(response.content)
            else:
                response = self._call_api(analysis_prompt)
                return self._parse_json_response(response['choices'][0]['message']['content'])
                
        except Exception as e:
            logger.error(f"Error analyzing business requirements: {e}")
            return {
                "business_rules": [],
                "integration_patterns": [],
                "complexity_score": 1,
                "performance_requirements": [],
                "security_considerations": [],
                "enterprise_patterns": []
            }
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from AI with error handling."""
        try:
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            
            # Fallback
            return {}
            
        except json.JSONDecodeError as e:
            logger.warning(f"Error parsing JSON response: {e}")
            return {}
    
    # Keep existing methods from original implementation
    def _build_enhancement_prompt(self, code: str, enhancement_type: str, context: Dict[str, Any]) -> str:
        """Build prompt for code enhancement."""
        prompts = {
            "logging": f"Add comprehensive logging to this {context.get('language', 'Java')} code:\n\n{code}\n\nAdd structured logging with proper levels, context, and performance monitoring.",
            "error_handling": f"Implement enterprise-grade error handling:\n\n{code}\n\nAdd custom exceptions, global error handling, circuit breakers, and recovery mechanisms.",
            "validation": f"Add comprehensive validation logic:\n\n{code}\n\nImplement business rule validation, input sanitization, and proper error responses.",
            "documentation": f"Add comprehensive documentation:\n\n{code}\n\nInclude API documentation, business logic explanation, and usage examples.",
            "optimization": f"Optimize for enterprise performance:\n\n{code}\n\nAdd caching, async processing, resource management, and performance monitoring."
        }
        
        return prompts.get(enhancement_type, f"Enhance this code:\n\n{code}")
    
    def _build_validation_prompt(self, code: str, language: str) -> str:
        """Build comprehensive validation prompt."""
        return f"""
        Perform enterprise-grade code analysis on this {language} code:
        
        {code}
        
        Analyze for:
        1. Code structure and organization (1-10)
        2. Business logic implementation (1-10)
        3. Error handling and resilience (1-10)
        4. Security best practices (1-10)
        5. Performance considerations (1-10)
        6. Enterprise patterns usage (1-10)
        7. Maintainability (1-10)
        8. Framework best practices (1-10)
        
        Provide detailed JSON response with scores, issues, and recommendations.
        """
    
    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Make direct API call to OpenAI."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.1
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60  # Increased timeout for complex prompts
        )
        
        if response.status_code != 200:
            raise AIProviderError(f"API call failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    def _extract_code_from_response(self, response: Dict[str, Any]) -> str:
        """Extract code content from API response."""
        try:
            content = response['choices'][0]['message']['content']
            
            # Remove code block markers if present
            if content.startswith('```'):
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1])
            
            return content.strip()
            
        except (KeyError, IndexError) as e:
            raise AIProviderError(f"Invalid API response format: {str(e)}")
    
    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse comprehensive validation response."""
        try:
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.warning(f"Error parsing validation response: {e}")
            return {
                "overall_score": 7,
                "category_scores": {},
                "critical_issues": [],
                "improvements": [],
                "security_issues": [],
                "performance_issues": [],
                "missing_patterns": [],
                "strengths": [],
                "recommendations": ["Manual review recommended"]
            }


# For backward compatibility, keep the original class name
OpenAIProvider = EnhancedOpenAIProvider


class AnthropicProvider(AIProvider):
    """Anthropic Claude API implementation."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
        self.logger = logging.getLogger(__name__)
    
    def generate_code(self, context: GenerationContext) -> GeneratedCode:
        """Generate code using Anthropic API."""
        # Implementation similar to OpenAI but using Anthropic's API
        raise AIProviderError("Anthropic provider not fully implemented yet")
    
    def enhance_code(self, code: str, enhancement_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Enhance existing code."""
        raise AIProviderError("Anthropic provider not fully implemented yet")
    
    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code quality and structure."""
        raise AIProviderError("Anthropic provider not fully implemented yet")
