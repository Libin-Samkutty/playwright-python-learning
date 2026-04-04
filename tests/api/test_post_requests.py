"""
Module 2 - Part 1: POST Requests & Creating Data
-------------------------------------------------
Learn how to create resources via API using POST requests.

Real-world scenarios:
- User registration
- Creating blog posts
- Adding products to cart
- Submitting orders
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


def test_create_post_basic():
    """
    LESSON: Creating a resource with POST request
    
    Real-world: User creates a new blog post
    POST /api/posts
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        # STEP 1: Prepare the data to send
        # This is the "request body" - what we're creating
        new_post = {
            "title": "My First API Test Post",
            "body": "This post was created via Playwright API testing",
            "userId": 1
        }
        
        # STEP 2: Make POST request
        # The 'data' parameter is automatically converted to JSON
        response = request_context.post(
            "https://jsonplaceholder.typicode.com/posts",
            data=new_post  # ← Playwright converts this dict to JSON automatically
        )
        
        # STEP 3: Verify response status
        # 201 = Created (successful resource creation)
        # 200 = OK (also acceptable for POST, but 201 is more specific)
        print(f"Status: {response.status}")
        assert response.status == 201, f"Expected 201, got {response.status}"
        
        # STEP 4: Parse response body
        created_post = response.json()
        print(f"Created Post: {created_post}")
        
        # STEP 5: Verify the server returned our data
        assert created_post["title"] == new_post["title"], "Title mismatch"
        assert created_post["body"] == new_post["body"], "Body mismatch"
        assert created_post["userId"] == new_post["userId"], "UserId mismatch"
        
        # STEP 6: Verify server assigned an ID
        # When creating resources, server assigns unique ID
        assert "id" in created_post, "Response missing 'id' field"
        assert isinstance(created_post["id"], int), "ID should be integer"
        print(f"✅ Created post with ID: {created_post['id']}")
        
    finally:
        request_context.dispose()


def test_create_user():
    """
    LESSON: Creating a user (registration scenario)
    
    Real-world: User registration form submits data to API
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        # User registration data
        new_user = {
            "name": "Jane Smith",
            "username": "janesmith",
            "email": "jane.smith@example.com",
            "phone": "555-1234",
            "website": "janesmith.com"
        }
        
        response = request_context.post(
            "https://jsonplaceholder.typicode.com/users",
            data=new_user
        )
        
        # Verify creation
        assert response.status == 201
        
        created_user = response.json()
        
        # Validate all fields were saved
        assert created_user["name"] == new_user["name"]
        assert created_user["username"] == new_user["username"]
        assert created_user["email"] == new_user["email"]
        assert created_user["phone"] == new_user["phone"]
        assert created_user["website"] == new_user["website"]
        
        # Server assigned ID
        assert created_user["id"] is not None
        
        print(f"✅ User created successfully: {created_user['username']}")
        
    finally:
        request_context.dispose()


def test_post_with_headers():
    """
    LESSON: Sending custom headers with POST request
    
    Real-world: APIs often require headers for:
    - Content-Type (telling server data format)
    - Authorization (API keys, tokens)
    - Custom headers (API version, tracking, etc.)
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        new_post = {
            "title": "Post with Custom Headers",
            "body": "Testing header configuration",
            "userId": 1
        }
        
        # Send POST with custom headers
        response = request_context.post(
            "https://jsonplaceholder.typicode.com/posts",
            data=new_post,
            headers={
                # Content-Type is automatically set to application/json when using 'data'
                # But you can override it or add custom headers
                "Content-Type": "application/json; charset=utf-8",
                "X-Custom-Header": "MyTestValue",  # Custom header
                "X-API-Version": "v1"              # API versioning
            }
        )
        
        assert response.status == 201
        
        created_post = response.json()
        print(f"✅ Created with headers: {created_post['id']}")
        
    finally:
        request_context.dispose()


def test_post_invalid_data():
    """
    LESSON: Testing error handling (negative testing)
    
    Real-world: Verify API rejects invalid data properly
    This is CRITICAL for security and data integrity
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        # Missing required field 'userId'
        invalid_post = {
            "title": "Invalid Post",
            "body": "Missing userId"
            # userId is missing!
        }
        
        response = request_context.post(
            "https://jsonplaceholder.typicode.com/posts",
            data=invalid_post
        )
        
        # Note: JSONPlaceholder is lenient and accepts this
        # In a real API, you'd expect:
        # assert response.status == 400  # Bad Request
        # OR
        # assert response.status == 422  # Unprocessable Entity
        
        # For this example, it still creates (201)
        # But in production, test that validation works!
        print(f"Status: {response.status}")
        
        # In a real API test, you'd validate error message:
        # error = response.json()
        # assert "userId is required" in error["message"]
        
    finally:
        request_context.dispose()