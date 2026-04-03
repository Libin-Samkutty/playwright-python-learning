"""
pages/login_page.py
Login Page Object

Handles:
- Login form interactions
- Error message handling
- Navigation after login
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Page Object for the Login Page
    
    URL: https://www.saucedemo.com/
    """
    
    # Page URL
    URL = "https://www.saucedemo.com/"
    URL_PATTERN = r".*saucedemo\.com/?$"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # ============================================================
        # LOCATORS
        # Define all locators as properties for lazy evaluation
        # ============================================================
    
    # -------------------- Form Elements --------------------
    
    @property
    def username_input(self):
        """Username input field"""
        return self.page.get_by_placeholder("Username")
    
    @property
    def password_input(self):
        """Password input field"""
        return self.page.get_by_placeholder("Password")
    
    @property
    def login_button(self):
        """Login submit button"""
        return self.page.get_by_role("button", name="Login")
    
    # -------------------- Error Elements --------------------
    
    @property
    def error_message(self):
        """Error message container"""
        return self.page.locator("[data-test='error']")
    
    @property
    def error_close_button(self):
        """Error message close button"""
        return self.page.locator("[data-test='error-button']")
    
    # -------------------- Branding --------------------
    
    @property
    def logo(self):
        """Swag Labs logo"""
        return self.page.locator(".login_logo")
    
    @property
    def credentials_info(self):
        """Accepted credentials info"""
        return self.page.locator("#login_credentials")
    
    # ============================================================
    # ACTIONS
    # Methods that perform actions on the page
    # ============================================================
    
    def enter_username(self, username: str) -> "LoginPage":
        """
        Enter username
        
        Args:
            username: Username to enter
        
        Returns:
            Self for method chaining
        """
        self.username_input.fill(username)
        return self
    
    def enter_password(self, password: str) -> "LoginPage":
        """
        Enter password
        
        Args:
            password: Password to enter
        
        Returns:
            Self for method chaining
        """
        self.password_input.fill(password)
        return self
    
    def click_login(self) -> "LoginPage":
        """
        Click the login button
        
        Returns:
            Self for method chaining
        """
        self.login_button.click()
        return self
    
    def login(self, username: str, password: str) -> "LoginPage":
        """
        Perform complete login
        
        Args:
            username: Username to enter
            password: Password to enter
        
        Returns:
            Self for method chaining
        
        Example:
            login_page.login("standard_user", "secret_sauce")
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        return self
    
    def login_as_standard_user(self) -> "LoginPage":
        """
        Login with standard user credentials
        
        Convenience method for common test scenario
        
        Returns:
            Self for method chaining
        """
        return self.login("standard_user", "secret_sauce")
    
    def login_as_locked_user(self) -> "LoginPage":
        """Login with locked out user"""
        return self.login("locked_out_user", "secret_sauce")
    
    def login_as_problem_user(self) -> "LoginPage":
        """Login with problem user"""
        return self.login("problem_user", "secret_sauce")
    
    def dismiss_error(self) -> "LoginPage":
        """
        Dismiss error message
        
        Returns:
            Self for method chaining
        """
        self.error_close_button.click()
        return self
    
    def clear_form(self) -> "LoginPage":
        """
        Clear login form fields
        
        Returns:
            Self for method chaining
        """
        self.username_input.clear()
        self.password_input.clear()
        return self
    
    # ============================================================
    # ASSERTIONS / VERIFICATIONS
    # Methods that verify page state
    # ============================================================
    
    def is_loaded(self) -> bool:
        """
        Check if login page is loaded
        
        Returns:
            True if login page is displayed
        """
        try:
            expect(self.login_button).to_be_visible(timeout=5000)
            return True
        except AssertionError:
            return False
    
    def get_error_message(self) -> str:
        """
        Get error message text
        
        Returns:
            Error message text or empty string
        """
        if self.error_message.is_visible():
            return self.error_message.text_content() or ""
        return ""
    
    def has_error(self) -> bool:
        """
        Check if error message is displayed
        
        Returns:
            True if error is visible
        """
        return self.error_message.is_visible()
    
    def verify_error_message(self, expected_message: str) -> "LoginPage":
        """
        Verify error message contains expected text
        
        Args:
            expected_message: Text to find in error
        
        Returns:
            Self for method chaining
        
        Raises:
            AssertionError: If message doesn't match
        """
        expect(self.error_message).to_be_visible()
        expect(self.error_message).to_contain_text(expected_message)
        return self
    
    def verify_login_successful(self) -> "LoginPage":
        """
        Verify login was successful
        
        Checks that we navigated away from login page
        
        Returns:
            Self for method chaining
        """
        expect(self.page).to_have_url(
            "https://www.saucedemo.com/inventory.html"
        )
        return self
