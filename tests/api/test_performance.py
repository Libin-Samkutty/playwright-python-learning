"""
Module 5 - Part 3B: Performance Testing
----------------------------------------
Validate API performance and response times
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state

sys.path.insert(0, os.path.dirname(__file__))
from helpers.performance_monitor import PerformanceMonitor, ResponseTimeValidator


def test_single_request_performance():
    """
    LESSON: Measuring single request performance
    
    Validates individual request meets SLA
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        # Measure request time
        start_time = time.time()
        
        response = request_context.get("/posts/1")
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Validate response
        assert response.status == 200
        
        # Validate performance (API should respond in < 2000ms)
        ResponseTimeValidator.assert_response_time(
            elapsed_ms,
            max_ms=2000,
            message=f"GET /posts/1 too slow: {elapsed_ms:.2f}ms"
        )
        
        print(f"✅ Request completed in {elapsed_ms:.2f}ms")
        
    finally:
        request_context.dispose()


def test_multiple_requests_performance():
    """
    LESSON: Load testing with performance monitoring
    
    Makes multiple requests and validates aggregate performance
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    monitor = PerformanceMonitor()
    
    try:
        print("\n🔄 Making 20 requests...")
        
        # Make 20 requests
        for i in range(1, 21):
            response, elapsed = monitor.measure_request(
                request_context.get,
                f"/posts/{i}"
            )
            
            assert response.status == 200
            print(f"  Request {i:2d}: {elapsed:6.2f}ms")
        
        # Print performance report
        monitor.print_report()
        
        # Assert performance requirements (SLA)
        monitor.assert_performance(
            max_mean_ms=1000,      # Mean < 1 second
            max_p95_ms=2000,       # P95 < 2 seconds
            min_success_rate=95    # 95% success rate
        )
        
        print("✅ Performance SLA met!")
        
    finally:
        request_context.dispose()


def test_concurrent_requests_simulation():
    """
    LESSON: Simulating concurrent users
    
    Tests API under concurrent load
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    monitor = PerformanceMonitor()
    
    try:
        print("\n👥 Simulating 10 concurrent users (sequential for demo)...")
        
        # In real concurrent testing, use threading or asyncio
        # Here we simulate by making rapid sequential requests
        
        endpoints = [
            "/posts/1", "/posts/2", "/posts/3",
            "/users/1", "/users/2", "/users/3",
            "/comments/1", "/comments/2", "/comments/3",
            "/albums/1"
        ]
        
        for endpoint in endpoints:
            response, elapsed = monitor.measure_request(
                request_context.get,
                endpoint
            )
            print(f"  {endpoint:15} - {elapsed:6.2f}ms - Status {response.status}")
        
        monitor.print_report()
        
        # Validate
        stats = monitor.get_statistics()
        assert stats["success_rate"] == 100, "All requests should succeed"
        
        print("✅ Concurrent load test passed!")
        
    finally:
        request_context.dispose()


def test_pagination_performance():
    """
    LESSON: Testing paginated endpoint performance
    
    Validates performance doesn't degrade with pagination
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    monitor = PerformanceMonitor()
    
    try:
        print("\n📄 Testing pagination performance...")
        
        # Test multiple pages
        for page in range(0, 50, 10):  # Pages 0, 10, 20, 30, 40
            response, elapsed = monitor.measure_request(
                request_context.get,
                f"/products?limit=10&skip={page}"
            )
            
            data = response.json()
            print(f"  Page skip={page:2d}: {elapsed:6.2f}ms - {len(data['products'])} products")
        
        monitor.print_report()
        
        # Assert pagination doesn't slow down
        stats = monitor.get_statistics()
        assert stats["max_ms"] < 3000, "No page should take > 3 seconds"
        
        print("✅ Pagination performance acceptable!")
        
    finally:
        request_context.dispose()


def test_search_performance():
    """
    LESSON: Testing search endpoint performance
    
    Search queries can be slow, validate performance
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    monitor = PerformanceMonitor()
    
    try:
        print("\n🔍 Testing search performance...")
        
        search_queries = ["phone", "laptop", "watch", "perfume", "bag"]
        
        for query in search_queries:
            response, elapsed = monitor.measure_request(
                request_context.get,
                f"/products/search?q={query}"
            )
            
            results = response.json()
            count = len(results.get("products", []))
            
            print(f"  Search '{query:10}': {elapsed:6.2f}ms - {count} results")
        
        monitor.print_report()
        
        # Search should be fast
        monitor.assert_performance(
            max_mean_ms=800,
            max_p95_ms=1500
        )
        
        print("✅ Search performance meets SLA!")
        
    finally:
        request_context.dispose()


def test_authentication_performance():
    """
    LESSON: Testing auth endpoint performance
    
    Login should be fast for good UX
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        credentials = {
            "username": "emilys",
            "password": "emilyspass"
        }
        
        # Measure login time
        start = time.time()
        
        response = request_context.post(
            "/auth/login",
            data=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        elapsed_ms = (time.time() - start) * 1000
        
        assert response.status == 200
        
        # Login should be very fast (< 1 second for good UX)
        ResponseTimeValidator.assert_response_time(
            elapsed_ms,
            max_ms=1000,
            message=f"Login too slow for good UX: {elapsed_ms:.2f}ms"
        )
        
        print(f"✅ Login completed in {elapsed_ms:.2f}ms (good UX)")
        
    finally:
        request_context.dispose()


@pytest.mark.slow
def test_stress_test():
    """
    LESSON: Stress testing
    
    Make many requests to test API under load
    
    Mark as 'slow' so it can be skipped in CI:
    pytest -m "not slow"
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    monitor = PerformanceMonitor()
    
    try:
        print("\n⚡ Stress test: 50 requests...")
        
        for i in range(50):
            post_id = (i % 100) + 1  # Cycle through posts 1-100
            
            response, elapsed = monitor.measure_request(
                request_context.get,
                f"/posts/{post_id}"
            )
            
            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/50 requests...")
        
        monitor.print_report()
        
        # Under stress, require:
        # - 95% success rate
        # - P95 < 3 seconds
        monitor.assert_performance(
            max_p95_ms=3000,
            min_success_rate=95
        )
        
        print("✅ Stress test passed!")
        
    finally:
        request_context.dispose()


def test_response_time_degradation():
    """
    LESSON: Detecting performance degradation
    
    Compare current performance vs baseline
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    monitor = PerformanceMonitor()
    
    try:
        # Make 10 requests
        for i in range(1, 11):
            monitor.measure_request(request_context.get, f"/posts/{i}")
        
        stats = monitor.get_statistics()
        
        # Baseline from previous test run (example)
        baseline_mean_ms = 300
        
        # Alert if performance degraded by > 50%
        degradation_threshold = baseline_mean_ms * 1.5
        
        if stats["mean_ms"] > degradation_threshold:
            print(f"⚠️  WARNING: Performance degraded!")
            print(f"   Baseline: {baseline_mean_ms}ms")
            print(f"   Current:  {stats['mean_ms']:.2f}ms")
            print(f"   Degradation: {((stats['mean_ms'] / baseline_mean_ms) - 1) * 100:.1f}%")
        else:
            print(f"✅ Performance stable (within {degradation_threshold}ms)")
        
    finally:
        request_context.dispose()
