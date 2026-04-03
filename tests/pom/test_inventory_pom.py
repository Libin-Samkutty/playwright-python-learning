"""
tests/pom/test_inventory_pom.py
Inventory tests using Page Object Model
"""

import pytest


class TestInventoryWithPOM:
    """
    Inventory/Product tests with POM
    """
    
    def test_all_products_displayed(self, logged_in_user):
        """Test: All 6 products are displayed"""
        
        # logged_in_user IS the inventory page (from fixture)
        logged_in_user.verify_product_count(6)
    
    def test_add_single_item_to_cart(self, logged_in_user, header):
        """Test: Add single item to cart"""
        
        logged_in_user.add_to_cart_by_name("Sauce Labs Backpack")
        
        # Verify using header component
        header.verify_cart_count(1)
        
        # Or using page method
        logged_in_user.verify_cart_count(1)
    
    def test_add_multiple_items_to_cart(self, logged_in_user):
        """Test: Add multiple items to cart"""
        
        logged_in_user.add_to_cart_by_name("Sauce Labs Backpack")
        logged_in_user.add_to_cart_by_name("Sauce Labs Bike Light")
        logged_in_user.add_to_cart_by_name("Sauce Labs Onesie")
        
        logged_in_user.verify_cart_count(3)
    
    def test_remove_item_from_cart(self, logged_in_user):
        """Test: Remove item from cart"""
        
        logged_in_user.add_to_cart_by_name("Sauce Labs Backpack")
        logged_in_user.verify_cart_count(1)
        
        logged_in_user.remove_from_cart_by_name("Sauce Labs Backpack")
        logged_in_user.verify_cart_count(0)
    
    def test_sort_by_price_low_to_high(self, logged_in_user):
        """Test: Sort products by price ascending"""
        
        logged_in_user.sort_by_price_low_to_high()
        
        # Verify first product is cheapest
        first_product = logged_in_user.get_first_product_name()
        assert first_product == "Sauce Labs Onesie"
        
        logged_in_user.verify_sorted_by_price_asc()
    
    def test_sort_by_price_high_to_low(self, logged_in_user):
        """Test: Sort products by price descending"""
        
        logged_in_user.sort_by_price_high_to_low()
        
        first_product = logged_in_user.get_first_product_name()
        assert first_product == "Sauce Labs Fleece Jacket"
        
        logged_in_user.verify_sorted_by_price_desc()
    
    def test_sort_by_name_a_to_z(self, logged_in_user):
        """Test: Sort products by name A-Z"""
        
        logged_in_user.sort_by_name_asc()
        
        logged_in_user.verify_sorted_by_name_asc()
    
    def test_sort_by_name_z_to_a(self, logged_in_user):
        """Test: Sort products by name Z-A"""
        
        logged_in_user.sort_by_name_desc()
        
        logged_in_user.verify_sorted_by_name_desc()
    
    def test_navigate_to_cart(self, logged_in_user, cart_page):
        """Test: Navigate to cart page"""
        
        logged_in_user.go_to_cart()
        
        assert cart_page.is_loaded()
    
    def test_product_prices_correct(self, logged_in_user):
        """Test: Verify specific product prices"""
        
        backpack_price = logged_in_user.get_product_price_by_name(
            "Sauce Labs Backpack"
        )
        assert backpack_price == "$29.99"
        
        onesie_price = logged_in_user.get_product_price_by_name(
            "Sauce Labs Onesie"
        )
        assert onesie_price == "$7.99"
