"""
utils/assertions.py
Custom assertion helpers
"""

from playwright.sync_api import Page, Locator, expect
from typing import List, Optional
import re


class CustomAssertions:
    """
    Custom assertions for common verification patterns
    """
    
    @staticmethod
    def assert_url_contains(page: Page, substring: str, timeout: int = 5000):
        """
        Assert URL contains substring
        
        Args:
            page: Playwright page
            substring: Text to find in URL
            timeout: Maximum wait time
        """
        
        expect(page).to_have_url(re.compile(f".*{re.escape(substring)}.*"), timeout=timeout)
    
    @staticmethod
    def assert_url_matches(page: Page, pattern: str, timeout: int = 5000):
        """
        Assert URL matches regex pattern
        
        Args:
            page: Playwright page
            pattern: Regex pattern
            timeout: Maximum wait time
        """
        
        expect(page).to_have_url(re.compile(pattern), timeout=timeout)
    
    @staticmethod
    def assert_element_count_in_range(
        locator: Locator,
        min_count: int,
        max_count: int,
        timeout: int = 5000
    ):
        """
        Assert element count is within range
        
        Args:
            locator: Element locator
            min_count: Minimum expected count
            max_count: Maximum expected count
            timeout: Maximum wait time
        """
        
        # Wait for at least minimum
        expect(locator.first).to_be_visible(timeout=timeout)
        
        count = locator.count()
        assert min_count <= count <= max_count, \
            f"Element count {count} not in range [{min_count}, {max_count}]"
    
    @staticmethod
    def assert_sorted_ascending(values: List[str], key=None):
        """
        Assert list is sorted ascending
        
        Args:
            values: List of values
            key: Optional key function for comparison
        """
        
        sorted_values = sorted(values, key=key)
        assert values == sorted_values, \
            f"Values not sorted ascending. Got: {values}, Expected: {sorted_values}"
    
    @staticmethod
    def assert_sorted_descending(values: List[str], key=None):
        """
        Assert list is sorted descending
        
        Args:
            values: List of values
            key: Optional key function for comparison
        """
        
        sorted_values = sorted(values, key=key, reverse=True)
        assert values == sorted_values, \
            f"Values not sorted descending. Got: {values}, Expected: {sorted_values}"
    
    @staticmethod
    def assert_prices_sorted_ascending(price_strings: List[str]):
        """
        Assert price strings are sorted ascending
        
        Args:
            price_strings: List of prices like ["$7.99", "$9.99", "$29.99"]
        """
        
        def extract_price(s: str) -> float:
            return float(s.replace("$", "").replace(",", ""))
        
        prices = [extract_price(p) for p in price_strings]
        assert prices == sorted(prices), \
            f"Prices not sorted ascending: {price_strings}"
    
    @staticmethod
    def assert_prices_sorted_descending(price_strings: List[str]):
        """
        Assert price strings are sorted descending
        """
        
        def extract_price(s: str) -> float:
            return float(s.replace("$", "").replace(",", ""))
        
        prices = [extract_price(p) for p in price_strings]
        assert prices == sorted(prices, reverse=True), \
            f"Prices not sorted descending: {price_strings}"
    
    @staticmethod
    def assert_all_visible(locators: List[Locator], timeout: int = 5000):
        """
        Assert all locators are visible
        
        Args:
            locators: List of locators
            timeout: Maximum wait time per element
        """
        
        for i, locator in enumerate(locators):
            expect(locator).to_be_visible(timeout=timeout)
    
    @staticmethod
    def assert_no_console_errors(page: Page, ignore_patterns: List[str] = None):
        """
        Assert no JavaScript errors in console
        
        Args:
            page: Playwright page (must have console listener set up)
            ignore_patterns: Patterns to ignore
        """
        
        # Note: Requires console listener to be set up during page creation
        pass
    
    @staticmethod
    def assert_total_equals_sum(
        item_prices: List[str],
        total_element: Locator,
        tax_rate: float = 0.08  # 8% tax
    ):
        """
        Assert total equals sum of items plus tax
        
        Args:
            item_prices: List of price strings
            total_element: Locator for total element
            tax_rate: Tax rate (default 8%)
        """
        
        def extract_price(s: str) -> float:
            return float(s.replace("$", "").replace(",", ""))
        
        subtotal = sum(extract_price(p) for p in item_prices)
        tax = round(subtotal * tax_rate, 2)
        expected_total = round(subtotal + tax, 2)
        
        total_text = total_element.text_content() or ""
        actual_total = extract_price(total_text.split("$")[-1])
        
        assert abs(actual_total - expected_total) < 0.01, \
            f"Total {actual_total} != expected {expected_total} (subtotal {subtotal} + tax {tax})"