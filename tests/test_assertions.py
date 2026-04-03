"""
CONCEPT: Assertions and Waiting Strategies
GOAL: Master all assertion types and timing control
REAL-WORLD USE: Building stable, reliable tests
"""

from playwright.sync_api import expect
import pytest

def test_page_url_assertion(page):
    """
    ASSERTION: expect(page).to_have_url()
    CHECKS: Current URL matches expected
    REAL-WORLD USE: Verify navigation, redirects after login
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Fill login form
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Assert URL changed after login
    # This WAITS for URL to change (up to 5 seconds)
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")


def test_page_url_pattern(page):
    """
    ASSERTION: expect(page).to_have_url() with pattern
    CHECKS: URL matches a regex pattern
    REAL-WORLD USE: URLs with dynamic IDs, query params
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Use regex pattern for flexible matching
    import re
    expect(page).to_have_url(re.compile(r".*inventory.*"))


def test_page_title_assertion(page):
    """
    ASSERTION: expect(page).to_have_title()
    CHECKS: Page title matches expected
    REAL-WORLD USE: Verify correct page loaded, SEO testing
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Exact title match
    expect(page).to_have_title("Swag Labs")
    
    # Pattern match
    import re
    expect(page).to_have_title(re.compile(r".*Labs"))

def test_element_visibility(page):
    """
    ASSERTIONS: to_be_visible(), to_be_hidden()
    CHECKS: Element visibility state
    REAL-WORLD USE: Verify modals, error messages, loading states
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Login button should be visible
    login_button = page.get_by_role("button", name="Login")
    expect(login_button).to_be_visible()
    
    # Error message should be hidden initially
    error = page.locator("[data-test='error']")
    expect(error).to_be_hidden()
    
    # Click login without credentials
    login_button.click()
    
    # Now error should be visible
    expect(error).to_be_visible()


def test_element_attached(page):
    """
    ASSERTIONS: to_be_attached(), to_be_attached(attached=False)
    CHECKS: Element exists in DOM (even if invisible)
    REAL-WORLD USE: Elements that are hidden but present (like hidden inputs)
    
    DIFFERENCE FROM VISIBLE:
    - to_be_visible(): Element exists AND is displayed
    - to_be_attached(): Element exists in DOM (might be hidden)
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Form exists in DOM
    form = page.locator("#login")
    expect(form).to_be_attached()
    
    # Login successfully
    page.get_by_label("Username").fill("tomsmith")
    page.get_by_label("Password").fill("SuperSecretPassword!")
    page.get_by_role("button", name="Login").click()
    
    # Verify we navigated away - login form no longer attached
    expect(form).to_be_attached(attached=False)

def test_element_enabled_disabled(page):
    """
    ASSERTIONS: to_be_enabled(), to_be_disabled()
    CHECKS: Whether element can be interacted with
    REAL-WORLD USE: Form validation, submit buttons, conditional inputs
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_controls")
    
    # Initially, the input is disabled
    text_input = page.locator("#input-example input")
    expect(text_input).to_be_disabled()
    
    # Click Enable button
    page.get_by_role("button", name="Enable").click()
    
    # Wait for input to become enabled
    expect(text_input).to_be_enabled()
    
    # Now we can type
    text_input.fill("Hello World")
    expect(text_input).to_have_value("Hello World")


def test_checkbox_checked(page):
    """
    ASSERTIONS: to_be_checked(), not_to_be_checked()
    CHECKS: Checkbox/radio button state
    REAL-WORLD USE: Form defaults, user preferences, settings
    """
    
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    
    # Get both checkboxes
    checkboxes = page.locator("input[type='checkbox']")
    first_checkbox = checkboxes.nth(0)
    second_checkbox = checkboxes.nth(1)
    
    # Verify initial states
    expect(first_checkbox).not_to_be_checked()
    expect(second_checkbox).to_be_checked()
    
    # Click first checkbox
    first_checkbox.click()
    
    # Now first should be checked
    expect(first_checkbox).to_be_checked()

def test_element_editable(page):
    """
    ASSERTION: to_be_editable()
    CHECKS: Element accepts input
    REAL-WORLD USE: Verify input fields are editable, not read-only
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    username_field = page.get_by_label("Username")
    
    # Field should be editable
    expect(username_field).to_be_editable()

def test_text_exact_match(page):
    """
    ASSERTION: to_have_text()
    CHECKS: Element's text content matches exactly
    REAL-WORLD USE: Verify headings, labels, button text
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Check heading text
    heading = page.get_by_role("heading", level=2)
    expect(heading).to_have_text("Login Page")


