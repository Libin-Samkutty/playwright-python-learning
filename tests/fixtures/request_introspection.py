"""
tests/fixtures/request_introspection.py
Using the request object for fixture introspection
"""

import pytest
import os


@pytest.fixture
def context_aware_fixture(request):
    """
    REQUEST OBJECT: Access test information
    
    The request object provides:
    - request.node: Current test item
    - request.param: Current fixture parameter (if parametrized)
    - request.fixturenames: All fixtures for this test
    - request.config: pytest configuration
    - request.function: Test function object
    - request.cls: Test class (if applicable)
    - request.module: Test module
    """
    
    print(f"\n--- Fixture Introspection ---")
    print(f"Test name: {request.node.name}")
    print(f"Test function: {request.function.__name__}")
    print(f"Test module: {request.module.__name__}")
    print(f"Fixtures requested: {request.fixturenames}")
    
    if request.cls:
        print(f"Test class: {request.cls.__name__}")
    
    yield
    
    print(f"\n--- Fixture Cleanup for {request.node.name} ---")


@pytest.fixture
def dynamic_timeout(request):
    """
    REQUEST OBJECT: Dynamic configuration based on markers
    
    USE CASE:
    - Different timeouts for tests marked as 'slow'
    - Custom behavior based on test markers
    """
    
    # Check if test has 'slow' marker
    if request.node.get_closest_marker("slow"):
        timeout = 60000
    else:
        timeout = 10000
    
    return timeout


@pytest.fixture
def conditional_fixture(request):
    """
    REQUEST OBJECT: Skip fixture based on conditions
    """
    
    # Skip if running in CI without display
    if os.environ.get("CI") and not os.environ.get("DISPLAY"):
        if request.node.get_closest_marker("visual"):
            pytest.skip("Visual tests require display")
    
    yield


@pytest.fixture
def test_artifacts_dir(request, tmp_path):
    """
    REQUEST OBJECT: Create test-specific artifact directory
    
    Creates unique directory for each test's artifacts
    """
    
    test_name = request.node.name
    # Sanitize test name for filesystem
    safe_name = "".join(c if c.isalnum() else "_" for c in test_name)
    
    artifacts_dir = tmp_path / safe_name
    artifacts_dir.mkdir(exist_ok=True)
    
    return artifacts_dir


@pytest.fixture
def fixture_with_indirect_param(request):
    """
    REQUEST OBJECT: Access parametrize values
    
    Used with @pytest.mark.parametrize(..., indirect=True)
    """
    
    if hasattr(request, "param"):
        # request.param contains the parameter value
        value = request.param
        # Transform or process the parameter
        return f"Processed: {value}"
    
    return "Default value"