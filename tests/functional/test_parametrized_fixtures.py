"""
tests/functional/test_parametrized_fixtures.py
Tests using parametrized fixtures
"""

import pytest
from playwright.sync_api import expect


class TestCrossBrowser:
    """
    Cross-browser tests using multi_browser fixture
    """
    
    def test_homepage_loads_all_browsers(self, multi_browser, test_data):
        """
        This test runs 3 times:
        - test_homepage_loads_all_browsers[chromium]
        - test_homepage_loads_all_browsers[firefox]
        - test_homepage_loads_all_browsers[webkit]
        """
        
        context = multi_browser.new_context()
        page = context.new_page()
        
        page.goto(test_data["urls"]["base"])
        
        expect(page).to_have_title("Swag Labs")
        
        context.close()


class TestResponsiveLayouts:
    """
    Responsive tests using responsive_page fixture
    """
    
    def test_login_form_visible_all_viewports(self, responsive_page, test_data):
        """
        Runs 3 times:
        - test_login_form_visible_all_viewports[mobile]
        - test_login_form_visible_all_viewports[tablet]
        - test_login_form_visible_all_viewports[desktop]
        """
        
        responsive_page.goto(test_data["urls"]["base"])
        
        # Login form should be visible in all viewports
        expect(responsive_page.get_by_placeholder("Username")).to_be_visible()
        expect(responsive_page.get_by_placeholder("Password")).to_be_visible()
        expect(
            responsive_page.get_by_role("button", name="Login")
        ).to_be_visible()
        
        print(f"Tested on: {responsive_page.viewport_name}")


class TestUserExperiences:
    """
    Tests for different user types
    """
    
    def test_products_visible_for_all_users(self, user_page):
        """
        Runs 3 times with different users
        """
        
        products = user_page.locator(".inventory_item")
        expect(products).to_have_count(6)
        
        print(f"Tested with user: {user_page.username}")


class TestProductCatalog:
    """
    Tests using product data fixture
    """
    
    def test_product_price_displayed(self, logged_in_page, product_info):
        """
        Runs 3 times:
        - test_product_price_displayed[backpack]
        - test_product_price_displayed[bike_light]
        - test_product_price_displayed[onesie]
        """
        
        product = logged_in_page.locator(".inventory_item").filter(
            has_text=product_info["name"]
        )
        
        price = product.locator(".inventory_item_price")
        expect(price).to_have_text(product_info["price"])