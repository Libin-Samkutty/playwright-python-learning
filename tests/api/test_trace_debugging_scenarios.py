"""
Advanced Tracing Scenarios
---------------------------
Real-world debugging scenarios using tracing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from helpers.trace_manager import SimpleTracer, APITraceManager


def test_debug_401_unauthorized():
    """
    SCENARIO: Debugging 401 Unauthorized errors
    
    Common causes visible in trace:
    1. Missing Authorization header
    2. Wrong token format (Bearer vs Basic)
    3. Expired token
    4. Wrong token value
    """
    
    with SimpleTracer("debug_401") as api_context:
        # Intentionally WRONG auth - trace will show why it fails
        
        # Mistake 1: Missing header entirely
        response1 = api_context.get("https://dummyjson.com/auth/me")
        print(f"No header: Status {response1.status}")
        
        # Mistake 2: Wrong header format
        response2 = api_context.get(
            "https://dummyjson.com/auth/me",
            headers={"Authorization": "wrong_format_token"}
        )
        print(f"Wrong format: Status {response2.status}")
        
        # Mistake 3: Wrong header name
        response3 = api_context.get(
            "https://dummyjson.com/auth/me",
            headers={"Auth": "Bearer some_token"}  # Wrong header name!
        )
        print(f"Wrong header name: Status {response3.status}")
        
        print("\n📋 Check trace to see all request headers!")


def test_debug_400_bad_request():
    """
    SCENARIO: Debugging 400 Bad Request errors
    
    Common causes visible in trace:
    1. Invalid JSON in body
    2. Missing required fields
    3. Wrong data types
    """
    
    with SimpleTracer("debug_400") as api_context:
        # Mistake: Missing required field
        response = api_context.post(
            "https://dummyjson.com/auth/login",
            data={"username": "emilys"},  # Missing password!
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status}")
        
        if response.status == 400:
            error = response.json()
            print(f"Error: {error}")
        
        print("\n📋 Trace shows exact request body sent!")


def test_debug_unexpected_response():
    """
    SCENARIO: Response doesn't match expectations
    
    Trace shows:
    1. Actual response vs expected
    2. Full response body
    3. Response headers
    """
    
    with SimpleTracer("debug_response") as api_context:
        response = api_context.get(
            "https://dummyjson.com/products/1"
        )
        
        assert response.status == 200
        
        product = response.json()
        
        # Print actual structure
        print("\n📦 Actual product fields:")
        for key in product.keys():
            print(f"   - {key}")
        
        # If you expected different fields, trace shows actual response
        

def test_debug_timing_issues():
    """
    SCENARIO: Debugging slow requests
    
    Trace shows:
    1. Request start time
    2. Response time
    3. Total duration
    """
    
    import time
    
    with SimpleTracer("debug_timing") as api_context:
        endpoints = [
            "/products?limit=100",
            "/users?limit=100",
            "/posts?limit=100"
        ]
        
        for endpoint in endpoints:
            start = time.time()
            
            response = api_context.get(f"https://dummyjson.com{endpoint}")
            
            elapsed = (time.time() - start) * 1000
            
            print(f"{endpoint:25} - {elapsed:6.2f}ms - Status {response.status}")
        
        print("\n📋 Trace shows precise timing for each request!")


def test_debug_redirect_chain():
    """
    SCENARIO: Debugging redirect issues
    
    Trace shows:
    1. Original request
    2. Redirect responses (301, 302)
    3. Final destination
    """
    
    with SimpleTracer("debug_redirects") as api_context:
        # httpbin can help test redirects
        response = api_context.get(
            "https://httpbin.org/redirect/3"  # Will redirect 3 times
        )
        
        print(f"Final status: {response.status}")
        print(f"Final URL: {response.url}")
        
        print("\n📋 Trace shows complete redirect chain!")


def test_debug_with_multiple_apis():
    """
    SCENARIO: Debugging multi-API workflows
    
    When your test calls multiple APIs, trace shows all of them
    """
    
    with SimpleTracer("multi_api_debug") as api_context:
        # API 1: JSONPlaceholder
        posts = api_context.get(
            "https://jsonplaceholder.typicode.com/posts?_limit=2"
        ).json()
        print(f"JSONPlaceholder: Got {len(posts)} posts")
        
        # API 2: DummyJSON
        products = api_context.get(
            "https://dummyjson.com/products?limit=2"
        ).json()
        print(f"DummyJSON: Got {len(products['products'])} products")
        
        # API 3: httpbin
        headers_check = api_context.get(
            "https://httpbin.org/headers"
        ).json()
        print(f"httpbin: Headers captured")
        
        print("\n📋 Trace shows all 3 API calls in sequence!")


def test_save_trace_for_ci_debugging():
    """
    SCENARIO: Saving traces for CI/CD debugging
    
    In CI, you can't debug interactively.
    Save trace as artifact, download, and view locally.
    """
    
    trace_manager = APITraceManager(trace_dir="artifacts/traces")
    api_context = trace_manager.start_tracing(name="ci_debugging_example")
    
    try:
        # Simulate CI test
        response = api_context.get("https://jsonplaceholder.typicode.com/posts/1")
        
        assert response.status == 200
        
        data = response.json()
        assert "title" in data
        
        # In CI, always save trace for later debugging
        trace_path = trace_manager.stop_tracing(save=True, test_passed=True)
        
        print(f"\n💾 Trace saved for CI artifact: {trace_path}")
        print("\n📋 In GitHub Actions, add this to workflow:")
        print("""
    - name: Upload traces
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: playwright-traces
        path: artifacts/traces/
        """)
        
    except Exception as e:
        trace_path = trace_manager.stop_tracing(save=True, test_passed=False)
        print(f"\n❌ CI Debug: Download {trace_path} from artifacts")
        raise