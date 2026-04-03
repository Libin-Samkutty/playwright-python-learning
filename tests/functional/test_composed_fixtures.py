"""
tests/functional/test_composed_fixtures.py
Tests demonstrating fixture composition
"""

from playwright.sync_api import expect


def test_inventory_products_visible(inventory_page):
    """
    Uses: browser_instance  logged_in_context  inventory_page
    
    Test starts with user already logged in and on inventory
    """
    
    products = inventory_page.locator(".inventory_item")
    expect(products).to_have_count(6)


def test_cart_shows_added_item(cart_page):
    """
    Uses: ...  inventory_page  cart_page
    
    Test starts with item already in cart
    """
    
    cart_items = cart_page.locator(".cart_item")
    expect(cart_items).to_have_count(1)
    expect(cart_items).to_contain_text("Sauce Labs Backpack")


def test_checkout_form_displayed(checkout_page):
    """
    Uses: ...  cart_page  checkout_page
    
    Test starts at checkout form
    """
    
    expect(checkout_page.get_by_placeholder("First Name")).to_be_visible()
    expect(checkout_page.get_by_placeholder("Last Name")).to_be_visible()
    expect(checkout_page.get_by_placeholder("Zip/Postal Code")).to_be_visible()


def test_complete_checkout_from_checkout_page(checkout_page):
    """
    Start at checkout, complete the purchase
    
    All prior setup (login, add to cart, navigate) done by fixtures
    """
    
    # Fill form
    checkout_page.get_by_placeholder("First Name").fill("John")
    checkout_page.get_by_placeholder("Last Name").fill("Doe")
    checkout_page.get_by_placeholder("Zip/Postal Code").fill("12345")
    
    # Continue
    checkout_page.get_by_role("button", name="Continue").click()
    
    # Finish
    checkout_page.get_by_role("button", name="Finish").click()
    
    # Verify success
    expect(checkout_page.locator(".complete-header")).to_have_text(
        "Thank you for your order!"
    )
