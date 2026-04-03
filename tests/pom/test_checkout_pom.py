"""
tests/pom/test_checkout_pom.py
Checkout tests using Page Object Model
"""

import pytest


class TestCheckoutWithPOM:
    """
    Checkout flow tests with POM
    """
    
    def test_complete_checkout_flow(
        self,
        login_page,
        inventory_page,
        cart_page,
        checkout_page,
        checkout_step_two_page,
        checkout_complete_page,
    ):
        """
        Test: Complete purchase flow
        
        Demonstrates full flow using multiple page objects
        """
        
        # Login
        login_page.navigate()
        login_page.login_as_standard_user()
        
        # Add item to cart
        inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
        inventory_page.go_to_cart()
        
        # Verify cart
        cart_page.verify_item_count(1)
        cart_page.verify_item_in_cart("Sauce Labs Backpack")
        
        # Checkout
        cart_page.proceed_to_checkout()
        
        # Fill information
        checkout_page.fill_information("John", "Doe", "12345")
        checkout_page.click_continue()
        
        # Verify overview
        assert checkout_step_two_page.is_loaded()
        checkout_step_two_page.verify_item_count(1)
        checkout_step_two_page.verify_total_calculation()
        
        # Complete purchase
        checkout_step_two_page.complete_purchase()
        
        # Verify success
        assert checkout_complete_page.is_loaded()
        checkout_complete_page.verify_order_complete()
    
    def test_checkout_with_fixture(self, user_at_checkout, checkout_step_two_page):
        """
        Test: Checkout using convenience fixture
        
        Fixture handles login, add to cart, navigate to checkout
        """
        
        user_at_checkout.fill_information("Jane", "Smith", "90210")
        user_at_checkout.click_continue()
        
        assert checkout_step_two_page.is_loaded()
        checkout_step_two_page.complete_purchase()
    
    def test_checkout_validation_first_name(self, user_at_checkout):
        """Test: First name required validation"""
        
        user_at_checkout.fill_information("", "Doe", "12345")
        user_at_checkout.click_continue()
        
        user_at_checkout.verify_error_message("First Name is required")
    
    def test_checkout_validation_last_name(self, user_at_checkout):
        """Test: Last name required validation"""
        
        user_at_checkout.fill_information("John", "", "12345")
        user_at_checkout.click_continue()
        
        user_at_checkout.verify_error_message("Last Name is required")
    
    def test_checkout_validation_postal_code(self, user_at_checkout):
        """Test: Postal code required validation"""
        
        user_at_checkout.fill_information("John", "Doe", "")
        user_at_checkout.click_continue()
        
        user_at_checkout.verify_error_message("Postal Code is required")
    
    def test_cancel_checkout_returns_to_cart(self, user_at_checkout, cart_page):
        """Test: Cancel returns to cart"""
        
        user_at_checkout.click_cancel()
        
        assert cart_page.is_loaded()
        cart_page.verify_item_count(1)
    
    def test_multiple_items_checkout(
        self,
        logged_in_user,
        cart_page,
        checkout_page,
        checkout_step_two_page,
    ):
        """Test: Checkout with multiple items"""
        
        # Add multiple items
        logged_in_user.add_to_cart_by_name("Sauce Labs Backpack")
        logged_in_user.add_to_cart_by_name("Sauce Labs Bike Light")
        logged_in_user.add_to_cart_by_name("Sauce Labs Onesie")
        
        logged_in_user.go_to_cart()
        
        cart_page.verify_item_count(3)
        
        cart_page.proceed_to_checkout()
        checkout_page.fill_information("Test", "User", "00000")
        checkout_page.click_continue()
        
        # Verify all items in summary
        checkout_step_two_page.verify_item_count(3)
        
        # Verify subtotal
        # Backpack $29.99 + Bike Light $9.99 + Onesie $7.99 = $47.97
        subtotal = checkout_step_two_page.get_subtotal()
        assert subtotal == 47.97
        
        checkout_step_two_page.verify_total_calculation()
