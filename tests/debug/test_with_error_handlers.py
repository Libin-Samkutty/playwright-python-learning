"""
tests/debug/test_with_error_handlers.py
Tests demonstrating error handler usage
"""

import pytest
from playwright.sync_api import expect
import sys
import os

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.error_handlers import with_error_handling, StepTracker

class TestWithErrorHandlers:
    """
    Tests using custom error handlers
    """
    
    @with_error_handling()
    def test_with_decorator(self, page):
        """
        Test using error handling decorator
        
        If this test fails, it will:
        - Capture screenshot
        - Save HTML
        - Log detailed error info
        """
        
        page.goto("https://www.saucedemo.com/")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        
        # This assertion is correct, so test passes
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    @with_error_handling()
    def test_with_decorator_failing(self, page):
        """
        Test that demonstrates error handling on failure
        
        Uncomment the bad assertion to see error handling in action
        """
        
        page.goto("https://www.saucedemo.com/")
        
        # Uncomment to see error handling:
        # expect(page).to_have_title("Wrong Title")
        
        expect(page).to_have_title("Swag Labs")
    
    def test_with_step_tracker(self, page):
        """
        Test using StepTracker for detailed step logging
        """
        
        tracker = StepTracker(page, "test_with_step_tracker")
        
        with tracker.step("Navigate to login page"):
            page.goto("https://www.saucedemo.com/")
        
        with tracker.step("Enter credentials"):
            page.get_by_placeholder("Username").fill("standard_user")
            page.get_by_placeholder("Password").fill("secret_sauce")
        
        with tracker.step("Submit login form"):
            page.get_by_role("button", name="Login").click()
        
        with tracker.step("Verify login success"):
            expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
        
        with tracker.step("Verify products displayed"):
            products = page.locator(".inventory_item")
            expect(products).to_have_count(6)
        
        print(f"\n All steps completed: {tracker.get_steps()}")
    
    def test_with_step_tracker_failure(self, page):
        """
        Test demonstrating step tracker on failure
        
        Shows which step failed and captures artifacts
        """
        
        tracker = StepTracker(page, "test_with_step_tracker_failure")
        
        with tracker.step("Navigate to login page"):
            page.goto("https://www.saucedemo.com/")
        
        with tracker.step("Enter credentials"):
            page.get_by_placeholder("Username").fill("wrong_user")
            page.get_by_placeholder("Password").fill("wrong_pass")
        
        with tracker.step("Submit login form"):
            page.get_by_role("button", name="Login").click()
        
        # This step will fail - but error is handled gracefully
        with tracker.step("Verify login success"):
            # This will fail since credentials are wrong
            # expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
            
            # Correct assertion for this test
            expect(page.locator("[data-test='error']")).to_be_visible()