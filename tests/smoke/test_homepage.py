"""
TEST FILE: test_homepage.py
CATEGORY: Smoke Tests
PURPOSE: Quick sanity checks for homepage functionality
RUN: pytest tests/smoke/test_homepage.py -v
     pytest -m smoke -v

REAL-WORLD USE:
- Run after deployments
- Quick health checks
- CI/CD pipeline gates
"""

import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_homepage_loads_successfully(page):
    """
    SMOKE TEST: Verify homepage is accessible
    
    WHAT IT CHECKS:
    - Page loads without errors
    - Correct title displayed
    
    WHY IT MATTERS:
    - If homepage fails, entire site is down
    - First thing to check after deployment
    """
    
    # Navigate to homepage
    page.goto("https://www.saucedemo.com/")
    
    # Verify page title
    expect(page).to_have_title("Swag Labs")


@pytest.mark.smoke
def test_homepage_has_login_form(page):
    """
    SMOKE TEST: Verify login form is present
    
    WHAT IT CHECKS:
    - Username field exists
    - Password field exists
    - Login button exists and is enabled
    
    WHY IT MATTERS:
    - Users must be able to log in
    - Form elements must be visible and functional
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Verify login form elements
    username_field = page.get_by_placeholder("Username")
    password_field = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")
    
    # All elements should be visible
    expect(username_field).to_be_visible()
    expect(password_field).to_be_visible()
    expect(login_button).to_be_visible()
    
    # Login button should be enabled
    expect(login_button).to_be_enabled()


@pytest.mark.smoke
def test_homepage_has_branding(page):
    """
    SMOKE TEST: Verify branding elements
    
    WHAT IT CHECKS:
    - Logo or brand name is displayed
    - Correct brand identity
    
    WHY IT MATTERS:
    - Ensures correct site is deployed
    - Catches white-label or branding issues
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Check for Swag Labs branding
    # The login page has "Swag Labs" text
    brand_text = page.locator(".login_logo")
    expect(brand_text).to_be_visible()
    expect(brand_text).to_have_text("Swag Labs")


@pytest.mark.smoke
def test_homepage_credentials_info_displayed(page):
    """
    SMOKE TEST: Verify accepted usernames info is shown
    
    WHAT IT CHECKS:
    - Help text with valid usernames is displayed
    - Password hint is displayed
    
    WHY IT MATTERS:
    - Demo site specific - users need to know valid credentials
    - Content verification
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Check for credentials information
    credentials_info = page.locator("#login_credentials")
    expect(credentials_info).to_be_visible()
    expect(credentials_info).to_contain_text("Accepted usernames")
    expect(credentials_info).to_contain_text("standard_user")
    
    # Check for password info
    password_info = page.locator(".login_password")
    expect(password_info).to_be_visible()
    expect(password_info).to_contain_text("secret_sauce")


@pytest.mark.smoke
def test_homepage_form_fields_are_editable(page):
    """
    SMOKE TEST: Verify form fields accept input
    
    WHAT IT CHECKS:
    - Username field is editable
    - Password field is editable
    - Fields accept and retain typed values
    
    WHY IT MATTERS:
    - Fields might be accidentally disabled
    - JavaScript errors could break inputs
    """
    
    page.goto("https://www.saucedemo.com/")
    
    username_field = page.get_by_placeholder("Username")
    password_field = page.get_by_placeholder("Password")
    
    # Verify fields are editable
    expect(username_field).to_be_editable()
    expect(password_field).to_be_editable()
    
    # Verify fields accept input
    username_field.fill("test_input")
    password_field.fill("test_password")
    
    expect(username_field).to_have_value("test_input")
    expect(password_field).to_have_value("test_password")


@pytest.mark.smoke
def test_homepage_url_is_correct(page):
    """
    SMOKE TEST: Verify correct URL
    
    WHAT IT CHECKS:
    - URL matches expected domain
    - No redirects to error pages
    
    WHY IT MATTERS:
    - DNS issues
    - Redirect misconfigurations
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Verify URL
    expect(page).to_have_url("https://www.saucedemo.com/")


@pytest.mark.smoke
def test_homepage_no_console_errors(page):
    """
    SMOKE TEST: Verify no JavaScript errors on load
    
    WHAT IT CHECKS:
    - No critical JavaScript errors
    - Page loads without script failures
    
    WHY IT MATTERS:
    - JS errors can break functionality
    - Indicates build/deployment issues
    """
    
    errors = []
    
    # Listen for console errors
    def handle_console(msg):
        if msg.type == "error":
            errors.append(msg.text)
    
    page.on("console", handle_console)
    
    # Load page
    page.goto("https://www.saucedemo.com/")
    
    # Wait a moment for any async errors
    page.wait_for_timeout(1000)
    
    # Filter out known/acceptable errors (favicon, 3rd-party 401s from analytics/tracking)
    critical_errors = [
        e for e in errors
        if "favicon" not in e.lower()
        and "401" not in e
    ]
    
    # Assert no critical errors
    assert len(critical_errors) == 0, f"Console errors found: {critical_errors}"