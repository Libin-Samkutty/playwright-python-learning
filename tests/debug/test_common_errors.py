"""
tests/debug/test_common_errors.py
Examples of common errors and how to fix them
"""

import pytest
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError


class TestTimeoutErrors:
    """
    Timeout errors occur when Playwright can't find or interact
    with an element within the specified time.
    """
    
    def test_element_not_found_timeout(self, page):
        """
        ERROR: Timeout waiting for element
        
        Message looks like:
        "Timeout 30000ms exceeded.
        =========================== logs ===========================
        waiting for locator('#non-existent-element')
        ============================================================"
        
        CAUSES:
        1. Wrong selector
        2. Element doesn't exist
        3. Element hasn't loaded yet
        4. Element is in iframe
        
        SOLUTIONS:
        1. Verify selector in browser DevTools
        2. Check if element exists in page source
        3. Add appropriate wait
        4. Check for iframes
        """
        
        page.goto("https://www.saucedemo.com/")
        
        # This will timeout - element doesn't exist
        with pytest.raises(PlaywrightTimeoutError):
            page.locator("#non-existent-element").click(timeout=3000)
    
    def test_element_not_visible_timeout(self, page):
        """
        ERROR: Element exists but not visible
        
        Message:
        "Timeout waiting for element to be visible"
        
        SOLUTION: Wait for element to be visible
        """
        
        page.goto("https://www.saucedemo.com/")
        
        # Error message is hidden until login fails
        error_element = page.locator("[data-test='error']")
        
        # This would timeout - error not visible yet
        # expect(error_element).to_be_visible(timeout=1000)
        
        # CORRECT: Trigger the error first, then check
        page.get_by_role("button", name="Login").click()
        expect(error_element).to_be_visible()
    
    def test_element_not_enabled_timeout(self, page):
        """
        ERROR: Element exists but disabled
        
        SOLUTION: Wait for element to be enabled
        """
        
        page.goto("https://the-internet.herokuapp.com/dynamic_controls")
        
        text_input = page.locator("#input-example input")
        
        # Input is disabled initially
        expect(text_input).to_be_disabled()
        
        # This would fail - can't fill disabled input
        # text_input.fill("test")
        
        # CORRECT: Enable first, then fill
        page.get_by_role("button", name="Enable").click()
        expect(text_input).to_be_enabled(timeout=10000)
        text_input.fill("test")


class TestLocatorErrors:
    """
    Errors related to locator issues
    """
    
    def test_strict_mode_violation(self, page):
        """
        ERROR: Strict mode violation - locator matched multiple elements
        
        Message:
        "Error: strict mode violation: locator('.inventory_item')
        resolved to 6 elements"
        
        CAUSE: Locator matches multiple elements but action expects one
        
        SOLUTIONS:
        1. Use more specific locator
        2. Use .first, .last, .nth(n)
        3. Use filter() to narrow down
        """
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        products = page.locator(".inventory_item")
        
        # This would fail - 6 elements match
        # products.click()
        
        # CORRECT: Be specific
        products.first.click()
        # OR
        # products.nth(0).click()
        # OR
        # page.locator(".inventory_item").filter(has_text="Backpack").click()
    
    def test_invalid_selector(self, page):
        """
        ERROR: Invalid selector syntax
        
        CAUSES:
        1. Typo in selector
        2. Invalid CSS/XPath syntax
        3. Using wrong selector type
        """
        
        page.goto("https://www.saucedemo.com/")
        
        # These would raise errors:
        # page.locator("##double-hash")  # Invalid CSS
        # page.locator("///invalid")      # Invalid XPath
        
        # CORRECT selectors:
        page.locator("#user-name")  # Valid CSS ID
        page.locator("//input[@id='user-name']")  # Valid XPath


class TestAssertionErrors:
    """
    Assertion-related errors
    """
    
    def test_text_mismatch(self, page):
        """
        ERROR: Text doesn't match expected value
        
        Message:
        "AssertionError: Locator expected to have text 'Wrong Text'
        Received: 'Actual Text'"
        
        CAUSES:
        1. Wrong expected text
        2. Extra whitespace
        3. Dynamic content
        4. Case sensitivity
        """
        
        page.goto("https://www.saucedemo.com/")
        
        # Case sensitivity matters
        # This would fail:
        # expect(page.locator(".login_logo")).to_have_text("swag labs")
        
        # CORRECT:
        expect(page.locator(".login_logo")).to_have_text("Swag Labs")
        
        # Or use regex for flexibility:
        import re
        expect(page.locator(".login_logo")).to_have_text(
            re.compile("swag labs", re.IGNORECASE)
        )
    
    def test_url_mismatch(self, page):
        """
        ERROR: URL doesn't match expected
        
        CAUSES:
        1. Redirect not complete
        2. Query parameters differ
        3. Trailing slash difference
        """
        
        page.goto("https://www.saucedemo.com")  # No trailing slash
        
        # Be flexible with URL matching
        import re
        expect(page).to_have_url(re.compile(r".*saucedemo\.com/?$"))
    
    def test_count_mismatch(self, page):
        """
        ERROR: Element count doesn't match
        
        CAUSES:
        1. Elements still loading
        2. Wrong selector
        3. Dynamic content changes
        """
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # Wait for products to load before counting
        products = page.locator(".inventory_item")
        expect(products.first).to_be_visible()  # Wait for at least one
        expect(products).to_have_count(6)


class TestNavigationErrors:
    """
    Navigation-related errors
    """
    
    def test_navigation_timeout(self, page):
        """
        ERROR: Navigation timeout
        
        Message:
        "Timeout 30000ms exceeded.
        navigating to 'https://example.com'"
        
        CAUSES:
        1. Slow network
        2. Server not responding
        3. Wrong URL
        """
        
        # Increase timeout for slow pages
        page.goto(
            "https://www.saucedemo.com/",
            timeout=60000,
            wait_until="domcontentloaded",  # Don't wait for all resources
        )
    
    def test_ssl_certificate_error(self, page, browser):
        """
        ERROR: SSL certificate error
        
        SOLUTION: Use ignore_https_errors (for testing only!)
        """
        
        # Create context that ignores HTTPS errors
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # Now can access sites with invalid certificates
        # (Only for testing, never in production!)
        
        context.close()