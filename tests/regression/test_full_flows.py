"""
TEST FILE: test_full_flows.py
CATEGORY: Regression Tests
PURPOSE: End-to-end flows testing complete user journeys
RUN: pytest tests/regression/test_full_flows.py -v
     pytest -m regression -v

REAL-WORLD USE:
- Full regression before releases
- Complete user journey validation
- Integration testing

NOTE: These tests are longer and cover complete workflows
"""

import pytest
from playwright.sync_api import expect
import re


@pytest.mark.regression
class TestCompleteCheckoutFlow:
    """
    End-to-end checkout flow tests
    """
    
    def test_complete_purchase_single_item(self, page):
        """
        REGRESSION TEST: Complete purchase flow with single item
        
        FLOW:
        1. Login
        2. Add one item to cart
        3. Go to cart
        4. Checkout
        5. Fill shipping info
        6. Complete purchase
        7. Verify confirmation
        
        WHY IT MATTERS:
        - Core business flow
        - Must work for revenue generation
        """
        
        # Step 1: Login
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
        
        # Step 2: Add item to cart
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        
        cart_badge = page.locator(".shopping_cart_badge")
        expect(cart_badge).to_have_text("1")
        
        # Step 3: Go to cart
        page.locator(".shopping_cart_link").click()
        
        expect(page).to_have_url("https://www.saucedemo.com/cart.html")
        
        cart_item = page.locator(".cart_item")
        expect(cart_item).to_have_count(1)
        expect(cart_item).to_contain_text("Sauce Labs Backpack")
        
        # Step 4: Checkout
        page.get_by_role("button", name="Checkout").click()
        
        expect(page).to_have_url(
            "https://www.saucedemo.com/checkout-step-one.html"
        )
        
        # Step 5: Fill shipping info
        page.get_by_placeholder("First Name").fill("John")
        page.get_by_placeholder("Last Name").fill("Doe")
        page.get_by_placeholder("Zip/Postal Code").fill("12345")
        page.get_by_role("button", name="Continue").click()
        
        expect(page).to_have_url(
            "https://www.saucedemo.com/checkout-step-two.html"
        )
        
        # Verify order summary
        summary_item = page.locator(".cart_item")
        expect(summary_item).to_contain_text("Sauce Labs Backpack")
        expect(summary_item).to_contain_text("$29.99")
        
        # Verify total (item + tax)
        total = page.locator(".summary_total_label")
        expect(total).to_contain_text("$")
        
        # Step 6: Complete purchase
        page.get_by_role("button", name="Finish").click()
        
        # Step 7: Verify confirmation
        expect(page).to_have_url(
            "https://www.saucedemo.com/checkout-complete.html"
        )
        
        complete_header = page.locator(".complete-header")
        expect(complete_header).to_have_text("Thank you for your order!")
        
        complete_text = page.locator(".complete-text")
        expect(complete_text).to_be_visible()
        
        # Verify back home button
        back_button = page.get_by_role("button", name="Back Home")
        expect(back_button).to_be_visible()
    
    def test_complete_purchase_multiple_items(self, page):
        """
        REGRESSION TEST: Complete purchase flow with multiple items
        
        FLOW: Same as single item but with 3 items
        
        WHY IT MATTERS:
        - Multi-item cart functionality
        - Price calculation with multiple items
        """
        
        # Login
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Add 3 items
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        page.locator("[data-test='add-to-cart-sauce-labs-bike-light']").click()
        page.locator("[data-test='add-to-cart-sauce-labs-bolt-t-shirt']").click()
        
        # Verify cart count
        expect(page.locator(".shopping_cart_badge")).to_have_text("3")
        
        # Go to cart
        page.locator(".shopping_cart_link").click()
        
        # Verify all items in cart
        cart_items = page.locator(".cart_item")
        expect(cart_items).to_have_count(3)
        
        # Checkout
        page.get_by_role("button", name="Checkout").click()
        
        # Fill info
        page.get_by_placeholder("First Name").fill("Jane")
        page.get_by_placeholder("Last Name").fill("Smith")
        page.get_by_placeholder("Zip/Postal Code").fill("90210")
        page.get_by_role("button", name="Continue").click()
        
        # Verify overview shows 3 items
        summary_items = page.locator(".cart_item")
        expect(summary_items).to_have_count(3)
        
        # Verify item subtotal
        # $29.99 + $9.99 + $15.99 = $55.97
        subtotal = page.locator(".summary_subtotal_label")
        expect(subtotal).to_contain_text("$55.97")
        
        # Complete purchase
        page.get_by_role("button", name="Finish").click()
        
        # Verify success
        expect(page.locator(".complete-header")).to_have_text(
            "Thank you for your order!"
        )
    
    def test_checkout_and_continue_shopping(self, page):
        """
        REGRESSION TEST: User completes purchase and continues shopping
        
        FLOW:
        1. Complete a purchase
        2. Click Back Home
        3. Verify can add more items
        
        WHY IT MATTERS:
        - Post-purchase navigation
        - State reset after purchase
        """
        
        # Login
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Quick purchase flow
        page.locator("[data-test='add-to-cart-sauce-labs-onesie']").click()
        page.locator(".shopping_cart_link").click()
        page.get_by_role("button", name="Checkout").click()
        
        page.get_by_placeholder("First Name").fill("Test")
        page.get_by_placeholder("Last Name").fill("User")
        page.get_by_placeholder("Zip/Postal Code").fill("00000")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("button", name="Finish").click()
        
        # Verify success
        expect(page.locator(".complete-header")).to_be_visible()
        
        # Go back home
        page.get_by_role("button", name="Back Home").click()
        
        # Verify on inventory page
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
        
        # Verify cart is empty (badge should not exist)
        expect(page.locator(".shopping_cart_badge")).to_have_count(0)
        
        # Verify can add items again
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("1")


