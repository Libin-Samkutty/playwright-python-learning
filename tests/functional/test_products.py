"""
TEST FILE: test_products.py
CATEGORY: Functional Tests
PURPOSE: Test product listing, sorting, and detail functionality
RUN: pytest tests/functional/test_products.py -v
     pytest -m functional -v

REAL-WORLD USE:
- Verify product catalog works correctly
- Test sorting and filtering features
- Ensure product details are accurate
"""

import pytest
from playwright.sync_api import expect
import re


class TestProductListing:
    """
    Tests for product listing page functionality
    """
    
    @pytest.fixture(autouse=True)
    def setup_logged_in(self, page):
        """Login before each test in this class"""
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Wait for products to load
        expect(page.locator(".inventory_item").first).to_be_visible()
        
        self.page = page
    
    def test_all_products_displayed(self):
        """
        Verify all 6 products are displayed
        
        WHAT IT CHECKS:
        - Correct number of products shown
        - All products are visible
        
        WHY IT MATTERS:
        - Data loading works correctly
        - No missing products
        """
        
        products = self.page.locator(".inventory_item")
        expect(products).to_have_count(6)
    
    def test_each_product_has_required_elements(self):
        """
        Verify each product has name, description, price, and image
        
        WHAT IT CHECKS:
        - Product structure is complete
        - No missing elements
        
        WHY IT MATTERS:
        - Product display is correct
        - All information available to users
        """
        
        products = self.page.locator(".inventory_item")
        
        for i in range(products.count()):
            product = products.nth(i)
            
            # Check name
            name = product.locator(".inventory_item_name")
            expect(name).to_be_visible()
            expect(name).not_to_be_empty()
            
            # Check description
            desc = product.locator(".inventory_item_desc")
            expect(desc).to_be_visible()
            
            # Check price
            price = product.locator(".inventory_item_price")
            expect(price).to_be_visible()
            expect(price).to_have_text(re.compile(r"\$\d+\.\d{2}"))
            
            # Check image
            image = product.locator("img.inventory_item_img")
            expect(image).to_be_visible()
    
    def test_products_have_add_to_cart_button(self):
        """
        Verify each product has Add to Cart button
        
        WHAT IT CHECKS:
        - Add to cart button exists for each product
        - Buttons are clickable
        
        WHY IT MATTERS:
        - Core e-commerce functionality
        - Users can add items to cart
        """
        
        add_buttons = self.page.locator("[data-test^='add-to-cart']")
        expect(add_buttons).to_have_count(6)
        
        # Check first button is enabled
        expect(add_buttons.first).to_be_enabled()


class TestProductSorting:
    """
    Tests for product sorting functionality
    """
    
    @pytest.fixture(autouse=True)
    def setup_logged_in(self, page):
        """Login before each test"""
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        expect(page.locator(".inventory_item").first).to_be_visible()
        self.page = page
    
    @pytest.mark.parametrize("sort_option,expected_first,expected_last", [
        ("Name (A to Z)", "Sauce Labs Backpack", "Test.allTheThings() T-Shirt (Red)"),
        ("Name (Z to A)", "Test.allTheThings() T-Shirt (Red)", "Sauce Labs Backpack"),
        ("Price (low to high)", "Sauce Labs Onesie", "Sauce Labs Fleece Jacket"),
        ("Price (high to low)", "Sauce Labs Fleece Jacket", "Sauce Labs Onesie"),
    ])
    def test_sorting_orders_products_correctly(
        self, sort_option, expected_first, expected_last
    ):
        """
        Verify sorting works for all options
        
        WHAT IT CHECKS:
        - Each sort option works
        - First and last products are correct
        
        WHY IT MATTERS:
        - Sort functionality is essential for UX
        - Users expect correct ordering
        """
        
        # Select sort option
        sort_dropdown = self.page.locator("[data-test='product-sort-container']")
        sort_dropdown.select_option(label=sort_option)
        
        # Verify first product
        first_product = self.page.locator(".inventory_item_name").first
        expect(first_product).to_have_text(expected_first)
        
        # Verify last product
        last_product = self.page.locator(".inventory_item_name").last
        expect(last_product).to_have_text(expected_last)
    
    def test_default_sort_is_a_to_z(self):
        """
        Verify default sort is Name (A to Z)
        
        WHAT IT CHECKS:
        - Initial page load has correct default sort
        - Dropdown shows correct selection
        
        WHY IT MATTERS:
        - Consistent user experience
        - Expected default behavior
        """
        
        # Check dropdown value
        sort_dropdown = self.page.locator("[data-test='product-sort-container']")
        expect(sort_dropdown).to_have_value("az")
        
        # Check first product
        first_product = self.page.locator(".inventory_item_name").first
        expect(first_product).to_have_text("Sauce Labs Backpack")
    
    def test_sort_persists_after_viewing_product(self):
        """
        Verify sort order persists after viewing product detail
        
        WHAT IT CHECKS:
        - Sort is maintained after navigation
        - User doesn't lose their selection
        
        WHY IT MATTERS:
        - UX - users expect sort to persist
        - State management works
        """
        
        # Sort by price high to low
        sort_dropdown = self.page.locator("[data-test='product-sort-container']")
        sort_dropdown.select_option(label="Price (high to low)")
        
        # Click on a product
        self.page.locator(".inventory_item_name").first.click()
        
        # Go back
        self.page.get_by_role("button", name="Back to products").click()
        
        # Verify sort is still applied
        expect(sort_dropdown).to_have_value("az")
        
        first_product = self.page.locator(".inventory_item_name").first
        expect(first_product).to_have_text("Sauce Labs Backpack")


