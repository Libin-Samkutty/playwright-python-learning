"""
tests/debug/test_debug_exercise.py
Debugging practice exercise
"""

import pytest
from playwright.sync_api import expect
import os
import sys

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.error_handlers import StepTracker, with_error_handling


@pytest.fixture
def traced_page(browser, request):
    """Page with tracing enabled"""
    
    os.makedirs("traces", exist_ok=True)
    
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    
    page = context.new_page()
    
    yield page
    
    # Save trace
    test_name = request.node.name
    safe_name = "".join(c if c.isalnum() else "_" for c in test_name)
    trace_path = f"traces/{safe_name}.zip"
    context.tracing.stop(path=trace_path)
    print(f"\n Trace saved: {trace_path}")
    
    context.close()


@with_error_handling()
def test_debug_exercise(traced_page):
    """
    Debug exercise test with full instrumentation
    
    Run: pytest tests/debug/test_debug_exercise.py -v -s
    View trace: playwright show-trace traces/test_debug_exercise.zip
    """
    
    page = traced_page
    tracker = StepTracker(page, "test_debug_exercise")
    
    with tracker.step("Navigate to SauceDemo"):
        page.goto("https://www.saucedemo.com/")
    
    with tracker.step("Fill login credentials"):
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
    
    with tracker.step("Click login button"):
        page.get_by_role("button", name="Login").click()
    
    with tracker.step("Verify login success"):
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    with tracker.step("Add item to cart"):
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    
    with tracker.step("Verify cart badge"):
        expect(page.locator(".shopping_cart_badge")).to_have_text("1")
    
    print(f"\n Test completed! Steps: {tracker.get_steps()}")
    print(" View trace: playwright show-trace traces/test_debug_exercise.zip")
