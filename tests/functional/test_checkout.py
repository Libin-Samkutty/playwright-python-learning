"""
TEST FILE: test_checkout.py
FEATURE: Checkout process
STRUCTURE: Class-based organization
"""

from playwright.sync_api import expect
import pytest


class TestCheckoutFlow:
    """
    Test class for checkout functionality
    
    WHY CLASS?
    - All tests share login setup
    - Logically grouped (checkout flow)
    - Can use class-level fixtures
    """
    
    @pytest.fixture(autouse=True)
    def setup_logged_in_with_cart(self, page):
        """
        Fixture that runs before EACH test in this class
        
        autouse=True: Automatically used by all tests in class
        """
        
        # Login
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Add item to cart
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        
        # Store page for use in tests
        self.page = page
        
        yield
        
        # Teardown (if needed)
        # This runs after each test
    
    def test_proceed_to_checkout(self):
        """Test navigating to checkout"""
        
        self.page.locator(".shopping_cart_link").click()
        self.page.get_by_role("button", name="Checkout").click()
        
        expect(self.page).to_have_url(
            "https://www.saucedemo.com/checkout-step-one.html"
        )
    
    def test_checkout_requires_information(self):
        """Test checkout form validation"""
        
        self.page.locator(".shopping_cart_link").click()
        self.page.get_by_role("button", name="Checkout").click()
        
        # Try to continue without filling form
        self.page.get_by_role("button", name="Continue").click()
        
        # Should show error
        error = self.page.locator("[data-test='error']")
        expect(error).to_be_visible()
        expect(error).to_contain_text("First Name is required")
    
    def test_complete_checkout_successfully(self):
        """Test successful checkout completion"""
        
        self.page.locator(".shopping_cart_link").click()
        self.page.get_by_role("button", name="Checkout").click()
        
        # Fill form
        self.page.get_by_placeholder("First Name").fill("John")
        self.page.get_by_placeholder("Last Name").fill("Doe")
        self.page.get_by_placeholder("Zip/Postal Code").fill("12345")
        self.page.get_by_role("button", name="Continue").click()
        
        # Complete purchase
        self.page.get_by_role("button", name="Finish").click()
        
        # Verify success
        expect(self.page.locator(".complete-header")).to_have_text(
            "Thank you for your order!"
        )


class TestCheckoutEdgeCases:
    """
    Separate class for edge cases
    
    WHY SEPARATE?
    - Different setup requirements
    - Clear separation of concerns
    """
    
    def test_checkout_with_empty_cart(self, page):
        """Test attempting checkout with empty cart"""
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Go directly to cart (empty)
        page.locator(".shopping_cart_link").click()
        
        # Checkout button should still be visible
        # (SauceDemo allows empty checkout)
        checkout_btn = page.get_by_role("button", name="Checkout")
        expect(checkout_btn).to_be_visible()
    
    def test_cancel_checkout_returns_to_cart(self, page):
        """Test cancel button during checkout"""
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Add item and go to checkout
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        page.locator(".shopping_cart_link").click()
        page.get_by_role("button", name="Checkout").click()
        
        # Cancel
        page.get_by_role("button", name="Cancel").click()
        
        # Should return to cart
        expect(page).to_have_url("https://www.saucedemo.com/cart.html")