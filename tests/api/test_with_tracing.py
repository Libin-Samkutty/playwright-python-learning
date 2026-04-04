"""
Module 4 Addition: API Testing with Tracing
--------------------------------------------
Demonstrates how to use tracing for debugging API tests

Key Concepts:
1. Tracing captures all HTTP traffic
2. Traces are saved on failure for debugging
3. Trace files can be viewed in Playwright Trace Viewer
4. Use context manager for simple tracing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state

sys.path.insert(0, os.path.dirname(__file__))
from helpers.trace_manager import APITraceManager, SimpleTracer


def test_basic_tracing():
    """
    LESSON: Basic tracing with manual control
    
    Use when you need fine-grained control over tracing
    """
    
    trace_manager = APITraceManager()
    
    # Start tracing
    api_context = trace_manager.start_tracing(name="basic_tracing_test")
    
    try:
        # Make API calls - all will be traced
        response = api_context.get("https://jsonplaceholder.typicode.com/posts/1")
        
        assert response.status == 200, f"Expected 200, got {response.status}"
        
        data = response.json()
        assert "title" in data
        
        print(f"✅ Test passed: {data['title'][:50]}...")
        
        # Test passed - save trace (optional, for debugging)
        trace_path = trace_manager.stop_tracing(save=True, test_passed=True)
        print(f"📝 Trace saved: {trace_path}")
        
    except Exception as e:
        # Test failed - ALWAYS save trace
        trace_path = trace_manager.stop_tracing(save=True, test_passed=False)
        
        print(f"\n❌ Test failed! Debugging trace saved.")
        APITraceManager.open_trace(trace_path)
        
        raise  # Re-raise the exception


def test_tracing_with_context_manager():
    """
    LESSON: Simplified tracing with context manager
    
    Automatically saves trace on failure
    """
    
    with SimpleTracer("context_manager_test") as api_context:
        # All requests are automatically traced
        response = api_context.get("https://jsonplaceholder.typicode.com/users/1")
        
        assert response.status == 200
        
        user = response.json()
        assert "name" in user
        assert "email" in user
        
        print(f"✅ Got user: {user['name']}")
    
    # Trace automatically saved when exiting context
    print("📝 Trace saved automatically")


def test_tracing_captures_failure():
    """
    LESSON: Tracing helps debug failures
    
    When test fails, trace shows exactly what happened
    """
    
    trace_manager = APITraceManager()
    api_context = trace_manager.start_tracing(name="failure_debug_test")
    
    try:
        # Make a request to non-existent endpoint
        response = api_context.get("https://jsonplaceholder.typicode.com/posts/99999")
        
        # This endpoint returns empty {}, not 404
        # Let's check the actual response
        data = response.json()
        
        print(f"Response status: {response.status}")
        print(f"Response data: {data}")
        
        # Verify we got data (will fail for non-existent post)
        if not data:
            print("⚠️ Empty response - post not found")
        
        trace_manager.stop_tracing(save=True, test_passed=True)
        
    except Exception as e:
        trace_path = trace_manager.stop_tracing(save=True, test_passed=False)
        print(f"\n❌ Debug this failure with trace:")
        APITraceManager.open_trace(trace_path)
        raise


def test_tracing_authentication_flow():
    """
    LESSON: Trace authentication for debugging
    
    When auth fails, trace shows:
    - Exact headers sent
    - Token format
    - Server response
    """
    
    with SimpleTracer("auth_flow_trace") as api_context:
        # Step 1: Login
        print("\n🔐 Step 1: Logging in...")
        
        login_response = api_context.post(
            "https://dummyjson.com/auth/login",
            data={
                "username": "emilys",
                "password": "emilyspass"
            },
            headers={"Content-Type": "application/json"}
        )
        
        assert login_response.status == 200, f"Login failed: {login_response.status}"
        
        login_data = login_response.json()
        
        # Note: accessToken, not token!
        access_token = login_data["accessToken"]
        print(f"✅ Got accessToken: {access_token[:30]}...")
        
        # Step 2: Use token
        print("\n🔒 Step 2: Accessing protected endpoint...")
        
        me_response = api_context.get(
            "https://dummyjson.com/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert me_response.status == 200, f"Auth failed: {me_response.status}"
        
        user = me_response.json()
        print(f"✅ Authenticated as: {user['username']}")
    
    # Trace saved - can see exact auth headers in trace viewer


def test_tracing_multiple_requests():
    """
    LESSON: Trace multiple requests in one test
    
    Trace captures entire sequence for debugging
    """
    
    with SimpleTracer("multiple_requests_trace") as api_context:
        print("\n📚 Making multiple requests...")
        
        # Request 1: Get all posts
        posts_response = api_context.get(
            "https://jsonplaceholder.typicode.com/posts?_limit=3"
        )
        assert posts_response.status == 200
        posts = posts_response.json()
        print(f"  1. Got {len(posts)} posts")
        
        # Request 2: Get specific user
        user_id = posts[0]["userId"]
        user_response = api_context.get(
            f"https://jsonplaceholder.typicode.com/users/{user_id}"
        )
        assert user_response.status == 200
        user = user_response.json()
        print(f"  2. Got user: {user['name']}")
        
        # Request 3: Get user's comments
        comments_response = api_context.get(
            f"https://jsonplaceholder.typicode.com/comments?postId={posts[0]['id']}"
        )
        assert comments_response.status == 200
        comments = comments_response.json()
        print(f"  3. Got {len(comments)} comments")
        
        # Request 4: Create a post
        create_response = api_context.post(
            "https://jsonplaceholder.typicode.com/posts",
            data={
                "title": "Traced Post",
                "body": "This request is traced",
                "userId": user_id
            }
        )
        assert create_response.status == 201
        created = create_response.json()
        print(f"  4. Created post ID: {created['id']}")
        
        print("\n✅ All 4 requests traced!")


def test_tracing_with_fixture(traced_api_context):
    """
    LESSON: Using traced fixture
    
    The traced_api_context fixture handles tracing automatically
    
    Note: Requires fixtures from tracing_fixtures.py to be in conftest.py
    """
    
    # Fixture provides pre-traced context
    response = traced_api_context.get(
        "https://jsonplaceholder.typicode.com/posts/1"
    )
    
    assert response.status == 200
    
    data = response.json()
    print(f"✅ Got post: {data['title'][:50]}...")
    
    # Trace automatically saved on fixture cleanup


def test_trace_shows_request_details():
    """
    LESSON: What trace captures
    
    Open trace to see:
    - Request URL, method
    - Request headers (including auth)
    - Request body (for POST/PUT)
    - Response status, headers
    - Response body
    - Timing information
    """
    
    with SimpleTracer("request_details_trace") as api_context:
        # POST with body - trace shows exact request
        response = api_context.post(
            "https://jsonplaceholder.typicode.com/posts",
            data={
                "title": "Check this in trace!",
                "body": "This body will appear in trace viewer",
                "userId": 1
            },
            headers={
                "Content-Type": "application/json",
                "X-Custom-Header": "Visible in trace"
            }
        )
        
        assert response.status == 201
        
        print("\n📋 Open the trace to see:")
        print("   - Request body")
        print("   - Custom headers")
        print("   - Response body")
        print("   - Timing data")


@pytest.mark.xfail(reason="Intentional failure to demonstrate trace debugging")
def test_intentional_failure_for_debugging():
    """
    LESSON: Intentional failure to demonstrate trace debugging
    
    Run this test, it will fail, then open the trace to debug
    
    Command:
        pytest tests/api/test_with_tracing.py::test_intentional_failure_for_debugging -v -s
    """
    
    with SimpleTracer("intentional_failure") as api_context:
        # Make a request
        response = api_context.get(
            "https://dummyjson.com/auth/me"  # Requires auth - will fail!
        )
        
        # This assertion will likely fail (401 Unauthorized)
        # The trace will show exactly why
        assert response.status == 200, \
            f"Expected 200 but got {response.status}. Check trace for headers!"
        
        # If we get here, parse response
        data = response.json()
        print(f"Got: {data}")


# ============================================
# FIXTURES (add to conftest.py)
# ============================================

@pytest.fixture
def traced_api_context(request):
    """
    API context with automatic tracing
    
    Copy this to tests/api/conftest.py
    """
    test_name = request.node.name
    trace_manager = APITraceManager()
    
    api_context = trace_manager.start_tracing(name=test_name)
    
    yield api_context
    
    # Check if test failed using pytest hook
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        trace_path = trace_manager.stop_tracing(save=True, test_passed=False)
        print(f"\n💾 Trace saved: {trace_path}")
        APITraceManager.open_trace(trace_path)
    else:
        trace_manager.stop_tracing(save=False)


# Hook to capture test result
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test result for fixtures"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)