"""
pages/the_internet/secure_area_page.py
Secure Area Page Object for The Internet

URL: https://the-internet.herokuapp.com/secure
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class SecureAreaPage(BasePage):
    """
    Page Object for The Internet Secure Area Page
    
    This page is displayed after successful login.
    
    Features:
    - Success flash message
    - Logout button
    - Secure content
    """
    
    # Page URL
    URL = "https://the-internet.herokuapp.com/secure"
    URL_PATTERN = r".*/secure$"
    
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
    def subheading(self):
        """Subheading (h4)"""
        return self.page.get_by_role("heading", level=4)
    
    @property
    def flash_message(self):
        """Flash message"""
        return self.page.locator("#flash")
    
    @property
    def flash_success(self):
        """Success flash message"""
        return self.page.locator(".flash.success")
    
    @property
    def logout_button(self):
        """Logout button/link"""
        return self.page.get_by_role("link", name="Logout")
    
    @property
    def content(self):
        """Main content area"""
        return self.page.locator("#content")
    
    @property
    def flash_close_button(self):
        """Flash message close button (X)"""
        return self.page.locator(".flash a.close")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def logout(self) -> "SecureAreaPage":
        """
        Logout from secure area
        
        Returns:
            Self for method chaining
        """
        self.logout_button.click()
        return self
    
    def dismiss_flash_message(self) -> "SecureAreaPage":
        """
        Dismiss/close the flash message
        
        Returns:
            Self for method chaining
        """
        if self.flash_close_button.is_visible():
            self.flash_close_button.click()
        return self
    
    # ============================================================
    # GETTERS
    # ============================================================
    
    def get_heading_text(self) -> str:
        """
        Get page heading text
        
        Returns:
            Heading text
        """
        return self.page_heading.text_content() or ""
    
    def get_subheading_text(self) -> str:
        """
        Get subheading text
        
        Returns:
            Subheading text
        """
        return self.subheading.text_content() or ""
    
    def get_flash_message_text(self) -> str:
        """
        Get flash message text
        
        Returns:
            Flash message text or empty string
        """
        if self.flash_message.is_visible():
            return self.flash_message.text_content() or ""
        return ""
    
    # ============================================================
    # STATE CHECKS
    # ============================================================
    
    def is_loaded(self) -> bool:
        """
        Check if secure area is loaded
        
        Returns:
            True if secure area is displayed
        """
        try:
            expect(self.logout_button).to_be_visible(timeout=5000)
            return True
        except AssertionError:
            return False
    
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
    
    def verify_page_loaded(self) -> "SecureAreaPage":
        """
        Verify secure area page is loaded
        
        Returns:
            Self for method chaining
        """
        expect(self.page_heading).to_have_text("Secure Area")
        expect(self.logout_button).to_be_visible()
        return self
    
    def verify_login_success_message(self) -> "SecureAreaPage":
        """
        Verify login success message is shown
        
        Returns:
            Self for method chaining
        """
        expect(self.flash_success).to_be_visible()
        expect(self.flash_success).to_contain_text("You logged into a secure area!")
        return self
    
    def verify_logged_in(self) -> "SecureAreaPage":
        """
        Verify user is logged in
        
        Complete verification of logged-in state
        
        Returns:
            Self for method chaining
        """
        self.verify_page_loaded()
        self.verify_login_success_message()
        return self
    
    def verify_logout_redirects_to_login(self) -> "SecureAreaPage":
        """
        Verify logout redirects to login page
        
        Returns:
            Self for method chaining
        """
        self.logout()
        expect(self.page).to_have_url(
            "https://the-internet.herokuapp.com/login"
        )
        return self