@pytest.mark.regression
class TestCartManagementFlow:
    """
    End-to-end cart management tests
    """
    
    def test_add_remove_multiple_items(self, page):
        """
        REGRESSION TEST: Add and remove multiple items from cart
        
        FLOW:
        1. Add items
        2. Remove some items
        3. Verify cart state
        4. Complete with remaining items
        
        WHY IT MATTERS:
        - Cart manipulation works correctly
        - State consistency
        """
        
        # Login
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Add 4 items
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        page.locator("[data-test='add-to-cart-sauce-labs-bike-light']").click()
        page.locator("[data-test='add-to-cart-sauce-labs-bolt-t-shirt']").click()
        page.locator("[data-test='add-to-cart-sauce-labs-onesie']").click()
        
        expect(page.locator(".shopping_cart_badge")).to_have_text("4")
        
        # Remove 2 items from inventory page
        page.locator("[data-test='remove-sauce-labs-backpack']").click()
        page.locator("[data-test='remove-sauce-labs-onesie']").click()
        
        expect(page.locator(".shopping_cart_badge")).to_have_text("2")
        
        # Go to cart
        page.locator(".shopping_cart_link").click()
        
        # Verify correct items remain
        cart_items = page.locator(".cart_item")
        expect(cart_items).to_have_count(2)
        
        # Verify specific items
        expect(cart_items).to_contain_text(["Sauce Labs Bike Light", "Sauce Labs Bolt T-Shirt"])
        
        # Remove one more from cart page
        page.locator("[data-test='remove-sauce-labs-bike-light']").click()
        
        expect(cart_items).to_have_count(1)
        expect(page.locator(".shopping_cart_badge")).to_have_text("1")
        
        # Complete purchase with remaining item
        page.get_by_role("button", name="Checkout").click()
        page.get_by_placeholder("First Name").fill("Test")
        page.get_by_placeholder("Last Name").fill("User")
        page.get_by_placeholder("Zip/Postal Code").fill("12345")
        page.get_by_role("button", name="Continue").click()
        
        # Verify only one item in summary
        expect(page.locator(".cart_item")).to_have_count(1)
        expect(page.locator(".cart_item")).to_contain_text("Sauce Labs Bolt T-Shirt")
        
        # Complete
        page.get_by_role("button", name="Finish").click()
        expect(page.locator(".complete-header")).to_be_visible()
    
    def test_cart_persists_through_navigation(self, page):
        """
        REGRESSION TEST: Cart contents persist through navigation
        
        FLOW:
        1. Add items
        2. Navigate to different pages
        3. Verify cart contents unchanged
        
        WHY IT MATTERS:
        - Cart state management
        - No accidental loss of cart items
        """
        
        # Login
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Add 2 items
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        page.locator("[data-test='add-to-cart-sauce-labs-bike-light']").click()
        
        expect(page.locator(".shopping_cart_badge")).to_have_text("2")
        
        # Navigate to product detail
        page.locator(".inventory_item_name").first.click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("2")
        
        # Back to products
        page.get_by_role("button", name="Back to products").click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("2")
        
        # Go to cart
        page.locator(".shopping_cart_link").click()
        expect(page.locator(".cart_item")).to_have_count(2)
        
        # Continue shopping
        page.get_by_role("button", name="Continue Shopping").click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("2")
        
        # Sort products
        page.locator("[data-test='product-sort-container']").select_option(
            label="Price (high to low)"
        )
        expect(page.locator(".shopping_cart_badge")).to_have_text("2")


