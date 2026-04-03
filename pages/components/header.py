"""
pages/components/header.py
Header Component - reusable across pages

Components are reusable UI elements that appear on multiple pages.
"""

from playwright.sync_api import Page, Locator, expect


class Header:
    """
    Header component shared across authenticated pages
    
    Contains:
    - Hamburger menu
    - Title
    - Cart link
    """
    
    def __init__(self, page: Page):
        self.page = page
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    @property
    def root(self) -> Locator:
        """Header container"""
        return self.page.locator(".primary_header")
    
    @property
    def menu_button(self) -> Locator:
        """Hamburger menu button"""
        return self.page.get_by_role("button", name="Open Menu")
    
    @property
    def title(self) -> Locator:
        """App title"""
        return self.page.locator(".app_logo")
    
    @property
    def cart_link(self) -> Locator:
        """Shopping cart link"""
        return self.page.locator(".shopping_cart_link")
    
    @property
    def cart_badge(self) -> Locator:
        """Cart item count badge"""
        return self.page.locator(".shopping_cart_badge")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def open_menu(self) -> "Header":
        """Open sidebar menu"""
        self.menu_button.click()
        return self
    
    def go_to_cart(self) -> "Header":
        """Navigate to cart"""
        self.cart_link.click()
        return self
    
    # ============================================================
    # GETTERS
    # ============================================================
    
    def get_cart_count(self) -> int:
        """Get cart item count"""
        if not self.cart_badge.is_visible():
            return 0
        return int(self.cart_badge.text_content() or "0")
    
    def get_title(self) -> str:
        """Get app title"""
        return self.title.text_content() or ""
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def verify_cart_count(self, expected: int) -> "Header":
        """Verify cart badge count"""
        if expected == 0:
            expect(self.cart_badge).to_have_count(0)
        else:
            expect(self.cart_badge).to_have_text(str(expected))
        return self