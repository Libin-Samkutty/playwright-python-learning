"""
Performance Monitoring for API Tests
-------------------------------------
Track and validate API response times
"""

import time
from typing import List, Dict
import statistics


class PerformanceMonitor:
    """
    Monitor API performance
    
    Tracks:
    - Response times
    - Success/failure rates
    - Percentiles (p50, p95, p99)
    """
    
    def __init__(self):
        self.measurements: List[Dict] = []
    
    def measure_request(self, func, *args, **kwargs):
        """
        Measure request execution time
        
        Args:
            func: Function to execute (e.g., api_client.get)
            *args, **kwargs: Arguments to pass to func
        
        Returns:
            tuple: (result, elapsed_time_ms)
        """
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000
            
            self.measurements.append({
                "elapsed_ms": elapsed_ms,
                "success": True,
                "status": getattr(result, 'status', None)
            })
            
            return result, elapsed_ms
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            
            self.measurements.append({
                "elapsed_ms": elapsed_ms,
                "success": False,
                "error": str(e)
            })
            
            raise
    
    def get_statistics(self) -> Dict:
        """
        Calculate performance statistics
        
        Returns:
            dict: Performance metrics
        """
        if not self.measurements:
            return {}
        
        times = [m["elapsed_ms"] for m in self.measurements]
        successes = [m for m in self.measurements if m["success"]]
        failures = [m for m in self.measurements if not m["success"]]
        
        return {
            "total_requests": len(self.measurements),
            "successful_requests": len(successes),
            "failed_requests": len(failures),
            "success_rate": len(successes) / len(self.measurements) * 100,
            "min_ms": min(times),
            "max_ms": max(times),
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "p95_ms": self._percentile(times, 95),
            "p99_ms": self._percentile(times, 99),
        }
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def assert_performance(
        self,
        max_mean_ms=None,
        max_p95_ms=None,
        max_p99_ms=None,
        min_success_rate=None
    ):
        """
        Assert performance meets SLA requirements
        
        Args:
            max_mean_ms: Maximum acceptable mean response time
            max_p95_ms: Maximum acceptable p95 response time
            max_p99_ms: Maximum acceptable p99 response time
            min_success_rate: Minimum acceptable success rate (0-100)
        
        Raises:
            AssertionError: If performance requirements not met
        """
        stats = self.get_statistics()
        
        if max_mean_ms and stats["mean_ms"] > max_mean_ms:
            raise AssertionError(
                f"Mean response time {stats['mean_ms']:.2f}ms exceeds limit {max_mean_ms}ms"
            )
        
        if max_p95_ms and stats["p95_ms"] > max_p95_ms:
            raise AssertionError(
                f"P95 response time {stats['p95_ms']:.2f}ms exceeds limit {max_p95_ms}ms"
            )
        
        if max_p99_ms and stats["p99_ms"] > max_p99_ms:
            raise AssertionError(
                f"P99 response time {stats['p99_ms']:.2f}ms exceeds limit {max_p99_ms}ms"
            )
        
        if min_success_rate and stats["success_rate"] < min_success_rate:
            raise AssertionError(
                f"Success rate {stats['success_rate']:.2f}% below minimum {min_success_rate}%"
            )
    
    def print_report(self):
        """Print performance report"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("PERFORMANCE REPORT")
        print("="*60)
        print(f"Total Requests:       {stats['total_requests']}")
        print(f"Successful:           {stats['successful_requests']}")
        print(f"Failed:               {stats['failed_requests']}")
        print(f"Success Rate:         {stats['success_rate']:.2f}%")
        print("-"*60)
        print(f"Min Response Time:    {stats['min_ms']:.2f} ms")
        print(f"Max Response Time:    {stats['max_ms']:.2f} ms")
        print(f"Mean Response Time:   {stats['mean_ms']:.2f} ms")
        print(f"Median Response Time: {stats['median_ms']:.2f} ms")
        print(f"P95 Response Time:    {stats['p95_ms']:.2f} ms")
        print(f"P99 Response Time:    {stats['p99_ms']:.2f} ms")
        print("="*60 + "\n")


class ResponseTimeValidator:
    """
    Simple response time validation
    
    For quick checks in individual tests
    """
    
    @staticmethod
    def assert_response_time(response_time_ms, max_ms, message=None):
        """
        Assert response time is within limit
        
        Args:
            response_time_ms: Actual response time
            max_ms: Maximum acceptable time
            message: Custom error message
        """
        msg = message or f"Response time {response_time_ms:.2f}ms exceeds limit {max_ms}ms"
        assert response_time_ms <= max_ms, msg
    
    @staticmethod
    def measure_and_validate(func, max_ms, *args, **kwargs):
        """
        Measure and validate in one call
        
        Usage:
            response = ResponseTimeValidator.measure_and_validate(
                api_client.get, 500, "/posts/1"
            )
        """
        start = time.time()
        result = func(*args, **kwargs)
        elapsed_ms = (time.time() - start) * 1000
        
        ResponseTimeValidator.assert_response_time(elapsed_ms, max_ms)
        
        return result
