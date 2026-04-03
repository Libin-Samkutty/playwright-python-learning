"""
tests/debug/test_with_logging.py
Debugging with detailed logging
"""

import logging
from playwright.sync_api import expect

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_with_detailed_logging(page):
    """
    Test with extensive logging for debugging
    """
    
    logger.info("Starting test: test_with_detailed_logging")
    
    # Navigation
    logger.debug("Navigating to SauceDemo...")
    page.goto("https://www.saucedemo.com/")
    logger.info(f"Current URL: {page.url}")
    logger.info(f"Page title: {page.title()}")
    
    # Login
    logger.debug("Filling username...")
    username_field = page.get_by_placeholder("Username")
    logger.debug(f"Username field visible: {username_field.is_visible()}")
    username_field.fill("standard_user")
    
    logger.debug("Filling password...")
    password_field = page.get_by_placeholder("Password")
    password_field.fill("secret_sauce")
    
    logger.debug("Clicking login button...")
    login_button = page.get_by_role("button", name="Login")
    logger.debug(f"Login button enabled: {login_button.is_enabled()}")
    login_button.click()
    
    # Verify
    logger.info(f"After login URL: {page.url}")
    
    products = page.locator(".inventory_item")
    product_count = products.count()
    logger.info(f"Products found: {product_count}")
    
    if product_count > 0:
        logger.debug("Getting product names...")
        for i in range(min(product_count, 3)):  # Log first 3
            name = products.nth(i).locator(".inventory_item_name").text_content()
            logger.debug(f"  Product {i+1}: {name}")
    
    logger.info("Test completed successfully")


class DebugHelper:
    """
    Helper class for debug logging
    """
    
    def __init__(self, page, logger=None):
        self.page = page
        self.logger = logger or logging.getLogger(__name__)
        self.step_counter = 0
    
    def log_step(self, description: str):
        """Log a test step"""
        self.step_counter += 1
        self.logger.info(f"Step {self.step_counter}: {description}")
    
    def log_page_state(self):
        """Log current page state"""
        self.logger.info(f"  URL: {self.page.url}")
        self.logger.info(f"  Title: {self.page.title()}")
    
    def log_element_state(self, locator, name: str):
        """Log element state"""
        try:
            visible = locator.is_visible()
            enabled = locator.is_enabled() if visible else False
            self.logger.debug(f"  {name}: visible={visible}, enabled={enabled}")
        except Exception as e:
            self.logger.warning(f"  {name}: Error getting state - {e}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error with context"""
        self.logger.error(f"Error in {context}: {error}")
        self.log_page_state()
        
        # Take screenshot
        try:
            path = f"screenshots/error_{self.step_counter}.png"
            self.page.screenshot(path=path)
            self.logger.info(f"  Screenshot saved: {path}")
        except Exception:
            pass


def test_with_debug_helper(page):
    """
    Test using DebugHelper for structured logging
    """
    
    debug = DebugHelper(page)
    
    try:
        debug.log_step("Navigate to SauceDemo")
        page.goto("https://www.saucedemo.com/")
        debug.log_page_state()
        
        debug.log_step("Fill login form")
        username = page.get_by_placeholder("Username")
        password = page.get_by_placeholder("Password")
        debug.log_element_state(username, "username_field")
        debug.log_element_state(password, "password_field")
        
        username.fill("standard_user")
        password.fill("secret_sauce")
        
        debug.log_step("Submit login")
        login_button = page.get_by_role("button", name="Login")
        debug.log_element_state(login_button, "login_button")
        login_button.click()
        
        debug.log_step("Verify login success")
        debug.log_page_state()
        expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
        
    except Exception as e:
        debug.log_error(e, "test_with_debug_helper")
        raise
