"""
tests/reporting/test_allure_reports.py
Tests demonstrating Allure reporting features
"""

import pytest
import allure
from playwright.sync_api import expect


@allure.epic("E-Commerce Platform")
@allure.feature("User Authentication")
class TestLoginAllure:
    """
    Login tests with Allure reporting
    """
    
    @allure.story("Valid Login")
    @allure.title("User can login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_login(self, page):
        """
        Test valid login flow with Allure annotations
        """
        
        with allure.step("Navigate to login page"):
            page.goto("https://www.saucedemo.com/")
            allure.attach(
                page.screenshot(),
                name="Login Page",
                attachment_type=allure.attachment_type.PNG,
            )
        
        with allure.step("Enter valid credentials"):
            page.get_by_placeholder("Username").fill("standard_user")
            page.get_by_placeholder("Password").fill("secret_sauce")
        
        with allure.step("Submit login form"):
            page.get_by_role("button", name="Login").click()
        
        with allure.step("Verify successful login"):
            expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
            allure.attach(
                page.screenshot(),
                name="After Login",
                attachment_type=allure.attachment_type.PNG,
            )
    
    @allure.story("Invalid Login")
    @allure.title("Error shown for invalid credentials")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username,password,error_msg", [
        pytest.param(
            "invalid_user", 
            "secret_sauce", 
            "Username and password do not match",
            id="invalid_username",
        ),
        pytest.param(
            "standard_user", 
            "wrong_pass", 
            "Username and password do not match",
            id="invalid_password",
        ),
        pytest.param(
            "locked_out_user", 
            "secret_sauce", 
            "Sorry, this user has been locked out",
            id="locked_user",
        ),
    ])
    def test_invalid_login(self, page, username, password, error_msg):
        """
        Test invalid login scenarios
        """
        
        with allure.step(f"Attempt login with user: {username}"):
            page.goto("https://www.saucedemo.com/")
            page.get_by_placeholder("Username").fill(username)
            page.get_by_placeholder("Password").fill(password)
            page.get_by_role("button", name="Login").click()
        
        with allure.step("Verify error message"):
            error = page.locator("[data-test='error']")
            expect(error).to_be_visible()
            expect(error).to_contain_text(error_msg)
            
            allure.attach(
                page.screenshot(),
                name="Error State",
                attachment_type=allure.attachment_type.PNG,
            )


@allure.epic("E-Commerce Platform")
@allure.feature("Shopping Cart")
class TestCartAllure:
    """
    Cart tests with Allure reporting
    """
    
    @allure.story("Add to Cart")
    @allure.title("User can add product to cart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart(self, page):
        """
        Test adding product to cart
        """
        
        with allure.step("Login"):
            page.goto("https://www.saucedemo.com/")
            page.get_by_placeholder("Username").fill("standard_user")
            page.get_by_placeholder("Password").fill("secret_sauce")
            page.get_by_role("button", name="Login").click()
        
        with allure.step("Add product to cart"):
            page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        
        with allure.step("Verify cart badge"):
            cart_badge = page.locator(".shopping_cart_badge")
            expect(cart_badge).to_have_text("1")
            
            allure.attach(
                page.screenshot(),
                name="Cart Updated",
                attachment_type=allure.attachment_type.PNG,
            )
    
    @allure.story("Remove from Cart")
    @allure.title("User can remove product from cart")
    @allure.severity(allure.severity_level.NORMAL)
    def test_remove_from_cart(self, page):
        """
        Test removing product from cart
        """
        
        with allure.step("Login and add product"):
            page.goto("https://www.saucedemo.com/")
            page.get_by_placeholder("Username").fill("standard_user")
            page.get_by_placeholder("Password").fill("secret_sauce")
            page.get_by_role("button", name="Login").click()
            page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        
        with allure.step("Remove product"):
            page.locator("[data-test='remove-sauce-labs-backpack']").click()
        
        with allure.step("Verify cart empty"):
            cart_badge = page.locator(".shopping_cart_badge")
            expect(cart_badge).to_have_count(0)


@allure.epic("E-Commerce Platform")
@allure.feature("Checkout")
class TestCheckoutAllure:
    """
    Checkout tests with Allure reporting
    """
    
    @allure.story("Complete Purchase")
    @allure.title("User can complete purchase flow")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("""
    This test verifies the complete checkout flow:
    1. Login
    2. Add item to cart
    3. Go to checkout
    4. Fill shipping info
    5. Complete purchase
    """)
    @allure.link("https://jira.example.com/SHOP-123", name="JIRA Ticket")
    def test_complete_checkout(self, page):
        """
        Complete checkout flow test
        """
        
        with allure.step("Login"):
            page.goto("https://www.saucedemo.com/")
            page.get_by_placeholder("Username").fill("standard_user")
            page.get_by_placeholder("Password").fill("secret_sauce")
            page.get_by_role("button", name="Login").click()
        
        with allure.step("Add item to cart"):
            page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
            allure.attach(
                page.screenshot(),
                name="Item Added",
                attachment_type=allure.attachment_type.PNG,
            )
        
        with allure.step("Navigate to cart"):
            page.locator(".shopping_cart_link").click()
            expect(page).to_have_url("https://www.saucedemo.com/cart.html")
        
        with allure.step("Proceed to checkout"):
            page.get_by_role("button", name="Checkout").click()
        
        with allure.step("Fill shipping information"):
            page.get_by_placeholder("First Name").fill("John")
            page.get_by_placeholder("Last Name").fill("Doe")
            page.get_by_placeholder("Zip/Postal Code").fill("12345")
            
            allure.attach(
                page.screenshot(),
                name="Shipping Info",
                attachment_type=allure.attachment_type.PNG,
            )
        
        with allure.step("Continue to overview"):
            page.get_by_role("button", name="Continue").click()
            expect(page).to_have_url(
                "https://www.saucedemo.com/checkout-step-two.html"
            )
        
        with allure.step("Complete purchase"):
            page.get_by_role("button", name="Finish").click()
        
        with allure.step("Verify order confirmation"):
            expect(page.locator(".complete-header")).to_have_text(
                "Thank you for your order!"
            )
            
            allure.attach(
                page.screenshot(),
                name="Order Complete",
                attachment_type=allure.attachment_type.PNG,
            )