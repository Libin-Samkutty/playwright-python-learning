"""
pages/base_page.py
Base Page class with common functionality

PURPOSE:
- Provide common methods for all page objects
- Reduce code duplication
- Centralize wait strategies and error handling
"""

from playwright.sync_api import Page, expect, Locator
from typing import Optional
import re


class BasePage:
    """
    Base class for all Page Objects
    
    All page classes inherit from this.
    Contains common methods used across pages.
    """
    
    # Override in child classes
    URL: str = ""
    URL_PATTERN: Optional[str] = None
    
    def __init__(self, page: Page):
        """
        Initialize the page object
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
    
    # ============================================================
    # NAVIGATION
    # ============================================================
    
    def navigate(self) -> "BasePage":
        """
        Navigate to the page URL
        
        Returns:
            Self for method chaining
        """
        if not self.URL:
            raise NotImplementedError(
                f"URL not defined for {self.__class__.__name__}"
            )
        
        self.page.goto(self.URL)
        return self
    
    def reload(self) -> "BasePage":
        """Reload the current page"""
        self.page.reload()
        return self
    
    def go_back(self) -> "BasePage":
        """Navigate back in browser history"""
        self.page.go_back()
        return self
    
    # ============================================================
    # PAGE STATE
    # ============================================================
    
    def is_loaded(self) -> bool:
        """
        Check if page is loaded
        
        Override in child classes with specific checks
        
        Returns:
            True if page is loaded
        """
        if self.URL_PATTERN:
            try:
                expect(self.page).to_have_url(
                    re.compile(self.URL_PATTERN),
                    timeout=5000
                )
                return True
            except AssertionError:
                return False
        return True
    
    def wait_for_page_load(self, timeout: int = 30000) -> "BasePage":
        """
        Wait for page to be fully loaded
        
        Args:
            timeout: Maximum wait time in milliseconds
        
        Returns:
            Self for method chaining
        """
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        return self
    
    def wait_for_network_idle(self, timeout: int = 30000) -> "BasePage":
        """
        Wait for network to be idle
        
        Args:
            timeout: Maximum wait time in milliseconds
        
        Returns:
            Self for method chaining
        """
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        return self
    
    @property
    def current_url(self) -> str:
        """Get current page URL"""
        return self.page.url
    
    @property
    def title(self) -> str:
        """Get page title"""
        return self.page.title()
    
    # ============================================================
    # COMMON ACTIONS
    # ============================================================
    
    def click(self, locator: Locator, timeout: int = 30000) -> "BasePage":
        """
        Click an element with wait
        
        Args:
            locator: Element to click
            timeout: Maximum wait time
        
        Returns:
            Self for method chaining
        """
        locator.click(timeout=timeout)
        return self
    
    def fill(
        self, 
        locator: Locator, 
        text: str, 
        clear_first: bool = True
    ) -> "BasePage":
        """
        Fill a text field
        
        Args:
            locator: Input element
            text: Text to enter
            clear_first: Whether to clear existing text
        
        Returns:
            Self for method chaining
        """
        if clear_first:
            locator.clear()
        locator.fill(text)
        return self
    
    def select_option(
        self, 
        locator: Locator, 
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None
    ) -> "BasePage":
        """
        Select dropdown option
        
        Args:
            locator: Select element
            value: Option value attribute
            label: Option visible text
            index: Option index
        
        Returns:
            Self for method chaining
        """
        if value:
            locator.select_option(value=value)
        elif label:
            locator.select_option(label=label)
        elif index is not None:
            locator.select_option(index=index)
        return self
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def expect_visible(
        self, 
        locator: Locator, 
        timeout: int = 5000
    ) -> "BasePage":
        """
        Assert element is visible
        
        Args:
            locator: Element to check
            timeout: Maximum wait time
        
        Returns:
            Self for method chaining
        """
        expect(locator).to_be_visible(timeout=timeout)
        return self
    
    def expect_hidden(
        self, 
        locator: Locator, 
        timeout: int = 5000
    ) -> "BasePage":
        """
        Assert element is hidden
        
        Args:
            locator: Element to check
            timeout: Maximum wait time
        
        Returns:
            Self for method chaining
        """
        expect(locator).to_be_hidden(timeout=timeout)
        return self
    
    def expect_text(
        self, 
        locator: Locator, 
        text: str, 
        timeout: int = 5000
    ) -> "BasePage":
        """
        Assert element has text
        
        Args:
            locator: Element to check
            text: Expected text
            timeout: Maximum wait time
        
        Returns:
            Self for method chaining
        """
        expect(locator).to_have_text(text, timeout=timeout)
        return self
    
    # ============================================================
    # SCREENSHOTS AND DEBUGGING
    # ============================================================
    
    def take_screenshot(self, name: str, full_page: bool = False) -> str:
        """
        Take a screenshot
        
        Args:
            name: Screenshot filename (without extension)
            full_page: Capture full scrollable page
        
        Returns:
            Path to screenshot file
        """
        path = f"screenshots/{name}.png"
        self.page.screenshot(path=path, full_page=full_page)
        return path
    
    def highlight_element(self, locator: Locator) -> "BasePage":
        """
        Highlight element for debugging
        
        Args:
            locator: Element to highlight
        
        Returns:
            Self for method chaining
        """
        locator.evaluate(
            "element => element.style.border = '3px solid red'"
        )
        return self
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def get_text(self, locator: Locator) -> str:
        """
        Get element text content
        
        Args:
            locator: Element
        
        Returns:
            Text content
        """
        return locator.text_content() or ""
    
    def get_attribute(self, locator: Locator, name: str) -> Optional[str]:
        """
        Get element attribute
        
        Args:
            locator: Element
            name: Attribute name
        
        Returns:
            Attribute value or None
        """
        return locator.get_attribute(name)
    
    def is_visible(self, locator: Locator) -> bool:
        """
        Check if element is visible
        
        Args:
            locator: Element
        
        Returns:
            True if visible
        """
        return locator.is_visible()
    
    def count(self, locator: Locator) -> int:
        """
        Count matching elements
        
        Args:
            locator: Locator
        
        Returns:
            Number of matching elements
        """
        return locator.count()