"""
Tracing Fixtures for API Tests
-------------------------------
Pytest fixtures that automatically trace API tests
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import playwright_state as _pw_state

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from helpers.trace_manager import APITraceManager


@pytest.fixture
def traced_api_context(request):
    """
    API context with automatic tracing
    
    Traces are saved only on test failure
    
    Usage:
        def test_something(traced_api_context):
            response = traced_api_context.get("https://api.example.com")
    """
    test_name = request.node.name
    trace_manager = APITraceManager()
    
    # Start tracing
    api_context = trace_manager.start_tracing(name=test_name)
    
    yield api_context
    
    # Check if test failed
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        # Test failed - save trace
        trace_path = trace_manager.stop_tracing(save=True, test_passed=False)
        print(f"\n💾 Trace saved for failed test: {trace_path}")
    else:
        # Test passed - discard trace (or save if you want all traces)
        trace_manager.stop_tracing(save=False)


@pytest.fixture
def always_traced_api_context(request):
    """
    API context that ALWAYS saves traces
    
    Useful for debugging or when you want trace history
    
    Usage:
        def test_something(always_traced_api_context):
            response = always_traced_api_context.get("https://api.example.com")
    """
    test_name = request.node.name
    trace_manager = APITraceManager()
    
    # Start tracing
    api_context = trace_manager.start_tracing(name=test_name)
    
    yield api_context
    
    # Always save trace
    test_passed = not (hasattr(request.node, 'rep_call') and request.node.rep_call.failed)
    trace_manager.stop_tracing(save=True, test_passed=test_passed)


@pytest.fixture
def traced_api_client(request):
    """
    Higher-level traced API client
    
    Returns dict with both context and trace manager
    for more control
    """
    test_name = request.node.name
    trace_manager = APITraceManager()
    
    api_context = trace_manager.start_tracing(name=test_name)
    
    yield {
        "context": api_context,
        "trace_manager": trace_manager,
        "test_name": test_name
    }
    
    # Check test result and save accordingly
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        trace_path = trace_manager.stop_tracing(save=True, test_passed=False)
        APITraceManager.open_trace(trace_path)
    else:
        trace_manager.stop_tracing(save=False)


# Hook to capture test result
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test result for fixtures
    
    This allows fixtures to know if test passed or failed
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Store result on the test item
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session")
def trace_on_failure_config():
    """
    Session-scoped configuration for tracing
    
    Can be overridden via environment variable:
        TRACE_ON_FAILURE=true pytest tests/
    """
    return os.getenv("TRACE_ON_FAILURE", "true").lower() == "true"


@pytest.fixture
def conditional_traced_context(request, trace_on_failure_config):
    """
    Traced context that respects configuration
    
    Only traces when TRACE_ON_FAILURE is enabled
    """
    test_name = request.node.name
    
    if trace_on_failure_config:
        trace_manager = APITraceManager()
        api_context = trace_manager.start_tracing(name=test_name)
        
        yield api_context
        
        if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            trace_manager.stop_tracing(save=True, test_passed=False)
        else:
            trace_manager.stop_tracing(save=False)
    else:
        # No tracing - use regular request context
        playwright = _pw_state.get_playwright()
        context = playwright.request.new_context()
        yield context
        context.dispose()