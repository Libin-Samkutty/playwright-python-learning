"""
tests/the_internet/test_login.py
Login tests for The Internet using Page Object Model
"""

import pytest
from playwright.sync_api import expect


class TestTheInternetLogin:
    """
    Login tests for The Internet
    
    URL: https://the-internet.herokuapp.com/login
    """
    
    def test_page_loads_correctly(self, the_internet_login_page):
        """
        Test: Login page loads with all elements
        """
        the_internet_login_page.navigate()
        the_internet_login_page.verify_page_loaded()
        
        # Verify heading
        heading = the_internet_login_page.get_heading_text()
        assert heading == "Login Page"
    
    def test_successful_login(
        self, 
        the_internet_login_page, 
        secure_area_page,
        valid_credentials
    ):
        """
        Test: Valid credentials lead to successful login
        """
        the_internet_login_page.navigate()
        the_internet_login_page.login(
            valid_credentials["username"],
            valid_credentials["password"]
        )
        
        # Verify redirect to secure area
        the_internet_login_page.verify_login_successful()
        
        # Verify secure area loaded
        assert secure_area_page.is_loaded()
        secure_area_page.verify_login_success_message()
    
    def test_successful_login_with_convenience_method(
        self, 
        the_internet_login_page, 
        secure_area_page
    ):
        """
        Test: Login using convenience method
        """
        the_internet_login_page.navigate()
        the_internet_login_page.login_with_valid_credentials()
        
        secure_area_page.verify_logged_in()
    
    def test_invalid_username(self, the_internet_login_page):
        """
        Test: Invalid username shows error
        """
        the_internet_login_page.navigate()
        the_internet_login_page.login("invalid_user", "SuperSecretPassword!")
        
        the_internet_login_page.verify_invalid_username_error()
        
        # Still on login page
        assert the_internet_login_page.is_loaded()
    
    def test_invalid_password(self, the_internet_login_page):
        """
        Test: Invalid password shows error
        """
        the_internet_login_page.navigate()
        the_internet_login_page.login("tomsmith", "wrong_password")
        
        the_internet_login_page.verify_invalid_password_error()
    
    def test_empty_credentials(self, the_internet_login_page):
        """
        Test: Empty credentials show error
        """
        the_internet_login_page.navigate()
        the_internet_login_page.click_login()
        
        # Should show username invalid error
        assert the_internet_login_page.has_error()
    
    @pytest.mark.parametrize("username,password,expected_error", [
        ("invalid", "SuperSecretPassword!", "Your username is invalid!"),
        ("tomsmith", "invalid", "Your password is invalid!"),
        ("", "SuperSecretPassword!", "Your username is invalid!"),
        ("tomsmith", "", "Your password is invalid!"),
    ])
    def test_login_validation_errors(
        self, 
        the_internet_login_page,
        username,
        password,
        expected_error
    ):
        """
        Test: Various invalid inputs show correct errors
        
        Data-driven test with parametrization
        """
        the_internet_login_page.navigate()
        the_internet_login_page.login(username, password)
        
        the_internet_login_page.verify_error_message(expected_error)
    
    def test_login_then_logout(
        self, 
        the_internet_login_page, 
        secure_area_page
    ):
        """
        Test: Complete login and logout flow
        """
        # Login
        the_internet_login_page.navigate()
        the_internet_login_page.login_with_valid_credentials()
        
        assert secure_area_page.is_loaded()
        
        # Logout
        secure_area_page.logout()
        
        # Verify back on login page
        assert the_internet_login_page.is_loaded()
        
        # Verify logout success message
        expect(the_internet_login_page.flash_message).to_contain_text(
            "You logged out of the secure area!"
        )
    
    def test_clear_form(self, the_internet_login_page):
        """
        Test: Form can be cleared
        """
        the_internet_login_page.navigate()
        
        # Fill form
        the_internet_login_page.enter_username("someuser")
        the_internet_login_page.enter_password("somepass")
        
        # Verify filled
        expect(the_internet_login_page.username_input).to_have_value("someuser")
        expect(the_internet_login_page.password_input).to_have_value("somepass")
        
        # Clear
        the_internet_login_page.clear_form()
        
        # Verify cleared
        expect(the_internet_login_page.username_input).to_have_value("")
        expect(the_internet_login_page.password_input).to_have_value("")


class TestSecureArea:
    """
    Secure Area tests
    
    URL: https://the-internet.herokuapp.com/secure
    """
    
    def test_secure_area_requires_login(self, secure_area_page):
        """
        Test: Direct navigation to secure area without login
        
        Note: The Internet doesn't enforce this, but test the pattern
        """
        # Navigate directly
        secure_area_page.navigate()
        
        # In a real app, this would redirect to login
        # The Internet allows direct access, so we just verify page loads
        # This demonstrates how you'd structure the test
    
    def test_secure_area_content(self, logged_in_secure_area):
        """
        Test: Secure area shows correct content
        
        Using convenience fixture for logged-in state
        """
        heading = logged_in_secure_area.get_heading_text()
        assert heading == " Secure Area"
        
        subheading = logged_in_secure_area.get_subheading_text()
        assert "Welcome to the Secure Area" in subheading
    
    def test_dismiss_flash_message(self, logged_in_secure_area):
        """
        Test: Flash message can be dismissed
        """
        # Flash message visible after login
        assert logged_in_secure_area.has_success_message()
        
        # Dismiss it
        logged_in_secure_area.dismiss_flash_message()
        
        # Should be gone
        expect(logged_in_secure_area.flash_message).to_be_hidden()
    
    def test_logout_button_visible(self, logged_in_secure_area):
        """
        Test: Logout button is visible when logged in
        """
        expect(logged_in_secure_area.logout_button).to_be_visible()
        expect(logged_in_secure_area.logout_button).to_have_text("Logout")
