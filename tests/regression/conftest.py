"""
tests/regression/conftest.py
Regression test specific fixtures

Extended timeouts and more thorough setup
"""

import pytest


@pytest.fixture
def page(browser_context):
    """
    OVERRIDE: Regression tests use longer timeouts
    
    Regression tests are thorough, may test slow scenarios
    """
    
    page = browser_context.new_page()
    
    # Longer timeouts for thorough testing
    page.set_default_timeout(60000)  # 60 seconds
    page.set_default_navigation_timeout(60000)
    
    yield page


@pytest.fixture
def full_checkout_setup(page, test_data):
    """
    REGRESSION SPECIFIC: Complete setup for checkout testing
    
    Sets up:
    - Logged in user
    - Multiple items in cart
    - Ready for checkout flow
    """
    
    # Login
    page.goto(test_data["urls"]["base"])
    page.get_by_placeholder("Username").fill(
        test_data["users"]["standard"]["username"]
    )
    page.get_by_placeholder("Password").fill(
        test_data["users"]["standard"]["password"]
    )
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/inventory.html")
    
    # Add multiple items
    products = [
        "sauce-labs-backpack",
        "sauce-labs-bike-light",
        "sauce-labs-onesie",
    ]
    
    for product_id in products:
        page.locator(f"[data-test='add-to-cart-{product_id}']").click()
    
    return {
        "page": page,
        "cart_items": products,
        "expected_count": len(products),
    }


@pytest.fixture(scope="module")
def shared_auth_state(browser_instance, test_data):
    """
    MODULE SCOPE: Shared authentication for regression module
    
    Login once, reuse for all tests in module
    Faster for comprehensive regression testing
    """
    
    context = browser_instance.new_context()
    page = context.new_page()
    
    # Login
    page.goto(test_data["urls"]["base"])
    page.get_by_placeholder("Username").fill(
        test_data["users"]["standard"]["username"]
    )
    page.get_by_placeholder("Password").fill(
        test_data["users"]["standard"]["password"]
    )
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/inventory.html")
    
    # Save storage state
    storage_state = context.storage_state()
    
    context.close()
    
    return storage_state


@pytest.fixture
def authenticated_page(browser_instance, shared_auth_state):
    """
    Use shared auth state for fast authenticated pages
    """
    
    context = browser_instance.new_context(storage_state=shared_auth_state)
    page = context.new_page()
    
    yield page
    
    context.close()