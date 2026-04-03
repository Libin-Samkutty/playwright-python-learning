"""
pages/checkout_page.py
Checkout Page Objects

Handles:
- Checkout step one (information)
- Checkout step two (overview)
- Checkout complete
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from typing import List
import re


class CheckoutPage(BasePage):
    """
    Page Object for Checkout Step One (Information)
    
    URL: https://www.saucedemo.com/checkout-step-one.html
    """
    
    URL = "https://www.saucedemo.com/checkout-step-one.html"
    URL_PATTERN = r".*checkout-step-one\.html$"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    @property
    def first_name_input(self):
        """First name input"""
        return self.page.get_by_placeholder("First Name")
    
    @property
    def last_name_input(self):
        """Last name input"""
        return self.page.get_by_placeholder("Last Name")
    
    @property
    def postal_code_input(self):
        """Postal code input"""
        return self.page.get_by_placeholder("Zip/Postal Code")
    
    @property
    def continue_button(self):
        """Continue button"""
        return self.page.get_by_role("button", name="Continue")
    
    @property
    def cancel_button(self):
        """Cancel button"""
        return self.page.get_by_role("button", name="Cancel")
    
    @property
    def error_message(self):
        """Error message"""
        return self.page.locator("[data-test='error']")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def enter_first_name(self, name: str) -> "CheckoutPage":
        """Enter first name"""
        self.first_name_input.fill(name)
        return self
    
    def enter_last_name(self, name: str) -> "CheckoutPage":
        """Enter last name"""
        self.last_name_input.fill(name)
        return self
    
    def enter_postal_code(self, code: str) -> "CheckoutPage":
        """Enter postal code"""
        self.postal_code_input.fill(code)
        return self
    
    def fill_information(
        self, 
        first_name: str, 
        last_name: str, 
        postal_code: str
    ) -> "CheckoutPage":
        """
        Fill all checkout information fields
        
        Args:
            first_name: First name
            last_name: Last name
            postal_code: Postal/ZIP code
        
        Returns:
            Self for method chaining
        
        Example:
            checkout.fill_information("John", "Doe", "12345")
        """
        self.enter_first_name(first_name)
        self.enter_last_name(last_name)
        self.enter_postal_code(postal_code)
        return self
    
    def click_continue(self) -> "CheckoutPage":
        """Click Continue button"""
        self.continue_button.click()
        return self
    
    def click_cancel(self) -> "CheckoutPage":
        """Click Cancel button"""
        self.cancel_button.click()
        return self
    
    def submit(self) -> "CheckoutPage":
        """Fill and submit checkout form"""
        self.click_continue()
        return self
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def is_loaded(self) -> bool:
        """Check if checkout page is loaded"""
        try:
            expect(self.first_name_input).to_be_visible(timeout=5000)
            return True
        except AssertionError:
            return False
    
    def has_error(self) -> bool:
        """Check if error message is displayed"""
        return self.error_message.is_visible()
    
    def get_error_message(self) -> str:
        """Get error message text"""
        if self.has_error():
            return self.error_message.text_content() or ""
        return ""
    
    def verify_error_message(self, expected: str) -> "CheckoutPage":
        """Verify error message contains expected text"""
        expect(self.error_message).to_be_visible()
        expect(self.error_message).to_contain_text(expected)
        return self


class CheckoutStepTwoPage(BasePage):
    """
    Page Object for Checkout Step Two (Overview)
    
    URL: https://www.saucedemo.com/checkout-step-two.html
    """
    
    URL = "https://www.saucedemo.com/checkout-step-two.html"
    URL_PATTERN = r".*checkout-step-two\.html$"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    @property
    def cart_items(self):
        """Items in summary"""
        return self.page.locator(".cart_item")
    
    @property
    def item_names(self):
        """Item names"""
        return self.page.locator(".inventory_item_name")
    
    @property
    def item_prices(self):
        """Item prices"""
        return self.page.locator(".inventory_item_price")
    
    @property
    def subtotal_label(self):
        """Subtotal"""
        return self.page.locator(".summary_subtotal_label")
    
    @property
    def tax_label(self):
        """Tax"""
        return self.page.locator(".summary_tax_label")
    
    @property
    def total_label(self):
        """Total"""
        return self.page.locator(".summary_total_label")
    
    @property
    def finish_button(self):
        """Finish button"""
        return self.page.get_by_role("button", name="Finish")
    
    @property
    def cancel_button(self):
        """Cancel button"""
        return self.page.get_by_role("button", name="Cancel")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def click_finish(self) -> "CheckoutStepTwoPage":
        """Click Finish button"""
        self.finish_button.click()
        return self
    
    def click_cancel(self) -> "CheckoutStepTwoPage":
        """Click Cancel button"""
        self.cancel_button.click()
        return self
    
    def complete_purchase(self) -> "CheckoutStepTwoPage":
        """Complete the purchase"""
        return self.click_finish()
    
    # ============================================================
    # GETTERS
    # ============================================================
    
    def get_item_count(self) -> int:
        """Get number of items"""
        return self.cart_items.count()
    
    def get_item_names(self) -> List[str]:
        """Get all item names"""
        return self.item_names.all_text_contents()
    
    def get_subtotal(self) -> float:
        """
        Get subtotal amount
        
        Returns:
            Subtotal as float
        """
        text = self.subtotal_label.text_content() or ""
        match = re.search(r"\$(\d+\.\d{2})", text)
        return float(match.group(1)) if match else 0.0
    
    def get_tax(self) -> float:
        """Get tax amount"""
        text = self.tax_label.text_content() or ""
        match = re.search(r"\$(\d+\.\d{2})", text)
        return float(match.group(1)) if match else 0.0
    
    def get_total(self) -> float:
        """Get total amount"""
        text = self.total_label.text_content() or ""
        match = re.search(r"\$(\d+\.\d{2})", text)
        return float(match.group(1)) if match else 0.0
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def is_loaded(self) -> bool:
        """Check if page is loaded"""
        try:
            expect(self.finish_button).to_be_visible(timeout=5000)
            return True
        except AssertionError:
            return False
    
    def verify_item_count(self, expected: int) -> "CheckoutStepTwoPage":
        """Verify number of items"""
        expect(self.cart_items).to_have_count(expected)
        return self
    
    def verify_total_calculation(self) -> "CheckoutStepTwoPage":
        """Verify total = subtotal + tax"""
        subtotal = self.get_subtotal()
        tax = self.get_tax()
        total = self.get_total()
        
        expected_total = round(subtotal + tax, 2)
        assert total == expected_total, \
            f"Total {total} != subtotal {subtotal} + tax {tax}"
        return self


class CheckoutCompletePage(BasePage):
    """
    Page Object for Checkout Complete Page
    
    URL: https://www.saucedemo.com/checkout-complete.html
    """
    
    URL = "https://www.saucedemo.com/checkout-complete.html"
    URL_PATTERN = r".*checkout-complete\.html$"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    @property
    def complete_header(self):
        """Success header"""
        return self.page.locator(".complete-header")
    
    @property
    def complete_text(self):
        """Success message text"""
        return self.page.locator(".complete-text")
    
    @property
    def pony_express_image(self):
        """Pony express success image"""
        return self.page.locator(".pony_express")
    
    @property
    def back_home_button(self):
        """Back Home button"""
        return self.page.get_by_role("button", name="Back Home")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def click_back_home(self) -> "CheckoutCompletePage":
        """Click Back Home button"""
        self.back_home_button.click()
        return self
    
    # ============================================================
    # GETTERS
    # ============================================================
    
    def get_header_text(self) -> str:
        """Get success header text"""
        return self.complete_header.text_content() or ""
    
    def get_complete_text(self) -> str:
        """Get complete message text"""
        return self.complete_text.text_content() or ""
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def is_loaded(self) -> bool:
        """Check if page is loaded"""
        try:
            expect(self.complete_header).to_be_visible(timeout=5000)
            return True
        except AssertionError:
            return False
    
    def verify_order_complete(self) -> "CheckoutCompletePage":
        """Verify order was completed successfully"""
        expect(self.complete_header).to_have_text("Thank you for your order!")
        return self
    
    def verify_success_image_visible(self) -> "CheckoutCompletePage":
        """Verify success image is displayed"""
        expect(self.pony_express_image).to_be_visible()
        return self
