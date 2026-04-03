"""
TEST FILE: test_cart.py
FEATURE: Shopping cart functionality
REAL-WORLD USE: Group related tests together

NAMING CONVENTIONS:
- File: test_<feature>.py
- Function: test_<action>_<expected_result>
"""

from playwright.sync_api import expect
import pytest


def test_add_single_item_to_cart(page):
    """
    Test adding one item to shopping cart
    """
    
    # Setup: Login
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Action: Add item
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    
    # Assert: Cart badge shows 1
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("1")


def test_add_multiple_items_to_cart(page):
    """
    Test adding multiple items to shopping cart
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Add three items
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    page.locator("[data-test='add-to-cart-sauce-labs-bike-light']").click()
    page.locator("[data-test='add-to-cart-sauce-labs-bolt-t-shirt']").click()
    
    # Verify count
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("3")


def test_remove_item_from_cart(page):
    """
    Test removing an item from shopping cart
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Add item
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")
    
    # Remove item
    page.locator("[data-test='remove-sauce-labs-backpack']").click()
    
    # Badge should disappear
    expect(page.locator(".shopping_cart_badge")).to_have_count(0)


def test_cart_persists_after_navigation(page):
    """
    Test that cart contents persist across page navigation
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Add item
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    
    # Navigate to product detail
    page.locator(".inventory_item_name").first.click()
    
    # Verify cart still has item
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")
    
    # Go back to inventory
    page.get_by_role("button", name="Back to products").click()
    
    # Verify cart still has item
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")