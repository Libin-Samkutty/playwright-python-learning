"""
tests/debug/test_isolation.py
Debugging by isolating the problem
"""

import pytest
from playwright.sync_api import expect


class TestIsolationStrategy:
    """
    Strategy: Break down failing test into smaller parts
    """
    
    def test_full_flow_that_might_fail(self, page):
        """
        BEFORE: Big test that fails somewhere
        Hard to know which part fails
        """
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        page.locator(".shopping_cart_link").click()
        page.get_by_role("button", name="Checkout").click()
        page.get_by_placeholder("First Name").fill("John")
        page.get_by_placeholder("Last Name").fill("Doe")
        page.get_by_placeholder("Zip/Postal Code").fill("12345")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("button", name="Finish").click()
        expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")
    
    # AFTER: Break into isolated tests
    
    def test_step1_login(self, page):
        """Isolated test: Just login"""
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    def test_step2_add_to_cart(self, page):
        """Isolated test: Add to cart"""
        # Setup
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Test
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("1")
    
    def test_step3_checkout_form(self, page):
        """Isolated test: Checkout form"""
        # Setup
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        page.locator(".shopping_cart_link").click()
        page.get_by_role("button", name="Checkout").click()
        
        # Test
        page.get_by_placeholder("First Name").fill("John")
        page.get_by_placeholder("Last Name").fill("Doe")
        page.get_by_placeholder("Zip/Postal Code").fill("12345")
        page.get_by_role("button", name="Continue").click()
        expect(page).to_have_url("https://www.saucedemo.com/checkout-step-two.html")
