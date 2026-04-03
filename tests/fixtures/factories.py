"""
tests/fixtures/factories.py
Fixture factory patterns
"""

import pytest
from playwright.sync_api import expect


@pytest.fixture
def create_browser_context(browser_instance):
    """
    FACTORY: Create browser contexts with custom settings
    
    RETURNS: Function that creates contexts
    
    USE CASE:
    - Tests need different viewport sizes
    - Tests need different locales
    - Tests need different permissions
    """
    
    created_contexts = []  # Track for cleanup
    
    def _create_context(
        viewport_width=1280,
        viewport_height=720,
        locale="en-US",
        timezone_id="America/New_York",
        permissions=None,
        geolocation=None,
    ):
        """
        Create a browser context with custom settings
        
        Args:
            viewport_width: Browser width
            viewport_height: Browser height
            locale: Language/locale setting
            timezone_id: Timezone
            permissions: List of permissions to grant
            geolocation: Geolocation coordinates
        
        Returns:
            Browser context
        """
        
        context_options = {
            "viewport": {"width": viewport_width, "height": viewport_height},
            "locale": locale,
            "timezone_id": timezone_id,
        }
        
        if permissions:
            context_options["permissions"] = permissions
        
        if geolocation:
            context_options["geolocation"] = geolocation
            context_options["permissions"] = context_options.get(
                "permissions", []
            ) + ["geolocation"]
        
        context = browser_instance.new_context(**context_options)
        created_contexts.append(context)
        
        return context
    
    yield _create_context
    
    # Cleanup: Close all created contexts
    for context in created_contexts:
        context.close()


@pytest.fixture
def create_page(create_browser_context):
    """
    FACTORY: Create pages with custom context settings
    
    Builds on context factory
    """
    
    def _create_page(**context_options):
        """
        Create a page with custom context settings
        
        Returns:
            Page object
        """
        
        context = create_browser_context(**context_options)
        page = context.new_page()
        
        return page
    
    return _create_page


@pytest.fixture
def create_authenticated_page(create_page, test_data):
    """
    FACTORY: Create authenticated pages for different users
    
    USE CASE:
    - Test with different user roles
    - Test user-specific behavior
    """
    
    def _create_authenticated_page(
        user_type="standard",
        **context_options
    ):
        """
        Create a page logged in as specified user
        
        Args:
            user_type: "standard", "locked", "problem", "performance"
            **context_options: Passed to context factory
        
        Returns:
            Logged-in page
        """
        
        page = create_page(**context_options)
        user = test_data["users"][user_type]
        base_url = test_data["urls"]["base"]
        
        page.goto(base_url)
        page.get_by_placeholder("Username").fill(user["username"])
        page.get_by_placeholder("Password").fill(user["password"])
        page.get_by_role("button", name="Login").click()
        
        # Wait for login (with extended timeout for performance user)
        timeout = 15000 if user_type == "performance" else 5000
        page.wait_for_url("**/inventory.html", timeout=timeout)
        
        return page
    
    return _create_authenticated_page


@pytest.fixture
def create_cart_with_items(create_authenticated_page, test_data):
    """
    FACTORY: Create page with specific items in cart
    
    USE CASE:
    - Test checkout with different item combinations
    - Test cart totals
    """
    
    def _create_cart_with_items(
        item_ids: list,
        user_type="standard",
    ):
        """
        Create page with specific items in cart
        
        Args:
            item_ids: List of product IDs to add
            user_type: User to login as
        
        Returns:
            Page with items in cart
        """
        
        page = create_authenticated_page(user_type=user_type)
        
        for item_id in item_ids:
            add_button = page.locator(f"[data-test='add-to-cart-{item_id}']")
            add_button.click()
        
        # Verify cart count
        expected_count = len(item_ids)
        if expected_count > 0:
            expect(page.locator(".shopping_cart_badge")).to_have_text(
                str(expected_count)
            )
        
        return page
    
    return _create_cart_with_items
