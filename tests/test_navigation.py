"""
CONCEPT: Testing navigation flows
GOAL: Verify users can navigate between pages
REAL-WORLD USE: E-commerce sites, dashboards, multi-page forms
"""

from playwright.sync_api import expect

def test_saucedemo_inventory_navigation(page):
    """
    Test: Login and verify navigation to inventory page
    
    REAL-WORLD USE: Testing post-login navigation
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Fill login form
    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
    
    # Click login
    page.locator("#login-button").click()
    
    # Verify redirected to inventory
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    # Verify products are visible
    products = page.locator(".inventory_item")
    expect(products.first).to_be_visible()