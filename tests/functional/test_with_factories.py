"""
tests/functional/test_with_factories.py
Tests using data factories
"""

import pytest
from playwright.sync_api import expect
from data import UserFactory, ProductFactory


class TestLoginWithFactories:
    """Login tests using data factories"""
    
    def test_login_standard_user(self, page):
        """Login with factory user"""
        
        user = UserFactory.standard_user()
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill(user.username)
        page.get_by_placeholder("Password").fill(user.password)
        page.get_by_role("button", name="Login").click()
        
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    @pytest.mark.parametrize("user", UserFactory.all_valid_users(), ids=lambda u: u.username)
    def test_all_valid_users_can_login(self, page, user):
        """Test all valid users can login"""
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill(user.username)
        page.get_by_placeholder("Password").fill(user.password)
        page.get_by_role("button", name="Login").click()
        
        # Performance user needs longer timeout
        timeout = 15000 if "performance" in user.username else 5000
        expect(page).to_have_url(
            "https://www.saucedemo.com/inventory.html",
            timeout=timeout
        )
    
    def test_invalid_user_rejected(self, page):
        """Invalid user should be rejected"""
        
        user = UserFactory.invalid_user()
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill(user.username)
        page.get_by_placeholder("Password").fill(user.password)
        page.get_by_role("button", name="Login").click()
        
        expect(page.locator("[data-test='error']")).to_be_visible()


class TestProductsWithFactories:
    """Product tests using data factories"""
    
    @pytest.fixture(autouse=True)
    def login(self, page):
        """Login before each test"""
        
        user = UserFactory.standard_user()
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill(user.username)
        page.get_by_placeholder("Password").fill(user.password)
        page.get_by_role("button", name="Login").click()
        
        expect(page.locator(".inventory_item").first).to_be_visible()
        self.page = page
    
    def test_all_products_displayed(self):
        """All products from factory should be displayed"""
        
        expected_count = len(ProductFactory.all_products())
        products = self.page.locator(".inventory_item")
        
        expect(products).to_have_count(expected_count)
    
    @pytest.mark.parametrize("product", ProductFactory.all_products(), ids=lambda p: p.id)
    def test_product_price_correct(self, product):
        """Verify each product has correct price"""
        
        product_card = self.page.locator(".inventory_item").filter(
            has_text=product.name
        )
        price_element = product_card.locator(".inventory_item_price")
        
        expect(price_element).to_have_text(product.price_display)
    
    def test_add_cheapest_product(self):
        """Add cheapest product to cart"""
        
        product = ProductFactory.get_cheapest()
        
        add_button = self.page.locator(f"[data-test='{product.add_to_cart_id}']")
        add_button.click()
        
        expect(self.page.locator(".shopping_cart_badge")).to_have_text("1")
    
    def test_sort_by_price_low_to_high(self):
        """Verify sort matches factory data"""
        
        # Sort on page
        self.page.locator("[data-test='product-sort-container']").select_option(
            label="Price (low to high)"
        )
        
        # Get expected order from factory
        expected_order = ProductFactory.sorted_by_price_asc()
        
        # Verify first product
        first_name = self.page.locator(".inventory_item_name").first
        expect(first_name).to_have_text(expected_order[0].name)
    
    def test_cart_total_calculation(self):
        """Verify cart total with multiple products"""
        
        # Get 3 random products
        products = ProductFactory.random_products(3)
        expected_total = ProductFactory.total_price(products)
        
        # Add products
        for product in products:
            self.page.locator(f"[data-test='{product.add_to_cart_id}']").click()
        
        # Go to checkout
        self.page.locator(".shopping_cart_link").click()
        self.page.get_by_role("button", name="Checkout").click()
        self.page.get_by_placeholder("First Name").fill("Test")
        self.page.get_by_placeholder("Last Name").fill("User")
        self.page.get_by_placeholder("Zip/Postal Code").fill("12345")
        self.page.get_by_role("button", name="Continue").click()
        
        # Verify subtotal
        subtotal = self.page.locator(".summary_subtotal_label")
        expect(subtotal).to_contain_text(f"${expected_total:.2f}")
