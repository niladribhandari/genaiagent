"""
OpenAI-powered Issue Processor
Enhances compilation issues with AI analysis and suggestions
"""

import os
import json
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import openai

from ..models.compilation_issue import (
    CompilationIssue, IssueSuggestion, IssueCategory, 
    IssueSeverity, IssueLocation
)


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI integration."""
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.3
    timeout: int = 30


class CompilationIssueProcessor:
    """
    Processes compilation issues using OpenAI to provide intelligent analysis,
    categorization, and fix suggestions.
    """
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI configuration
        if config:
            self.config = config
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            self.config = OpenAIConfig(api_key=api_key)
        
        # Initialize OpenAI client
        try:
            openai.api_key = self.config.api_key
            self.client = openai
            self.logger.info("OpenAI client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
        
        # Issue categorization patterns
        self.category_patterns = {
            IssueCategory.SYNTAX: [
                r"syntax error", r"unexpected token", r"invalid syntax",
                r"illegal character", r"missing semicolon", r"unclosed"
            ],
            IssueCategory.TYPE: [
                r"type mismatch", r"cannot convert", r"incompatible types",
                r"undefined symbol", r"cannot resolve symbol"
            ],
            IssueCategory.IMPORT: [
                r"cannot find symbol", r"package .* does not exist",
                r"import .* cannot be resolved", r"class not found"
            ],
            IssueCategory.DEPENDENCY: [
                r"dependency", r"missing artifact", r"could not resolve",
                r"repository", r"version conflict"
            ]
        }
    
    async def process_issues(self, issues: List[CompilationIssue], 
                           project_context: Optional[Dict[str, Any]] = None) -> List[CompilationIssue]:
        """
        Process a list of compilation issues with OpenAI enhancement.
        
        Args:
            issues: List of compilation issues to process
            project_context: Optional context about the project
            
        Returns:
            List of enhanced compilation issues with AI suggestions
        """
        self.logger.info(f"Processing {len(issues)} compilation issues with OpenAI")
        
        enhanced_issues = []
        
        for issue in issues:
            try:
                # First categorize the issue
                self._categorize_issue(issue)
                
                # Then enhance with OpenAI
                enhanced_issue = await self._enhance_issue_with_openai(issue, project_context)
                enhanced_issues.append(enhanced_issue)
                
            except Exception as e:
                self.logger.warning(f"Failed to process issue {issue.id}: {e}")
                # Return original issue if processing fails
                enhanced_issues.append(issue)
        
        self.logger.info(f"Successfully processed {len(enhanced_issues)} issues")
        return enhanced_issues
    
    def _categorize_issue(self, issue: CompilationIssue) -> None:
        """Categorize an issue based on its message."""
        message_lower = issue.message.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    issue.category = category
                    return
        
        # Default to compilation category
        issue.category = IssueCategory.COMPILATION
    
    async def _enhance_issue_with_openai(self, issue: CompilationIssue,
                                       project_context: Optional[Dict[str, Any]] = None) -> CompilationIssue:
        """Enhance a single issue with OpenAI analysis."""
        try:
            # Prepare the prompt
            prompt = self._create_analysis_prompt(issue, project_context)
            
            # Call OpenAI API
            response = await self._call_openai_api(prompt)
            
            # Parse the response
            ai_analysis = self._parse_openai_response(response)
            
            # Update the issue with AI enhancements
            if ai_analysis:
                issue.ai_processed = True
                issue.ai_summary = ai_analysis.get("summary")
                
                # Add suggestions
                suggestions_data = ai_analysis.get("suggestions", [])
                for suggestion_data in suggestions_data:
                    suggestion = IssueSuggestion(
                        description=suggestion_data.get("description", ""),
                        fix_type=suggestion_data.get("fix_type", "manual"),
                        confidence=suggestion_data.get("confidence", 0.5),
                        code_snippet=suggestion_data.get("code_snippet"),
                        explanation=suggestion_data.get("explanation"),
                        related_links=suggestion_data.get("related_links", [])
                    )
                    issue.ai_suggestions.append(suggestion)
                
                # Update category if AI suggests a better one
                ai_category = ai_analysis.get("category")
                if ai_category:
                    try:
                        issue.category = IssueCategory(ai_category)
                    except ValueError:
                        pass  # Keep original category if AI suggestion is invalid
            
            return issue
            
        except Exception as e:
            self.logger.warning(f"OpenAI enhancement failed for issue {issue.id}: {e}")
            return issue
    
    def _create_analysis_prompt(self, issue: CompilationIssue,
                              project_context: Optional[Dict[str, Any]] = None) -> str:
        """Create a detailed prompt for OpenAI analysis."""
        
        context_info = ""
        if project_context:
            project_type = project_context.get("project_type", "Unknown")
            build_tool = project_context.get("build_tool", "Unknown")
            context_info = f"\nProject Type: {project_type}\nBuild Tool: {build_tool}\n"
        
        prompt = f"""
You are an expert software developer and code analyst. Analyze the following compilation issue and provide detailed insights and fix suggestions.

