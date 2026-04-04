"""
Module 1: Introduction to API Testing with Playwright
------------------------------------------------------
This demonstrates the basic structure of an API test using Playwright's
request context (sync API).

IMPORTANT: We use _pw_state.get_playwright() instead of sync_playwright()
to avoid asyncio conflicts on Windows/Python 3.14+
"""

import pytest
import sys
import os

# Add parent directory to path to import playwright_state
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


def test_basic_api_call():
    """
    LESSON: Understanding the API test lifecycle
    
    Real-world usage: Verify that the API server is running and responding
    This is often the first smoke test in a test suite.
    """
    
    # STEP 1: Get Playwright instance (already initialized in conftest.py)
    playwright = _pw_state.get_playwright()
    
    # STEP 2: Create a request context (like opening a browser for API calls)
    # This is your HTTP client that will make API requests
    request_context = playwright.request.new_context()
    
    try:
        # STEP 3: Make a GET request to a public API
        # JSONPlaceholder is a free fake REST API for testing
        response = request_context.get("https://jsonplaceholder.typicode.com/posts/1")
        
        # STEP 4: Validate the response
        # - Status code: Did the request succeed?
        print(f"Status Code: {response.status}")  # Should print: 200
        assert response.status == 200, f"Expected 200, got {response.status}"
        
        # STEP 5: Inspect response headers (metadata)
        headers = response.headers
        print(f"Content-Type: {headers.get('content-type')}")  # application/json
        
        # STEP 6: Parse the response body as JSON
        data = response.json()
        print(f"Response Data: {data}")
        
        # STEP 7: Validate the data structure
        assert "userId" in data, "Response missing 'userId' field"
        assert "id" in data, "Response missing 'id' field"
        assert "title" in data, "Response missing 'title' field"
        assert "body" in data, "Response missing 'body' field"
        
        # STEP 8: Validate specific values
        assert data["id"] == 1, f"Expected id=1, got {data['id']}"
        assert isinstance(data["userId"], int), "userId should be an integer"
        
        print("\nTest passed! API is working correctly.")
        
    finally:
        # STEP 9: ALWAYS close the request context to free resources
        # This is like closing a browser after UI tests
        request_context.dispose()


def test_understanding_response_object():
    """
    LESSON: Deep dive into the Response object
    
    Real-world usage: When debugging API failures, you need to inspect
    every part of the response (status, headers, body, timing)
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        response = request_context.get("https://jsonplaceholder.typicode.com/users/1")
        
        # 1️⃣ STATUS CODE - Most important check
        # 200: Success
        # 201: Created (POST)
        # 400: Bad Request (client error)
        # 401: Unauthorized
        # 404: Not Found
        # 500: Server Error
        print(f"\n1. Status Code: {response.status}")
        assert response.status == 200
        
        # 2️⃣ STATUS TEXT - Human-readable status
        print(f"2. Status Text: {response.status_text}")  # "OK"
        
        # 3️⃣ HEADERS - Metadata about the response
        headers = response.headers
        print(f"3. Content-Type: {headers.get('content-type')}")
        print(f"   Server: {headers.get('server')}")
        
        # 4️⃣ URL - Final URL after redirects
        print(f"4. URL: {response.url}")
        
        # 5️⃣ BODY - The actual data
        # Method 1: Parse as JSON
        json_data = response.json()
        print(f"5a. JSON Body (first 100 chars): {str(json_data)[:100]}...")
        
        # Method 2: Get raw text
        # response.text()  # Returns string
        
        # Method 3: Get raw bytes
        # response.body()  # Returns bytes
        
        # 6️⃣ OK property - Quick check if status is 2xx
        print(f"6. Is OK (2xx status): {response.ok}")
        assert response.ok is True
        
    finally:
        request_context.dispose()


def test_common_mistake_not_disposing():
    """
    COMMON MISTAKE: Forgetting to dispose request_context
    
    ❌ BAD:
    def test_bad():
        ctx = playwright.request.new_context()
        response = ctx.get("...")
        # Forgot to dispose! Causes resource leaks
    
    GOOD:
    def test_good():
        ctx = playwright.request.new_context()
        try:
            response = ctx.get("...")
        finally:
            ctx.dispose()
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        response = request_context.get("https://jsonplaceholder.typicode.com/posts/1")
        assert response.status == 200
    finally:
        # ALWAYS dispose in finally block
        # This runs even if the test fails/raises exception
        request_context.dispose()
def test_practice_exercise():
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        response = request_context.get("https://jsonplaceholder.typicode.com/users")
        
        # 1. Status is 200
        assert response.status == 200
        
        # 2. Parse JSON
        users = response.json()
        
        # 3. Is a list
        assert isinstance(users, list), "Response should be a list"
        
        # 4. Has 10 users
        assert len(users) == 10, f"Expected 10 users, got {len(users)}"
        
        # 5. First user has email
        first_user = users[0]
        assert "email" in first_user, "First user missing email field"
        
        print(f"Exercise passed! Found {len(users)} users")
        
    finally:
        request_context.dispose()