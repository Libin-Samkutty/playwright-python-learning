"""
tests/debug/test_with_pause.py
Debugging with page.pause()
"""

from playwright.sync_api import expect


def test_debug_with_pause(page):
    """
    Test demonstrating page.pause() for debugging
    
    USAGE:
    1. Run with: pytest tests/debug/test_with_pause.py -s
    2. Browser pauses at page.pause()
    3. Use Inspector to:
       - Explore elements
       - Try locators
       - Step through actions
    4. Click 'Resume' to continue
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Pause here - Inspector opens
    page.pause()
    
    # Fill login form
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    
    # Pause again to inspect before clicking
    page.pause()
    
    page.get_by_role("button", name="Login").click()
    
    # Pause to verify result
    page.pause()
    
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")