class TestProductDetail:
    """
    Tests for product detail page
    """
    
    @pytest.fixture(autouse=True)
    def setup_logged_in(self, page):
        """Login before each test"""
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        expect(page.locator(".inventory_item").first).to_be_visible()
        self.page = page
    
    def test_click_product_opens_detail_page(self):
        """
        Verify clicking product name opens detail page
        
        WHAT IT CHECKS:
        - Product name is clickable
        - Detail page loads
        
        WHY IT MATTERS:
        - Navigation to product details works
        - Users can view more information
        """
        
        # Click first product name
        first_product_name = self.page.locator(".inventory_item_name").first
        product_text = first_product_name.text_content()
        first_product_name.click()
        
        # Verify on detail page
        expect(self.page).to_have_url(re.compile(r".*inventory-item.*"))
        
        # Verify product name on detail page
        detail_name = self.page.locator(".inventory_details_name")
        expect(detail_name).to_have_text(product_text)
    
    def test_product_detail_shows_all_information(self):
        """
        Verify product detail page shows complete information
        
        WHAT IT CHECKS:
        - Name, description, price, image present
        - Add to cart button available
        
        WHY IT MATTERS:
        - Users need complete product information
        - Call-to-action (add to cart) must be present
        """
        
        # Go to first product detail
        self.page.locator(".inventory_item_name").first.click()
        
        # Check all elements
        expect(self.page.locator(".inventory_details_name")).to_be_visible()
        expect(self.page.locator(".inventory_details_desc")).to_be_visible()
        expect(self.page.locator(".inventory_details_price")).to_be_visible()
        expect(self.page.locator(".inventory_details_img")).to_be_visible()
        expect(self.page.locator("[data-test^='add-to-cart']")).to_be_visible()
    
    def test_back_button_returns_to_inventory(self):
        """
        Verify back button returns to product listing
        
        WHAT IT CHECKS:
        - Back button works
        - Returns to correct page
        
        WHY IT MATTERS:
        - Navigation flow works
        - Users can return to shopping
        """
        
        # Go to product detail
        self.page.locator(".inventory_item_name").first.click()
        expect(self.page).to_have_url(re.compile(r".*inventory-item.*"))
        
        # Click back
        self.page.get_by_role("button", name="Back to products").click()
        
        # Verify back on inventory
        expect(self.page).to_have_url("https://www.saucedemo.com/inventory.html")
        expect(self.page.locator(".inventory_item")).to_have_count(6)
    
    def test_add_to_cart_from_detail_page(self):
        """
        Verify add to cart works from detail page
        
        WHAT IT CHECKS:
        - Add to cart button works
        - Cart badge updates
        - Button changes to Remove
        
        WHY IT MATTERS:
        - Core purchase functionality
        - Visual feedback works
        """
        
        # Go to product detail
        self.page.locator(".inventory_item_name").first.click()
        
        # Add to cart
        add_button = self.page.locator("[data-test^='add-to-cart']")
        add_button.click()
        
        # Verify cart badge
        cart_badge = self.page.locator(".shopping_cart_badge")
        expect(cart_badge).to_have_text("1")
        
        # Verify button changed to Remove
        remove_button = self.page.locator("[data-test^='remove']")
        expect(remove_button).to_be_visible()


class TestProductPrices:
    """
    Tests for product pricing
    """
    
    @pytest.fixture(autouse=True)
    def setup_logged_in(self, page):
        """Login before each test"""
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        self.page = page
    
    @pytest.mark.parametrize("product_name,expected_price", [
        ("Sauce Labs Backpack", "$29.99"),
        ("Sauce Labs Bike Light", "$9.99"),
        ("Sauce Labs Bolt T-Shirt", "$15.99"),
        ("Sauce Labs Fleece Jacket", "$49.99"),
        ("Sauce Labs Onesie", "$7.99"),
        ("Test.allTheThings() T-Shirt (Red)", "$15.99"),
    ])
    def test_product_prices_are_correct(self, product_name, expected_price):
        """
        Verify each product has correct price
        
        WHAT IT CHECKS:
        - Price matches expected value
        - No pricing errors
        
        WHY IT MATTERS:
        - Pricing accuracy is critical
        - Errors can cause legal/financial issues
        """
        
        product = self.page.locator(".inventory_item").filter(has_text=product_name)
        price = product.locator(".inventory_item_price")
        
        expect(price).to_have_text(expected_price)
    
    def test_all_prices_have_valid_format(self):
        """
        Verify all prices follow correct format
        
        WHAT IT CHECKS:
        - Price format is $XX.XX
        - No malformed prices
        
        WHY IT MATTERS:
        - Consistent display
        - Data integrity
        """
        
        prices = self.page.locator(".inventory_item_price")
        
        for i in range(prices.count()):
            price = prices.nth(i)
            expect(price).to_have_text(re.compile(r"^\$\d+\.\d{2}$"))