@pytest.mark.regression
class TestUserTypesFlow:
    """
    End-to-end tests for different user types
    """
    
    @pytest.mark.parametrize("username", [
        "standard_user",
        "performance_glitch_user",
    ])
    def test_different_users_can_complete_purchase(self, page, username):
        """
        REGRESSION TEST: Different user types can complete purchase
        
        FLOW: Complete purchase for each user type
        
        WHY IT MATTERS:
        - All user types have working functionality
        - No user-specific bugs
        """
        
        # Login
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill(username)
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Wait for products (performance_glitch_user is slow)
        expect(page.locator(".inventory_item").first).to_be_visible(timeout=15000)
        
        # Add item
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        
        # Complete purchase
        page.locator(".shopping_cart_link").click()
        page.get_by_role("button", name="Checkout").click()
        
        page.get_by_placeholder("First Name").fill("Test")
        page.get_by_placeholder("Last Name").fill("User")
        page.get_by_placeholder("Zip/Postal Code").fill("12345")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("button", name="Finish").click()
        
        # Verify success
        expect(page.locator(".complete-header")).to_have_text(
            "Thank you for your order!"
        )


@pytest.mark.regression
class TestNavigationFlow:
    """
    End-to-end navigation tests
    """
    
    def test_complete_site_navigation(self, page):
        """
        REGRESSION TEST: Navigate through all main pages
        
        FLOW:
        1. Login page  Inventory
        2. Inventory  Product detail
        3. Product detail  Cart
        4. Cart  Checkout step 1
        5. Checkout step 1  Checkout step 2
        6. Checkout step 2  Complete
        7. Complete  Inventory (back home)
        
        WHY IT MATTERS:
        - All navigation paths work
        - No dead ends or broken links
        """
        
        # Login
        page.goto("https://www.saucedemo.com/")
        expect(page).to_have_url("https://www.saucedemo.com/")
        
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Inventory
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
        
        # Add item for later
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        
        # Product detail
        page.locator(".inventory_item_name").first.click()
        expect(page).to_have_url(re.compile(r".*inventory-item.*"))
        
        # Back to inventory
        page.get_by_role("button", name="Back to products").click()
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
        
        # Cart
        page.locator(".shopping_cart_link").click()
        expect(page).to_have_url("https://www.saucedemo.com/cart.html")
        
        # Checkout step 1
        page.get_by_role("button", name="Checkout").click()
        expect(page).to_have_url(
            "https://www.saucedemo.com/checkout-step-one.html"
        )
        
        # Fill form
        page.get_by_placeholder("First Name").fill("Test")
        page.get_by_placeholder("Last Name").fill("User")
        page.get_by_placeholder("Zip/Postal Code").fill("12345")
        
        # Checkout step 2
        page.get_by_role("button", name="Continue").click()
        expect(page).to_have_url(
            "https://www.saucedemo.com/checkout-step-two.html"
        )
        
        # Complete
        page.get_by_role("button", name="Finish").click()
        expect(page).to_have_url(
            "https://www.saucedemo.com/checkout-complete.html"
        )
        
        # Back to inventory
        page.get_by_role("button", name="Back Home").click()
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    def test_hamburger_menu_navigation(self, page):
        """
        REGRESSION TEST: Hamburger menu navigation
        
        FLOW:
        1. Open menu
        2. Navigate to About
        3. Go back and logout
        
        WHY IT MATTERS:
        - Menu functionality
        - Logout works
        """
        
        # Login
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Open menu
        page.get_by_role("button", name="Open Menu").click()
        
        # Verify menu items visible
        menu = page.locator(".bm-menu")
        expect(menu).to_be_visible()
        
        expect(page.locator("#inventory_sidebar_link")).to_be_visible()
        expect(page.locator("#about_sidebar_link")).to_be_visible()
        expect(page.locator("#logout_sidebar_link")).to_be_visible()
        expect(page.locator("#reset_sidebar_link")).to_be_visible()
        
        # Close menu
        page.get_by_role("button", name="Close Menu").click()
        expect(menu).to_be_hidden()
        
        # Open again and logout
        page.get_by_role("button", name="Open Menu").click()
        page.locator("#logout_sidebar_link").click()
        
        # Verify logged out
        expect(page).to_have_url("https://www.saucedemo.com/")
        expect(page.get_by_role("button", name="Login")).to_be_visible()


