"""
TEST FILE: test_smoke_suite.py
PURPOSE: Quick sanity tests to verify basic functionality
RUN: pytest -m smoke
"""

from playwright.sync_api import expect
import pytest


@pytest.mark.smoke
def test_homepage_loads(page):
    """
    SMOKE TEST: Verify homepage is accessible
    PRIORITY: Critical - run first
    """
    
    page.goto("https://www.saucedemo.com/")
    
    expect(page).to_have_title("Swag Labs")
    expect(page.get_by_role("button", name="Login")).to_be_visible()


@pytest.mark.smoke
@pytest.mark.login
def test_valid_login(page):
    """
    SMOKE TEST: Verify login works
    MARKERS: smoke, login
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")


@pytest.mark.smoke
@pytest.mark.cart
def test_add_to_cart_works(page):
    """
    SMOKE TEST: Verify cart functionality
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")


@pytest.mark.regression
@pytest.mark.slow
def test_complete_purchase_flow(page):
    """
    REGRESSION TEST: Full purchase flow
    MARKER: slow - takes longer than smoke tests
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Add item
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    
    # Checkout
    page.locator(".shopping_cart_link").click()
    page.get_by_role("button", name="Checkout").click()
    
    # Fill form
    page.get_by_placeholder("First Name").fill("John")
    page.get_by_placeholder("Last Name").fill("Doe")
    page.get_by_placeholder("Zip/Postal Code").fill("12345")
    page.get_by_role("button", name="Continue").click()
    
    # Complete
    page.get_by_role("button", name="Finish").click()
    
    expect(page.locator(".complete-header")).to_have_text(
        "Thank you for your order!"
    )


@pytest.mark.wip
def test_feature_in_development(page):
    """
    WIP TEST: Not ready yet
    Use: pytest -m "not wip" to exclude
    """
    
    pytest.skip("Feature not implemented yet")
