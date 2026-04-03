"""
TEST FILE: test_login_parametrized.py
CONCEPT: Data-driven testing with parametrize
REAL-WORLD USE: Testing multiple user types, input combinations
"""

from playwright.sync_api import expect
import pytest


@pytest.mark.parametrize("username,password,expected_url", [
    # Valid credentials
    ("standard_user", "secret_sauce", "inventory.html"),
    ("problem_user", "secret_sauce", "inventory.html"),
    ("performance_glitch_user", "secret_sauce", "inventory.html"),
])
def test_valid_login_multiple_users(page, username, password, expected_url):
    """
    Test login with multiple valid user accounts
    
    Each tuple in the parametrize list creates a separate test:
    - test_valid_login_multiple_users[standard_user-secret_sauce-inventory.html]
    - test_valid_login_multiple_users[problem_user-secret_sauce-inventory.html]
    - etc.
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    
    expect(page).to_have_url(f"https://www.saucedemo.com/{expected_url}")


@pytest.mark.parametrize("username,password,error_message", [
    # Invalid credentials
    ("invalid_user", "secret_sauce", "Username and password do not match"),
    ("standard_user", "wrong_password", "Username and password do not match"),
    ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out"),
    ("", "secret_sauce", "Username is required"),
    ("standard_user", "", "Password is required"),
])
def test_invalid_login_shows_error(page, username, password, error_message):
    """
    Test that invalid login attempts show appropriate errors
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text(error_message)


# Parametrize with IDs for better readability
@pytest.mark.parametrize(
    "username,password,should_succeed",
    [
        pytest.param("standard_user", "secret_sauce", True, id="valid_standard"),
        pytest.param("locked_out_user", "secret_sauce", False, id="locked_user"),
        pytest.param("invalid", "invalid", False, id="invalid_creds"),
    ]
)
def test_login_with_ids(page, username, password, should_succeed):
    """
    Test with custom IDs for clearer test names
    
    Output:
    - test_login_with_ids[valid_standard] PASSED
    - test_login_with_ids[locked_user] PASSED
    - test_login_with_ids[invalid_creds] PASSED
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    
    if should_succeed:
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    else:
        expect(page.locator("[data-test='error']")).to_be_visible()

"""
Advanced parametrization patterns
"""

import pytest
from playwright.sync_api import expect


# Multiple parametrize decorators = cartesian product
@pytest.mark.parametrize("sort_option", [
    "Name (A to Z)",
    "Name (Z to A)",
    "Price (low to high)",
    "Price (high to low)",
])
@pytest.mark.parametrize("first_item_check", [
    True,
    False,
])
def test_sorting_combinations(page, sort_option, first_item_check):
    """
    Tests all combinations:
    - "Name (A to Z)" + True
    - "Name (A to Z)" + False
    - "Name (Z to A)" + True
    - etc.
    
    Total: 4 x 2 = 8 tests
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Apply sort
    page.locator("[data-test='product-sort-container']").select_option(
        label=sort_option
    )
    
    if first_item_check:
        first_item = page.locator(".inventory_item_name").first
        expect(first_item).to_be_visible()


# Parametrize with fixtures
@pytest.fixture(params=["standard_user", "problem_user"])
def logged_in_user(request, page):
    """
    Fixture that runs tests for each user type
    
    request.param contains the current parameter value
    """
    
    username = request.param
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    return {"page": page, "username": username}


def test_products_visible_for_all_users(logged_in_user):
    """
    This test runs twice:
    - Once with standard_user
    - Once with problem_user
    """
    
    page = logged_in_user["page"]
    products = page.locator(".inventory_item")
    expect(products).to_have_count(6)


# Indirect parametrization
@pytest.fixture
def product_data(request):
    """Fixture that returns product test data"""
    
    products = {
        "backpack": {
            "name": "Sauce Labs Backpack",
            "price": "$29.99",
            "add_button": "add-to-cart-sauce-labs-backpack",
        },
        "bike_light": {
            "name": "Sauce Labs Bike Light",
            "price": "$9.99",
            "add_button": "add-to-cart-sauce-labs-bike-light",
        },
        "onesie": {
            "name": "Sauce Labs Onesie",
            "price": "$7.99",
            "add_button": "add-to-cart-sauce-labs-onesie",
        },
    }
    
    return products[request.param]


@pytest.mark.parametrize("product_data", ["backpack", "bike_light"], indirect=True)
def test_product_details(page, product_data):
    """
    indirect=True tells pytest to pass the parameter
    to the fixture instead of the test
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Find product by name
    product = page.locator(".inventory_item").filter(
        has_text=product_data["name"]
    )
    
    # Verify price
    price = product.locator(".inventory_item_price")
    expect(price).to_have_text(product_data["price"])