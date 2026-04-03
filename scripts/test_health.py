"""
scripts/test_health.py
Monitor test health and identify issues
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics


class TestHealthMonitor:
    """
    Analyze test execution history for health metrics
    
    Tracks:
    - Flaky tests
    - Slow tests
    - Failure trends
    - Test coverage gaps
    """
    
    def __init__(self, history_dir: str = "reports/history"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def record_run(self, results: List[Dict[str, Any]]):
        """
        Record a test run
        
        Args:
            results: List of test results with name, status, duration
        """
        
        timestamp = datetime.now().isoformat()
        filename = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "timestamp": timestamp,
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.get("status") == "passed"),
            "failed": sum(1 for r in results if r.get("status") == "failed"),
            "skipped": sum(1 for r in results if r.get("status") == "skipped"),
            "total_duration": sum(r.get("duration", 0) for r in results),
            "results": results,
        }
        
        with open(self.history_dir / filename, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_history(self, days: int = 7) -> List[Dict]:
        """Load test history for specified days"""
        
        cutoff = datetime.now() - timedelta(days=days)
        history = []
        
        for file in sorted(self.history_dir.glob("run_*.json")):
            try:
                with open(file) as f:
                    data = json.load(f)
                
                run_time = datetime.fromisoformat(data["timestamp"])
                
                if run_time >= cutoff:
                    history.append(data)
            except Exception:
                continue
        
        return history
    
    def identify_flaky_tests(
        self,
        days: int = 7,
        threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Identify flaky tests
        
        A test is flaky if it has both passes and failures
        
        Args:
            days: History to analyze
            threshold: Minimum failure rate to consider flaky
        
        Returns:
            List of flaky tests with stats
        """
        
        history = self.load_history(days)
        
        test_stats: Dict[str, Dict] = defaultdict(
            lambda: {"passed": 0, "failed": 0, "durations": []}
        )
        
        for run in history:
            for result in run.get("results", []):
                name = result["name"]
                status = result["status"]
                duration = result.get("duration", 0)
                
                if status == "passed":
                    test_stats[name]["passed"] += 1
                elif status == "failed":
                    test_stats[name]["failed"] += 1
                
                test_stats[name]["durations"].append(duration)
        
        flaky_tests = []
        
        for name, stats in test_stats.items():
            total = stats["passed"] + stats["failed"]
            
            if total == 0:
                continue
            
            failure_rate = stats["failed"] / total
            
            # Flaky = has both passes and failures
            if stats["passed"] > 0 and stats["failed"] > 0:
                if failure_rate >= threshold:
                    flaky_tests.append({
                        "name": name,
                        "passed": stats["passed"],
                        "failed": stats["failed"],
                        "total_runs": total,
                        "failure_rate": round(failure_rate * 100, 1),
                        "avg_duration": round(statistics.mean(stats["durations"]), 2),
                    })
        
        return sorted(flaky_tests, key=lambda x: x["failure_rate"], reverse=True)
    
    def identify_slow_tests(
        self,
        days: int = 7,
        threshold_seconds: float = 30
    ) -> List[Dict[str, Any]]:
        """
        Identify slow tests
        
        Args:
            days: History to analyze
            threshold_seconds: Tests slower than this are flagged
        
        Returns:
            List of slow tests with average duration
        """
        
        history = self.load_history(days)
        
        test_durations: Dict[str, List[float]] = defaultdict(list)
        
        for run in history:
            for result in run.get("results", []):
                name = result["name"]
                duration = result.get("duration", 0)
                test_durations[name].append(duration)
        
        slow_tests = []
        
        for name, durations in test_durations.items():
            avg_duration = statistics.mean(durations)
            
            if avg_duration >= threshold_seconds:
                slow_tests.append({
                    "name": name,
                    "avg_duration": round(avg_duration, 2),
                    "max_duration": round(max(durations), 2),
                    "min_duration": round(min(durations), 2),
                    "run_count": len(durations),
                    "std_dev": round(statistics.stdev(durations), 2) if len(durations) > 1 else 0,
                })
        
        return sorted(slow_tests, key=lambda x: x["avg_duration"], reverse=True)
    
    def get_failure_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze failure trends over time
        
        Returns:
            Dictionary with trend analysis
        """
        
        history = self.load_history(days)
        
        if not history:
            return {"error": "No history available"}
        
        daily_stats = defaultdict(lambda: {"passed": 0, "failed": 0, "total": 0})
        
        for run in history:
            date = datetime.fromisoformat(run["timestamp"]).strftime("%Y-%m-%d")
            daily_stats[date]["passed"] += run.get("passed", 0)
            daily_stats[date]["failed"] += run.get("failed", 0)
            daily_stats[date]["total"] += run.get("total_tests", 0)
        
        # Calculate daily pass rates
        daily_pass_rates = []
        for date in sorted(daily_stats.keys()):
            stats = daily_stats[date]
            total = stats["passed"] + stats["failed"]
            pass_rate = (stats["passed"] / total * 100) if total > 0 else 0
            daily_pass_rates.append({
                "date": date,
                "pass_rate": round(pass_rate, 1),
                "passed": stats["passed"],
                "failed": stats["failed"],
            })
        
        # Calculate trend
        if len(daily_pass_rates) >= 2:
            first_rate = daily_pass_rates[0]["pass_rate"]
            last_rate = daily_pass_rates[-1]["pass_rate"]
            trend = "improving" if last_rate > first_rate else (
                "declining" if last_rate < first_rate else "stable"
            )
        else:
            trend = "insufficient_data"
        
        return {
            "daily_stats": daily_pass_rates,
            "trend": trend,
            "average_pass_rate": round(
                statistics.mean(d["pass_rate"] for d in daily_pass_rates), 1
            ),
            "total_runs": len(history),
        }
    
    def get_most_failing_tests(
        self,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get tests with most failures
        
        Args:
            days: History to analyze
            limit: Number of tests to return
        
        Returns:
            List of failing tests sorted by failure count
        """
        
        history = self.load_history(days)
        
        failure_counts: Dict[str, Dict] = defaultdict(
            lambda: {"failures": 0, "total": 0, "error_messages": []}
        )
        
        for run in history:
            for result in run.get("results", []):
                name = result["name"]
                status = result["status"]
                
                failure_counts[name]["total"] += 1
                
                if status == "failed":
                    failure_counts[name]["failures"] += 1
                    if result.get("error_message"):
                        failure_counts[name]["error_messages"].append(
                            result["error_message"][:200]  # Truncate
                        )
        
        failing_tests = []
        
        for name, stats in failure_counts.items():
            if stats["failures"] > 0:
                failing_tests.append({
                    "name": name,
                    "failures": stats["failures"],
                    "total_runs": stats["total"],
                    "failure_rate": round(stats["failures"] / stats["total"] * 100, 1),
                    "recent_errors": stats["error_messages"][-3],  # Last 3 errors
                })
        
        return sorted(
            failing_tests, 
            key=lambda x: x["failures"], 
            reverse=True
        )[:limit]
    
    def generate_health_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive health report
        
        Args:
            days: History to analyze
        
        Returns:
            Complete health report
        """
        
        return {
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days,
            "flaky_tests": self.identify_flaky_tests(days),
            "slow_tests": self.identify_slow_tests(days),
            "most_failing": self.get_most_failing_tests(days),
            "trends": self.get_failure_trends(days),
        }
    
    def print_health_report(self, days: int = 7):
        """Print formatted health report to console"""
        
        report = self.generate_health_report(days)
        
        print("\n" + "=" * 70)
        print("TEST HEALTH REPORT")
        print(f"   Analysis Period: Last {days} days")
        print(f"   Generated: {report['generated_at']}")
        print("=" * 70)
        
        # Trends
        trends = report["trends"]
        print(f"\nTRENDS")
        print(f"   Total Runs: {trends.get('total_runs', 0)}")
        print(f"   Average Pass Rate: {trends.get('average_pass_rate', 0)}%")
        print(f"   Trend: {trends.get('trend', 'unknown').upper()}")
        
        # Flaky tests
        flaky = report["flaky_tests"]
        print(f"\nFLAKY TESTS ({len(flaky)} found)")
        if flaky:
            for test in flaky[:5]:
                print(f"   - {test['name']}")
                print(f"     Failure Rate: {test['failure_rate']}% "
                      f"({test['failed']}/{test['total_runs']} runs)")
        else:
            print("   No flaky tests detected!")
        
        # Slow tests
        slow = report["slow_tests"]
        print(f"\nSLOW TESTS ({len(slow)} found)")
        if slow:
            for test in slow[:5]:
                print(f"   - {test['name']}")
                print(f"     Avg Duration: {test['avg_duration']}s "
                      f"(max: {test['max_duration']}s)")
        else:
            print("   No slow tests detected!")
        
        # Most failing
        failing = report["most_failing"]
        print(f"\nMOST FAILING TESTS ({len(failing)} with failures)")
        if failing:
            for test in failing[:5]:
                print(f"   - {test['name']}")
                print(f"     Failures: {test['failures']}/{test['total_runs']} "
                      f"({test['failure_rate']}%)")
        
        print("\n" + "=" * 70)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Health Monitor")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    parser.add_argument("--output", type=str, help="Output JSON file")
    
    args = parser.parse_args()
    
    monitor = TestHealthMonitor()
    
    if args.output:
        report = monitor.generate_health_report(args.days)
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.output}")
    else:
        monitor.print_health_report(args.days)