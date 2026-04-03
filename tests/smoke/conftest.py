"""
tests/smoke/conftest.py
Smoke test specific fixtures

These fixtures override or extend root conftest.py fixtures
"""

import pytest


@pytest.fixture
def page(browser_context):
    """
    OVERRIDE: Smoke tests use shorter timeouts
    
    This overrides the 'page' fixture from root conftest.py
    Tests in tests/smoke/ will use THIS fixture
    """
    
    page = browser_context.new_page()
    
    # Shorter timeouts for smoke tests (should be fast)
    page.set_default_timeout(10000)  # 10 seconds
    page.set_default_navigation_timeout(10000)
    
    yield page


@pytest.fixture
def fast_login(page, test_data):
    """
    SMOKE SPECIFIC: Fast login without extensive waits
    """
    
    page.goto(test_data["urls"]["base"])
    page.get_by_placeholder("Username").fill(
        test_data["users"]["standard"]["username"]
    )
    page.get_by_placeholder("Password").fill(
        test_data["users"]["standard"]["password"]
    )
    page.get_by_role("button", name="Login").click()
    
    # Quick check, no extensive waits
    page.wait_for_url("**/inventory.html", timeout=5000)
    
    return page


# Smoke tests should run quickly
@pytest.fixture(autouse=True)
def smoke_test_timeout(request):
    """
    AUTO FIXTURE: Set maximum time for smoke tests
    
    autouse=True: Automatically used by all tests in smoke/
    """
    
    # Could implement test timeout logic here
    yield
    
    # Could check test duration and warn if too slow