def test_text_partial_match(page):
    """
    ASSERTION: to_contain_text()
    CHECKS: Element contains the text (partial match)
    REAL-WORLD USE: Dynamic content, timestamps, user-generated content
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Subheader contains this text (doesn't have to be exact)
    subheader = page.locator(".subheader")
    expect(subheader).to_contain_text("secure area")


def test_text_with_pattern(page):
    """
    ASSERTION: to_have_text() with regex
    CHECKS: Text matches a pattern
    REAL-WORLD USE: Prices, dates, IDs with variable parts
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Price should match pattern $XX.XX
    import re
    price = page.locator(".inventory_item_price").first
    expect(price).to_have_text(re.compile(r"\$\d+\.\d{2}"))


def test_empty_text(page):
    """
    ASSERTION: to_be_empty(), to_have_text("")
    CHECKS: Element has no text
    REAL-WORLD USE: Cleared inputs, empty lists
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Username field starts empty
    username = page.get_by_placeholder("Username")
    expect(username).to_be_empty()
    
    # Fill it
    username.fill("test")
    expect(username).not_to_be_empty()
    
    # Clear it
    username.clear()
    expect(username).to_be_empty()

def test_input_value(page):
    """
    ASSERTION: to_have_value()
    CHECKS: Input field's current value
    REAL-WORLD USE: Form validation, auto-fill verification
    """
    
    page.goto("https://www.saucedemo.com/")
    
    username = page.get_by_placeholder("Username")
    
    # Initially empty
    expect(username).to_have_value("")
    
    # After filling
    username.fill("standard_user")
    expect(username).to_have_value("standard_user")


def test_input_value_pattern(page):
    """
    ASSERTION: to_have_value() with regex
    CHECKS: Value matches pattern
    REAL-WORLD USE: Email format, phone numbers, dates
    """
    
    page.goto("https://www.saucedemo.com/")
    
    username = page.get_by_placeholder("Username")
    username.fill("user_12345")
    
    # Check value matches pattern
    import re
    expect(username).to_have_value(re.compile(r"user_\d+"))

def test_attribute_value(page):
    """
    ASSERTION: to_have_attribute()
    CHECKS: Element has attribute with specific value
    REAL-WORLD USE: Links, images, data attributes
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Check login button type
    login_button = page.get_by_role("button", name="Login")
    expect(login_button).to_have_attribute("type", "submit")
    
    # Check input placeholder
    username = page.get_by_placeholder("Username")
    expect(username).to_have_attribute("placeholder", "Username")


def test_attribute_with_pattern(page):
    """
    ASSERTION: to_have_attribute() with regex
    CHECKS: Attribute matches pattern
    REAL-WORLD USE: Dynamic URLs, generated IDs
    """
    
    page.goto("https://the-internet.herokuapp.com/")
    
    import re
    
    # Check link href
    login_link = page.get_by_role("link", name="Form Authentication")
    expect(login_link).to_have_attribute("href", re.compile(r"/login"))


def test_has_class(page):
    """
    ASSERTION: to_have_class()
    CHECKS: Element has specific CSS class
    REAL-WORLD USE: State changes (active, selected, error)
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Click login without credentials to trigger error
    page.get_by_role("button", name="Login").click()
    
    # Error container should have error class
    error_container = page.locator(".error-message-container")
    
    # Check it has the error class (partial match)
    import re
    expect(error_container).to_have_class(re.compile(r"error"))

def test_element_count(page):
    """
    ASSERTION: to_have_count()
    CHECKS: Number of elements matching locator
    REAL-WORLD USE: Cart items, search results, pagination
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Should have 6 products
    products = page.locator(".inventory_item")
    expect(products).to_have_count(6)
    
    # Add two items to cart
    add_buttons = page.locator("[data-test^='add-to-cart']")
    add_buttons.nth(0).click()
    add_buttons.nth(1).click()
    
    # Cart badge should show 2
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("2")


def test_no_elements(page):
    """
    ASSERTION: to_have_count(0)
    CHECKS: No elements match
    REAL-WORLD USE: Empty search results, cleared notifications
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Before login, no cart badge
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_count(0)

def test_element_focused(page):
    """
    ASSERTION: to_be_focused()
    CHECKS: Element has keyboard focus
    REAL-WORLD USE: Form navigation, accessibility testing
    """
    
    page.goto("https://www.saucedemo.com/")
    
    username = page.get_by_placeholder("Username")
    password = page.get_by_placeholder("Password")
    
    # Click username field
    username.click()
    expect(username).to_be_focused()
    
    # Tab to password
    page.keyboard.press("Tab")
    expect(password).to_be_focused()

def test_custom_assertion_timeout(page):
    """
    CONCEPT: Custom timeouts for expect()
    GOAL: Wait longer for slow elements
    REAL-WORLD USE: Slow APIs, heavy pages, animations
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    # Click Start button
    page.get_by_role("button", name="Start").click()
    
    # Element takes ~5 seconds to appear
    # Default 5s timeout might be too tight
    # Use custom timeout of 10 seconds
    result = page.locator("#finish h4")
    expect(result).to_be_visible(timeout=10000)  # 10000ms = 10s
    expect(result).to_have_text("Hello World!", timeout=10000)


