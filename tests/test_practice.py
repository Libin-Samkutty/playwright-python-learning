from playwright.sync_api import expect

def test_internet_homepage(page):
    """Verify The Internet homepage loads"""
    page.goto("https://the-internet.herokuapp.com/")
    assert page.title() == "The Internet"

def test_navigate_to_login(page):
    """Navigate to login page"""
    page.goto("https://the-internet.herokuapp.com/")
    
    # Click Form Authentication link
    page.locator("text=Form Authentication").click()
    
    # Verify URL
    expect(page).to_have_url("https://the-internet.herokuapp.com/login")