{context_info}
Issue Details:
- Severity: {issue.severity.value}
- Message: {issue.message}
- File: {issue.location.file_path}
- Line: {issue.location.line_number}
- Column: {issue.location.column_number}
- Tool: {issue.tool}
- Error Code: {issue.error_code}

Context Lines:
{chr(10).join(issue.context_lines) if issue.context_lines else "No context available"}

Please provide your analysis in the following JSON format:
{{
    "summary": "Brief explanation of what causes this issue",
    "category": "syntax|type|import|dependency|compilation|runtime|security|performance|code_style|unknown",
    "suggestions": [
        {{
            "description": "Clear description of the fix",
            "fix_type": "quick_fix|refactor|manual",
            "confidence": 0.0-1.0,
            "code_snippet": "Fixed code if applicable",
            "explanation": "Detailed explanation of why this fix works",
            "related_links": ["URLs to relevant documentation"]
        }}
    ]
}}

Focus on:
1. Accurate categorization of the issue
2. Practical, actionable fix suggestions
3. Code snippets when possible
4. Clear explanations suitable for developers of all levels
5. Confidence scores based on how certain you are about each suggestion

Provide only the JSON response, no additional text.
"""
        return prompt
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with error handling and retries."""
        try:
            response = await self.client.ChatCompletion.acreate(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are an expert code analyst providing JSON-formatted responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.timeout
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_openai_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse OpenAI JSON response with error handling."""
        try:
            # Clean up the response (remove markdown code blocks if present)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned_response)
            
            # Validate structure
            if not isinstance(parsed, dict):
                self.logger.warning("OpenAI response is not a dictionary")
                return None
            
            return parsed
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse OpenAI JSON response: {e}")
            self.logger.debug(f"Raw response: {response}")
            return None
        except Exception as e:
            self.logger.warning(f"Unexpected error parsing OpenAI response: {e}")
            return None
    
    async def generate_issue_summary(self, issues: List[CompilationIssue]) -> str:
        """Generate a human-readable summary of all issues using OpenAI."""
        if not issues:
            return "No compilation issues found."
        
        try:
            # Prepare issue summary for OpenAI
            issue_summary = self._prepare_issues_summary(issues)
            
            prompt = f"""
Analyze the following compilation issues and provide a concise, human-readable summary for developers.

Issue Summary:
{issue_summary}

Please provide:
1. Overall assessment of the compilation status
2. Most critical issues that need immediate attention
3. Common patterns or root causes
4. Recommended approach for fixing
5. Estimated complexity of fixes

Keep the summary concise but informative, suitable for both technical and non-technical stakeholders.
"""
            
            response = await self._call_openai_api(prompt)
            return response.strip()
            
        except Exception as e:
            self.logger.warning(f"Failed to generate issue summary: {e}")
            return f"Found {len(issues)} compilation issues. Please review individual issues for details."
    
    def _prepare_issues_summary(self, issues: List[CompilationIssue]) -> str:
        """Prepare a structured summary of issues for OpenAI analysis."""
        lines = []
        
        # Group by severity
        error_count = sum(1 for i in issues if i.severity == IssueSeverity.ERROR)
        warning_count = sum(1 for i in issues if i.severity == IssueSeverity.WARNING)
        
        lines.append(f"Total Issues: {len(issues)}")
        lines.append(f"Errors: {error_count}")
        lines.append(f"Warnings: {warning_count}")
        lines.append("")
        
        # List top 10 issues
        lines.append("Top Issues:")
        for i, issue in enumerate(issues[:10], 1):
            location = f"{issue.get_short_location()}"
            if issue.location.line_number:
                location += f":{issue.location.line_number}"
            
            lines.append(f"{i}. [{issue.severity.value.upper()}] {issue.message}")
            lines.append(f"   Location: {location}")
            
            if issue.category != IssueCategory.UNKNOWN:
                lines.append(f"   Category: {issue.category.value}")
            lines.append("")
        
        if len(issues) > 10:
            lines.append(f"... and {len(issues) - 10} more issues")
        
        return "\n".join(lines)


# Utility functions for easy integration

async def process_compilation_issues(issues: List[CompilationIssue],
                                   openai_api_key: Optional[str] = None,
                                   project_context: Optional[Dict[str, Any]] = None) -> List[CompilationIssue]:
    """
    Convenience function to process compilation issues with OpenAI.
    
    Args:
        issues: List of compilation issues
        openai_api_key: OpenAI API key (uses env var if not provided)
        project_context: Optional project context
        
    Returns:
        List of enhanced compilation issues
    """
    if openai_api_key:
        config = OpenAIConfig(api_key=openai_api_key)
    else:
        config = None
    
    processor = CompilationIssueProcessor(config)
    return await processor.process_issues(issues, project_context)


async def generate_issues_summary(issues: List[CompilationIssue],
                                 openai_api_key: Optional[str] = None) -> str:
    """
    Convenience function to generate a summary of compilation issues.
    
    Args:
        issues: List of compilation issues
        openai_api_key: OpenAI API key (uses env var if not provided)
        
    Returns:
        Human-readable summary string
    """
    if openai_api_key:
        config = OpenAIConfig(api_key=openai_api_key)
    else:
        config = None
    
    processor = CompilationIssueProcessor(config)
    return await processor.generate_issue_summary(issues)
