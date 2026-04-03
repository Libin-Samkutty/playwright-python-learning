from playwright.sync_api import expect

def test_login_with_various_locators(page):
    """Practice: Use multiple locator strategies"""
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # 1. get_by_label for username
    username = page.get_by_label("Username")
    username.fill("tomsmith")
    
    # 2. CSS selector for password
    password = page.locator("input[type='password']")
    password.fill("SuperSecretPassword!")
    
    # 3. get_by_role for login button
    login_button = page.get_by_role("button", name="Login")
    login_button.click()
    
    # 4. get_by_role for logout
    logout_button = page.get_by_role("link", name="Logout")
    expect(logout_button).to_be_visible()
    
    # 5. Verify flash message
    flash_message = page.locator(".flash")
    expect(flash_message).to_contain_text("You logged into")