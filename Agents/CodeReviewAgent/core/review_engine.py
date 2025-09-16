"""
Core review engine for analyzing code files.
"""

import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..models.review_result import (
    ReviewResult, CodeIssue, FileMetrics, ReviewSummary,
    Severity, IssueCategory
)
from ..analyzers.java_analyzer import JavaAnalyzer
from ..analyzers.python_analyzer import PythonAnalyzer
from ..analyzers.generic_analyzer import GenericAnalyzer


class ReviewEngine:
    """Main engine for conducting code reviews."""
    
    def __init__(self, config: Dict[str, Any], language: str = "auto", 
                 severity_threshold: str = "medium"):
        """Initialize the review engine."""
        self.config = config
        self.language = language
        self.severity_threshold = Severity(severity_threshold)
        self.logger = logging.getLogger(__name__)
        
        # Initialize analyzers
        self.analyzers = {
            "java": JavaAnalyzer(config.get("rules", {}).get("java", {})),
            "python": PythonAnalyzer(config.get("rules", {}).get("python", {})),
            "generic": GenericAnalyzer(config.get("rules", {}).get("generic", {}))
        }
        
        # Statistics tracking
        self.summary = ReviewSummary()
        self.start_time = None
    
    def detect_language(self, file_path: Path) -> str:
        """Detect the programming language of a file."""
        suffix = file_path.suffix.lower()
        language_map = {
            ".java": "java",
            ".py": "python", 
            ".js": "javascript",
            ".ts": "typescript",
            ".xml": "xml",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".json": "json",
            ".properties": "properties"
        }
        return language_map.get(suffix, "unknown")
    
    def review_files(self, file_paths: List[Path]) -> List[ReviewResult]:
        """Review a list of files and return results."""
        self.start_time = time.time()
        results = []
        
        self.logger.info(f"Starting review of {len(file_paths)} files")
        
        for i, file_path in enumerate(file_paths, 1):
            self.logger.debug(f"Reviewing file {i}/{len(file_paths)}: {file_path}")
            
            try:
                result = self.review_single_file(file_path)
                results.append(result)
                
                # Update summary statistics
                self._update_summary(result)
                
            except Exception as e:
                self.logger.error(f"Failed to review {file_path}: {e}")
                # Create a minimal result with error
                error_result = ReviewResult(
                    file_path=str(file_path),
                    language="unknown"
                )
                error_result.review_notes.append(f"Review failed: {e}")
                results.append(error_result)
        
        # Finalize summary
        self.summary.review_duration = time.time() - self.start_time
        self.logger.info(f"Review completed in {self.summary.review_duration:.2f} seconds")
        
        return results
    
    def review_single_file(self, file_path: Path) -> ReviewResult:
        """Review a single file."""
        # Detect language
        language = self.detect_language(file_path)
        if self.language != "auto":
            language = self.language
        
        # Create review result
        result = ReviewResult(
            file_path=str(file_path),
            language=language
        )
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            result.review_notes.append(f"Failed to read file: {e}")
            return result
        
        # Calculate basic metrics
        result.metrics = self._calculate_metrics(file_path, content, language)
        
        # Select appropriate analyzer
        analyzer = self._get_analyzer(language)
        
        # Perform analysis
        issues = analyzer.analyze(content, file_path)
        
        # Filter issues by severity threshold
        filtered_issues = [
            issue for issue in issues 
            if self._meets_severity_threshold(issue.severity)
        ]
        
        result.issues = filtered_issues
        
        # Add general review notes
        self._add_general_notes(result, content)
        
        return result
    
    def _get_analyzer(self, language: str):
        """Get the appropriate analyzer for a language."""
        if language in self.analyzers:
            return self.analyzers[language]
        return self.analyzers["generic"]
    
    def _calculate_metrics(self, file_path: Path, content: str, language: str) -> FileMetrics:
        """Calculate basic metrics for a file."""
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Count comment lines (basic heuristic)
        comment_patterns = {
            "java": [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            "python": [r'^\s*#'],
            "javascript": [r'^\s*//', r'^\s*/\*'],
            "typescript": [r'^\s*//', r'^\s*/\*']
        }
        
        comment_lines = 0
        patterns = comment_patterns.get(language, [r'^\s*#', r'^\s*//'])
        
        for line in lines:
            for pattern in patterns:
                if re.match(pattern, line):
                    comment_lines += 1
                    break
        
        code_lines = total_lines - comment_lines - len([l for l in lines if not l.strip()])
        
        return FileMetrics(
            file_path=str(file_path),
            language=language,
            lines_of_code=code_lines,
            lines_of_comments=comment_lines
        )
    
    def _meets_severity_threshold(self, severity: Severity) -> bool:
        """Check if an issue meets the severity threshold."""
        severity_order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        threshold_index = severity_order.index(self.severity_threshold)
        issue_index = severity_order.index(severity)
        return issue_index >= threshold_index
    
    def _add_general_notes(self, result: ReviewResult, content: str) -> None:
        """Add general review notes based on file analysis."""
        lines = content.split('\n')
        
        # Check file size
        if len(lines) > 500:
            result.review_notes.append("Large file - consider breaking into smaller modules")
        
        # Check for TODO/FIXME comments
        todo_count = sum(1 for line in lines if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.IGNORECASE))
        if todo_count > 0:
            result.review_notes.append(f"Found {todo_count} TODO/FIXME comments")
        
        # Language-specific notes
        if result.language == "java":
            if not any("package " in line for line in lines[:10]):
                result.review_notes.append("Missing package declaration")
        
        elif result.language == "python":
            if not any(line.startswith('"""') or line.startswith("'''") for line in lines[:10]):
                result.review_notes.append("Consider adding module docstring")
    
    def _update_summary(self, result: ReviewResult) -> None:
        """Update summary statistics with results from a file."""
        self.summary.total_files_reviewed += 1
        self.summary.total_issues_found += len(result.issues)
        
        # Count issues by severity
        for issue in result.issues:
            if issue.severity not in self.summary.issues_by_severity:
                self.summary.issues_by_severity[issue.severity] = 0
            self.summary.issues_by_severity[issue.severity] += 1
            
            # Count issues by category
            if issue.category not in self.summary.issues_by_category:
                self.summary.issues_by_category[issue.category] = 0
            self.summary.issues_by_category[issue.category] += 1
        
        # Track languages
        if result.language not in self.summary.languages_analyzed:
            self.summary.languages_analyzed.append(result.language)
    
    def get_summary_statistics(self) -> ReviewSummary:
        """Get the current summary statistics."""
        return self.summary
