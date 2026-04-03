"""
tests/utils/error_decoder.py
Helper to decode and explain Playwright errors
"""

import re
from typing import Dict, Tuple


class ErrorDecoder:
    """
    Decode Playwright error messages into actionable advice
    """
    
    ERROR_PATTERNS: Dict[str, Tuple[str, str]] = {
        r"Timeout \d+ms exceeded.*waiting for locator": (
            "TIMEOUT: Element Not Found",
            """
            The element could not be found within the timeout period.
            
            POSSIBLE CAUSES:
            1. Wrong selector - verify in browser DevTools
            2. Element doesn't exist on page
            3. Element is dynamically loaded
            4. Element is inside an iframe
            
            SOLUTIONS:
            1. Use page.pause() to inspect the page
            2. Check if element exists: print(locator.count())
            3. Increase timeout: locator.click(timeout=60000)
            4. Wait for page load: page.wait_for_load_state('networkidle')
            5. Check for iframes: page.frame_locator('iframe').locator(...)
            """
        ),
        
        r"strict mode violation.*resolved to \d+ elements": (
            "STRICT MODE: Multiple Elements Match",
            """
            The locator matches more than one element.
            
            SOLUTIONS:
            1. Use .first: locator.first.click()
            2. Use .nth(n): locator.nth(0).click()
            3. Use filter: locator.filter(has_text='specific').click()
            4. Make selector more specific
            """
        ),
        
        r"element is not visible": (
            "VISIBILITY: Element Hidden",
            """
            The element exists but is not visible.
            
            SOLUTIONS:
            1. Wait for visibility: expect(locator).to_be_visible()
            2. Scroll into view: locator.scroll_into_view_if_needed()
            3. Check for overlays/modals blocking the element
            4. Check CSS: display, visibility, opacity
            """
        ),
        
        r"element is not enabled": (
            "DISABLED: Element Not Enabled",
            """
            The element is disabled.
            
            SOLUTIONS:
            1. Wait for enabled: expect(locator).to_be_enabled()
            2. Check if prerequisite action is needed
            3. Verify element should be enabled at this point
            """
        ),
        
        r"element is outside of the viewport": (
            "VIEWPORT: Element Not Visible in Viewport",
            """
            The element is not in the visible area.
            
            SOLUTIONS:
            1. Scroll into view: locator.scroll_into_view_if_needed()
            2. Set larger viewport: browser.new_context(viewport={...})
            3. Use force=True (last resort): locator.click(force=True)
            """
        ),
        
        r"net::ERR_": (
            "NETWORK: Network Error",
            """
            A network error occurred.
            
            COMMON ERRORS:
            - ERR_CONNECTION_REFUSED: Server not running
            - ERR_NAME_NOT_RESOLVED: Invalid domain
            - ERR_CONNECTION_TIMED_OUT: Server not responding
            - ERR_CERT_AUTHORITY_INVALID: SSL certificate issue
            
            SOLUTIONS:
            1. Verify URL is correct
            2. Check if server is running
            3. For SSL: use ignore_https_errors=True (testing only)
            """
        ),
        
        r"expected.*to have (text|value).*Received": (
            "ASSERTION: Text/Value Mismatch",
            """
            The actual text doesn't match expected.
            
            SOLUTIONS:
            1. Check for extra whitespace
            2. Check case sensitivity
            3. Use contain_text() for partial match
            4. Use regex for flexible matching
            5. Wait for text to update before asserting
            """
        ),
    }
    
    @classmethod
    def decode(cls, error_message: str) -> str:
        """
        Decode an error message into helpful guidance
        
        Args:
            error_message: The error message string
        
        Returns:
            Decoded explanation and suggestions
        """
        
        for pattern, (title, explanation) in cls.ERROR_PATTERNS.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return f"\n{'='*60}\n {title}\n{'='*60}\n{explanation}"
        
        return f"\n{'='*60}\n UNKNOWN ERROR\n{'='*60}\nNo specific guidance available.\n\nOriginal error:\n{error_message}"
    
    @classmethod
    def wrap_test(cls, func):
        """
        Decorator to add error decoding to tests
        """
        
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(cls.decode(str(e)))
                raise
        
        return wrapper


# Usage example:
# @ErrorDecoder.wrap_test
# def test_something(page):
#     ...