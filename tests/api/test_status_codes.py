
"""
Module 3 - Part 4: HTTP Status Codes Deep Dive
-----------------------------------------------
Understanding and testing different HTTP status codes

Categories:
- 2xx: Success
- 3xx: Redirection
- 4xx: Client Errors
- 5xx: Server Errors
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


def test_2xx_success_codes():
    """
    LESSON: Success status codes (2xx)
    
    200 OK          - Standard success
    201 Created     - Resource created (POST)
    204 No Content  - Success but no response body (DELETE)
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        # ========================================
        # 200 OK - Standard success
        # ========================================
        print("\nTesting 200 OK...")
        
        response = request_context.get(
            "https://jsonplaceholder.typicode.com/posts/1"
        )
        
        assert response.status == 200
        assert response.status_text == "OK"
        assert response.ok is True  # True for any 2xx status
        
        data = response.json()
        assert len(data) > 0
        
        print("   200 OK - GET request successful")
        
        # ========================================
        # 201 Created - Resource created
        # ========================================
        print("\nTesting 201 Created...")
        
        new_post = {
            "title": "Test Post",
            "body": "Test content",
            "userId": 1
        }
        
        response = request_context.post(
            "https://jsonplaceholder.typicode.com/posts",
            data=new_post
        )
        
        assert response.status == 201
        assert response.status_text == "Created"
        assert response.ok is True
        
        created = response.json()
        assert "id" in created
        
        print(f"   201 Created - Resource created with ID {created['id']}")
        
        # ========================================
        # 200/204 for DELETE
        # ========================================
        print("\nTesting DELETE response...")
        
        response = request_context.delete(
            "https://jsonplaceholder.typicode.com/posts/1"
        )
        
        # Can be 200 or 204
        assert response.status in [200, 204]
        assert response.ok is True
        
        print(f"   {response.status} - Resource deleted")
        
    finally:
        request_context.dispose()


def test_4xx_client_errors():
    """
    LESSON: Client error status codes (4xx)
    
    400 Bad Request      - Invalid request data
    401 Unauthorized     - Not authenticated
    403 Forbidden        - Authenticated but not authorized
    404 Not Found        - Resource doesn't exist
    422 Unprocessable    - Validation failed
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        # ========================================
        # 404 Not Found
        # ========================================
        print("\nTesting 404 Not Found...")
        
        response = request_context.get(
            "https://jsonplaceholder.typicode.com/posts/9999999"
        )
        
        assert response.status == 404
        assert response.status_text == "Not Found"
        assert response.ok is False  # False for non-2xx
        
        print("   404 - Resource not found (as expected)")
        
        # ========================================
        # 401 Unauthorized (using DummyJSON)
        # ========================================
        print("\nTesting 401 Unauthorized...")
        
        response = request_context.get("https://dummyjson.com/auth/me")
        
        # No auth token provided
        assert response.status in [401, 403]
        assert response.ok is False
        
        print(f"   {response.status} - Authentication required")
        
        # ========================================
        # 400 Bad Request (using DummyJSON)
        # ========================================
        print("\nTesting 400 Bad Request...")
        
        # Login with missing password
        response = request_context.post(
            "https://dummyjson.com/auth/login",
            data={"username": "test"},  # Missing password
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status == 400
        assert response.ok is False
        
        error = response.json()
        print(f"   400 - {error.get('message', 'Bad Request')}")
        
    finally:
        request_context.dispose()


def test_status_code_assertions():
    """
    LESSON: Different ways to assert status codes
    
    Best practices for status code validation
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        response = request_context.get(
            "https://jsonplaceholder.typicode.com/posts/1"
        )
        
        # ========================================
        # Method 1: Exact status code (RECOMMENDED)
        # ========================================
        assert response.status == 200, \
            f"Expected 200, got {response.status}"
        
        # ========================================
        # Method 2: Status range (for multiple acceptable codes)
        # ========================================
        assert response.status in [200, 201], \
            f"Expected 200 or 201, got {response.status}"
        
        # ========================================
        # Method 3: Status category (use sparingly)
        # ========================================
        assert 200 <= response.status < 300, \
            f"Expected 2xx status, got {response.status}"
        
        # ========================================
        # Method 4: Using .ok property (AVOID - too vague)
        # ========================================
        # AVOID THIS:
        # assert response.ok  # Which 2xx code? Unclear!
        
        # PREFER THIS:
        assert response.status == 200  # Clear expectation
        
        print("Status code validation complete")
        
    finally:
        request_context.dispose()


def test_httpbin_status_codes():
    """
    LESSON: Testing specific status codes with httpbin
    
    httpbin.org allows testing any status code
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    
    try:
        # Test various status codes
        test_codes = [200, 201, 400, 404, 500]
        
        for code in test_codes:
            print(f"\nTesting status {code}...")
            
            response = request_context.get(f"/status/{code}")
            
            assert response.status == code, \
                f"Expected {code}, got {response.status}"
            
            if 200 <= code < 300:
                assert response.ok is True
            else:
                assert response.ok is False
            
            print(f"{code} - {response.status_text}")
        
    finally:
        request_context.dispose()
