"""
CONCEPT: Handling Dynamic Elements
GOAL: Master waiting strategies for unreliable UI
REAL-WORLD USE: SPAs, AJAX-heavy sites, modern web apps
"""

from playwright.sync_api import expect, TimeoutError as PlaywrightTimeout
import pytest

# Tests will be added as we learn each pattern
def test_element_appears_after_delay(page):
    """
    SCENARIO: Element appears after clicking a button
    PATTERN: Use expect().to_be_visible() with timeout
    REAL-WORLD USE: Loading content, search results, form submissions
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    # Element exists in DOM but is hidden
    hidden_element = page.locator("#finish h4")
    expect(hidden_element).to_be_hidden()
    
    # Click Start button
    page.get_by_role("button", name="Start").click()
    
    # Wait for element to become visible (up to 10 seconds)
    expect(hidden_element).to_be_visible(timeout=10000)
    
    # Verify content
    expect(hidden_element).to_have_text("Hello World!")


def test_element_added_to_dom_after_delay(page):
    """
    SCENARIO: Element doesn't exist initially, added later
    PATTERN: Use expect().to_be_attached() then to_be_visible()
    REAL-WORLD USE: Dynamic content injection, lazy loading
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/2")
    
    # Element does NOT exist in DOM initially
    dynamic_element = page.locator("#finish h4")
    expect(dynamic_element).to_have_count(0)
    
    # Click Start
    page.get_by_role("button", name="Start").click()
    
    # Wait for element to be added to DOM AND become visible
    expect(dynamic_element).to_be_visible(timeout=10000)
    expect(dynamic_element).to_have_text("Hello World!")


def test_wait_for_specific_text(page):
    """
    SCENARIO: Element exists but text changes
    PATTERN: Use expect().to_have_text() or to_contain_text()
    REAL-WORLD USE: Status updates, async operations
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    # Start loading
    page.get_by_role("button", name="Start").click()
    
    # Wait for specific text to appear
    result = page.locator("#finish h4")
    expect(result).to_have_text("Hello World!", timeout=10000)

def test_wait_for_loading_spinner_to_disappear(page):
    """
    SCENARIO: Loading spinner blocks interaction
    PATTERN: Wait for spinner to be hidden before proceeding
    REAL-WORLD USE: Any page with loading indicators
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    # Click Start
    page.get_by_role("button", name="Start").click()
    
    # Wait for loading indicator to disappear
    loading_indicator = page.locator("#loading")
    expect(loading_indicator).to_be_visible()  # Confirm loading started
    expect(loading_indicator).to_be_hidden(timeout=10000)  # Wait for it to finish
    
    # Now the content should be visible
    result = page.locator("#finish h4")
    expect(result).to_be_visible()


def test_wait_for_loading_complete(page):
    """
    SCENARIO: Multiple loading indicators
    PATTERN: Wait for ALL loading to complete
    REAL-WORLD USE: Dashboard with multiple data sources
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    page.get_by_role("button", name="Start").click()
    
    # Wait for loading to disappear AND result to appear
    # This is more reliable than waiting for just one
    loading = page.locator("#loading")
    result = page.locator("#finish")
    
    # Approach 1: Wait for loading to hide
    expect(loading).to_be_hidden(timeout=10000)
    
    # Approach 2: Wait for result to show (often better)
    expect(result).to_be_visible()


def test_generic_loading_spinner_pattern(page):
    """
    PATTERN: Reusable loading wait function
    REAL-WORLD USE: Use across all tests
    """
    
    def wait_for_loading_complete(page, timeout=10000):
        """
        Waits for common loading indicators to disappear.
        Add selectors for your app's specific loaders.
        """
        
        # Common loading indicator selectors
        loading_selectors = [
            ".loading",
            ".spinner",
            ".loader",
            "[data-loading='true']",
            "#loading",
            ".skeleton",  # Skeleton screens
        ]
        
        for selector in loading_selectors:
            loader = page.locator(selector)
            # Only wait if the loader exists
            if loader.count() > 0:
                expect(loader).to_be_hidden(timeout=timeout)
    
    # Usage
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    page.get_by_role("button", name="Start").click()
    
    wait_for_loading_complete(page)
    
    expect(page.locator("#finish h4")).to_be_visible()

def test_element_disappears(page):
    """
    SCENARIO: Element should disappear after action
    PATTERN: Use expect().to_be_hidden() or not_to_be_visible()
    REAL-WORLD USE: Toast notifications, modals, temporary messages
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_controls")
    
    # Checkbox exists initially
    checkbox = page.locator("#checkbox")
    expect(checkbox).to_be_visible()
    
    # Click Remove button
    page.get_by_role("button", name="Remove").click()
    
    # Wait for checkbox to disappear
    expect(checkbox).to_be_hidden(timeout=10000)
    
    # Verify removal message
    message = page.locator("#message")
    expect(message).to_have_text("It's gone!")


