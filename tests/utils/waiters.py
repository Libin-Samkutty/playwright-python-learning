"""
utils/waiters.py
Custom wait utilities
"""

from playwright.sync_api import Page, Locator, expect
from typing import Callable, Optional
import time


class WaitHelpers:
    """
    Custom wait helpers for complex scenarios
    """
    
    @staticmethod
    def wait_for_condition(
        condition: Callable[[], bool],
        timeout: float = 10,
        poll_interval: float = 0.5,
        message: str = "Condition not met"
    ) -> bool:
        """
        Wait for a custom condition to be true
        
        Args:
            condition: Callable that returns True when condition is met
            timeout: Maximum wait time in seconds
            poll_interval: Time between checks in seconds
            message: Error message if timeout
        
        Returns:
            True if condition met
        
        Raises:
            TimeoutError: If condition not met within timeout
        """
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if condition():
                    return True
            except Exception:
                pass
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"{message} (timeout: {timeout}s)")
    
    @staticmethod
    def wait_for_element_count_stable(
        locator: Locator,
        stability_time: float = 1.0,
        timeout: float = 10
    ) -> int:
        """
        Wait for element count to stabilize
        
        Useful for dynamic lists that load items gradually
        
        Args:
            locator: Element locator
            stability_time: How long count must be stable
            timeout: Maximum wait time
        
        Returns:
            Final element count
        """
        
        start_time = time.time()
        last_count = -1
        stable_since = None
        
        while time.time() - start_time < timeout:
            current_count = locator.count()
            
            if current_count == last_count:
                if stable_since is None:
                    stable_since = time.time()
                elif time.time() - stable_since >= stability_time:
                    return current_count
            else:
                stable_since = None
                last_count = current_count
            
            time.sleep(0.1)
        
        return locator.count()
    
    @staticmethod
    def wait_for_network_idle(
        page: Page,
        idle_time: float = 0.5,
        timeout: float = 30
    ):
        """
        Wait for network to be idle
        
        Args:
            page: Playwright page
            idle_time: How long network must be idle
            timeout: Maximum wait time
        """
        
        page.wait_for_load_state("networkidle", timeout=timeout * 1000)
    
    @staticmethod
    def wait_for_text_to_change(
        locator: Locator,
        initial_text: str,
        timeout: float = 10
    ) -> str:
        """
        Wait for element text to change from initial value
        
        Args:
            locator: Element locator
            initial_text: Current text that should change
            timeout: Maximum wait time
        
        Returns:
            New text value
        """
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_text = locator.text_content() or ""
            
            if current_text != initial_text:
                return current_text
            
            time.sleep(0.1)
        
        raise TimeoutError(f"Text did not change from '{initial_text}' within {timeout}s")
    
    @staticmethod
    def wait_for_url_change(
        page: Page,
        initial_url: str,
        timeout: float = 10
    ) -> str:
        """
        Wait for URL to change from initial value
        
        Args:
            page: Playwright page
            initial_url: Current URL that should change
            timeout: Maximum wait time
        
        Returns:
            New URL
        """
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_url = page.url
            
            if current_url != initial_url:
                return current_url
            
            time.sleep(0.1)
        
        raise TimeoutError(f"URL did not change from '{initial_url}' within {timeout}s")
    
    @staticmethod
    def wait_for_animation(
        locator: Locator,
        timeout: float = 5
    ):
        """
        Wait for element animation to complete
        
        Uses bounding box stability as indicator
        """
        
        start_time = time.time()
        last_box = None
        stable_count = 0
        
        while time.time() - start_time < timeout:
            try:
                box = locator.bounding_box()
                
                if box == last_box:
                    stable_count += 1
                    if stable_count >= 3:  # Stable for 3 checks
                        return
                else:
                    stable_count = 0
                    last_box = box
            except Exception:
                pass
            
            time.sleep(0.1)