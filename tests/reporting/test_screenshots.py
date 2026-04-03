"""
tests/reporting/test_screenshots.py
Tests demonstrating screenshot management
"""

import pytest
from playwright.sync_api import expect


class TestScreenshotCapture:
    """
    Demonstrate various screenshot techniques
    """
    
    def test_capture_test_flow(self, page, screenshot_manager):
        """
        Capture screenshots at each step of a test
        """
        
        # Step 1: Login page
        page.goto("https://www.saucedemo.com/")
        screenshot_manager.capture(
            page, 
            "01_login_page", 
            "Initial login page"
        )
        
        # Step 2: Fill credentials
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        screenshot_manager.capture(
            page, 
            "02_credentials_filled", 
            "Login form with credentials"
        )
        
        # Step 3: After login
        page.get_by_role("button", name="Login").click()
        expect(page.locator(".inventory_item").first).to_be_visible()
        screenshot_manager.capture(
            page, 
            "03_logged_in", 
            "Inventory page after login",
            full_page=True,
        )
        
        # Step 4: Capture specific element
        first_product = page.locator(".inventory_item").first
        screenshot_manager.capture_element(
            first_product,
            "04_first_product",
            "First product card",
        )
        
        # Get all screenshots
        screenshots = screenshot_manager.get_all_screenshots()
        print(f"\n Captured {len(screenshots)} screenshots")
        for ss in screenshots:
            print(f"  - {ss['name']}: {ss['filepath']}")
    
    def test_capture_with_highlights(self, page, screenshot_manager):
        """
        Capture screenshots with highlighted elements
        """
        
        page.goto("https://www.saucedemo.com/")
        
        # Highlight username field
        username_field = page.get_by_placeholder("Username")
        screenshot_manager.capture_with_highlight(
            page,
            username_field,
            "highlighted_username",
            "Username field highlighted",
        )
        
        # Highlight login button
        login_button = page.get_by_role("button", name="Login")
        screenshot_manager.capture_with_highlight(
            page,
            login_button,
            "highlighted_login_button",
            "Login button highlighted",
            highlight_style="5px solid blue",
        )
    
    def test_before_after_comparison(self, page, screenshot_manager):
        """
        Capture before/after screenshots for comparison
        """
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        expect(page.locator(".inventory_item").first).to_be_visible()
        
        def before_sort():
            pass  # Already on page
        
        def after_sort():
            page.locator("[data-test='product-sort-container']").select_option(
                label="Price (low to high)"
            )
        
        before_path, after_path = screenshot_manager.capture_comparison(
            page,
            "sort_products",
            before_sort,
            after_sort,
            "Product sorting comparison",
        )
        
        print(f"\n Comparison screenshots:")
        print(f"  Before: {before_path}")
        print(f"  After: {after_path}")
