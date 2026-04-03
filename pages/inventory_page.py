"""
pages/inventory_page.py
Inventory/Products Page Object

Handles:
- Product listing
- Sorting
- Add to cart
- Navigation to product details
"""

from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage
from typing import List, Optional
import re


class InventoryPage(BasePage):
    """
    Page Object for the Inventory/Products Page
    
    URL: https://www.saucedemo.com/inventory.html
    """
    
    URL = "https://www.saucedemo.com/inventory.html"
    URL_PATTERN = r".*inventory\.html$"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    # -------------------- Header --------------------
    
    @property
    def header_title(self):
        """Page header title"""
        return self.page.locator(".title")
    
    @property
    def shopping_cart_link(self):
        """Shopping cart icon/link"""
        return self.page.locator(".shopping_cart_link")
    
    @property
    def cart_badge(self):
        """Cart item count badge"""
        return self.page.locator(".shopping_cart_badge")
    
    @property
    def hamburger_menu(self):
        """Menu button (hamburger icon)"""
        return self.page.get_by_role("button", name="Open Menu")
    
    # -------------------- Sorting --------------------
    
    @property
    def sort_dropdown(self):
        """Product sort dropdown"""
        return self.page.locator("[data-test='product-sort-container']")
    
    # -------------------- Products --------------------
    
    @property
    def product_items(self):
        """All product items"""
        return self.page.locator(".inventory_item")
    
    @property
    def product_names(self):
        """All product name elements"""
        return self.page.locator(".inventory_item_name")
    
    @property
    def product_prices(self):
        """All product price elements"""
        return self.page.locator(".inventory_item_price")
    
    @property
    def product_descriptions(self):
        """All product description elements"""
        return self.page.locator(".inventory_item_desc")
    
    @property
    def add_to_cart_buttons(self):
        """All 'Add to cart' buttons"""
        return self.page.locator("[data-test^='add-to-cart']")
    
    @property
    def remove_buttons(self):
        """All 'Remove' buttons"""
        return self.page.locator("[data-test^='remove']")
    
    # -------------------- Menu --------------------
    
    @property
    def menu_panel(self):
        """Side menu panel"""
        return self.page.locator(".bm-menu")
    
    @property
    def logout_link(self):
        """Logout menu link"""
        return self.page.locator("#logout_sidebar_link")
    
    @property
    def close_menu_button(self):
        """Close menu button"""
        return self.page.get_by_role("button", name="Close Menu")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def sort_by(self, option: str) -> "InventoryPage":
        """
        Sort products by given option
        
        Args:
            option: Sort option label
                - "Name (A to Z)"
                - "Name (Z to A)"
                - "Price (low to high)"
                - "Price (high to low)"
        
        Returns:
            Self for method chaining
        
        Example:
            inventory_page.sort_by("Price (low to high)")
        """
        self.sort_dropdown.select_option(label=option)
        return self
    
    def sort_by_name_asc(self) -> "InventoryPage":
        """Sort by name A to Z"""
        return self.sort_by("Name (A to Z)")
    
    def sort_by_name_desc(self) -> "InventoryPage":
        """Sort by name Z to A"""
        return self.sort_by("Name (Z to A)")
    
    def sort_by_price_low_to_high(self) -> "InventoryPage":
        """Sort by price ascending"""
        return self.sort_by("Price (low to high)")
    
    def sort_by_price_high_to_low(self) -> "InventoryPage":
        """Sort by price descending"""
        return self.sort_by("Price (high to low)")
    
    def add_to_cart_by_name(self, product_name: str) -> "InventoryPage":
        """
        Add product to cart by name
        
        Args:
            product_name: Product name to add
        
        Returns:
            Self for method chaining
        
        Example:
            inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
        """
        product = self.product_items.filter(has_text=product_name)
        product.locator("[data-test^='add-to-cart']").click()
        return self
    
    def add_to_cart_by_index(self, index: int) -> "InventoryPage":
        """
        Add product to cart by index
        
        Args:
            index: 0-based product index
        
        Returns:
            Self for method chaining
        """
        self.add_to_cart_buttons.nth(index).click()
        return self
    
    def add_all_to_cart(self) -> "InventoryPage":
        """
        Add all products to cart
        
        Returns:
            Self for method chaining
        """
        count = self.add_to_cart_buttons.count()
        for i in range(count):
            self.add_to_cart_buttons.first.click()  # Always click first available
        return self
    
    def remove_from_cart_by_name(self, product_name: str) -> "InventoryPage":
        """
        Remove product from cart by name
        
        Args:
            product_name: Product name to remove
        
        Returns:
            Self for method chaining
        """
        product = self.product_items.filter(has_text=product_name)
        product.locator("[data-test^='remove']").click()
        return self
    
    def go_to_cart(self) -> "InventoryPage":
        """
        Navigate to shopping cart
        
        Returns:
            Self for method chaining
        """
        self.shopping_cart_link.click()
        return self
    
    def open_product_details(self, product_name: str) -> "InventoryPage":
        """
        Click on product to view details
        
        Args:
            product_name: Product name to view
        
        Returns:
            Self for method chaining
        """
        self.product_names.filter(has_text=product_name).click()
        return self
    
    def open_menu(self) -> "InventoryPage":
        """Open hamburger menu"""
        self.hamburger_menu.click()
        expect(self.menu_panel).to_be_visible()
        return self
    
    def close_menu(self) -> "InventoryPage":
        """Close hamburger menu"""
        self.close_menu_button.click()
        expect(self.menu_panel).to_be_hidden()
        return self
    
    def logout(self) -> "InventoryPage":
        """
        Logout via menu
        
        Returns:
            Self for method chaining
        """
        self.open_menu()
        self.logout_link.click()
        return self
    
    # ============================================================
    # GETTERS
    # ============================================================
    
    def get_cart_count(self) -> int:
        """
        Get number of items in cart
        
        Returns:
            Cart item count (0 if badge not visible)
        """
        if not self.cart_badge.is_visible():
            return 0
        return int(self.cart_badge.text_content() or "0")
    
    def get_product_count(self) -> int:
        """
        Get number of products displayed
        
        Returns:
            Product count
        """
        return self.product_items.count()
    
    def get_product_names(self) -> List[str]:
        """
        Get all product names
        
        Returns:
            List of product names
        """
        return self.product_names.all_text_contents()
    
    def get_product_prices(self) -> List[str]:
        """
        Get all product prices
        
        Returns:
            List of price strings (e.g., ["$29.99", "$9.99"])
        """
        return self.product_prices.all_text_contents()
    
    def get_product_price_by_name(self, product_name: str) -> str:
        """
        Get price for specific product
        
        Args:
            product_name: Product name
        
        Returns:
            Price string (e.g., "$29.99")
        """
        product = self.product_items.filter(has_text=product_name)
        return product.locator(".inventory_item_price").text_content() or ""
    
    def get_first_product_name(self) -> str:
        """Get first product name"""
        return self.product_names.first.text_content() or ""
    
    def get_last_product_name(self) -> str:
        """Get last product name"""
        return self.product_names.last.text_content() or ""
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def is_loaded(self) -> bool:
        """
        Check if inventory page is loaded
        
        Returns:
            True if on inventory page
        """
        try:
            expect(self.product_items.first).to_be_visible(timeout=5000)
            return True
        except AssertionError:
            return False
    
    def verify_product_count(self, expected: int) -> "InventoryPage":
        """
        Verify number of products
        
        Args:
            expected: Expected product count
        
        Returns:
            Self for method chaining
        """
        expect(self.product_items).to_have_count(expected)
        return self
    
    def verify_cart_count(self, expected: int) -> "InventoryPage":
        """
        Verify cart badge count
        
        Args:
            expected: Expected cart count
        
        Returns:
            Self for method chaining
        """
        if expected == 0:
            expect(self.cart_badge).to_have_count(0)
        else:
            expect(self.cart_badge).to_have_text(str(expected))
        return self
    
    def verify_sorted_by_name_asc(self) -> "InventoryPage":
        """Verify products sorted by name A-Z"""
        names = self.get_product_names()
        assert names == sorted(names), "Products not sorted A-Z"
        return self
    
    def verify_sorted_by_name_desc(self) -> "InventoryPage":
        """Verify products sorted by name Z-A"""
        names = self.get_product_names()
        assert names == sorted(names, reverse=True), "Products not sorted Z-A"
        return self
    
    def verify_sorted_by_price_asc(self) -> "InventoryPage":
        """Verify products sorted by price low to high"""
        prices = self.get_product_prices()
        # Convert "$29.99" to 29.99
        numeric_prices = [float(p.replace("$", "")) for p in prices]
        assert numeric_prices == sorted(numeric_prices), \
            "Products not sorted by price ascending"
        return self
    
    def verify_sorted_by_price_desc(self) -> "InventoryPage":
        """Verify products sorted by price high to low"""
        prices = self.get_product_prices()
        numeric_prices = [float(p.replace("$", "")) for p in prices]
        assert numeric_prices == sorted(numeric_prices, reverse=True), \
            "Products not sorted by price descending"
        return self
