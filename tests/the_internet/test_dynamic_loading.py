"""
tests/the_internet/test_dynamic_loading.py
Dynamic Loading tests for The Internet using Page Object Model
"""

import pytest
from playwright.sync_api import expect


class TestDynamicLoadingExample1:
    """
    Dynamic Loading Example 1 tests
    
    URL: https://the-internet.herokuapp.com/dynamic_loading/1
    
    Scenario: Element exists in DOM but is hidden until loading completes
    """
    
    def test_page_loads_correctly(self, dynamic_loading_page_1):
        """
        Test: Page loads with Start button
        """
        dynamic_loading_page_1.navigate()
        dynamic_loading_page_1.verify_page_loaded()
    
    def test_start_triggers_loading(self, dynamic_loading_page_1):
        """
        Test: Clicking Start shows loading indicator
        """
        dynamic_loading_page_1.navigate()
        dynamic_loading_page_1.click_start()
        
        # Loading should be visible
        dynamic_loading_page_1.verify_loading_in_progress()
    
    def test_loading_completes_with_hello_world(self, dynamic_loading_page_1):
        """
        Test: After loading completes, "Hello World!" is displayed
        """
        dynamic_loading_page_1.navigate()
        dynamic_loading_page_1.verify_hello_world_displayed()
    
    def test_content_hidden_before_start(self, dynamic_loading_page_1):
        """
        Test: Content element exists but is hidden before Start
        """
        dynamic_loading_page_1.navigate()
        
        # Element should be in DOM (Example 1)
        assert dynamic_loading_page_1.is_content_in_dom()
        
        # But not visible
        assert not dynamic_loading_page_1.is_content_loaded()
    
    def test_complete_loading_flow(self, dynamic_loading_page_1):
        """
        Test: Complete flow from start to content
        """
        dynamic_loading_page_1.navigate()
        
        # Verify initial state
        dynamic_loading_page_1.verify_page_loaded()
        assert not dynamic_loading_page_1.is_loading()
        assert not dynamic_loading_page_1.is_content_loaded()
        
        # Start loading
        dynamic_loading_page_1.click_start()
        
        # Wait for loading to appear then disappear
        dynamic_loading_page_1.wait_for_loading_to_start()
        dynamic_loading_page_1.wait_for_loading_to_complete()
        
        # Verify content
        dynamic_loading_page_1.verify_content_visible()
        dynamic_loading_page_1.verify_content_text("Hello World!")
    
    def test_loading_indicator_disappears(self, dynamic_loading_page_1):
        """
        Test: Loading indicator disappears after loading completes
        """
        dynamic_loading_page_1.navigate()
        dynamic_loading_page_1.click_start()
        
        # Wait for loading to complete
        dynamic_loading_page_1.wait_for_loading_to_complete(timeout=10000)
        
        # Loading should be hidden
        assert not dynamic_loading_page_1.is_loading()
    
    def test_get_loaded_text(self, dynamic_loading_page_1):
        """
        Test: Can retrieve loaded text
        """
        dynamic_loading_page_1.navigate()
        dynamic_loading_page_1.start_and_wait_for_content()
        
        text = dynamic_loading_page_1.get_loaded_text()
        assert text == "Hello World!"


class TestDynamicLoadingExample2:
    """
    Dynamic Loading Example 2 tests
    
    URL: https://the-internet.herokuapp.com/dynamic_loading/2
    
    Scenario: Element is NOT in DOM until loading completes
    """
    
    def test_page_loads_correctly(self, dynamic_loading_page_2):
        """
        Test: Page loads with Start button
        """
        dynamic_loading_page_2.navigate()
        dynamic_loading_page_2.verify_page_loaded()
    
    def test_content_not_in_dom_initially(self, dynamic_loading_page_2):
        """
        Test: Content element does NOT exist in DOM before Start
        
        This is the key difference from Example 1
        """
        dynamic_loading_page_2.navigate()
        
        # Element should NOT be in DOM (Example 2)
        assert not dynamic_loading_page_2.is_content_in_dom()
    
    def test_content_added_to_dom_after_loading(self, dynamic_loading_page_2):
        """
        Test: Content element is added to DOM after loading
        """
        dynamic_loading_page_2.navigate()
        
        # Not in DOM initially
        assert not dynamic_loading_page_2.is_content_in_dom()
        
        # Start and wait
        dynamic_loading_page_2.start_and_wait_for_content()
        
        # Now in DOM and visible
        assert dynamic_loading_page_2.is_content_in_dom()
        assert dynamic_loading_page_2.is_content_loaded()
    
    def test_loading_completes_with_hello_world(self, dynamic_loading_page_2):
        """
        Test: After loading completes, "Hello World!" is displayed
        """
        dynamic_loading_page_2.navigate()
        dynamic_loading_page_2.verify_hello_world_displayed()
    
    def test_complete_loading_flow(self, dynamic_loading_page_2):
        """
        Test: Complete flow with detailed state verification
        """
        dynamic_loading_page_2.navigate()
        
        # Verify initial state
        dynamic_loading_page_2.verify_page_loaded()
        assert not dynamic_loading_page_2.is_content_in_dom()  # Key difference
        
        # Start loading
        dynamic_loading_page_2.click_start()
        
        # Wait for content
        dynamic_loading_page_2.wait_for_loading_to_complete()
        dynamic_loading_page_2.wait_for_content()
        
        # Verify content
        dynamic_loading_page_2.verify_content_text("Hello World!")


class TestDynamicLoadingComparison:
    """
    Tests comparing Example 1 and Example 2 behavior
    """
    
    def test_example1_has_element_in_dom(self, dynamic_loading_page_1):
        """Example 1: Element exists in DOM initially"""
        dynamic_loading_page_1.navigate()
        assert dynamic_loading_page_1.is_content_in_dom()
    
    def test_example2_no_element_in_dom(self, dynamic_loading_page_2):
        """Example 2: Element NOT in DOM initially"""
        dynamic_loading_page_2.navigate()
        assert not dynamic_loading_page_2.is_content_in_dom()
    
    def test_both_examples_show_same_result(
        self, 
        dynamic_loading_page_1,
        dynamic_loading_page_2
    ):
        """Both examples show "Hello World!" after loading"""
        
        # Example 1
        dynamic_loading_page_1.navigate()
        dynamic_loading_page_1.start_and_wait_for_content()
        text1 = dynamic_loading_page_1.get_loaded_text()
        
        # Example 2
        dynamic_loading_page_2.navigate()
        dynamic_loading_page_2.start_and_wait_for_content()
        text2 = dynamic_loading_page_2.get_loaded_text()
        
        # Same result
        assert text1 == text2 == "Hello World!"


class TestDynamicLoadingWithTimeouts:
    """
    Tests demonstrating timeout handling
    """
    
    def test_custom_timeout(self, dynamic_loading_page_1):
        """
        Test: Using custom timeout for slow loading
        """
        dynamic_loading_page_1.navigate()
        
        # Use longer timeout
        dynamic_loading_page_1.start_and_wait_for_content(timeout=15000)
        
        dynamic_loading_page_1.verify_content_text("Hello World!")
    
    @pytest.mark.skip(reason="Demonstrates timeout failure - runs slowly")
    def test_timeout_too_short(self, dynamic_loading_page_1):
        """
        Test: Timeout too short causes failure
        
        Skipped by default to avoid slow test runs
        """
        dynamic_loading_page_1.navigate()
        
        # This will likely fail - loading takes ~5 seconds
        with pytest.raises(AssertionError):
            dynamic_loading_page_1.start_and_wait_for_content(timeout=1000)