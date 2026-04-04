"""
API Test Fixtures
-----------------
Reusable fixtures for API testing to avoid code duplication.

Fixtures provide:
- Automatic setup (create request context)
- Automatic teardown (dispose context)
- Reusability across tests
- Composition (combine multiple fixtures)
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state

from clients.base_client import JSONPlaceholderClient, DummyJSONClient
from helpers.performance_monitor import PerformanceMonitor
from helpers.trace_manager import APITraceManager

@pytest.fixture
def api_context():
    """
    Basic API request context fixture
    
    Usage:
        def test_something(api_context):
            response = api_context.get("https://...")
    
    Benefits:
    - No need to manually create/dispose context
    - Automatic cleanup even if test fails
    - Reusable across all tests
    """
    playwright = _pw_state.get_playwright()
    context = playwright.request.new_context()
    
    yield context  # ← Test runs here, gets 'context' object
    
    # Cleanup (runs after test, even if test fails)
    context.dispose()


@pytest.fixture
def api_context_with_base_url():
    """
    API context with base URL configured
    
    Usage:
        def test_users(api_context_with_base_url):
            # No need to type full URL each time
            response = api_context_with_base_url.get("/users/1")
    
    Real-world: 
    - Switch environments easily (dev, staging, prod)
    - Avoid repetition of base URL
    """
    playwright = _pw_state.get_playwright()
    
    # Set base URL - all requests will be relative to this
    context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    yield context
    context.dispose()


@pytest.fixture
def api_context_with_headers():
    """
    API context with default headers (e.g., auth token)
    
    Real-world: Most APIs require authentication
    - Bearer tokens
    - API keys
    - Custom headers
    """
    playwright = _pw_state.get_playwright()
    
    context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com",
        extra_http_headers={
            # In real projects, these would be:
            # "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            # "X-API-Key": os.getenv('API_KEY'),
            "Content-Type": "application/json",
            "X-Custom-Header": "TestValue"
        }
    )
    
    yield context
    context.dispose()


@pytest.fixture
def created_post(api_context):
    """
    Fixture that creates a post and returns it
    
    Usage:
        def test_update_post(created_post, api_context):
            # created_post is already created, just use it
            updated = api_context.put(f"/posts/{created_post['id']}", ...)
    
    Real-world:
    - Setup test data
    - Create user before testing profile update
    - Create order before testing payment
    """
    # Setup: Create a post
    new_post = {
        "title": "Fixture Created Post",
        "body": "This post was created by a fixture",
        "userId": 1
    }
    
    response = api_context.post(
        "https://jsonplaceholder.typicode.com/posts",
        data=new_post
    )
    
    assert response.status == 201
    post = response.json()
    
    # Provide the post to the test
    yield post
    
    # Teardown: Clean up (delete the post)
    # In real APIs, you'd delete:
    # api_context.delete(f"https://jsonplaceholder.typicode.com/posts/{post['id']}")
    # JSONPlaceholder doesn't actually delete, so we skip cleanup


@pytest.fixture
def created_user(api_context):
    """
    Fixture that creates a user for testing
    
    Real-world: User registration tests, profile tests
    """
    new_user = {
        "name": "Test User",
        "username": "testuser",
        "email": "test@example.com"
    }
    
    response = api_context.post(
        "https://jsonplaceholder.typicode.com/users",
        data=new_user
    )
    
    assert response.status == 201
    user = response.json()
    
    yield user
    
    # Cleanup would go here in real project
    # api_context.delete(f"https://jsonplaceholder.typicode.com/users/{user['id']}")

@pytest.fixture
def managed_user(api_context):
    """Creates and manages a user"""
    user_data = {
        "name": "Managed User",
        "username": "manageduser",
        "email": "managed@example.com"
    }
    
    resp = api_context.post(
        "https://jsonplaceholder.typicode.com/users",
        data=user_data
    )
    user = resp.json()
    
    yield user
    
    # Cleanup
    api_context.delete(
        f"https://jsonplaceholder.typicode.com/users/{user['id']}"
    )

# ============================================
# ENVIRONMENT DETECTION
# ============================================

def is_ci():
    """Check if running in CI environment"""
    return os.getenv("CI") == "true"


# ============================================
# API CLIENT FIXTURES
# ============================================

@pytest.fixture(scope="function")
def jsonplaceholder_client():
    """JSONPlaceholder API client"""
    client = JSONPlaceholderClient()
    yield client
    client.dispose()


@pytest.fixture(scope="function")
def dummyjson_client():
    """DummyJSON API client"""
    client = DummyJSONClient()
    yield client
    client.dispose()


@pytest.fixture(scope="function")
def authenticated_client():
    """Pre-authenticated DummyJSON client"""
    client = DummyJSONClient()
    client.login("emilys", "emilyspass")
    yield client
    client.dispose()


# ============================================
# PERFORMANCE MONITORING
# ============================================

@pytest.fixture(scope="function")
def performance_monitor():
    """Performance monitoring fixture"""
    return PerformanceMonitor()


# ============================================
# CI/CD SPECIFIC CONFIGURATION
# ============================================

@pytest.fixture(scope="session", autouse=True)
def configure_for_ci():
    """Auto-configure for CI environment"""
    if is_ci():
        print("\n🤖 Running in CI environment")
        print("   - Stricter timeouts")
        print("   - Detailed logging enabled")
        print("   - Skipping slow tests")
    else:
        print("\n💻 Running in local environment")


# ============================================
# PYTEST CONFIGURATION
# ============================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "contract: marks tests as contract tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment"""
    if is_ci():
        # Skip slow tests in CI by default
        skip_slow = pytest.mark.skip(reason="Skipping slow test in CI")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

"""
Add tracing fixtures to conftest.py
"""
# ============================================
# TRACING FIXTURES
# ============================================

@pytest.fixture
def traced_api_context(request):
    """
    API context with automatic tracing
    
    Saves trace only on test failure
    """
    test_name = request.node.name
    trace_manager = APITraceManager()
    
    api_context = trace_manager.start_tracing(name=test_name)
    
    yield api_context
    
    # Check if test failed
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        trace_path = trace_manager.stop_tracing(save=True, test_passed=False)
        print(f"\n💾 Debug trace: {trace_path}")
        print(f"   Run: playwright show-trace {trace_path}")
    else:
        trace_manager.stop_tracing(save=False)


@pytest.fixture
def always_traced_context(request):
    """
    API context that ALWAYS saves traces
    
    Useful for debugging CI failures
    """
    test_name = request.node.name
    trace_manager = APITraceManager()
    
    api_context = trace_manager.start_tracing(name=test_name)
    
    yield api_context
    
    test_passed = not (hasattr(request.node, 'rep_call') and request.node.rep_call.failed)
    trace_path = trace_manager.stop_tracing(save=True, test_passed=test_passed)
    print(f"\n💾 Trace: {trace_path}")


# Hook to capture test result
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test result for traced fixtures"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
