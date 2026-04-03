"""
scripts/maintenance.py
Test maintenance utilities
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re


class TestMaintenance:
    """
    Utilities for maintaining test suite
    
    Features:
    - Cleanup old artifacts
    - Find unused page objects
    - Detect duplicate tests
    - Generate test documentation
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
    
    def cleanup_artifacts(
        self,
        max_age_days: int = 7,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Clean up old test artifacts
        
        Args:
            max_age_days: Delete artifacts older than this
            dry_run: If True, only report what would be deleted
        
        Returns:
            Cleanup statistics
        """
        
        cutoff = datetime.now() - timedelta(days=max_age_days)
        cutoff_timestamp = cutoff.timestamp()
        
        artifact_dirs = [
            "artifacts/screenshots",
            "artifacts/videos",
            "artifacts/traces",
            "reports/html",
            "reports/allure-results",
        ]
        
        stats = {
            "files_found": 0,
            "files_deleted": 0,
            "bytes_freed": 0,
            "directories_cleaned": [],
        }
        
        for dir_path in artifact_dirs:
            full_path = self.project_root / dir_path
            
            if not full_path.exists():
                continue
            
            for file_path in full_path.rglob("*"):
                if not file_path.is_file():
                    continue
                
                stats["files_found"] += 1
                
                # Check file age
                if file_path.stat().st_mtime < cutoff_timestamp:
                    file_size = file_path.stat().st_size
                    
                    if dry_run:
                        print(f"Would delete: {file_path} ({file_size} bytes)")
                    else:
                        file_path.unlink()
                        print(f"Deleted: {file_path}")
                    
                    stats["files_deleted"] += 1
                    stats["bytes_freed"] += file_size
            
            if not dry_run:
                stats["directories_cleaned"].append(dir_path)
        
        # Convert bytes to MB
        stats["mb_freed"] = round(stats["bytes_freed"] / (1024 * 1024), 2)
        
        return stats
    
    def find_unused_page_objects(self) -> List[str]:
        """
        Find page objects not imported in any test
        
        Returns:
            List of potentially unused page objects
        """
        
        pages_dir = self.project_root / "pages"
        tests_dir = self.project_root / "tests"
        
        if not pages_dir.exists() or not tests_dir.exists():
            return []
        
        # Find all page classes
        page_classes = set()
        
        for py_file in pages_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            content = py_file.read_text()
            
            # Find class definitions
            classes = re.findall(r"class\s+(\w+Page)\s*[\(:]", content)
            page_classes.update(classes)
        
        # Find imports in tests
        used_classes = set()
        
        for py_file in tests_dir.rglob("*.py"):
            content = py_file.read_text()
            
            for page_class in page_classes:
                if page_class in content:
                    used_classes.add(page_class)
        
        unused = page_classes - used_classes
        
        return sorted(list(unused))
    
    def find_duplicate_tests(self) -> List[Dict[str, Any]]:
        """
        Find potentially duplicate tests
        
        Returns:
            List of potential duplicates
        """
        
        tests_dir = self.project_root / "tests"
        
        if not tests_dir.exists():
            return []
        
        test_signatures: Dict[str, List[str]] = {}
        
        for py_file in tests_dir.rglob("test_*.py"):
            content = py_file.read_text()
            
            # Find test functions
            tests = re.findall(
                r"def\s+(test_\w+)\s*\([^)]*\):\s*\n((?:\s+.*\n)*)",
                content
            )
            
            for test_name, test_body in tests:
                # Normalize body (remove whitespace, comments)
                normalized = re.sub(r"#.*$", "", test_body, flags=re.MULTILINE)
                normalized = re.sub(r"\s+", " ", normalized).strip()
                
                # Hash the body
                body_hash = hash(normalized)
                
                key = f"{body_hash}"
                
                if key not in test_signatures:
                    test_signatures[key] = []
                
                test_signatures[key].append(f"{py_file}::{test_name}")
        
        duplicates = []
        
        for key, tests in test_signatures.items():
            if len(tests) > 1:
                duplicates.append({
                    "tests": tests,
                    "count": len(tests),
                })
        
        return duplicates
    
    def generate_test_docs(self, output_file: str = "docs/tests.md"):
        """
        Generate markdown documentation for tests
        
        Args:
            output_file: Output file path
        """
        
        tests_dir = self.project_root / "tests"
        output_path = self.project_root / output_file
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        docs = ["# Test Documentation\n"]
        docs.append(f"Generated: {datetime.now().isoformat()}\n\n")
        
        # Group tests by directory
        test_structure: Dict[str, List[Dict]] = {}
        
        for py_file in sorted(tests_dir.rglob("test_*.py")):
            relative_path = py_file.relative_to(tests_dir)
            category = str(relative_path.parent) if relative_path.parent != Path(".") else "root"
            
            if category not in test_structure:
                test_structure[category] = []
            
            content = py_file.read_text()
            
            # Extract module docstring
            module_doc_match = re.match(r'^"""(.*?)"""', content, re.DOTALL)
            module_doc = module_doc_match.group(1).strip() if module_doc_match else ""
            
            # Find test functions with docstrings
            tests = re.findall(
                r'def\s+(test_\w+)\s*\([^)]*\):\s*\n\s*"""(.*?)"""',
                content,
                re.DOTALL
            )
            
            test_structure[category].append({
                "file": str(relative_path),
                "module_doc": module_doc,
                "tests": [
                    {"name": name, "doc": doc.strip()}
                    for name, doc in tests
                ],
            })
        
        # Generate markdown
        for category, files in sorted(test_structure.items()):
            docs.append(f"## {category.replace('/', ' / ').title()}\n\n")
            
            for file_info in files:
                docs.append(f"### {file_info['file']}\n\n")
                
                if file_info["module_doc"]:
                    docs.append(f"{file_info['module_doc']}\n\n")
                
                if file_info["tests"]:
                    docs.append("| Test | Description |\n")
                    docs.append("|------|-------------|\n")
                    
                    for test in file_info["tests"]:
                        # Get first line of docstring
                        first_line = test["doc"].split("\n")[0]
                        docs.append(f"| `{test['name']}` | {first_line} |\n")
                    
                    docs.append("\n")
        
        output_path.write_text("".join(docs))
        print(f"Documentation generated: {output_path}")
    
    def check_test_naming(self) -> List[Dict[str, Any]]:
        """
        Check test naming conventions
        
        Returns:
            List of naming issues
        """
        
        tests_dir = self.project_root / "tests"
        issues = []
        
        # Naming conventions
        patterns = {
            "test_function": r"^test_[a-z][a-z0-9_]*$",
            "test_class": r"^Test[A-Z][a-zA-Z0-9]*$",
            "test_file": r"^test_[a-z][a-z0-9_]*\.py$",
        }
        
        for py_file in tests_dir.rglob("test_*.py"):
            # Check file name
            if not re.match(patterns["test_file"], py_file.name):
                issues.append({
                    "file": str(py_file),
                    "type": "file_name",
                    "issue": f"File name doesn't match pattern: {py_file.name}",
                })
            
            content = py_file.read_text()
            
            # Check class names
            classes = re.findall(r"class\s+(\w+)\s*[\(:]", content)
            for class_name in classes:
                if class_name.startswith("Test") and not re.match(
                    patterns["test_class"], class_name
                ):
                    issues.append({
                        "file": str(py_file),
                        "type": "class_name",
                        "issue": f"Class name doesn't match pattern: {class_name}",
                    })
            
            # Check function names
            functions = re.findall(r"def\s+(test_\w+)\s*\(", content)
            for func_name in functions:
                if not re.match(patterns["test_function"], func_name):
                    issues.append({
                        "file": str(py_file),
                        "type": "function_name",
                        "issue": f"Function name doesn't match pattern: {func_name}",
                    })
        
        return issues
    
    def run_full_maintenance(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Run all maintenance checks
        
        Args:
            dry_run: If True, don't make changes
        
        Returns:
            Complete maintenance report
        """
        
        print("Running test maintenance checks...\n")

        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
        }

        # Cleanup
        print("Checking artifacts...")
        report["cleanup"] = self.cleanup_artifacts(dry_run=dry_run)
        print(f"   Files to clean: {report['cleanup']['files_deleted']}")
        print(f"   Space to free: {report['cleanup']['mb_freed']} MB\n")

        # Unused page objects
        print("Checking for unused page objects...")
        report["unused_pages"] = self.find_unused_page_objects()
        print(f"   Found: {len(report['unused_pages'])}\n")

        # Duplicates
        print("Checking for duplicate tests...")
        report["duplicates"] = self.find_duplicate_tests()
        print(f"   Found: {len(report['duplicates'])}\n")

        # Naming
        print("Checking naming conventions...")
        report["naming_issues"] = self.check_test_naming()
        print(f"   Issues: {len(report['naming_issues'])}\n")
        
        return report


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Maintenance Utilities")
    parser.add_argument(
        "action",
        choices=["cleanup", "unused", "duplicates", "naming", "docs", "full"],
        help="Maintenance action to perform"
    )
    parser.add_argument("--dry-run", action="store_true", help="Don't make changes")
    parser.add_argument("--days", type=int, default=7, help="Max age for cleanup")
    
    args = parser.parse_args()
    
    maintenance = TestMaintenance()
    
    if args.action == "cleanup":
        stats = maintenance.cleanup_artifacts(
            max_age_days=args.days,
            dry_run=args.dry_run
        )
        print(f"\nCleanup complete: {stats}")
    
    elif args.action == "unused":
        unused = maintenance.find_unused_page_objects()
        print(f"\nPotentially unused page objects:")
        for page in unused:
            print(f"  - {page}")
    
    elif args.action == "duplicates":
        duplicates = maintenance.find_duplicate_tests()
        print(f"\nPotential duplicate tests:")
        for dup in duplicates:
            print(f"  - {dup['tests']}")
    
    elif args.action == "naming":
        issues = maintenance.check_test_naming()
        print(f"\nNaming convention issues:")
        for issue in issues:
            print(f"  - {issue['file']}: {issue['issue']}")
    
    elif args.action == "docs":
        maintenance.generate_test_docs()
    
    elif args.action == "full":
        report = maintenance.run_full_maintenance(dry_run=args.dry_run)
        print(f"\nFull report: {report}")