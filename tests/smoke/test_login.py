"""
TEST FILE: test_login.py
CATEGORY: Smoke Tests
PURPOSE: Quick sanity checks for login functionality
RUN: pytest tests/smoke/test_login.py -v
     pytest -m smoke -m login -v

REAL-WORLD USE:
- Verify authentication works after deployment
- Quick regression check for login
- CI/CD gate before running full suite
"""

import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
@pytest.mark.login
def test_valid_login_redirects_to_inventory(page):
    """
    SMOKE TEST: Verify valid login works
    
    WHAT IT CHECKS:
    - User can log in with valid credentials
    - Redirect to inventory page after login
    
    WHY IT MATTERS:
    - Core functionality - if login fails, nothing else works
    - Most critical user flow
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Enter valid credentials
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    
    # Click login
    page.get_by_role("button", name="Login").click()
    
    # Verify redirect to inventory
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")


@pytest.mark.smoke
@pytest.mark.login
def test_valid_login_shows_products(page):
    """
    SMOKE TEST: Verify products appear after login
    
    WHAT IT CHECKS:
    - Products are displayed after login
    - At least one product is visible
    
    WHY IT MATTERS:
    - Login might work but products fail to load
    - Catches API or data issues
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Verify products are visible
    products = page.locator(".inventory_item")
    expect(products.first).to_be_visible()
    expect(products).to_have_count(6)


@pytest.mark.smoke
@pytest.mark.login
def test_invalid_login_shows_error(page):
    """
    SMOKE TEST: Verify invalid login is rejected
    
    WHAT IT CHECKS:
    - Invalid credentials are rejected
    - Error message is displayed
    
    WHY IT MATTERS:
    - Security - shouldn't allow invalid access
    - Error handling works correctly
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Enter invalid credentials
    page.get_by_placeholder("Username").fill("invalid_user")
    page.get_by_placeholder("Password").fill("invalid_password")
    
    # Click login
    page.get_by_role("button", name="Login").click()
    
    # Verify error message
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Username and password do not match")
    
    # Verify still on login page
    expect(page).to_have_url("https://www.saucedemo.com/")


@pytest.mark.smoke
@pytest.mark.login
def test_empty_username_shows_error(page):
    """
    SMOKE TEST: Verify empty username validation
    
    WHAT IT CHECKS:
    - Empty username is not allowed
    - Appropriate error message shown
    
    WHY IT MATTERS:
    - Form validation works
    - User gets helpful feedback
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Leave username empty, fill password
    page.get_by_placeholder("Password").fill("secret_sauce")
    
    # Click login
    page.get_by_role("button", name="Login").click()
    
    # Verify error
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Username is required")


@pytest.mark.smoke
@pytest.mark.login
def test_empty_password_shows_error(page):
    """
    SMOKE TEST: Verify empty password validation
    
    WHAT IT CHECKS:
    - Empty password is not allowed
    - Appropriate error message shown
    
    WHY IT MATTERS:
    - Form validation works
    - User gets helpful feedback
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Fill username, leave password empty
    page.get_by_placeholder("Username").fill("standard_user")
    
    # Click login
    page.get_by_role("button", name="Login").click()
    
    # Verify error
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Password is required")


@pytest.mark.smoke
@pytest.mark.login
def test_locked_user_shows_error(page):
    """
    SMOKE TEST: Verify locked user cannot login
    
    WHAT IT CHECKS:
    - Locked user account is rejected
    - Appropriate error message shown
    
    WHY IT MATTERS:
    - Account lockout functionality works
    - Security feature verification
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Use locked out user
    page.get_by_placeholder("Username").fill("locked_out_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    
    # Click login
    page.get_by_role("button", name="Login").click()
    
    # Verify error
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Sorry, this user has been locked out")


@pytest.mark.smoke
@pytest.mark.login
def test_login_error_can_be_dismissed(page):
    """
    SMOKE TEST: Verify error can be dismissed
    
    WHAT IT CHECKS:
    - Error close button works
    - Error disappears when dismissed
    
    WHY IT MATTERS:
    - UX - users should be able to clear errors
    - UI component functionality
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Trigger error
    page.get_by_role("button", name="Login").click()
    
    # Verify error visible
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()
    
    # Click close button
    error_button = page.locator("[data-test='error-button']")
    error_button.click()
    
    # Verify error dismissed
    expect(error).to_be_hidden()


@pytest.mark.smoke
@pytest.mark.login
def test_login_via_enter_key(page):
    """
    SMOKE TEST: Verify login works with Enter key
    
    WHAT IT CHECKS:
    - Form submission via Enter key
    - Keyboard accessibility
    
    WHY IT MATTERS:
    - Accessibility requirement
    - Common user behavior
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Fill credentials
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    
    # Press Enter instead of clicking button
    page.get_by_placeholder("Password").press("Enter")
    
    # Verify login successful
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")