"""
scripts/run_ui_mode.py
Run tests in UI mode (development helper)
"""

from playwright.sync_api import sync_playwright

def run_in_ui_mode():
    """
    Launch browser for interactive testing
    
    Usage: python scripts/run_ui_mode.py
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to your app
        page.goto("https://www.saucedemo.com/")
        
        # Pause for interaction
        page.pause()
        
        browser.close()

if __name__ == "__main__":
    run_in_ui_mode()
