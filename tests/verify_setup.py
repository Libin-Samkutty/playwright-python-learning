"""
CONCEPT: Basic Playwright Usage
GOAL: Understand how Playwright opens a browser and navigates to a page
REAL-WORLD USE: This is the foundation of every test you'll write
"""

from playwright.sync_api import sync_playwright

# This is NOT a pytest test yet - just a script to verify setup
def run_basic_navigation():
    # sync_playwright() is the entry point - it manages browser lifecycle
    with sync_playwright() as p:
        # Launch a browser (headless=False means you'll see the browser window)
        browser = p.chromium.launch(headless=False)
        
        # Create a new browser context (like an incognito window)
        context = browser.new_context()
        
        # Open a new page (tab)
        page = context.new_page()
        
        # Navigate to a reliable URL
        page.goto("https://example.com")
        
        # Print the page title
        print(f"Page title: {page.title()}")
        
        # Wait 3 seconds so you can see the browser (NOT for real tests!)
        page.wait_for_timeout(3000)
        
        # Close everything
        context.close()
        browser.close()

# Run the function
if __name__ == "__main__":
    run_basic_navigation()