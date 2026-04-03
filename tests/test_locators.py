"""
CONCEPT: Understanding all locator types
GOAL: Learn when and how to use each locator strategy
REAL-WORLD USE: Finding elements reliably in any web application
"""

from playwright.sync_api import expect

# We'll add tests here as we learn each locator type

def test_get_by_role_button(page):
    """
    LOCATOR: get_by_role('button')
    FINDS: Elements with button role
    REAL-WORLD USE: Clicking submit buttons, action buttons
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Find login button by role
    # 'name' parameter matches the button's accessible name (text content)
    login_button = page.get_by_role("button", name="Login")
    
    # Verify it exists and is visible
    expect(login_button).to_be_visible()
    expect(login_button).to_be_enabled()
    
    # Click it (will fail login since we didn't fill credentials)
    login_button.click()
    
    # Verify error appears
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()


def test_get_by_role_link(page):
    """
    LOCATOR: get_by_role('link')
    FINDS: Anchor elements (<a>)
    REAL-WORLD USE: Navigation testing
    """
    
    page.goto("https://the-internet.herokuapp.com/")
    
    # Find link by its text
    form_auth_link = page.get_by_role("link", name="Form Authentication")
    
    # Verify and click
    expect(form_auth_link).to_be_visible()
    form_auth_link.click()
    
    # Verify navigation worked
    expect(page).to_have_url("https://the-internet.herokuapp.com/login")


def test_get_by_role_heading(page):
    """
    LOCATOR: get_by_role('heading')
    FINDS: h1, h2, h3, etc.
    REAL-WORLD USE: Verifying page titles, section headers
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Find h2 heading
    # level=2 means <h2>
    login_heading = page.get_by_role("heading", level=2)
    
    # Verify text
    expect(login_heading).to_have_text("Login Page")


def test_get_by_role_textbox(page):
    """
    LOCATOR: get_by_role('textbox')
    FINDS: Input fields, textareas
    REAL-WORLD USE: Form filling
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Find username input
    # When there are multiple textboxes, combine with other attributes
    username_input = page.get_by_role("textbox", name="Username")
    
    # Fill and verify
    username_input.fill("testuser")
    expect(username_input).to_have_value("testuser")

def test_get_by_label(page):
    """
    LOCATOR: get_by_label()
    FINDS: Form inputs by their label text
    REAL-WORLD USE: Filling registration forms, contact forms
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Find inputs by their labels
    username_field = page.get_by_label("Username")
    password_field = page.get_by_label("Password")
    
    # Fill the form
    username_field.fill("tomsmith")
    password_field.fill("SuperSecretPassword!")
    
    # Verify values
    expect(username_field).to_have_value("tomsmith")
    expect(password_field).to_have_value("SuperSecretPassword!")
    
    # Submit (using role-based locator)
    page.get_by_role("button", name="Login").click()
    
    # Verify success
    success_message = page.locator(".flash.success")
    expect(success_message).to_be_visible()

def test_get_by_placeholder(page):
    """
    LOCATOR: get_by_placeholder()
    FINDS: Inputs by placeholder attribute
    REAL-WORLD USE: Modern login forms, search boxes
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # SauceDemo has placeholder text on inputs
    username_field = page.get_by_placeholder("Username")
    password_field = page.get_by_placeholder("Password")
    
    # Fill credentials
    username_field.fill("standard_user")
    password_field.fill("secret_sauce")
    
    # Verify
    expect(username_field).to_have_value("standard_user")
    expect(password_field).to_have_value("secret_sauce")

def test_get_by_text_exact(page):
    """
    LOCATOR: get_by_text() with exact=True
    FINDS: Elements with exact text match
    REAL-WORLD USE: Finding specific buttons, links, labels
    """
    
    page.goto("https://the-internet.herokuapp.com/")
    
    # Find exact text match
    ab_testing_link = page.get_by_text("A/B Testing", exact=True)
    
    expect(ab_testing_link).to_be_visible()
    ab_testing_link.click()
    
    # Verify navigation
    expect(page).to_have_url("https://the-internet.herokuapp.com/abtest")


def test_get_by_text_partial(page):
    """
    LOCATOR: get_by_text() partial match
    FINDS: Elements containing the text
    REAL-WORLD USE: Finding elements with dynamic text
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Login first
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Find any element containing "Sauce Labs"
    # This is partial match - finds "Sauce Labs Backpack", "Sauce Labs Bike Light", etc.
    sauce_labs_items = page.get_by_text("Sauce Labs")
    
    # Should find multiple items
    expect(sauce_labs_items.first).to_be_visible()