def test_element_detached_from_dom(page):
    """
    SCENARIO: Element completely removed from DOM
    PATTERN: Use to_be_detached() or to_have_count(0)
    
    DIFFERENCE:
    - to_be_hidden(): Element in DOM but not visible
    - to_be_attached(attached=False): Element removed from DOM entirely
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_controls")
    
    checkbox = page.locator("#checkbox")
    
    # Remove the checkbox
    page.get_by_role("button", name="Remove").click()
    
    # Wait for complete removal from DOM
    expect(checkbox).to_be_attached(attached=False,timeout=10000)
    
    # Alternative: check count is 0
    # expect(checkbox).to_have_count(0, timeout=10000)


def test_toast_notification_disappears(page):
    """
    SCENARIO: Toast notification auto-dismisses
    PATTERN: Wait for appearance, then disappearance
    REAL-WORLD USE: Success/error toasts
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Login successfully
    page.get_by_label("Username").fill("tomsmith")
    page.get_by_label("Password").fill("SuperSecretPassword!")
    page.get_by_role("button", name="Login").click()
    
    # Flash message appears
    flash = page.locator(".flash")
    expect(flash).to_be_visible()
    expect(flash).to_contain_text("You logged into")
    
    # If the flash auto-dismisses, wait for it
    # (This particular site doesn't auto-dismiss, but here's the pattern)
    # expect(flash).to_be_hidden(timeout=5000)

def test_add_elements_dynamically(page):
    """
    SCENARIO: Elements added to page on demand
    PATTERN: Wait for count to change
    REAL-WORLD USE: Adding items to cart, todo lists
    """
    
    page.goto("https://the-internet.herokuapp.com/add_remove_elements/")
    
    # Initially no Delete buttons
    delete_buttons = page.locator(".added-manually")
    expect(delete_buttons).to_have_count(0)
    
    # Add 3 elements
    add_button = page.get_by_role("button", name="Add Element")
    add_button.click()
    add_button.click()
    add_button.click()
    
    # Verify 3 elements exist
    expect(delete_buttons).to_have_count(3)


def test_remove_elements_dynamically(page):
    """
    SCENARIO: Elements removed from page
    PATTERN: Wait for count to decrease
    REAL-WORLD USE: Cart removal, delete actions
    """
    
    page.goto("https://the-internet.herokuapp.com/add_remove_elements/")
    
    # Add 3 elements
    add_button = page.get_by_role("button", name="Add Element")
    for _ in range(3):
        add_button.click()
    
    delete_buttons = page.locator(".added-manually")
    expect(delete_buttons).to_have_count(3)
    
    # Remove first element
    delete_buttons.first.click()
    expect(delete_buttons).to_have_count(2)
    
    # Remove all remaining
    while delete_buttons.count() > 0:
        delete_buttons.first.click()
    
    expect(delete_buttons).to_have_count(0)


