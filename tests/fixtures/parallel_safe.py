"""
tests/fixtures/parallel_safe.py
Fixtures designed for parallel execution
"""

import pytest
from typing import Generator
import uuid
import os


@pytest.fixture(scope="function")
def unique_id() -> str:
    """
    Generate unique ID for this test run
    
    Useful for creating unique test data
    """
    return str(uuid.uuid4())[:8]


@pytest.fixture(scope="function")
def worker_id(request) -> str:
    """
    Get pytest-xdist worker ID
    
    Returns:
        "master" if not running parallel
        "gw0", "gw1", etc. if running parallel
    """
    
    if hasattr(request.config, "workerinput"):
        return request.config.workerinput["workerid"]
    return "master"


@pytest.fixture(scope="function")
def unique_user(unique_id):
    """
    User with unique credentials for parallel-safe tests
    
    Note: For SauceDemo, we still need to use predefined users
    This is an example for apps where you can create users
    """
    
    from data import UserFactory
    
    # For SauceDemo, cycle through available users
    # In a real app, you'd create unique users
    return UserFactory.standard_user()


@pytest.fixture(scope="function")
def isolated_page(browser, worker_id, settings):
    """
    Completely isolated page for parallel execution
    
    Each worker gets its own context and page
    """
    
    # Create unique context
    context = browser.new_context(
        viewport={
            "width": settings.browser.viewport_width,
            "height": settings.browser.viewport_height,
        },
    )
    
    page = context.new_page()
    
    # Tag page with worker ID for debugging
    page._worker_id = worker_id
    
    yield page
    
    context.close()


# Marker for tests that cannot run in parallel
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "serial: Mark test to run serially (not in parallel)"
    )


@pytest.fixture(scope="session")
def serial_lock(tmp_path_factory):
    """
    Lock for serial tests when running in parallel
    
    Usage:
        @pytest.mark.serial
        def test_requires_serial(serial_lock):
            with serial_lock:
                # This code runs serially
                pass
    """
    
    import filelock
    
    lock_file = tmp_path_factory.getbasetemp().parent / "serial.lock"
    lock = filelock.FileLock(str(lock_file))
    
    return lock