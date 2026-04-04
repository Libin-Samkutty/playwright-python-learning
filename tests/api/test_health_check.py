"""
Real-World Scenario: API Health Check
--------------------------------------
Before deploying a new version, verify the API is responding correctly.
This is typically the first test in a CI/CD pipeline.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


def test_api_health_check():
    """
    Verify the API service is running and responding
    
    Real usage: Run this in CI/CD before deploying:
    - Jenkins: pytest tests/api/test_health_check.py
    - GitHub Actions: pytest tests/api/test_health_check.py
    - If this fails, deployment stops
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        # Using JSONPlaceholder as example
        # In production: https://api.yourcompany.com/health
        response = request_context.get("https://jsonplaceholder.typicode.com/posts")
        
        # Health check criteria:
        # 1. Status is 200 OK
        assert response.status == 200, f"Health check failed: status {response.status}"
        
        # 2. Response is valid JSON
        try:
            data = response.json()
        except Exception as e:
            pytest.fail(f"Health check failed: Invalid JSON response - {e}")
        
        # 3. Response is not empty
        assert len(data) > 0, "Health check failed: Empty response"
        
        # 4. Response time is acceptable (under 2 seconds)
        # Note: Playwright doesn't expose timing directly, but in production
        # you can wrap the call with time.time()
        
        print("✅ Health check passed - API is healthy")
        
    finally:
        request_context.dispose()


def test_api_returns_correct_data_structure():
    """
    Verify the API returns data in the expected format
    
    Real usage: Catch breaking changes when backend team modifies API
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        response = request_context.get("https://jsonplaceholder.typicode.com/users/1")
        
        assert response.status == 200
        
        user = response.json()
        
        # Validate expected fields exist
        # This is called "schema validation" or "contract testing"
        required_fields = ["id", "name", "username", "email", "address", "phone", "website", "company"]
        
        for field in required_fields:
            assert field in user, f"Missing required field: {field}"
        
        # Validate nested objects
        assert "street" in user["address"], "Missing address.street"
        assert "city" in user["address"], "Missing address.city"
        
        print(f"✅ User data structure is valid: {user['name']}")
        
    finally:
        request_context.dispose()