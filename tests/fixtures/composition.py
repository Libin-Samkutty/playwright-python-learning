"""
tests/fixtures/composition.py
Fixture composition patterns
"""

import pytest
from playwright.sync_api import expect


# ============ BASE FIXTURES ============

@pytest.fixture
def base_url(test_data):
    """Base fixture: URL configuration"""
    return test_data["urls"]["base"]


@pytest.fixture
def standard_user(test_data):
    """Base fixture: Standard user credentials"""
    return test_data["users"]["standard"]


# ============ COMPOSED FIXTURES ============

@pytest.fixture
def logged_in_context(browser_instance, base_url, standard_user):
    """
    COMPOSED FIXTURE: Browser context with login
    
    Combines:
    - browser_instance (session scope)
    - base_url (from test_data)
    - standard_user (from test_data)
    """
    
    context = browser_instance.new_context()
    page = context.new_page()
    
    # Login
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(standard_user["username"])
    page.get_by_placeholder("Password").fill(standard_user["password"])
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/inventory.html")
    
    yield context
    
    context.close()


@pytest.fixture
def inventory_page(logged_in_context):
    """
    COMPOSED FIXTURE: Page on inventory
    
    Builds on: logged_in_context
    """
    
    # Create new page in logged-in context (shares cookies)
    page = logged_in_context.new_page()
    page.goto("https://www.saucedemo.com/inventory.html")
    
    # Verify we're on inventory
    expect(page.locator(".inventory_item").first).to_be_visible()
    
    return page


@pytest.fixture
def cart_page(inventory_page):
    """
    COMPOSED FIXTURE: Page with cart open
    
    Builds on: inventory_page
    """
    
    # Add item and go to cart
    inventory_page.locator(
        "[data-test='add-to-cart-sauce-labs-backpack']"
    ).click()
    inventory_page.locator(".shopping_cart_link").click()
    
    # Verify on cart page
    expect(inventory_page).to_have_url("**/cart.html")
    
    return inventory_page


@pytest.fixture
def checkout_page(cart_page):
    """
    COMPOSED FIXTURE: Page at checkout step 1
    
    Builds on: cart_page
    """
    
    cart_page.get_by_role("button", name="Checkout").click()
    
    expect(cart_page).to_have_url("**/checkout-step-one.html")
    
    return cart_page


# ============ FIXTURE CHAIN VISUALIZATION ============
#
# browser_instance (session)
#         
#         
# logged_in_context (function)
#         
#         
#    inventory_page (function)
#         
#         
#      cart_page (function)
#         
#         
#    checkout_page (function)
#
# Each fixture builds on the previous one
# Tests can use any level based on what they need