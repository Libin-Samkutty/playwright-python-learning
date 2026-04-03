"""
tests/debug/test_flaky_debugging.py
Strategies for debugging flaky tests
"""

import pytest
from playwright.sync_api import expect
import time


class TestFlakyDebugging:
    """
    Techniques for finding flakiness
    """
    
    @pytest.mark.parametrize("run_number", range(5))
    def test_run_multiple_times(self, page, run_number):
        """
        STRATEGY: Run test multiple times to reproduce flakiness
        
        Usage: pytest tests/debug/test_flaky_debugging.py::TestFlakyDebugging::test_run_multiple_times -v
        """
        
        print(f"\n--- Run {run_number + 1} ---")
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # This is the potentially flaky part
        products = page.locator(".inventory_item")
        expect(products).to_have_count(6)
    
    def test_with_timing_info(self, page):
        """
        STRATEGY: Add timing to identify slow operations
        """
        
        timings = {}
        
        # Navigation
        start = time.time()
        page.goto("https://www.saucedemo.com/")
        timings["navigation"] = time.time() - start
        
        # Login
        start = time.time()
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        timings["login"] = time.time() - start
        
        # Wait for products
        start = time.time()
        products = page.locator(".inventory_item")
        expect(products.first).to_be_visible()
        timings["products_visible"] = time.time() - start
        
        # Print timing report
        print("\n--- Timing Report ---")
        for step, duration in timings.items():
            status = " SLOW" if duration > 2 else ""
            print(f"  {step}: {duration:.2f}s {status}")
        print(f"  TOTAL: {sum(timings.values()):.2f}s")
    
    def test_with_explicit_waits(self, page):
        """
        STRATEGY: Add explicit waits to stabilize flaky test
        """
        
        page.goto("https://www.saucedemo.com/")
        
        # Wait for page to be ready
        page.wait_for_load_state("networkidle")
        
        # Wait for specific element before interacting
        username = page.get_by_placeholder("Username")
        expect(username).to_be_visible()
        expect(username).to_be_editable()
        username.fill("standard_user")
        
        password = page.get_by_placeholder("Password")
        expect(password).to_be_visible()
        expect(password).to_be_editable()
        password.fill("secret_sauce")
        
        login_button = page.get_by_role("button", name="Login")
        expect(login_button).to_be_enabled()
        login_button.click()
        
        # Wait for navigation
        page.wait_for_url("**/inventory.html")
        
        # Wait for products to load
        products = page.locator(".inventory_item")
        expect(products.first).to_be_visible()
        expect(products).to_have_count(6)
    
    def test_with_retry_decorator(self, page):
        """
        STRATEGY: Retry flaky test (use sparingly!)
        """
        
        # Custom retry decorator
        def retry_test(max_attempts=3):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    last_exception = None
                    for attempt in range(max_attempts):
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            last_exception = e
                            print(f"Attempt {attempt + 1} failed: {e}")
                            if attempt < max_attempts - 1:
                                time.sleep(1)  # Brief pause before retry
                    raise last_exception
                return wrapper
            return decorator
        
        @retry_test(max_attempts=3)
        def flaky_operation():
            page.goto("https://www.saucedemo.com/")
            page.get_by_placeholder("Username").fill("standard_user")
            page.get_by_placeholder("Password").fill("secret_sauce")
            page.get_by_role("button", name="Login").click()
            expect(page.locator(".inventory_item")).to_have_count(6)
        
        flaky_operation()
