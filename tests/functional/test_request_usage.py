"""
tests/functional/test_request_usage.py
Tests demonstrating request object usage
"""

import pytest
from playwright.sync_api import expect


class TestWithIntrospection:
    """
    Tests using request-aware fixtures
    """
    
    def test_basic_introspection(self, context_aware_fixture, page, test_data):
        """This test will print fixture information"""
        
        page.goto(test_data["urls"]["base"])
        expect(page).to_have_title("Swag Labs")
    
    @pytest.mark.slow
    def test_with_slow_marker(self, dynamic_timeout, page, test_data):
        """Test with slow marker gets longer timeout"""
        
        print(f"Timeout configured: {dynamic_timeout}ms")
        assert dynamic_timeout == 60000  # Slow marker = 60s
        
        page.set_default_timeout(dynamic_timeout)
        page.goto(test_data["urls"]["base"])
    
    def test_without_slow_marker(self, dynamic_timeout, page, test_data):
        """Test without slow marker gets normal timeout"""
        
        print(f"Timeout configured: {dynamic_timeout}ms")
        assert dynamic_timeout == 10000  # Normal = 10s
        
        page.set_default_timeout(dynamic_timeout)
        page.goto(test_data["urls"]["base"])
    
    def test_with_artifacts(self, test_artifacts_dir, page, test_data):
        """Test using dedicated artifacts directory"""
        
        page.goto(test_data["urls"]["base"])
        
        # Save screenshot to test-specific directory
        screenshot_path = test_artifacts_dir / "homepage.png"
        page.screenshot(path=str(screenshot_path))
        
        assert screenshot_path.exists()
        print(f"Screenshot saved to: {screenshot_path}")


@pytest.mark.parametrize("fixture_with_indirect_param", ["apple", "banana", "cherry"], indirect=True)
def test_indirect_parametrize(fixture_with_indirect_param):
    """
    Test with indirect parametrization
    
    The parameter goes to the fixture first, then to the test
    """
    
    # fixture_with_indirect_param receives "apple", "banana", "cherry"
    # and returns "Processed: apple", etc.
    assert fixture_with_indirect_param.startswith("Processed:")