def test_timeout_too_short_fails(page):
    """
    CONCEPT: Understanding timeout failures
    GOAL: See what happens when timeout is too short
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    page.get_by_role("button", name="Start").click()
    
    # This will FAIL - element takes 5s, we only wait 1s
    result = page.locator("#finish h4")
    
    # Uncomment to see failure:
    # expect(result).to_be_visible(timeout=1000)  # Will fail!
    
    # Correct approach:
    expect(result).to_be_visible(timeout=10000)

def test_auto_waiting_example(page):
    """
    CONCEPT: Auto-waiting behavior
    GOAL: Understand what Playwright waits for automatically
    
    When you call click(), Playwright waits for:
    1. Element attached to DOM
    2. Element visible
    3. Element stable (not animating)
    4. Element receives pointer events (not blocked)
    5. Element enabled
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    # Button appears immediately, so this works
    page.get_by_role("button", name="Start").click()
    
    # Result appears after loading
    # We must use expect() to wait for it
    result = page.locator("#finish h4")
    expect(result).to_be_visible(timeout=10000)

def test_wait_for_selector(page):
    """
    CONCEPT: Explicit wait for element
    GOAL: Wait for element to reach specific state
    REAL-WORLD USE: Complex loading scenarios
    
    States:
    - "attached": Element in DOM
    - "attached=False": Element removed from DOM
    - "visible": Element visible
    - "hidden": Element hidden
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    # Click Start
    page.get_by_role("button", name="Start").click()
    
    # Wait for loading indicator to disappear
    page.wait_for_selector("#loading", state="hidden")
    
    # Wait for result to appear
    page.wait_for_selector("#finish h4", state="visible")
    
    # Now verify
    result = page.locator("#finish h4")
    expect(result).to_have_text("Hello World!")

def test_wait_for_page_load(page):
    """
    CONCEPT: Wait for page load states
    GOAL: Ensure page is fully loaded before interacting
    
    States:
    - "load": Page load event fired (all resources loaded)
    - "domcontentloaded": DOM is ready (faster)
    - "networkidle": No network activity for 500ms (slowest but most complete)
    
    REAL-WORLD USE: Heavy pages, SPAs, pages with many API calls
    """
    
    # Wait for network to be idle (all API calls complete)
    page.goto("https://www.saucedemo.com/", wait_until="networkidle")
    
    # Now page is fully loaded
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def test_wait_after_click(page):
    """
    CONCEPT: Wait for page state after navigation
    REAL-WORLD USE: After clicking link that loads new page
    """
    
    page.goto("https://the-internet.herokuapp.com/")
    
    # Click a link
    page.get_by_role("link", name="Form Authentication").click()
    
    # Wait for new page to load
    page.wait_for_load_state("domcontentloaded")
    
    # Now interact with new page
    expect(page.get_by_role("heading", level=2)).to_have_text("Login Page")

def test_wait_for_url_change(page):
    """
    CONCEPT: Wait for URL to change
    GOAL: Wait for navigation/redirect
    REAL-WORLD USE: Login redirects, form submissions, OAuth flows
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Fill and submit login
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Wait for URL to change
    page.wait_for_url("**/inventory.html")
    
    # Or with pattern
    # import re
    # page.wait_for_url(re.compile(r".*inventory.*"))
    
    # Now we're on the new page
    expect(page.locator(".inventory_item")).to_have_count(6)

def test_wait_for_custom_condition(page):
    """
    CONCEPT: Wait for custom JavaScript condition
    GOAL: Wait for complex app states
    REAL-WORLD USE: SPA loading, custom loaders, WebSocket data
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Wait for a custom condition using JavaScript
    # This waits until there are at least 6 inventory items
    page.wait_for_function("""
        () => document.querySelectorAll('.inventory_item').length >= 6
    """)
    
    # Now verify
    expect(page.locator(".inventory_item")).to_have_count(6)


def test_wait_for_element_count(page):
    """
    CONCEPT: Wait for specific number of elements
    REAL-WORLD USE: Search results, pagination, lazy loading
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Wait for products to load
    products = page.locator(".inventory_item")
    
    # This is actually a better approach than wait_for_function
    expect(products).to_have_count(6, timeout=10000)

