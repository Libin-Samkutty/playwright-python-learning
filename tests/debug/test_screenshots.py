"""
tests/debug/test_screenshots.py
Manual screenshot examples
"""

from playwright.sync_api import expect
import pytest
import os


def test_screenshot_types(page):
    """
    Demonstrate different screenshot options
    """
    
    os.makedirs("screenshots", exist_ok=True)
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Wait for products to load
    expect(page.locator(".inventory_item").first).to_be_visible()
    
    # Screenshot 1: Visible viewport only
    page.screenshot(path="screenshots/viewport_only.png")
    
    # Screenshot 2: Full page (scrollable content)
    page.screenshot(path="screenshots/full_page.png", full_page=True)
    
    # Screenshot 3: Specific element
    first_product = page.locator(".inventory_item").first
    first_product.screenshot(path="screenshots/first_product.png")
    
    # Screenshot 4: With quality settings (JPEG)
    page.screenshot(
        path="screenshots/quality_test.jpg",
        type="jpeg",
        quality=80,
    )
    
    # Screenshot 5: With clip (specific region)
    page.screenshot(
        path="screenshots/clipped_region.png",
        clip={"x": 0, "y": 0, "width": 500, "height": 300},
    )
    
    # Screenshot 6: Omit background (transparent PNG)
    page.screenshot(
        path="screenshots/transparent.png",
        omit_background=True,
    )


@pytest.mark.xfail(reason="Intentionally fails to demonstrate screenshot capture on assertion failure", strict=True)
def test_screenshot_on_assertion_failure(page):
    """
    Capture screenshot when assertion fails
    """
    
    os.makedirs("screenshots", exist_ok=True)
    
    page.goto("https://www.saucedemo.com/")
    
    try:
        # This will fail
        expect(page).to_have_title("Wrong Title")
    except AssertionError as e:
        # Capture screenshot before re-raising
        page.screenshot(path="screenshots/assertion_failure.png")
        print(f"Screenshot captured for failed assertion")
        raise


def test_screenshot_helper_function(page):
    """
    Using a helper function for screenshots
    """
    
    def screenshot_step(page, name: str, description: str = ""):
        """
        Capture screenshot with logging
        """
        os.makedirs("screenshots/steps", exist_ok=True)
        path = f"screenshots/steps/{name}.png"
        page.screenshot(path=path)
        print(f" Step: {description or name} -> {path}")
        return path
    
    page.goto("https://www.saucedemo.com/")
    screenshot_step(page, "01_login_page", "Login page loaded")
    
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    screenshot_step(page, "02_credentials_filled", "Credentials entered")
    
    page.get_by_role("button", name="Login").click()
    
    expect(page.locator(".inventory_item").first).to_be_visible()
    screenshot_step(page, "03_logged_in", "Successfully logged in")
