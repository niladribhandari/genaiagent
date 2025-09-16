"""
Capabilities for AgenticAI code review system.
Each capability represents a specific skill that agents can use to accomplish tasks.
"""

from typing import Dict, List, Any, Optional
import re
import ast
import logging
from pathlib import Path
import json

from .core import AgentCapability, AgentTask


class FileDiscoveryCapability(AgentCapability):
    """Capability for intelligent file discovery and analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this capability can handle file discovery tasks."""
        return task.task_type in ["file_discovery", "file_filtering", "file_classification"]
    
    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file discovery task."""
        if task.task_type == "file_discovery":
            return await self._discover_files(task, context)
        elif task.task_type == "file_filtering":
            return await self._filter_files(task, context)
        elif task.task_type == "file_classification":
            return await self._classify_files(task, context)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _discover_files(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Discover files in the project directory."""
        project_path = Path(task.input_data.get("project_path", "."))
        extensions = task.input_data.get("extensions", [".java", ".py", ".js", ".ts"])
        
        discovered_files = []
        for ext in extensions:
            files = list(project_path.rglob(f"*{ext}"))
            discovered_files.extend(files)
        
        # Filter out common ignore patterns
        ignore_patterns = [
            "target/", "build/", "node_modules/", "__pycache__/",
            ".git/", ".idea/", ".vscode/"
        ]
        
        filtered_files = []
        for file_path in discovered_files:
            if not any(pattern in str(file_path) for pattern in ignore_patterns):
                filtered_files.append(file_path)
        
        self.logger.info(f"Discovered {len(filtered_files)} files for analysis")
        
        return {
            "discovered_files": [str(f) for f in filtered_files],
            "total_count": len(filtered_files),
            "by_extension": self._group_by_extension(filtered_files)
        }
    
    async def _filter_files(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Filter files based on criteria."""
        files = task.input_data.get("files", [])
        criteria = task.input_data.get("criteria", {})
        
        filtered_files = []
        for file_path in files:
            if self._meets_criteria(Path(file_path), criteria):
                filtered_files.append(file_path)
        
        return {
            "filtered_files": filtered_files,
            "original_count": len(files),
            "filtered_count": len(filtered_files)
        }
    
    async def _classify_files(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify files by type and purpose."""
        files = task.input_data.get("files", [])
        
        classification = {
            "controllers": [],
            "services": [],
            "models": [],
            "repositories": [],
            "configs": [],
            "tests": [],
            "utilities": [],
            "other": []
        }
        
        for file_path in files:
            path = Path(file_path)
            category = self._classify_file(path)
            classification[category].append(str(path))
        
        return {
            "classification": classification,
            "summary": {k: len(v) for k, v in classification.items()}
        }
    
    def _group_by_extension(self, files: List[Path]) -> Dict[str, int]:
        """Group files by extension."""
        by_ext = {}
        for file_path in files:
            ext = file_path.suffix
            by_ext[ext] = by_ext.get(ext, 0) + 1
        return by_ext
    
    def _meets_criteria(self, file_path: Path, criteria: Dict[str, Any]) -> bool:
        """Check if file meets filtering criteria."""
        # Size criteria
        max_size = criteria.get("max_size_mb")
        if max_size:
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > max_size:
                    return False
            except OSError:
                return False
        
        # Pattern criteria
        include_patterns = criteria.get("include_patterns", [])
        exclude_patterns = criteria.get("exclude_patterns", [])
        
        file_str = str(file_path)
        
        if include_patterns and not any(pattern in file_str for pattern in include_patterns):
            return False
        
        if exclude_patterns and any(pattern in file_str for pattern in exclude_patterns):
            return False
        
        return True
    
    def _classify_file(self, file_path: Path) -> str:
        """Classify a file based on its path and name."""
        path_str = str(file_path).lower()
        name = file_path.name.lower()
        
        if "controller" in path_str or "controller" in name:
            return "controllers"
        elif "service" in path_str or "service" in name:
            return "services"
        elif "model" in path_str or "entity" in path_str or "dto" in path_str:
            return "models"
        elif "repository" in path_str or "dao" in path_str:
            return "repositories"
        elif "config" in path_str or "configuration" in name:
            return "configs"
        elif "test" in path_str or name.endswith("test.java") or name.endswith("test.py"):
            return "tests"
        elif "util" in path_str or "helper" in path_str:
            return "utilities"
        else:
            return "other"
    
    def learn_from_result(self, task: AgentTask, result: Dict[str, Any]) -> None:
        """Learn from file discovery results."""
        # Could implement adaptive file discovery based on success patterns
        pass


class JavaAnalysisCapability(AgentCapability):
    """Advanced Java code analysis capability."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this capability can handle Java analysis tasks."""
        java_task_types = [
            "complexity_analysis", "nesting_analysis", "structure_analysis",
            "pattern_analysis", "java_standards_check", "injection_scan",
            "auth_scan", "crypto_scan"
        ]
        return task.task_type in java_task_types
    
    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Java analysis task."""
        if task.task_type == "complexity_analysis":
            return await self._analyze_complexity(task, context)
        elif task.task_type == "nesting_analysis":
            return await self._analyze_nesting(task, context)
        elif task.task_type == "structure_analysis":
            return await self._analyze_structure(task, context)
        elif task.task_type == "pattern_analysis":
            return await self._analyze_patterns(task, context)
        elif task.task_type == "java_standards_check":
            return await self._check_java_standards(task, context)
        elif task.task_type in ["injection_scan", "auth_scan", "crypto_scan"]:
            return await self._security_analysis(task, context)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _analyze_complexity(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code complexity."""
        files = task.input_data.get("files", [])
        max_complexity = self.config.get("max_complexity", 10)
        
        complexity_results = {}
        violations = []
        
        for file_path in files:
            if not str(file_path).endswith('.java'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple complexity analysis based on control structures
                complexity_issues = self._find_complexity_issues(content, file_path, max_complexity)
                complexity_results[str(file_path)] = len(complexity_issues)
                violations.extend(complexity_issues)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze complexity for {file_path}: {e}")
        
        return {
            "complexity_scores": complexity_results,
            "violations": violations,
            "average_complexity": sum(complexity_results.values()) / len(complexity_results) if complexity_results else 0
        }
    
    def _find_complexity_issues(self, content: str, file_path: str, max_complexity: int) -> List[Dict[str, Any]]:
        """Find complexity issues in Java code."""
        issues = []
        lines = content.split('\n')
        
        # Count control structures per method
        in_method = False
        method_complexity = 0
        method_start_line = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Detect method start
            if re.search(r'(public|private|protected)\s+\w+.*\([^)]*\)\s*\{', stripped):
                in_method = True
                method_complexity = 1  # Base complexity
                method_start_line = i
            
            # Count complexity-adding constructs
            if in_method:
                complexity_patterns = [
                    r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
                    r'\bcatch\b', r'\?\s*:', r'\&\&', r'\|\|'
                ]
                
                for pattern in complexity_patterns:
                    if re.search(pattern, stripped):
                        method_complexity += 1
            
            # Detect method end
            if in_method and stripped == '}':
                if method_complexity > max_complexity:
                    issues.append({
                        "file_path": str(file_path),
                        "line_number": method_start_line,
                        "severity": "high" if method_complexity > max_complexity * 2 else "medium",
                        "category": "complexity",
                        "title": f"High cyclomatic complexity: {method_complexity}",
                        "description": f"Method has cyclomatic complexity of {method_complexity}, exceeding threshold of {max_complexity}",
                        "suggestion": "Consider breaking this method into smaller, more focused methods"
                    })
                
                in_method = False
                method_complexity = 0
        
        return issues
    
    async def _analyze_nesting(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code nesting depth."""
        files = task.input_data.get("files", [])
        max_depth = task.input_data.get("max_depth", 4)
        
        nesting_violations = []
        
        for file_path in files:
            if not str(file_path).endswith('.java'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                violations = self._find_deep_nesting(content, file_path, max_depth)
                nesting_violations.extend(violations)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze nesting for {file_path}: {e}")
        
        return {
            "nesting_violations": nesting_violations,
            "violation_count": len(nesting_violations)
        }
    
    async def _analyze_structure(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project structure."""
        files = task.input_data.get("files", [])
        project_type = task.input_data.get("project_type", "unknown")
        
        structure_analysis = {
            "package_organization": self._analyze_package_structure(files),
            "layering_compliance": self._check_layering(files),
            "naming_consistency": self._check_naming_consistency(files)
        }
        
        structure_score = self._calculate_structure_score(structure_analysis)
        
        return {
            "structure_score": structure_score,
            "analysis": structure_analysis,
            "issues": self._extract_structure_issues(structure_analysis)
        }
    
    async def _analyze_patterns(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze design pattern usage."""
        files = task.input_data.get("files", [])
        patterns = task.input_data.get("patterns", ["mvc", "dependency_injection", "singleton"])
        
        pattern_usage = {}
        anti_patterns = []
        
        for pattern in patterns:
            usage = self._detect_pattern_usage(files, pattern)
            pattern_usage[pattern] = usage
        
        # Detect anti-patterns
        anti_patterns.extend(self._detect_anti_patterns(files))
        
        return {
            "pattern_usage": pattern_usage,
            "anti_patterns": anti_patterns,
            "pattern_compliance_score": self._calculate_pattern_score(pattern_usage)
        }
    
    async def _check_java_standards(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check Java coding standards compliance."""
        files = task.input_data.get("files", [])
        standards = task.input_data.get("standards", ["naming", "formatting", "structure"])
        
        violations = []
        compliance_scores = {}
        
        for file_path in files:
            if not str(file_path).endswith('.java'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_violations = []
                for standard in standards:
                    standard_violations = self._check_standard(content, file_path, standard)
                    file_violations.extend(standard_violations)
                
                violations.extend(file_violations)
                compliance_scores[str(file_path)] = len(file_violations)
                
            except Exception as e:
                self.logger.error(f"Failed to check standards for {file_path}: {e}")
        
        overall_compliance = 1.0 - (len(violations) / max(len(files), 1))
        
        return {
            "violations": violations,
            "compliance_score": max(0.0, overall_compliance),
            "file_scores": compliance_scores
        }
    
    async def _security_analysis(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform security analysis."""
        files = task.input_data.get("files", [])
        scan_type = task.task_type
        
        security_issues = []
        
        for file_path in files:
            if not str(file_path).endswith('.java'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if scan_type == "injection_scan":
                    issues = self._scan_injection_vulnerabilities(content, file_path)
                elif scan_type == "auth_scan":
                    issues = self._scan_auth_issues(content, file_path)
                elif scan_type == "crypto_scan":
                    issues = self._scan_crypto_issues(content, file_path)
                else:
                    issues = []
                
                security_issues.extend(issues)
                
            except Exception as e:
                self.logger.error(f"Failed security scan for {file_path}: {e}")
        
        risk_level = self._calculate_risk_level(security_issues)
        
        return {
            "vulnerabilities": security_issues,
            "risk_level": risk_level,
            "vulnerability_count": len(security_issues)
        }
    
    def _find_deep_nesting(self, content: str, file_path: str, max_depth: int) -> List[Dict[str, Any]]:
        """Find deeply nested code structures."""
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Simple indentation-based nesting detection
            indent_level = (len(line) - len(line.lstrip())) // 4
            if indent_level > max_depth:
                violations.append({
                    "file": str(file_path),
                    "line": i,
                    "nesting_depth": indent_level,
                    "description": f"Code nested {indent_level} levels deep"
                })
        
        return violations
    
    def _analyze_package_structure(self, files: List[str]) -> Dict[str, Any]:
        """Analyze package organization."""
        packages = set()
        package_files = {}
        
        for file_path in files:
            if file_path.endswith('.java'):
                # Extract package from file path
                path_parts = Path(file_path).parts
                if 'java' in path_parts:
                    java_index = path_parts.index('java')
                    if java_index + 1 < len(path_parts):
                        package_path = '/'.join(path_parts[java_index + 1:-1])
                        packages.add(package_path)
                        if package_path not in package_files:
                            package_files[package_path] = []
                        package_files[package_path].append(file_path)
        
        return {
            "total_packages": len(packages),
            "packages": list(packages),
            "files_per_package": {k: len(v) for k, v in package_files.items()},
            "average_files_per_package": sum(len(v) for v in package_files.values()) / len(package_files) if package_files else 0
        }
    
    def _check_layering(self, files: List[str]) -> Dict[str, Any]:
        """Check architectural layering compliance."""
        layers = {"controller": [], "service": [], "repository": [], "model": [], "config": []}
        
        for file_path in files:
            path_lower = file_path.lower()
            for layer in layers:
                if layer in path_lower:
                    layers[layer].append(file_path)
                    break
        
        layer_compliance = {
            "has_controller_layer": len(layers["controller"]) > 0,
            "has_service_layer": len(layers["service"]) > 0,
            "has_repository_layer": len(layers["repository"]) > 0,
            "separation_score": self._calculate_separation_score(layers)
        }
        
        return layer_compliance
    
    def _check_naming_consistency(self, files: List[str]) -> Dict[str, Any]:
        """Check naming consistency across files."""
        naming_patterns = {}
        inconsistencies = []
        
        for file_path in files:
            file_name = Path(file_path).stem
            
            # Check common naming patterns
            if "Controller" in file_name:
                if not file_name.endswith("Controller"):
                    inconsistencies.append(f"Controller naming: {file_name}")
            elif "Service" in file_name:
                if not file_name.endswith("Service"):
                    inconsistencies.append(f"Service naming: {file_name}")
            elif "Repository" in file_name:
                if not file_name.endswith("Repository"):
                    inconsistencies.append(f"Repository naming: {file_name}")
        
        return {
            "inconsistencies": inconsistencies,
            "consistency_score": 1.0 - (len(inconsistencies) / max(len(files), 1))
        }
    
    def _calculate_structure_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall structure score."""
        scores = []
        
        # Package organization score
        pkg_analysis = analysis["package_organization"]
        if pkg_analysis["total_packages"] > 0:
            scores.append(min(1.0, pkg_analysis["average_files_per_package"] / 10))
        
        # Layering score
        layer_analysis = analysis["layering_compliance"]
        scores.append(layer_analysis["separation_score"])
        
        # Naming consistency score
        naming_analysis = analysis["naming_consistency"]
        scores.append(naming_analysis["consistency_score"])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _extract_structure_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract structural issues from analysis."""
        issues = []
        
        # Add naming inconsistencies
        issues.extend(analysis["naming_consistency"]["inconsistencies"])
        
        # Add layering issues
        layering = analysis["layering_compliance"]
        if not layering["has_service_layer"]:
            issues.append("Missing service layer")
        if not layering["has_repository_layer"]:
            issues.append("Missing repository layer")
        
        return issues
    
    def _detect_pattern_usage(self, files: List[str], pattern: str) -> Dict[str, Any]:
        """Detect usage of specific design pattern."""
        usage = {"detected": False, "files": [], "confidence": 0.0}
        
        if pattern == "mvc":
            # Check for MVC pattern indicators
            has_controllers = any("controller" in f.lower() for f in files)
            has_views = any("view" in f.lower() for f in files)
            has_models = any("model" in f.lower() or "entity" in f.lower() for f in files)
            
            if has_controllers and has_models:
                usage["detected"] = True
                usage["confidence"] = 0.8 if has_views else 0.6
        
        elif pattern == "dependency_injection":
            # Look for DI annotations or patterns in file content
            # This is a simplified check - would need content analysis
            usage["detected"] = True
            usage["confidence"] = 0.7
        
        return usage
    
    def _detect_anti_patterns(self, files: List[str]) -> List[Dict[str, Any]]:
        """Detect anti-patterns in the codebase."""
        anti_patterns = []
        
        # God object detection (oversimplified)
        for file_path in files:
            try:
                file_size = Path(file_path).stat().st_size
                if file_size > 10000:  # Large file threshold
                    anti_patterns.append({
                        "pattern": "God Object",
                        "file": file_path,
                        "description": "Very large file may indicate god object anti-pattern"
                    })
            except OSError:
                pass
        
        return anti_patterns
    
    def _calculate_pattern_score(self, pattern_usage: Dict[str, Any]) -> float:
        """Calculate pattern compliance score."""
        total_patterns = len(pattern_usage)
        detected_patterns = sum(1 for usage in pattern_usage.values() if usage["detected"])
        
        return detected_patterns / total_patterns if total_patterns > 0 else 0.0
    
    def _check_standard(self, content: str, file_path: str, standard: str) -> List[Dict[str, Any]]:
        """Check specific coding standard."""
        violations = []
        
        if standard == "naming":
            violations.extend(self._check_naming_conventions(content, file_path))
        elif standard == "formatting":
            violations.extend(self._check_formatting(content, file_path))
        elif standard == "structure":
            violations.extend(self._check_structure_standards(content, file_path))
        
        return violations
    
    def _check_naming_conventions(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Check Java naming conventions."""
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check class naming (should be PascalCase)
            class_match = re.search(r'class\s+([a-z][a-zA-Z]*)', line)
            if class_match:
                violations.append({
                    "file": str(file_path),
                    "line": i,
                    "type": "naming",
                    "description": f"Class name should start with uppercase: {class_match.group(1)}"
                })
            
            # Check method naming (should be camelCase)
            method_match = re.search(r'public\s+\w+\s+([A-Z][a-zA-Z]*)\s*\(', line)
            if method_match:
                violations.append({
                    "file": str(file_path),
                    "line": i,
                    "type": "naming",
                    "description": f"Method name should start with lowercase: {method_match.group(1)}"
                })
        
        return violations
    
    def _check_formatting(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Check formatting standards."""
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                violations.append({
                    "file": str(file_path),
                    "line": i,
                    "type": "formatting",
                    "description": f"Line too long: {len(line)} characters"
                })
        
        return violations
    
    def _check_structure_standards(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Check structural standards."""
        violations = []
        
        # Check for missing package declaration
        if 'package ' not in content[:200]:  # Check first 200 chars
            violations.append({
                "file": str(file_path),
                "line": 1,
                "type": "structure",
                "description": "Missing package declaration"
            })
        
        return violations
    
    def _scan_injection_vulnerabilities(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Scan for injection vulnerabilities."""
        vulnerabilities = []
        
        # SQL injection patterns
        sql_patterns = [
            r'executeQuery\s*\(\s*["\'][^"\']*\+',  # String concatenation in SQL
            r'createQuery\s*\(\s*["\'][^"\']*\+',   # JPA query concatenation
        ]
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    "type": "SQL Injection",
                    "file": str(file_path),
                    "line": line_num,
                    "description": "Potential SQL injection vulnerability",
                    "severity": "HIGH"
                })
        
        return vulnerabilities
    
    def _scan_auth_issues(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Scan for authentication/authorization issues."""
        issues = []
        
        # Check for missing authentication annotations
        if '@RestController' in content and '@PreAuthorize' not in content:
            issues.append({
                "type": "Authentication",
                "file": str(file_path),
                "line": 1,
                "description": "Controller missing authorization annotations",
                "severity": "MEDIUM"
            })
        
        return issues
    
    def _scan_crypto_issues(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Scan for cryptographic issues."""
        issues = []
        
        # Check for weak algorithms
        weak_algorithms = ['MD5', 'SHA1', 'DES']
        for algorithm in weak_algorithms:
            if algorithm in content:
                line_num = content.find(algorithm)
                line_num = content[:line_num].count('\n') + 1
                issues.append({
                    "type": "Cryptography",
                    "file": str(file_path),
                    "line": line_num,
                    "description": f"Weak cryptographic algorithm: {algorithm}",
                    "severity": "HIGH"
                })
        
        return issues
    
    def _calculate_separation_score(self, layers: Dict[str, List[str]]) -> float:
        """Calculate architectural separation score."""
        # Simple scoring based on layer presence
        present_layers = sum(1 for files in layers.values() if files)
        total_layers = len(layers)
        return present_layers / total_layers
    
    def _calculate_risk_level(self, security_issues: List[Dict[str, Any]]) -> str:
        """Calculate overall security risk level."""
        if not security_issues:
            return "LOW"
        
        high_severity_count = sum(1 for issue in security_issues if issue.get("severity") == "HIGH")
        
        if high_severity_count > 0:
            return "HIGH"
        elif len(security_issues) > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _issue_to_dict(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Convert issue to dictionary (simplified version)."""
        return issue
    
    def learn_from_result(self, task: AgentTask, result: Dict[str, Any]) -> None:
        """Learn from Java analysis results."""
        # Could implement learning mechanisms to improve analysis quality
        pass


class PythonAnalysisCapability(AgentCapability):
    """Python code analysis capability."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this capability can handle Python analysis tasks."""
        python_task_types = [
            "python_complexity_analysis", "python_standards_check",
            "python_security_scan", "maintainability_analysis"
        ]
        return task.task_type in python_task_types
    
    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python analysis task."""
        files = task.input_data.get("files", [])
        python_files = [f for f in files if str(f).endswith('.py')]
        
        if not python_files:
            return {"message": "No Python files to analyze", "results": []}
        
        results = []
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = self._analyze_python_code(content, file_path)
                results.append({
                    "file": str(file_path),
                    "issues": issues
                })
                
            except Exception as e:
                self.logger.error(f"Failed to analyze Python file {file_path}: {e}")
        
        return {
            "python_analysis_results": results,
            "total_files": len(python_files),
            "total_issues": sum(len(r["issues"]) for r in results)
        }
    
    def _analyze_python_code(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Simple Python code analysis."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for long lines
            if len(line) > 100:
                issues.append({
                    "file_path": str(file_path),
                    "line_number": i,
                    "severity": "low",
                    "category": "style",
                    "title": "Line too long",
                    "description": f"Line {i} exceeds 100 characters",
                    "suggestion": "Break long lines for better readability"
                })
            
            # Check for TODO comments
            if 'TODO' in stripped.upper():
                issues.append({
                    "file_path": str(file_path),
                    "line_number": i,
                    "severity": "low",
                    "category": "maintenance",
                    "title": "TODO comment found",
                    "description": "Unfinished work item detected",
                    "suggestion": "Complete the TODO or create a proper issue"
                })
        
        return issues
    
    def learn_from_result(self, task: AgentTask, result: Dict[str, Any]) -> None:
        """Learn from Python analysis results."""
        pass


class GenericAnalysisCapability(AgentCapability):
    """Generic analysis capability for all file types."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this capability can handle generic analysis tasks."""
        generic_task_types = [
            "generic_standards_check", "documentation_coverage",
            "documentation_quality", "smell_detection"
        ]
        return task.task_type in generic_task_types
    
    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic analysis task."""
        files = task.input_data.get("files", [])
        
        results = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = self._analyze_generic_file(content, file_path)
                results.append({
                    "file": str(file_path),
                    "issues": issues
                })
                
            except Exception as e:
                self.logger.error(f"Failed to analyze file {file_path}: {e}")
        
        return {
            "generic_analysis_results": results,
            "total_files": len(files),
            "total_issues": sum(len(r["issues"]) for r in results)
        }
    
    def _analyze_generic_file(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Generic file analysis."""
        issues = []
        
        # Check file size
        if len(content) > 50000:  # Large file
            issues.append({
                "file_path": str(file_path),
                "line_number": 1,
                "severity": "medium",
                "category": "maintainability",
                "title": "Large file detected",
                "description": "File is very large and may be difficult to maintain",
                "suggestion": "Consider breaking into smaller, more focused files"
            })
        
        # Check for empty files
        if len(content.strip()) == 0:
            issues.append({
                "file_path": str(file_path),
                "line_number": 1,
                "severity": "low",
                "category": "structure",
                "title": "Empty file",
                "description": "File appears to be empty",
                "suggestion": "Remove unused files or add content"
            })
        
        return issues
    
    def learn_from_result(self, task: AgentTask, result: Dict[str, Any]) -> None:
        """Learn from generic analysis results."""
        pass


class ReportGenerationCapability(AgentCapability):
    """Capability for generating comprehensive reports."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this capability can handle report generation tasks."""
        return task.task_type in ["generate_report", "synthesize_results", "create_summary"]
    
    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation task."""
        if task.task_type == "generate_report":
            return await self._generate_comprehensive_report(task, context)
        elif task.task_type == "synthesize_results":
            return await self._synthesize_agent_results(task, context)
        elif task.task_type == "create_summary":
            return await self._create_executive_summary(task, context)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _generate_comprehensive_report(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive analysis report."""
        agent_results = task.input_data.get("agent_results", {})
        format_type = task.input_data.get("format", "json")
        
        report = {
            "metadata": {
                "report_type": "Comprehensive Code Review",
                "generated_by": "AgenticAI Review System",
                "timestamp": "2025-08-14T22:00:00Z",  # Would use actual timestamp
                "format": format_type
            },
            "executive_summary": self._create_executive_summary_data(agent_results),
            "agent_analyses": agent_results,
            "recommendations": self._generate_recommendations(agent_results),
            "metrics": self._calculate_overall_metrics(agent_results)
        }
        
        return {"comprehensive_report": report}
    
    async def _synthesize_agent_results(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple agents."""
        agent_results = task.input_data.get("agent_results", {})
        
        synthesis = {
            "cross_agent_patterns": self._identify_cross_patterns(agent_results),
            "consensus_issues": self._find_consensus_issues(agent_results),
            "conflicting_assessments": self._identify_conflicts(agent_results),
            "integrated_metrics": self._integrate_metrics(agent_results)
        }
        
        return {"synthesis": synthesis}
    
    async def _create_executive_summary(self, task: AgentTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary."""
        agent_results = task.input_data.get("agent_results", {})
        
        summary = self._create_executive_summary_data(agent_results)
        return {"executive_summary": summary}
    
    def _create_executive_summary_data(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary data."""
        total_issues = 0
        critical_issues = 0
        files_analyzed = 0
        
        for agent_id, results in agent_results.items():
            if isinstance(results, dict):
                # Extract metrics from agent results
                if "total_issues" in results:
                    total_issues += results["total_issues"]
                if "critical_issues" in results:
                    critical_issues += results["critical_issues"]
                if "files_analyzed" in results:
                    files_analyzed += results["files_analyzed"]
        
        return {
            "total_files_analyzed": files_analyzed,
            "total_issues_found": total_issues,
            "critical_issues": critical_issues,
            "overall_quality_score": self._calculate_quality_score(agent_results),
            "key_findings": self._extract_key_findings(agent_results),
            "priority_actions": self._identify_priority_actions(agent_results)
        }
    
    def _generate_recommendations(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Analyze patterns across agent results to generate recommendations
        for agent_id, results in agent_results.items():
            if agent_id == "security_analysis_agent":
                if results.get("vulnerabilities", []):
                    recommendations.append({
                        "priority": "CRITICAL",
                        "category": "Security",
                        "title": "Address Security Vulnerabilities",
                        "description": "Critical security vulnerabilities found",
                        "actions": ["Review identified vulnerabilities", "Implement fixes", "Add security testing"]
                    })
            
            elif agent_id == "code_analysis_agent":
                complexity_issues = results.get("complexity_violations", [])
                if len(complexity_issues) > 5:
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Code Quality",
                        "title": "Reduce Code Complexity",
                        "description": "Multiple complex methods detected",
                        "actions": ["Refactor complex methods", "Extract helper methods", "Consider design patterns"]
                    })
        
        return recommendations
    
    def _calculate_overall_metrics(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall project metrics."""
        return {
            "quality_score": self._calculate_quality_score(agent_results),
            "security_score": self._calculate_security_score(agent_results),
            "maintainability_score": self._calculate_maintainability_score(agent_results),
            "compliance_score": self._calculate_compliance_score(agent_results)
        }
    
    def _identify_cross_patterns(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify patterns across multiple agents."""
        patterns = []
        
        # Example: Files mentioned by multiple agents
        file_mentions = {}
        for agent_id, results in agent_results.items():
            if isinstance(results, dict) and "files" in results:
                for file_path in results["files"]:
                    if file_path not in file_mentions:
                        file_mentions[file_path] = []
                    file_mentions[file_path].append(agent_id)
        
        # Files with issues from multiple agents
        problematic_files = {f: agents for f, agents in file_mentions.items() if len(agents) > 1}
        if problematic_files:
            patterns.append({
                "type": "Multi-Agent Issues",
                "description": "Files with issues identified by multiple agents",
                "files": problematic_files
            })
        
        return patterns
    
    def _find_consensus_issues(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find issues where multiple agents agree."""
        # Simplified implementation
        return []
    
    def _identify_conflicts(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify conflicting assessments between agents."""
        # Simplified implementation
        return []
    
    def _integrate_metrics(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate metrics from all agents."""
        return {
            "overall_score": self._calculate_quality_score(agent_results),
            "agent_contributions": {agent_id: "analysis_complete" for agent_id in agent_results.keys()}
        }
    
    def _calculate_quality_score(self, agent_results: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        # Simplified scoring - would be more sophisticated in practice
        scores = []
        
        for agent_id, results in agent_results.items():
            if isinstance(results, dict):
                if "compliance_score" in results:
                    scores.append(results["compliance_score"])
                elif "structure_score" in results:
                    scores.append(results["structure_score"])
        
        return sum(scores) / len(scores) if scores else 0.8
    
    def _calculate_security_score(self, agent_results: Dict[str, Any]) -> float:
        """Calculate security score."""
        security_results = agent_results.get("security_analysis_agent", {})
        if isinstance(security_results, dict):
            vulnerability_count = len(security_results.get("vulnerabilities", []))
            if vulnerability_count == 0:
                return 1.0
            else:
                return max(0.0, 1.0 - (vulnerability_count * 0.1))
        return 0.8
    
    def _calculate_maintainability_score(self, agent_results: Dict[str, Any]) -> float:
        """Calculate maintainability score."""
        # Simplified implementation
        return 0.75
    
    def _calculate_compliance_score(self, agent_results: Dict[str, Any]) -> float:
        """Calculate compliance score."""
        qa_results = agent_results.get("quality_assurance_agent", {})
        if isinstance(qa_results, dict):
            return qa_results.get("compliance_score", 0.8)
        return 0.8
    
    def _extract_key_findings(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from agent results."""
        findings = []
        
        for agent_id, results in agent_results.items():
            if agent_id == "security_analysis_agent" and isinstance(results, dict):
                vulnerability_count = len(results.get("vulnerabilities", []))
                if vulnerability_count > 0:
                    findings.append(f"Found {vulnerability_count} security vulnerabilities")
            
            elif agent_id == "code_analysis_agent" and isinstance(results, dict):
                if results.get("structure_score", 0) < 0.7:
                    findings.append("Code structure needs improvement")
        
        return findings
    
    def _identify_priority_actions(self, agent_results: Dict[str, Any]) -> List[str]:
        """Identify priority actions based on results."""
        actions = []
        
        # Check for critical security issues
        security_results = agent_results.get("security_analysis_agent", {})
        if isinstance(security_results, dict):
            if security_results.get("risk_level") == "HIGH":
                actions.append("Address critical security vulnerabilities immediately")
        
        # Check for major quality issues
        qa_results = agent_results.get("quality_assurance_agent", {})
        if isinstance(qa_results, dict):
            if qa_results.get("compliance_score", 1.0) < 0.7:
                actions.append("Improve coding standards compliance")
        
        return actions
    
    def learn_from_result(self, task: AgentTask, result: Dict[str, Any]) -> None:
        """Learn from report generation results."""
        pass
