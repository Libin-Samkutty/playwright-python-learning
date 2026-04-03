"""
pages/cart_page.py
Shopping Cart Page Object

Handles:
- Cart item management
- Checkout navigation
- Continue shopping
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from typing import List


class CartPage(BasePage):
    """
    Page Object for the Shopping Cart Page
    
    URL: https://www.saucedemo.com/cart.html
    """
    
    URL = "https://www.saucedemo.com/cart.html"
    URL_PATTERN = r".*cart\.html$"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    @property
    def cart_items(self):
        """All cart items"""
        return self.page.locator(".cart_item")
    
    @property
    def cart_item_names(self):
        """All cart item names"""
        return self.page.locator(".inventory_item_name")
    
    @property
    def cart_item_prices(self):
        """All cart item prices"""
        return self.page.locator(".inventory_item_price")
    
    @property
    def cart_item_quantities(self):
        """All cart item quantities"""
        return self.page.locator(".cart_quantity")
    
    @property
    def remove_buttons(self):
        """All remove buttons"""
        return self.page.locator("[data-test^='remove']")
    
    @property
    def continue_shopping_button(self):
        """Continue Shopping button"""
        return self.page.get_by_role("button", name="Continue Shopping")
    
    @property
    def checkout_button(self):
        """Checkout button"""
        return self.page.get_by_role("button", name="Checkout")
    
    @property
    def cart_badge(self):
        """Cart badge showing item count"""
        return self.page.locator(".shopping_cart_badge")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def remove_item_by_name(self, product_name: str) -> "CartPage":
        """
        Remove item from cart by name
        
        Args:
            product_name: Product name to remove
        
        Returns:
            Self for method chaining
        """
        item = self.cart_items.filter(has_text=product_name)
        item.locator("[data-test^='remove']").click()
        return self
    
    def remove_item_by_index(self, index: int) -> "CartPage":
        """
        Remove item by index
        
        Args:
            index: 0-based index
        
        Returns:
            Self for method chaining
        """
        self.remove_buttons.nth(index).click()
        return self
    
    def remove_all_items(self) -> "CartPage":
        """
        Remove all items from cart
        
        Returns:
            Self for method chaining
        """
        while self.remove_buttons.count() > 0:
            self.remove_buttons.first.click()
        return self
    
    def continue_shopping(self) -> "CartPage":
        """
        Click Continue Shopping button
        
        Returns:
            Self for method chaining
        """
        self.continue_shopping_button.click()
        return self
    
    def proceed_to_checkout(self) -> "CartPage":
        """
        Click Checkout button
        
        Returns:
            Self for method chaining
        """
        self.checkout_button.click()
        return self
    
    # ============================================================
    # GETTERS
    # ============================================================
    
    def get_item_count(self) -> int:
        """
        Get number of items in cart
        
        Returns:
            Item count
        """
        return self.cart_items.count()
    
    def get_item_names(self) -> List[str]:
        """
        Get all item names in cart
        
        Returns:
            List of item names
        """
        return self.cart_item_names.all_text_contents()
    
    def get_item_prices(self) -> List[str]:
        """
        Get all item prices
        
        Returns:
            List of price strings
        """
        return self.cart_item_prices.all_text_contents()
    
    def get_total_price(self) -> float:
        """
        Calculate total price of cart items
        
        Returns:
            Total price as float
        """
        prices = self.get_item_prices()
        return sum(float(p.replace("$", "")) for p in prices)
    
    def has_item(self, product_name: str) -> bool:
        """
        Check if cart has specific item
        
        Args:
            product_name: Product name to check
        
        Returns:
            True if item in cart
        """
        return self.cart_items.filter(has_text=product_name).count() > 0
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def is_loaded(self) -> bool:
        """Check if cart page is loaded"""
        try:
            expect(self.checkout_button).to_be_visible(timeout=5000)
            return True
        except AssertionError:
            return False
    
    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return self.cart_items.count() == 0
    
    def verify_item_count(self, expected: int) -> "CartPage":
        """Verify number of items in cart"""
        expect(self.cart_items).to_have_count(expected)
        return self
    
    def verify_item_in_cart(self, product_name: str) -> "CartPage":
        """Verify specific item is in cart"""
        item = self.cart_items.filter(has_text=product_name)
        expect(item).to_have_count(1)
        return self
    
    def verify_item_not_in_cart(self, product_name: str) -> "CartPage":
        """Verify specific item is NOT in cart"""
        item = self.cart_items.filter(has_text=product_name)
        expect(item).to_have_count(0)
        return self
    
    def verify_cart_empty(self) -> "CartPage":
        """Verify cart is empty"""
        expect(self.cart_items).to_have_count(0)
        return self