def test_get_by_test_id(page):
    """
    LOCATOR: get_by_test_id()
    FINDS: Elements with data-testid attribute
    REAL-WORLD USE: Best practice in teams where developers add test IDs
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # SauceDemo uses 'data-test' attribute instead of 'data-testid'
    # We can use locator with attribute selector for this
    username = page.locator("[data-test='username']")
    password = page.locator("[data-test='password']")
    login_button = page.locator("[data-test='login-button']")
    
    # Fill and submit
    username.fill("standard_user")
    password.fill("secret_sauce")
    login_button.click()
    
    # Verify success using data-test attributes
    inventory = page.locator("[data-test='inventory-container']")
    expect(inventory).to_be_visible()

def test_css_selector_by_id(page):
    """
    LOCATOR: CSS selector with ID (#)
    FINDS: Element with specific ID
    REAL-WORLD USE: When element has unique ID but no semantic role
    
     STABILITY: Medium - IDs can change during refactoring
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Find by ID
    username = page.locator("#user-name")
    password = page.locator("#password")
    
    username.fill("standard_user")
    password.fill("secret_sauce")
    
    expect(username).to_have_value("standard_user")


def test_css_selector_by_class(page):
    """
    LOCATOR: CSS selector with class (.)
    FINDS: Elements with specific class
    REAL-WORLD USE: Finding styled components
    
     STABILITY: Low - classes are often used for styling and change frequently
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Find by class
    inventory_items = page.locator(".inventory_item")
    
    # Should find 6 products
    expect(inventory_items).to_have_count(6)


def test_css_selector_combined(page):
    """
    LOCATOR: Combined CSS selectors
    FINDS: Elements matching multiple criteria
    REAL-WORLD USE: Precise element targeting
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Find input inside specific form
    # Syntax: ancestor descendant
    add_to_cart_buttons = page.locator(".inventory_item button")
    
    # All should be visible
    expect(add_to_cart_buttons.first).to_be_visible()
    
    # Click first "Add to cart" button
    add_to_cart_buttons.first.click()
    
    # Verify cart badge shows 1
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("1")


def test_css_selector_attribute(page):
    """
    LOCATOR: CSS attribute selector
    FINDS: Elements with specific attributes
    REAL-WORLD USE: Finding elements by data attributes, types
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Find by attribute
    password_input = page.locator("input[type='password']")
    
    password_input.fill("mypassword")
    expect(password_input).to_have_value("mypassword")


def test_css_nth_child(page):
    """
    LOCATOR: CSS :nth-child selector
    FINDS: Element at specific position
    REAL-WORLD USE: Selecting from lists, tables
    
     STABILITY: Low - breaks if order changes
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Get third inventory item
    third_item = page.locator(".inventory_item:nth-child(3)")
    
    expect(third_item).to_be_visible()

def test_xpath_basic(page):
    """
    LOCATOR: Basic XPath
    FINDS: Elements using path expressions
    REAL-WORLD USE: When CSS selectors aren't sufficient
    
     STABILITY: Low - very dependent on DOM structure
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # XPath to find input by ID
    username = page.locator("//input[@id='user-name']")
    
    username.fill("standard_user")
    expect(username).to_have_value("standard_user")


def test_xpath_text_contains(page):
    """
    LOCATOR: XPath with contains()
    FINDS: Elements containing text
    REAL-WORLD USE: Finding elements with partial text match
    """
    
    page.goto("https://the-internet.herokuapp.com/")
    
    # Find link containing "Form"
    form_link = page.locator("//a[contains(text(),'Form')]").first
    
    expect(form_link).to_be_visible()


def test_xpath_parent_navigation(page):
    """
    LOCATOR: XPath parent navigation (..)
    FINDS: Parent elements (impossible with CSS!)
    REAL-WORLD USE: When you need to go UP the DOM tree
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Find inventory item containing specific product name
    # Then go to parent to get the whole item card
    
    # First, find the product name
    backpack_name = page.locator("text=Sauce Labs Backpack")
    
    # This XPath goes UP to the inventory item container
    # We use // to find ancestor with specific class
    backpack_card = page.locator(
        "//div[contains(@class,'inventory_item_name') and text()='Sauce Labs Backpack']"
        "/ancestor::div[@data-test='inventory-item']"
    )
    
    expect(backpack_card).to_be_visible()

def test_locator_chaining(page):
    """
    CONCEPT: Chaining locators
    GOAL: Narrow down to specific elements
    REAL-WORLD USE: Finding elements within specific containers
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Get the first inventory item container
    first_item = page.locator(".inventory_item").first
    
    # Chain: find button WITHIN that container
    add_button = first_item.get_by_role("button", name="Add to cart")
    
    # Click it
    add_button.click()
    
    # Verify cart updated
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("1")


def test_locator_filtering(page):
    """
    CONCEPT: Filtering locators
    GOAL: Filter elements by additional criteria
    REAL-WORLD USE: Finding specific items in a list
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Find all inventory items
    all_items = page.locator(".inventory_item")
    
    # Filter to find item containing "Backpack"
    backpack_item = all_items.filter(has_text="Backpack")
    
    # Should find exactly one
    expect(backpack_item).to_have_count(1)
    
    # Get the price from this filtered item
    price = backpack_item.locator(".inventory_item_price")
    expect(price).to_have_text("$29.99")


def test_locator_filter_has(page):
    """
    CONCEPT: Filter with has= for nested elements
    GOAL: Find parent by what it contains
    REAL-WORLD USE: Finding rows/cards containing specific child elements
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Find inventory item that HAS a specific price
    cheap_item = page.locator(".inventory_item").filter(
        has=page.locator(".inventory_item_price", has_text="$7.99")
    )
    
    # Get the name of this cheap item
    item_name = cheap_item.locator(".inventory_item_name")
    expect(item_name).to_have_text("Sauce Labs Onesie")

def test_multiple_elements(page):
    """
    CONCEPT: Working with multiple elements
    GOAL: Access specific elements from a collection
    REAL-WORLD USE: Testing lists, tables, search results
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Get all inventory items
    items = page.locator(".inventory_item")
    
    # Verify count
    expect(items).to_have_count(6)
    
    # Access first item
    first_item = items.first
    expect(first_item).to_be_visible()
    
    # Access last item
    last_item = items.last
    expect(last_item).to_be_visible()
    
    # Access by index (0-based)
    third_item = items.nth(2)
    expect(third_item).to_be_visible()


def test_iterate_elements(page):
    """
    CONCEPT: Iterating over elements
    GOAL: Check properties of all matched elements
    REAL-WORLD USE: Verifying all items in a list meet criteria
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Get all prices
    prices = page.locator(".inventory_item_price")
    
    # Verify all prices start with $
    for price in prices.all():
        text = price.text_content()
        assert text.startswith("$"), f"Price {text} doesn't start with $"

def test_ecommerce_locator_strategy(page):
    """
    Real-world example: Complete checkout flow with proper locators
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Login form (labels/placeholders)
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Product page (role + filtering)
    products = page.locator(".inventory_item")
    backpack = products.filter(has_text="Sauce Labs Backpack")
    backpack.get_by_role("button", name="Add to cart").click()
    
    # Cart (role-based)
    page.locator("[data-test='shopping-cart-link']").click()  # Cart icon with badge
    
    # Checkout (role-based)
    page.get_by_role("button", name="Checkout").click()
    
    # Checkout form (labels or placeholders)
    page.get_by_placeholder("First Name").fill("John")
    page.get_by_placeholder("Last Name").fill("Doe")
    page.get_by_placeholder("Zip/Postal Code").fill("12345")
    
    page.get_by_role("button", name="Continue").click()
    
    # Verify total
    total = page.locator(".summary_total_label")
    expect(total).to_contain_text("$")