from playwright.sync_api import expect

def test_dynamic_loading(page):
    """Practice: Dynamic loading with proper waits"""
    
    # Navigate to page
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/2")
    
    # Verify Start button visible
    start_button = page.get_by_role("button", name="Start")
    expect(start_button).to_be_visible()
    
    # Click Start
    start_button.click()
    
    # Wait for loading indicator to disappear
    loading = page.locator("#loading")
    expect(loading).to_be_hidden(timeout=10000)
    
    # Verify result appears
    result = page.locator("#finish h4")
    expect(result).to_be_visible(timeout=10000)
    expect(result).to_have_text("Hello World!")
    
    # Start button should be hidden now
    expect(start_button).to_be_hidden()
