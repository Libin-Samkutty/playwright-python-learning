"""
CONCEPT: Playwright's expect assertions
GOAL: Use assertions that wait for conditions automatically
REAL-WORLD USE: Handles timing issues in dynamic web apps
"""

from playwright.sync_api import expect

def test_example_heading_visible(page):
    """
    Test: Verify the main heading is visible on example.com
    
    This uses Playwright's expect() which:
    - Waits up to 5 seconds for the element to appear
    - Retries if element is not immediately visible
    - Fails only if timeout is reached
    """
    
    page.goto("https://example.com")
    
    # Find the heading (example.com has an h1)
    heading = page.locator("h1")
    
    # Assert element is visible (auto-waits!)
    expect(heading).to_be_visible()


def test_saucedemo_login_button_enabled(page):
    """
    Test: Verify login button is enabled and clickable
    
    REAL-WORLD USE: Ensure interactive elements are ready before testing
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Find the login button
    login_button = page.locator("#login-button")
    
    # Multiple assertions (all auto-wait!)
    expect(login_button).to_be_visible()     # Is it on the page?
    expect(login_button).to_be_enabled()     # Can it be clicked?
    expect(login_button).to_have_attribute("type", "submit")  # Correct type?