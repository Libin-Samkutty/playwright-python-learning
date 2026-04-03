"""
Reusable wait utilities for handling dynamic elements
"""

from playwright.sync_api import Page, expect, Locator
import time


class WaitHelper:
    """Collection of waiting utilities"""
    
    def __init__(self, page: Page, default_timeout: int = 10000):
        self.page = page
        self.default_timeout = default_timeout
    
    def wait_for_loading_complete(self, timeout: int = None):
        """
        Wait for common loading indicators to disappear
        
        Args:
            timeout: Milliseconds to wait (default: self.default_timeout)
        """
        timeout = timeout or self.default_timeout
        
        loading_selectors = [
            ".loading",
            ".spinner",
            ".loader",
            "[data-loading='true']",
            "#loading",
            ".skeleton",
        ]
        
        for selector in loading_selectors:
            loader = self.page.locator(selector)
            if loader.count() > 0:
                try:
                    expect(loader.first).to_be_hidden(timeout=timeout)
                except Exception:
                    pass  # Loader might have disappeared
    
    def wait_for_element_count(
        self, 
        locator: Locator, 
        expected_count: int, 
        timeout: int = None
    ):
        """
        Wait for element count to reach expected value
        
        Args:
            locator: Playwright locator
            expected_count: Expected number of elements
            timeout: Milliseconds to wait
        """
        timeout = timeout or self.default_timeout
        expect(locator).to_have_count(expected_count, timeout=timeout)
    
    def wait_for_element_count_greater_than(
        self, 
        locator: Locator, 
        min_count: int, 
        timeout: int = None
    ):
        """
        Wait for element count to exceed minimum
        
        Args:
            locator: Playwright locator
            min_count: Minimum number of elements
            timeout: Milliseconds to wait
        """
        timeout = timeout or self.default_timeout
        timeout_seconds = timeout / 1000
        
        start = time.time()
        while time.time() - start < timeout_seconds:
            if locator.count() > min_count:
                return
            time.sleep(0.1)
        
        raise TimeoutError(
            f"Element count did not exceed {min_count} within {timeout}ms"
        )
    
    def wait_for_text_to_change(
        self, 
        locator: Locator, 
        initial_text: str, 
        timeout: int = None
    ):
        """
        Wait for element text to change from initial value
        
        Args:
            locator: Playwright locator
            initial_text: Current text that should change
            timeout: Milliseconds to wait
        """
        timeout = timeout or self.default_timeout
        
        self.page.wait_for_function(
            f"""
            (selector) => {{
                const el = document.querySelector(selector);
                return el && el.textContent.trim() !== '{initial_text}';
            }}
            """,
            locator.first.evaluate("el => el.tagName.toLowerCase()"),
            timeout=timeout
        )
    
    def wait_for_url_contains(self, url_part: str, timeout: int = None):
        """
        Wait for URL to contain specific string
        
        Args:
            url_part: String that URL should contain
            timeout: Milliseconds to wait
        """
        timeout = timeout or self.default_timeout
        
        import re
        expect(self.page).to_have_url(
            re.compile(f".*{url_part}.*"), 
            timeout=timeout
        )
    
    def wait_for_network_idle(self, timeout: int = None):
        """
        Wait for network to be idle
        
        Args:
            timeout: Milliseconds to wait
        """
        timeout = timeout or self.default_timeout
        
        self.page.wait_for_load_state("networkidle", timeout=timeout)
    
    def scroll_and_wait_for_content(
        self, 
        content_locator: Locator,
        min_count: int,
        max_scrolls: int = 10
    ):
        """
        Scroll page and wait for content to load (infinite scroll)
        
        Args:
            content_locator: Locator for content items
            min_count: Minimum items to load
            max_scrolls: Maximum scroll attempts
        
        Returns:
            bool: True if min_count reached, False otherwise
        """
        for _ in range(max_scrolls):
            if content_locator.count() >= min_count:
                return True
            
            # Scroll to bottom
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Brief wait for content
            self.page.wait_for_timeout(500)
        
        return content_locator.count() >= min_count