def test_cart_item_count_changes(page):
    """
    REAL-WORLD EXAMPLE: Shopping cart count
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Initially no cart badge (count = 0)
    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_count(0)
    
    # Add first item
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    
    # Badge should appear with count 1
    expect(cart_badge).to_be_visible()
    expect(cart_badge).to_have_text("1")
    
    # Add second item
    page.locator("[data-test='add-to-cart-sauce-labs-bike-light']").click()
    
    # Badge should show 2
    expect(cart_badge).to_have_text("2")
    
    # Remove first item
    page.locator("[data-test='remove-sauce-labs-backpack']").click()
    
    # Badge should show 1
    expect(cart_badge).to_have_text("1")

def test_wait_for_animation_to_complete(page):
    """
    SCENARIO: Element animates before becoming interactive
    PATTERN: Use force=True or wait for stability
    REAL-WORLD USE: Modals, accordions, slide-ins
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_controls")
    
    # Input is initially disabled
    text_input = page.locator("#input-example input")
    expect(text_input).to_be_disabled()
    
    # Click Enable
    page.get_by_role("button", name="Enable").click()
    
    # Wait for input to be enabled (animation may occur)
    expect(text_input).to_be_enabled(timeout=10000)
    
    # Now we can interact
    text_input.fill("Hello World")
    expect(text_input).to_have_value("Hello World")


def test_force_click_during_animation(page):
    """
    SCENARIO: Need to click during animation
    PATTERN: Use force=True (use sparingly!)
    
     WARNING: force=True bypasses actionability checks
    Only use when you KNOW the element should be clickable
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Sometimes elements are briefly covered during transitions
    # force=True clicks even if element is "not ready"
    
    add_button = page.locator("[data-test='add-to-cart-sauce-labs-backpack']")
    
    # Normal click (recommended)
    add_button.click()
    
    # Force click (use only when necessary)
    # add_button.click(force=True)


def test_disable_animations_for_stability(page, browser):
    """
    PATTERN: Disable CSS animations for faster, more stable tests
    REAL-WORLD USE: CI/CD environments, speed optimization
    """
    
    # Create context with reduced motion preference
    context = browser.new_context(
        reduced_motion="reduce"
    )
    
    test_page = context.new_page()
    
    try:
        test_page.goto("https://www.saucedemo.com/")
        
        # Alternatively, inject CSS to disable animations
        test_page.add_style_tag(content="""
            *, *::before, *::after {
                animation-duration: 0s !important;
                animation-delay: 0s !important;
                transition-duration: 0s !important;
                transition-delay: 0s !important;
            }
        """)
        
        # Now interactions are faster and more stable
        test_page.get_by_placeholder("Username").fill("standard_user")
        test_page.get_by_placeholder("Password").fill("secret_sauce")
        test_page.get_by_role("button", name="Login").click()
        
        expect(test_page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    finally:
        context.close()

def test_wait_for_network_idle(page):
    """
    SCENARIO: Page makes multiple API calls
    PATTERN: Wait for network to be idle
    REAL-WORLD USE: SPAs, dashboards with data loading
    """
    
    # Navigate and wait for network to settle
    page.goto(
        "https://www.saucedemo.com/",
        wait_until="networkidle"  # Wait for no network activity for 500ms
    )
    
    # Page is fully loaded including all API calls
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def test_wait_for_specific_api_call(page):
    """
    SCENARIO: Wait for specific API response before proceeding
    PATTERN: Use expect_response() or wait_for_response()
    REAL-WORLD USE: Form submissions, data loading
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    
    # Wait for any response that matches pattern
    # Note: SauceDemo doesn't have API calls, this is pattern demonstration
    
    # with page.expect_response("**/api/login") as response_info:
    #     page.get_by_role("button", name="Login").click()
    # 
    # response = response_info.value
    # assert response.ok
    
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")


def test_wait_for_request_to_complete(page):
    """
    PATTERN: Wait for request to be made
    REAL-WORLD USE: Analytics tracking, form submissions
    """
    
    # Pattern:
    # with page.expect_request("**/api/analytics") as request_info:
    #     page.get_by_role("button", name="Track").click()
    # 
    # request = request_info.value
    # assert "event=click" in request.url
    
    pass  # Pattern demonstration