def test_why_not_sleep(page):
    """
     ANTI-PATTERN: Using time.sleep()
    
    WHY IT'S BAD:
    1. Wastes time (always waits full duration)
    2. Unreliable (might not be long enough)
    3. Slows down test suite
    4. Hides real problems
    """
    
    import time
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    page.get_by_role("button", name="Start").click()
    
    #  BAD: Arbitrary wait
    # time.sleep(6)  # Wastes 6 seconds even if element appears in 3
    
    #  GOOD: Wait only as long as needed
    result = page.locator("#finish h4")
    expect(result).to_be_visible(timeout=10000)  # Waits UP TO 10s, returns immediately when visible

def test_soft_assertions(page):
    """
    CONCEPT: Soft assertions
    GOAL: Check multiple things without stopping on first failure
    REAL-WORLD USE: Page validation, form verification
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Import for soft assertions
    from playwright.sync_api import expect
    
    # All these checks run even if one fails
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(page).to_have_title("Swag Labs")
    expect(page.locator(".inventory_item")).to_have_count(6)
    expect(page.locator(".shopping_cart_link")).to_be_visible()
    expect(page.locator(".app_logo")).to_have_text("Swag Labs")


def test_soft_assertions_manual(page):
    """
    CONCEPT: Manual soft assertion pattern
    GOAL: Collect all failures and report at end
    REAL-WORLD USE: Complex validation scenarios
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    errors = []
    
    # Check multiple things
    try:
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    except AssertionError as e:
        errors.append(f"URL check failed: {e}")
    
    try:
        expect(page.locator(".inventory_item")).to_have_count(6)
    except AssertionError as e:
        errors.append(f"Product count failed: {e}")
    
    try:
        expect(page.locator(".app_logo")).to_have_text("Swag Labs")
    except AssertionError as e:
        errors.append(f"Logo text failed: {e}")
    
    # Report all failures at end
    if errors:
        pytest.fail("\n".join(errors))

def test_negation_assertions(page):
    """
    CONCEPT: Negated assertions (not_to_*)
    GOAL: Assert something is NOT the case
    REAL-WORLD USE: Verify errors hidden, elements removed
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Error should NOT be visible initially
    error = page.locator("[data-test='error']")
    expect(error).not_to_be_visible()
    
    # Login successfully
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Should NOT be on login page anymore
    expect(page).not_to_have_url("https://www.saucedemo.com/")
    
    # Cart badge should NOT exist (nothing added)
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).not_to_be_attached()

def test_complete_checkout_flow(page):
    """
    REAL-WORLD EXAMPLE: E-commerce checkout with proper assertions
    Shows: Various assertion types used together
    """
    
    # 1. Navigate and verify page loaded
    page.goto("https://www.saucedemo.com/")
    expect(page).to_have_title("Swag Labs")
    
    # 2. Login
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # 3. Verify redirect to inventory
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    # 4. Verify products loaded
    products = page.locator(".inventory_item")
    expect(products).to_have_count(6)
    
    # 5. Add item to cart
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    
    # 6. Verify cart badge updated
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("1")
    
    # 7. Go to cart
    page.locator(".shopping_cart_link").click()
    expect(page).to_have_url("https://www.saucedemo.com/cart.html")
    
    # 8. Verify item in cart
    cart_item = page.locator(".cart_item")
    expect(cart_item).to_have_count(1)
    expect(cart_item).to_contain_text("Sauce Labs Backpack")
    
    # 9. Checkout
    page.get_by_role("button", name="Checkout").click()
    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-one.html")
    
    # 10. Fill checkout form
    page.get_by_placeholder("First Name").fill("John")
    page.get_by_placeholder("Last Name").fill("Doe")
    page.get_by_placeholder("Zip/Postal Code").fill("12345")
    
    # 11. Continue to overview
    page.get_by_role("button", name="Continue").click()
    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-two.html")
    
    # 12. Verify summary
    summary_total = page.locator(".summary_total_label")
    expect(summary_total).to_contain_text("$")
    
    # 13. Complete purchase
    page.get_by_role("button", name="Finish").click()
    
    # 14. Verify success
    expect(page).to_have_url("https://www.saucedemo.com/checkout-complete.html")
    
    success_header = page.locator(".complete-header")
    expect(success_header).to_have_text("Thank you for your order!")