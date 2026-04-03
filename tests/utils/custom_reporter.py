"""
tests/utils/custom_reporter.py
Custom reporting solution combining all artifacts
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict
import html


@dataclass
class TestResult:
    """Single test result"""
    
    name: str
    status: str  # passed, failed, skipped
    duration: float
    error_message: str = ""
    screenshot_path: str = ""
    video_path: str = ""
    trace_path: str = ""
    steps: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TestReport:
    """Complete test report"""
    
    title: str
    timestamp: str
    duration: float
    total: int
    passed: int
    failed: int
    skipped: int
    tests: List[TestResult] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)


class CustomReporter:
    """
    Custom test reporter that generates comprehensive reports
    
    Features:
    - JSON report
    - HTML report
    - Summary statistics
    - Embedded screenshots
    """
    
    def __init__(
        self,
        report_dir: str = "reports/custom",
        title: str = "Test Report",
    ):
        self.report_dir = Path(report_dir)
        self.title = title
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
        
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def add_result(self, result: TestResult):
        """Add a test result"""
        self.results.append(result)
    
    def create_result(
        self,
        name: str,
        status: str,
        duration: float,
        **kwargs,
    ) -> TestResult:
        """Create and add a test result"""
        
        result = TestResult(
            name=name,
            status=status,
            duration=duration,
            **kwargs,
        )
        self.add_result(result)
        return result
    
    def generate_report(self) -> TestReport:
        """Generate the complete report"""
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        report = TestReport(
            title=self.title,
            timestamp=self.start_time.isoformat(),
            duration=total_duration,
            total=len(self.results),
            passed=sum(1 for r in self.results if r.status == "passed"),
            failed=sum(1 for r in self.results if r.status == "failed"),
            skipped=sum(1 for r in self.results if r.status == "skipped"),
            tests=self.results,
            environment={
                "Python": os.sys.version,
                "Platform": os.sys.platform,
                "User": os.environ.get("USER", "Unknown"),
            },
        )
        
        return report
    
    def save_json(self, report: TestReport = None) -> str:
        """Save report as JSON"""
        
        report = report or self.generate_report()
        
        json_path = self.report_dir / "report.json"
        
        with open(json_path, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        return str(json_path)
    
    def save_html(self, report: TestReport = None) -> str:
        """Save report as HTML"""
        
        report = report or self.generate_report()
        
        html_path = self.report_dir / "report.html"
        
        html_content = self._generate_html(report)
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return str(html_path)
    
    def _generate_html(self, report: TestReport) -> str:
        """Generate HTML report content"""
        
        # Calculate pass rate
        pass_rate = (report.passed / report.total * 100) if report.total > 0 else 0
        
        # Generate test rows
        test_rows = []
        for test in report.tests:
            status_class = test.status
            status_icon = {
                "passed": "[PASS]",
                "failed": "[FAIL]",
                "skipped": "[SKIP]",
            }.get(test.status, "[?]")
            
            # Screenshot embed
            screenshot_html = ""
            if test.screenshot_path and os.path.exists(test.screenshot_path):
                import base64
                with open(test.screenshot_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                screenshot_html = f'''
                <details>
                    <summary>Screenshot</summary>
                    <img src="data:image/png;base64,{img_data}" style="max-width: 800px;">
                </details>
                '''
            
            # Error message
            error_html = ""
            if test.error_message:
                error_html = f'''
                <details>
                    <summary>Error</summary>
                    <pre class="error">{html.escape(test.error_message)}</pre>
                </details>
                '''
            
            # Steps
            steps_html = ""
            if test.steps:
                steps_list = "\n".join(f"<li>{html.escape(step)}</li>" for step in test.steps)
                steps_html = f'''
                <details>
                    <summary>Steps ({len(test.steps)})</summary>
                    <ol>{steps_list}</ol>
                </details>
                '''
            
            test_rows.append(f'''
            <tr class="{status_class}">
                <td>{status_icon} {html.escape(test.name)}</td>
                <td class="status-{test.status}">{test.status.upper()}</td>
                <td>{test.duration:.2f}s</td>
                <td>
                    {screenshot_html}
                    {error_html}
                    {steps_html}
                </td>
            </tr>
            ''')
        
        # Environment info
        env_rows = "\n".join(
            f"<tr><td>{k}</td><td>{v}</td></tr>"
            for k, v in report.environment.items()
        )
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{html.escape(report.title)}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                .summary {{
                    display: flex;
                    gap: 20px;
                    margin: 20px 0;
                }}
                .summary-card {{
                    flex: 1;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .summary-card.total {{ background: #3498db; color: white; }}
                .summary-card.passed {{ background: #27ae60; color: white; }}
                .summary-card.failed {{ background: #e74c3c; color: white; }}
                .summary-card.skipped {{ background: #f39c12; color: white; }}
                .summary-card h2 {{ margin: 0; font-size: 36px; }}
                .summary-card p {{ margin: 5px 0 0; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background: #3498db;
                    color: white;
                }}
                .passed {{ background: #d4edda; }}
                .failed {{ background: #f8d7da; }}
                .skipped {{ background: #fff3cd; }}
                .status-passed {{ color: #155724; font-weight: bold; }}
                .status-failed {{ color: #721c24; font-weight: bold; }}
                .status-skipped {{ color: #856404; font-weight: bold; }}
                details {{
                    margin: 5px 0;
                }}
                summary {{
                    cursor: pointer;
                    color: #3498db;
                }}
                pre.error {{
                    background: #f8d7da;
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                }}
                img {{
                    border: 2px solid #ddd;
                    border-radius: 4px;
                    margin: 10px 0;
                }}
                .progress-bar {{
                    height: 20px;
                    background: #ddd;
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 10px 0;
                }}
                .progress-bar .fill {{
                    height: 100%;
                    background: #27ae60;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{html.escape(report.title)}</h1>
                
                <p>Generated: {report.timestamp}</p>
                <p>Duration: {report.duration:.2f} seconds</p>
                
                <div class="summary">
                    <div class="summary-card total">
                        <h2>{report.total}</h2>
                        <p>Total Tests</p>
                    </div>
                    <div class="summary-card passed">
                        <h2>{report.passed}</h2>
                        <p>Passed</p>
                    </div>
                    <div class="summary-card failed">
                        <h2>{report.failed}</h2>
                        <p>Failed</p>
                    </div>
                    <div class="summary-card skipped">
                        <h2>{report.skipped}</h2>
                        <p>Skipped</p>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="fill" style="width: {pass_rate}%"></div>
                </div>
                <p>Pass Rate: {pass_rate:.1f}%</p>
                
                <h2>Test Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Test Name</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(test_rows)}
                    </tbody>
                </table>
                
                <h2>Environment</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        {env_rows}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        '''
    
    def print_summary(self, report: TestReport = None):
        """Print summary to console"""
        
        report = report or self.generate_report()
        
        print("\n" + "=" * 60)
        print(f"{report.title}")
        print("=" * 60)
        print(f"Duration: {report.duration:.2f}s")
        print(f"Total: {report.total}")
        print(f"Passed: {report.passed}")
        print(f"Failed: {report.failed}")
        print(f"Skipped: {report.skipped}")

        if report.total > 0:
            pass_rate = report.passed / report.total * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        
        print("=" * 60)
        
        # Print failed tests
        failed_tests = [t for t in report.tests if t.status == "failed"]
        if failed_tests:
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test.name}")
                if test.error_message:
                    # Print first line of error
                    first_line = test.error_message.split("\n")[0][:80]
                    print(f"    Error: {first_line}...")