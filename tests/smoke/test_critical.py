import pytest
from playwright.sync_api import expect

@pytest.mark.smoke
def test_homepage_accessible(page):
    page.goto("https://www.saucedemo.com/")
    expect(page).to_have_title("Swag Labs")

@pytest.mark.smoke
def test_login_works(page):
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")


# tests/functional/test_sorting.py
import pytest
from playwright.sync_api import expect

@pytest.mark.parametrize("sort_option,first_item", [
    ("Name (A to Z)", "Sauce Labs Backpack"),
    ("Name (Z to A)", "Test.allTheThings() T-Shirt (Red)"),
    ("Price (low to high)", "Sauce Labs Onesie"),
    ("Price (high to low)", "Sauce Labs Fleece Jacket"),
])
def test_product_sorting(logged_in_page, sort_option, first_item):
    logged_in_page.locator("[data-test='product-sort-container']").select_option(
        label=sort_option
    )
    first_product = logged_in_page.locator(".inventory_item_name").first
    expect(first_product).to_have_text(first_item)
