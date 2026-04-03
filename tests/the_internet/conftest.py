"""
tests/the_internet/conftest.py
Fixtures for The Internet tests
"""

import pytest
import playwright_state as _pw_state
from playwright.sync_api import Page
from collections.abc import Iterator

# Import page objects
from pages.the_internet import (
    TheInternetLoginPage,
    SecureAreaPage,
    DynamicLoadingPage,
)


# ============================================================
# BROWSER FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def browser():
    """Session-scoped browser (shared via playwright_state)"""
    yield _pw_state.get_browser()


@pytest.fixture(scope="function")
def context(browser):
    """Fresh context for each test"""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context) -> Iterator[Page]:
    """Fresh page for each test"""
    page = context.new_page()
    page.set_default_timeout(30000)
    yield page


# ============================================================
# PAGE OBJECT FIXTURES
# ============================================================

@pytest.fixture
def the_internet_login_page(page) -> TheInternetLoginPage:
    """The Internet Login Page Object fixture"""
    return TheInternetLoginPage(page)


@pytest.fixture
def secure_area_page(page) -> SecureAreaPage:
    """Secure Area Page Object fixture"""
    return SecureAreaPage(page)


@pytest.fixture
def dynamic_loading_page_1(page) -> DynamicLoadingPage:
    """Dynamic Loading Example 1 Page Object fixture"""
    return DynamicLoadingPage(page, example=1)


@pytest.fixture
def dynamic_loading_page_2(page) -> DynamicLoadingPage:
    """Dynamic Loading Example 2 Page Object fixture"""
    return DynamicLoadingPage(page, example=2)


# ============================================================
# CONVENIENCE FIXTURES
# ============================================================

@pytest.fixture
def logged_in_secure_area(
    the_internet_login_page, 
    secure_area_page
) -> SecureAreaPage:
    """
    Fixture providing logged-in state on secure area
    
    Usage:
        def test_secure_content(logged_in_secure_area):
            # Already logged in
            logged_in_secure_area.verify_logged_in()
    """
    the_internet_login_page.navigate()
    the_internet_login_page.login_with_valid_credentials()
    
    assert secure_area_page.is_loaded()
    
    return secure_area_page


# ============================================================
# TEST DATA
# ============================================================

@pytest.fixture
def valid_credentials():
    """Valid credentials for The Internet"""
    return {
        "username": "tomsmith",
        "password": "SuperSecretPassword!",
    }


@pytest.fixture
def invalid_credentials():
    """Invalid credentials for testing"""
    return [
        {"username": "invalid", "password": "SuperSecretPassword!", "error": "Your username is invalid!"},
        {"username": "tomsmith", "password": "invalid", "error": "Your password is invalid!"},
        {"username": "", "password": "SuperSecretPassword!", "error": "Your username is invalid!"},
        {"username": "tomsmith", "password": "", "error": "Your password is invalid!"},
    ]