@pytest.mark.regression
class TestCheckoutValidation:
    """
    Checkout form validation tests
    """
    
    @pytest.fixture(autouse=True)
    def setup_cart(self, page):
        """Setup: Login and add item to cart"""
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        page.locator(".shopping_cart_link").click()
        page.get_by_role("button", name="Checkout").click()
        
        self.page = page
    
    def test_empty_first_name_shows_error(self):
        """Verify first name is required"""
        
        self.page.get_by_placeholder("Last Name").fill("Doe")
        self.page.get_by_placeholder("Zip/Postal Code").fill("12345")
        self.page.get_by_role("button", name="Continue").click()
        
        error = self.page.locator("[data-test='error']")
        expect(error).to_be_visible()
        expect(error).to_contain_text("First Name is required")
    
    def test_empty_last_name_shows_error(self):
        """Verify last name is required"""
        
        self.page.get_by_placeholder("First Name").fill("John")
        self.page.get_by_placeholder("Zip/Postal Code").fill("12345")
        self.page.get_by_role("button", name="Continue").click()
        
        error = self.page.locator("[data-test='error']")
        expect(error).to_be_visible()
        expect(error).to_contain_text("Last Name is required")
    
    def test_empty_postal_code_shows_error(self):
        """Verify postal code is required"""
        
        self.page.get_by_placeholder("First Name").fill("John")
        self.page.get_by_placeholder("Last Name").fill("Doe")
        self.page.get_by_role("button", name="Continue").click()
        
        error = self.page.locator("[data-test='error']")
        expect(error).to_be_visible()
        expect(error).to_contain_text("Postal Code is required")
    
    def test_cancel_returns_to_cart(self):
        """Verify cancel button returns to cart"""
        
        self.page.get_by_role("button", name="Cancel").click()
        
        expect(self.page).to_have_url("https://www.saucedemo.com/cart.html")
        expect(self.page.locator(".cart_item")).to_have_count(1)