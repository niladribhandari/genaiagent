"""
Report generator for creating review reports in various formats.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from ..models.review_result import ReviewResult, ReviewSummary


class ReportGenerator:
    """Generates review reports in various formats."""
    
    def __init__(self, format: str = "json"):
        """Initialize the report generator."""
        self.format = format.lower()
        self.logger = logging.getLogger(__name__)
        
    def generate_report(self, review_results: List[ReviewResult], 
                       output_path: str, summary_stats: ReviewSummary) -> None:
        """Generate a report in the specified format."""
        self.logger.info(f"Generating {self.format} report to {output_path}")
        
        if self.format == "json":
            self._generate_json_report(review_results, output_path, summary_stats)
        elif self.format == "html":
            self._generate_html_report(review_results, output_path, summary_stats)
        elif self.format == "markdown":
            self._generate_markdown_report(review_results, output_path, summary_stats)
        elif self.format == "text":
            self._generate_text_report(review_results, output_path, summary_stats)
        else:
            raise ValueError(f"Unsupported format: {self.format}")
    
    def _generate_json_report(self, review_results: List[ReviewResult], 
                             output_path: str, summary_stats: ReviewSummary) -> None:
        """Generate JSON format report."""
        report_data = {
            "metadata": {
                "generator": "Code Review Agent",
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
                "format": "json"
            },
            "summary": summary_stats.to_dict(),
            "results": [result.to_dict() for result in review_results]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self, review_results: List[ReviewResult], 
                             output_path: str, summary_stats: ReviewSummary) -> None:
        """Generate HTML format report."""
        html_content = self._build_html_report(review_results, summary_stats)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_markdown_report(self, review_results: List[ReviewResult], 
                                 output_path: str, summary_stats: ReviewSummary) -> None:
        """Generate Markdown format report."""
        md_content = self._build_markdown_report(review_results, summary_stats)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _generate_text_report(self, review_results: List[ReviewResult], 
                             output_path: str, summary_stats: ReviewSummary) -> None:
        """Generate plain text format report."""
        text_content = self._build_text_report(review_results, summary_stats)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
    
    def _build_html_report(self, review_results: List[ReviewResult], 
                          summary_stats: ReviewSummary) -> str:
        """Build HTML report content."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Review Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .file-result {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .file-header {{ background-color: #f9f9f9; padding: 10px; font-weight: bold; }}
        .issue {{ margin: 10px; padding: 10px; border-left: 4px solid #ccc; }}
        .critical {{ border-left-color: #d32f2f; }}
        .high {{ border-left-color: #f57c00; }}
        .medium {{ border-left-color: #fbc02d; }}
        .low {{ border-left-color: #388e3c; }}
        .metrics {{ background-color: #f5f5f5; padding: 10px; margin: 10px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f0f0f0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Code Review Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Files Reviewed</td><td>{summary_stats.total_files_reviewed}</td></tr>
            <tr><td>Total Issues</td><td>{summary_stats.total_issues_found}</td></tr>
            <tr><td>Critical Issues</td><td>{summary_stats.issues_by_severity.get('critical', 0)}</td></tr>
            <tr><td>High Issues</td><td>{summary_stats.issues_by_severity.get('high', 0)}</td></tr>
            <tr><td>Medium Issues</td><td>{summary_stats.issues_by_severity.get('medium', 0)}</td></tr>
            <tr><td>Low Issues</td><td>{summary_stats.issues_by_severity.get('low', 0)}</td></tr>
            <tr><td>Review Duration</td><td>{summary_stats.review_duration:.2f}s</td></tr>
        </table>
    </div>
    
    <div class="results">
        <h2>Detailed Results</h2>
"""
        
        for result in review_results:
            html += f"""
        <div class="file-result">
            <div class="file-header">{result.file_path} ({result.language})</div>
"""
            
            if result.metrics:
                html += f"""
            <div class="metrics">
                <strong>Metrics:</strong> 
                Lines of Code: {result.metrics.lines_of_code}, 
                Comments: {result.metrics.lines_of_comments}
            </div>
"""
            
            for issue in result.issues:
                html += f"""
            <div class="issue {issue.severity.value}">
                <strong>{issue.title}</strong> (Line {issue.line_number}) - {issue.severity.value.upper()}
                <br>{issue.description}
                {f"<br><em>Suggestion: {issue.suggestion}</em>" if issue.suggestion else ""}
            </div>
"""
            
            html += "        </div>"
        
        html += """
    </div>
</body>
</html>"""
        
        return html
    
    def _build_markdown_report(self, review_results: List[ReviewResult], 
                              summary_stats: ReviewSummary) -> str:
        """Build Markdown report content."""
        md = f"""# Code Review Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Files Reviewed | {summary_stats.total_files_reviewed} |
| Total Issues | {summary_stats.total_issues_found} |
| Critical Issues | {summary_stats.issues_by_severity.get('critical', 0)} |
| High Issues | {summary_stats.issues_by_severity.get('high', 0)} |
| Medium Issues | {summary_stats.issues_by_severity.get('medium', 0)} |
| Low Issues | {summary_stats.issues_by_severity.get('low', 0)} |
| Review Duration | {summary_stats.review_duration:.2f}s |

## Detailed Results

"""
        
        for result in review_results:
            md += f"### {result.file_path} ({result.language})\n\n"
            
            if result.metrics:
                md += f"**Metrics:** Lines of Code: {result.metrics.lines_of_code}, Comments: {result.metrics.lines_of_comments}\n\n"
            
            if result.issues:
                md += "**Issues:**\n\n"
                for issue in result.issues:
                    md += f"- **{issue.title}** (Line {issue.line_number}) - `{issue.severity.value.upper()}`\n"
                    md += f"  {issue.description}\n"
                    if issue.suggestion:
                        md += f"  *Suggestion: {issue.suggestion}*\n"
                    md += "\n"
            else:
                md += "No issues found.\n\n"
            
            if result.review_notes:
                md += "**Notes:**\n"
                for note in result.review_notes:
                    md += f"- {note}\n"
                md += "\n"
        
        return md
    
    def _build_text_report(self, review_results: List[ReviewResult], 
                          summary_stats: ReviewSummary) -> str:
        """Build plain text report content."""
        text = f"""CODE REVIEW REPORT
{'=' * 50}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Files Reviewed: {summary_stats.total_files_reviewed}
Total Issues: {summary_stats.total_issues_found}
Critical Issues: {summary_stats.issues_by_severity.get('critical', 0)}
High Issues: {summary_stats.issues_by_severity.get('high', 0)}
Medium Issues: {summary_stats.issues_by_severity.get('medium', 0)}
Low Issues: {summary_stats.issues_by_severity.get('low', 0)}
Review Duration: {summary_stats.review_duration:.2f}s

DETAILED RESULTS
----------------

"""
        
        for result in review_results:
            text += f"File: {result.file_path} ({result.language})\n"
            text += "-" * (len(result.file_path) + len(result.language) + 8) + "\n"
            
            if result.metrics:
                text += f"Metrics: Lines of Code: {result.metrics.lines_of_code}, Comments: {result.metrics.lines_of_comments}\n"
            
            if result.issues:
                text += f"Issues ({len(result.issues)}):\n"
                for i, issue in enumerate(result.issues, 1):
                    text += f"  {i}. {issue.title} (Line {issue.line_number}) - {issue.severity.value.upper()}\n"
                    text += f"     {issue.description}\n"
                    if issue.suggestion:
                        text += f"     Suggestion: {issue.suggestion}\n"
                    text += "\n"
            else:
                text += "No issues found.\n"
            
            if result.review_notes:
                text += "Notes:\n"
                for note in result.review_notes:
                    text += f"  - {note}\n"
            
            text += "\n"
        
        return text