def test_wait_for_load_state_after_action(page):
    """
    SCENARIO: Action triggers page reload or heavy loading
    PATTERN: Use wait_for_load_state()
    REAL-WORLD USE: Form submissions, navigation
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    page.get_by_label("Username").fill("tomsmith")
    page.get_by_label("Password").fill("SuperSecretPassword!")
    page.get_by_role("button", name="Login").click()
    
    # Wait for navigation to complete
    page.wait_for_load_state("domcontentloaded")
    
    # Or wait for all resources
    # page.wait_for_load_state("load")
    
    # Or wait for network idle
    # page.wait_for_load_state("networkidle")
    
    expect(page).to_have_url("https://the-internet.herokuapp.com/secure")

def test_avoid_stale_elements(page):
    """
    SCENARIO: Element is re-rendered after action
    PATTERN: Re-query elements after actions that modify DOM
    REAL-WORLD USE: SPA frameworks that re-render components
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Get all products
    products = page.locator(".inventory_item")
    
    # Sort changes the DOM (products might be re-rendered)
    page.locator("[data-test='product-sort-container']").select_option(
        label="Price (low to high)"
    )
    
    #  BAD: Using old reference after DOM changed
    # first_product = products.first  # Might be stale!
    
    #  GOOD: Re-query after DOM change
    products = page.locator(".inventory_item")
    first_product = products.first
    
    # Verify first product is cheapest
    price = first_product.locator(".inventory_item_price")
    expect(price).to_have_text("$7.99")


def test_playwright_handles_staleness(page):
    """
    GOOD NEWS: Playwright handles most staleness automatically!
    
    Unlike Selenium, Playwright locators are "lazy" -
    they re-query on each action.
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # This locator doesn't query immediately
    first_product_price = page.locator(".inventory_item_price").first
    
    # Change sort
    page.locator("[data-test='product-sort-container']").select_option(
        label="Price (high to low)"
    )
    
    # This works! Playwright re-queries automatically
    expect(first_product_price).to_have_text("$49.99")

def test_infinite_scroll(page):
    """
    SCENARIO: Content loads as user scrolls
    PATTERN: Scroll, wait for new content, repeat
    REAL-WORLD USE: Social feeds, product listings
    
    NOTE: Using a pattern since the-internet doesn't have infinite scroll
    """
    
    page.goto("https://the-internet.herokuapp.com/infinite_scroll")
    
    # Get initial paragraph count
    paragraphs = page.locator(".jscroll-added")
    initial_count = paragraphs.count()
    
    # Scroll to bottom
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    
    # Wait for new content to load
    # Option 1: Wait for count to increase
    page.wait_for_function(
        f"document.querySelectorAll('.jscroll-added').length > {initial_count}"
    )
    
    # Option 2: Wait for specific element
    # expect(paragraphs).to_have_count(initial_count + 1, timeout=5000)
    
    # Verify more content loaded
    new_count = paragraphs.count()
    assert new_count > initial_count


def test_scroll_until_element_found(page):
    """
    PATTERN: Scroll until specific element is visible
    REAL-WORLD USE: Finding item in long list
    """
    
    page.goto("https://the-internet.herokuapp.com/infinite_scroll")
    
    def scroll_until_count(target_count, max_scrolls=10):
        """Scroll until we have enough paragraphs"""
        
        for _ in range(max_scrolls):
            paragraphs = page.locator(".jscroll-added")
            current_count = paragraphs.count()
            
            if current_count >= target_count:
                return True
            
            # Scroll down
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait a bit for content to load
            page.wait_for_timeout(500)
        
        return False
    
    # Scroll until we have at least 5 paragraphs
    success = scroll_until_count(5)
    assert success, "Could not load enough content"


def test_lazy_loaded_images(page):
    """
    SCENARIO: Images load as they enter viewport
    PATTERN: Scroll element into view, verify loaded
    REAL-WORLD USE: Image galleries, product images
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Get all product images
    images = page.locator(".inventory_item_img")
    
    # Scroll each into view and verify loaded
    for i in range(images.count()):
        image = images.nth(i)
        
        # Scroll into view
        image.scroll_into_view_if_needed()
        
        # Verify visible
        expect(image).to_be_visible()

def test_wait_for_custom_javascript_condition(page):
    """
    PATTERN: Wait for arbitrary JavaScript condition
    REAL-WORLD USE: Complex app states, custom loaders
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Wait for custom condition
    page.wait_for_function("""
        () => {
            const items = document.querySelectorAll('.inventory_item');
            return items.length === 6;
        }
    """)
    
    # Verify
    expect(page.locator(".inventory_item")).to_have_count(6)


def test_wait_for_element_with_specific_style(page):
    """
    PATTERN: Wait for CSS property to change
    REAL-WORLD USE: Animations, visibility transitions
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    page.get_by_role("button", name="Start").click()
    
    # Wait for element to have specific style (display: block)
    page.wait_for_function("""
        () => {
            const el = document.querySelector('#finish');
            if (!el) return false;
            const style = window.getComputedStyle(el);
            return style.display !== 'none';
        }
    """)
    
    expect(page.locator("#finish h4")).to_be_visible()


