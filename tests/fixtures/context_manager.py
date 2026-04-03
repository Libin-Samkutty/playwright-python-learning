"""
tests/fixtures/context_managers.py
Context manager based fixtures
"""

import pytest
from contextlib import contextmanager


@contextmanager
def managed_page(browser_instance):
    """
    CONTEXT MANAGER: Page with automatic cleanup
    
    Can be used directly or converted to fixture
    """
    
    context = browser_instance.new_context()
    page = context.new_page()
    
    try:
        yield page
    finally:
        context.close()


@pytest.fixture
def page_from_context_manager(browser_instance):
    """
    FIXTURE: Wraps context manager
    """
    
    with managed_page(browser_instance) as page:
        yield page


@contextmanager
def authenticated_session(browser_instance, username, password, base_url):
    """
    REUSABLE CONTEXT MANAGER: Authentication
    
    Can be used in fixtures or directly in tests
    """
    
    context = browser_instance.new_context()
    page = context.new_page()
    
    try:
        # Login
        page.goto(base_url)
        page.get_by_placeholder("Username").fill(username)
        page.get_by_placeholder("Password").fill(password)
        page.get_by_role("button", name="Login").click()
        page.wait_for_url("**/inventory.html")
        
        yield page
    finally:
        context.close()


@pytest.fixture
def admin_session(browser_instance, test_data):
    """
    FIXTURE: Admin user session using context manager
    """
    
    user = test_data["users"]["standard"]  # Would be admin in real app
    
    with authenticated_session(
        browser_instance,
        user["username"],
        user["password"],
        test_data["urls"]["base"],
    ) as page:
        yield page
