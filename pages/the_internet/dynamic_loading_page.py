"""
pages/the_internet/dynamic_loading_page.py
Dynamic Loading Page Object for The Internet

URL: https://the-internet.herokuapp.com/dynamic_loading/1
     https://the-internet.herokuapp.com/dynamic_loading/2
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from typing import Literal


class DynamicLoadingPage(BasePage):
    """
    Page Object for The Internet Dynamic Loading Pages
    
    Two variants:
    - /dynamic_loading/1: Element hidden, then revealed
    - /dynamic_loading/2: Element not in DOM, then added
    
    Features:
    - Start button to trigger loading
    - Loading indicator
    - Dynamic content reveal
    """
    
    # Default URL (Example 1)
    URL = "https://the-internet.herokuapp.com/dynamic_loading/1"
    URL_PATTERN = r".*/dynamic_loading/\d+$"
    
    def __init__(self, page: Page, example: Literal[1, 2] = 1):
        """
        Initialize Dynamic Loading Page
        
        Args:
            page: Playwright page
            example: Which example (1 or 2)
        """
        super().__init__(page)
        self.example = example
        self.URL = f"https://the-internet.herokuapp.com/dynamic_loading/{example}"
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    @property
    def page_heading(self):
        """Page heading"""
        return self.page.get_by_role("heading", level=3)
    
    @property
    def start_button(self):
        """Start button to trigger loading"""
        return self.page.get_by_role("button", name="Start")
    
    @property
    def loading_indicator(self):
        """Loading spinner/indicator"""
        return self.page.locator("#loading")
    
    @property
    def loading_bar(self):
        """Loading progress bar"""
        return self.page.locator("#loading img")
    
    @property
    def finish_element(self):
        """Element that appears after loading"""
        return self.page.locator("#finish")
    
    @property
    def finish_text(self):
        """Text inside finish element"""
        return self.page.locator("#finish h4")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def click_start(self) -> "DynamicLoadingPage":
        """
        Click the Start button to begin loading
        
        Returns:
            Self for method chaining
        """
        self.start_button.click()
        return self
    
    def wait_for_loading_to_start(
        self, 
        timeout: int = 5000
    ) -> "DynamicLoadingPage":
        """
        Wait for loading indicator to appear
        
        Args:
            timeout: Maximum wait time in ms
        
        Returns:
            Self for method chaining
        """
        expect(self.loading_indicator).to_be_visible(timeout=timeout)
        return self
    
    def wait_for_loading_to_complete(
        self, 
        timeout: int = 10000
    ) -> "DynamicLoadingPage":
        """
        Wait for loading indicator to disappear
        
        Args:
            timeout: Maximum wait time in ms
        
        Returns:
            Self for method chaining
        """
        expect(self.loading_indicator).to_be_hidden(timeout=timeout)
        return self
    
    def wait_for_content(self, timeout: int = 10000) -> "DynamicLoadingPage":
        """
        Wait for dynamic content to appear
        
        Args:
            timeout: Maximum wait time in ms
        
        Returns:
            Self for method chaining
        """
        expect(self.finish_text).to_be_visible(timeout=timeout)
        return self
    
    def start_and_wait_for_content(
        self, 
        timeout: int = 10000
    ) -> "DynamicLoadingPage":
        """
        Click start and wait for content to load
        
        Complete action: start  wait for loading  wait for content
        
        Args:
            timeout: Maximum wait time in ms
        
        Returns:
            Self for method chaining
        """
        self.click_start()
        self.wait_for_loading_to_complete(timeout=timeout)
        self.wait_for_content(timeout=timeout)
        return self
    
    # ============================================================
    # GETTERS
    # ============================================================
    
    def get_loaded_text(self) -> str:
        """
        Get text of loaded content
        
        Returns:
            Loaded text or empty string
        """
        if self.finish_text.is_visible():
            return self.finish_text.text_content() or ""
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
        Check if page is loaded
        
        Returns:
            True if page is loaded with Start button visible
        """
        try:
            expect(self.start_button).to_be_visible(timeout=5000)
            return True
        except AssertionError:
            return False
    
    def is_loading(self) -> bool:
        """
        Check if loading is in progress
        
        Returns:
            True if loading indicator visible
        """
        return self.loading_indicator.is_visible()
    
    def is_content_loaded(self) -> bool:
        """
        Check if dynamic content has loaded
        
        Returns:
            True if content is visible
        """
        return self.finish_text.is_visible()
    
    def is_content_in_dom(self) -> bool:
        """
        Check if content element exists in DOM
        
        Useful for Example 2 where element is added to DOM
        
        Returns:
            True if element attached to DOM
        """
        return self.finish_element.count() > 0
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def verify_page_loaded(self) -> "DynamicLoadingPage":
        """
        Verify dynamic loading page is ready
        
        Returns:
            Self for method chaining
        """
        expect(self.start_button).to_be_visible()
        expect(self.start_button).to_be_enabled()
        return self
    
    def verify_loading_in_progress(self) -> "DynamicLoadingPage":
        """
        Verify loading indicator is showing
        
        Returns:
            Self for method chaining
        """
        expect(self.loading_indicator).to_be_visible()
        return self
    
    def verify_loading_complete(self) -> "DynamicLoadingPage":
        """
        Verify loading has completed
        
        Returns:
            Self for method chaining
        """
        expect(self.loading_indicator).to_be_hidden()
        return self
    
    def verify_content_text(
        self, 
        expected_text: str = "Hello World!"
    ) -> "DynamicLoadingPage":
        """
        Verify loaded content text
        
        Args:
            expected_text: Expected text content
        
        Returns:
            Self for method chaining
        """
        expect(self.finish_text).to_have_text(expected_text)
        return self
    
    def verify_content_visible(self) -> "DynamicLoadingPage":
        """
        Verify dynamic content is visible
        
        Returns:
            Self for method chaining
        """
        expect(self.finish_text).to_be_visible()
        return self
    
    def verify_hello_world_displayed(
        self, 
        timeout: int = 10000
    ) -> "DynamicLoadingPage":
        """
        Complete verification: start, wait, verify text
        
        Convenience method for common test scenario
        
        Args:
            timeout: Maximum wait time
        
        Returns:
            Self for method chaining
        """
        self.start_and_wait_for_content(timeout=timeout)
        self.verify_content_text("Hello World!")
        return self