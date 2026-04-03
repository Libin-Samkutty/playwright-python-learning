"""
tests/fixtures/parametrized.py
Parametrized fixtures for data-driven testing
"""

import pytest


@pytest.fixture(params=["chromium", "firefox", "webkit"])
def multi_browser(request, playwright_instance):
    """
    PARAMETRIZED FIXTURE: Run tests on multiple browsers
    
    HOW IT WORKS:
    - params=["chromium", "firefox", "webkit"]
    - Each test using this fixture runs 3 times
    - request.param contains current browser name
    
    USE CASE:
    - Cross-browser testing
    - Browser compatibility checks
    """
    
    browser_name = request.param
    print(f"\n[BROWSER] Launching {browser_name}...")
    
    browser_launcher = getattr(playwright_instance, browser_name)
    browser = browser_launcher.launch(headless=True)
    
    yield browser
    
    browser.close()


@pytest.fixture(params=[
    {"width": 375, "height": 667, "name": "mobile"},
    {"width": 768, "height": 1024, "name": "tablet"},
    {"width": 1280, "height": 720, "name": "desktop"},
])
def responsive_page(request, browser_instance):
    """
    PARAMETRIZED FIXTURE: Test across viewports
    
    Each test runs 3 times with different viewport sizes
    """
    
    viewport_config = request.param
    
    context = browser_instance.new_context(
        viewport={
            "width": viewport_config["width"],
            "height": viewport_config["height"],
        }
    )
    page = context.new_page()
    
    # Attach viewport name for test reference
    page.viewport_name = viewport_config["name"]
    
    yield page
    
    context.close()


@pytest.fixture(
    params=[
        pytest.param("standard_user", id="standard"),
        pytest.param("problem_user", id="problem"),
        pytest.param("performance_glitch_user", id="performance"),
    ]
)
def user_page(request, browser_instance, test_data):
    """
    PARAMETRIZED FIXTURE: Test with different user types
    
    Using pytest.param with id for readable test names:
    - test_something[standard]
    - test_something[problem]
    - test_something[performance]
    """
    
    username = request.param
    
    context = browser_instance.new_context()
    page = context.new_page()
    
    # Login
    page.goto(test_data["urls"]["base"])
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Wait with appropriate timeout
    timeout = 15000 if "performance" in username else 5000
    page.wait_for_url("**/inventory.html", timeout=timeout)
    
    # Attach username for reference
    page.username = username
    
    yield page
    
    context.close()


@pytest.fixture(
    params=[
        pytest.param(
            {"name": "Sauce Labs Backpack", "price": "$29.99"},
            id="backpack"
        ),
        pytest.param(
            {"name": "Sauce Labs Bike Light", "price": "$9.99"},
            id="bike_light"
        ),
        pytest.param(
            {"name": "Sauce Labs Onesie", "price": "$7.99"},
            id="onesie"
        ),
    ]
)
def product_info(request):
    """
    PARAMETRIZED FIXTURE: Product test data
    
    Pure data fixture - no browser involvement
    """
    
    return request.param