def test_wait_for_text_to_change(page):
    """
    PATTERN: Wait for element text to change
    REAL-WORLD USE: Counters, live updates, status changes
    """
    
    page.goto("https://the-internet.herokuapp.com/dynamic_controls")
    
    # Get initial message (if any)
    message = page.locator("#message")
    
    # Click Enable
    page.get_by_role("button", name="Enable").click()
    
    # Wait for message to appear with specific text
    expect(message).to_have_text("It's enabled!", timeout=10000)


def test_polling_for_condition(page):
    """
    PATTERN: Poll until condition is met
    REAL-WORLD USE: External process completion, async operations
    """
    
    import time
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    def poll_until(condition_fn, timeout=10, interval=0.5):
        """
        Poll until condition function returns True
        
        Args:
            condition_fn: Function that returns True when condition is met
            timeout: Maximum seconds to wait
            interval: Seconds between checks
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if condition_fn():
                    return True
            except Exception:
                pass
            
            time.sleep(interval)
        
        raise TimeoutError(f"Condition not met within {timeout} seconds")
    
    # Usage
    products = page.locator(".inventory_item")
    poll_until(lambda: products.count() == 6)
    
    expect(products).to_have_count(6)

def test_retry_on_failure(page):
    """
    PATTERN: Retry action on failure
    REAL-WORLD USE: Flaky buttons, network hiccups
    
     NOTE: This should be a last resort!
    First, try to fix the root cause of flakiness.
    """
    
    def retry_click(locator, max_attempts=3):
        """Retry clicking an element"""
        
        for attempt in range(max_attempts):
            try:
                locator.click(timeout=5000)
                return True
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e
                print(f"Attempt {attempt + 1} failed, retrying...")
        
        return False
    
    page.goto("https://www.saucedemo.com/")
    
    # Fill form
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    
    # Retry click on login button
    login_button = page.get_by_role("button", name="Login")
    retry_click(login_button)
    
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")


def test_retry_with_decorator(page):
    """
    PATTERN: Use decorator for retry logic
    REAL-WORLD USE: Clean, reusable retry mechanism
    """
    
    import functools
    import time
    
    def retry(max_attempts=3, delay=1):
        """Decorator to retry a function on failure"""
        
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            time.sleep(delay)
                
                raise last_exception
            
            return wrapper
        
        return decorator
    
    @retry(max_attempts=3, delay=0.5)
    def add_item_to_cart(page, item_name):
        """Add item to cart with retry"""
        add_button = page.locator(f"[data-test='add-to-cart-{item_name}']")
        add_button.click()
    
    # Usage
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    add_item_to_cart(page, "sauce-labs-backpack")
    
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")


def test_conditional_wait(page):
    """
    PATTERN: Wait only if condition exists
    REAL-WORLD USE: Optional loading indicators, A/B tests
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    def wait_if_loading(page, timeout=5000):
        """Wait for loading only if loading indicator exists"""
        
        loading = page.locator(".loading-indicator")
        
        # Only wait if loading indicator is present
        if loading.count() > 0:
            try:
                expect(loading).to_be_hidden(timeout=timeout)
            except Exception:
                pass  # Loading indicator might have disappeared already
    
    wait_if_loading(page)
    
    expect(page.locator(".inventory_item")).to_have_count(6)

def test_with_wait_helper(page, wait_helper):
    """
    Using the wait helper utility
    """
    
    if wait_helper is None:
        pytest.skip("WaitHelper not available")
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Use helper methods
    wait_helper.wait_for_loading_complete()
    wait_helper.wait_for_url_contains("inventory")
    
    products = page.locator(".inventory_item")
    wait_helper.wait_for_element_count(products, 6)
    
    expect(products).to_have_count(6)
