"""
pages/the_internet/login_page.py
Login Page Object for The Internet

URL: https://the-internet.herokuapp.com/login
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class TheInternetLoginPage(BasePage):
    """
    Page Object for The Internet Login Page
    
    Features:
    - Username/Password authentication
    - Flash messages for success/error
    """
    
    # Page URL
    URL = "https://the-internet.herokuapp.com/login"
    URL_PATTERN = r".*/login$"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    @property
    def page_heading(self):
        """Page heading (h2)"""
        return self.page.get_by_role("heading", level=2)
    
    @property
    def username_input(self):
        """Username input field"""
        return self.page.get_by_label("Username")
    
    @property
    def password_input(self):
        """Password input field"""
        return self.page.get_by_label("Password")
    
    @property
    def login_button(self):
        """Login submit button"""
        return self.page.get_by_role("button", name="Login")
    
    @property
    def flash_message(self):
        """Flash message (success or error)"""
        return self.page.locator("#flash")
    
    @property
    def flash_success(self):
        """Success flash message"""
        return self.page.locator(".flash.success")
    
    @property
    def flash_error(self):
        """Error flash message"""
        return self.page.locator(".flash.error")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def enter_username(self, username: str) -> "TheInternetLoginPage":
        """
        Enter username
        
        Args:
            username: Username to enter
        
        Returns:
            Self for method chaining
        """
        self.username_input.fill(username)
        return self
    
    def enter_password(self, password: str) -> "TheInternetLoginPage":
        """
        Enter password
        
        Args:
            password: Password to enter
        
        Returns:
            Self for method chaining
        """
        self.password_input.fill(password)
        return self
    
    def click_login(self) -> "TheInternetLoginPage":
        """
        Click the login button
        
        Returns:
            Self for method chaining
        """
        self.login_button.click()
        return self
    
    def login(self, username: str, password: str) -> "TheInternetLoginPage":
        """
        Perform complete login
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Self for method chaining
        
        Example:
            login_page.login("tomsmith", "SuperSecretPassword!")
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        return self
    
    def login_with_valid_credentials(self) -> "TheInternetLoginPage":
        """
        Login with known valid credentials
        
        The Internet uses:
        - Username: tomsmith
        - Password: SuperSecretPassword!
        
        Returns:
            Self for method chaining
        """
        return self.login("tomsmith", "SuperSecretPassword!")
    
    def clear_form(self) -> "TheInternetLoginPage":
        """
        Clear all form fields
        
        Returns:
            Self for method chaining
        """
        self.username_input.clear()
        self.password_input.clear()
        return self
    
    # ============================================================
    # GETTERS
    # ============================================================
    
    def get_flash_message_text(self) -> str:
        """
        Get flash message text
        
        Returns:
            Flash message text or empty string
        """
        if self.flash_message.is_visible():
            return self.flash_message.text_content() or ""
        return ""
    
    def get_heading_text(self) -> str:
        """
        Get page heading text
        
        Returns:
            Heading text
        """
        return self.page_heading.text_content() or ""
    
    # ============================================================
    # STATE CHECKS
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
    
    def has_error(self) -> bool:
        """
        Check if error message is displayed
        
        Returns:
            True if error is visible
        """
        return self.flash_error.is_visible()
    
    def has_success_message(self) -> bool:
        """
        Check if success message is displayed
        
        Returns:
            True if success message visible
        """
        return self.flash_success.is_visible()
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def verify_page_loaded(self) -> "TheInternetLoginPage":
        """
        Verify login page is loaded
        
        Returns:
            Self for method chaining
        
        Raises:
            AssertionError: If page not loaded
        """
        expect(self.page_heading).to_have_text("Login Page")
        expect(self.login_button).to_be_visible()
        return self
    
    def verify_error_message(self, expected_text: str) -> "TheInternetLoginPage":
        """
        Verify error message contains expected text
        
        Args:
            expected_text: Text to find in error message
        
        Returns:
            Self for method chaining
        """
        expect(self.flash_error).to_be_visible()
        expect(self.flash_error).to_contain_text(expected_text)
        return self
    
    def verify_invalid_username_error(self) -> "TheInternetLoginPage":
        """Verify invalid username error shown"""
        return self.verify_error_message("Your username is invalid!")
    
    def verify_invalid_password_error(self) -> "TheInternetLoginPage":
        """Verify invalid password error shown"""
        return self.verify_error_message("Your password is invalid!")
    
    def verify_login_successful(self) -> "TheInternetLoginPage":
        """
        Verify login was successful
        
        Checks that we navigated to secure area
        
        Returns:
            Self for method chaining
        """
        expect(self.page).to_have_url(
            "https://the-internet.herokuapp.com/secure"
        )
        return self