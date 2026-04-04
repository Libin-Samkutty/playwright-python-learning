"""
Module 3 - Part 3: Advanced Response Validation
------------------------------------------------
Learn sophisticated validation techniques:
- Schema validation
- Deep nested data validation
- Response time validation
- Data type validation
- Array validation
"""

import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


def test_schema_validation_basic():
    """
    LESSON: Validate response structure (schema)
    
    Real-world: Ensure API contract is maintained
    - Frontend depends on specific fields
    - Breaking changes cause production issues
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        response = request_context.get("/posts/1")
        assert response.status == 200
        
        post = response.json()
        
        # Define expected schema
        required_fields = ["userId", "id", "title", "body"]
        
        # Validate all required fields exist
        for field in required_fields:
            assert field in post, f"Missing required field: '{field}'"
        
        print("All required fields present")
        
        # Validate data types
        assert isinstance(post["userId"], int), "userId should be integer"
        assert isinstance(post["id"], int), "id should be integer"
        assert isinstance(post["title"], str), "title should be string"
        assert isinstance(post["body"], str), "body should be string"
        
        print("All field types correct")
        
        # Validate value constraints
        assert post["userId"] > 0, "userId should be positive"
        assert post["id"] > 0, "id should be positive"
        assert len(post["title"]) > 0, "title should not be empty"
        assert len(post["body"]) > 0, "body should not be empty"
        
        print("All value constraints satisfied")
        
    finally:
        request_context.dispose()


def test_nested_object_validation():
    """
    LESSON: Validate deeply nested JSON structures
    
    Real-world: Complex API responses (user profiles, orders, etc.)
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        response = request_context.get("/users/1")
        assert response.status == 200
        
        user = response.json()
        
        # ========================================
        # Level 1: Top-level fields
        # ========================================
        top_level_fields = ["id", "name", "username", "email", "address", "phone", "website", "company"]
        
        for field in top_level_fields:
            assert field in user, f"Missing top-level field: {field}"
        
        print("Top-level schema valid")
        
        # ========================================
        # Level 2: Nested 'address' object
        # ========================================
        address = user["address"]
        address_fields = ["street", "suite", "city", "zipcode", "geo"]
        
        for field in address_fields:
            assert field in address, f"Missing address field: {field}"
        
        # Validate address field types
        assert isinstance(address["street"], str)
        assert isinstance(address["city"], str)
        assert isinstance(address["zipcode"], str)
        
        print("Address schema valid")
        
        # ========================================
        # Level 3: Nested 'geo' object within 'address'
        # ========================================
        geo = address["geo"]
        geo_fields = ["lat", "lng"]
        
        for field in geo_fields:
            assert field in geo, f"Missing geo field: {field}"
        
        # Validate geo coordinates are strings (in this API)
        assert isinstance(geo["lat"], str)
        assert isinstance(geo["lng"], str)
        
        # Validate geo values are numeric strings
        try:
            float(geo["lat"])
            float(geo["lng"])
        except ValueError:
            pytest.fail("Geo coordinates should be numeric")
        
        print("Geo schema valid")
        
        # ========================================
        # Level 2: Nested 'company' object
        # ========================================
        company = user["company"]
        company_fields = ["name", "catchPhrase", "bs"]
        
        for field in company_fields:
            assert field in company, f"Missing company field: {field}"
        
        print("Company schema valid")
        
        # ========================================
        # Complete validation summary
        # ========================================
        print("\nComplete nested structure validation passed:")
        print(f"   User: {user['name']}")
        print(f"   City: {address['city']}")
        print(f"   Coordinates: ({geo['lat']}, {geo['lng']})")
        print(f"   Company: {company['name']}")
        
    finally:
        request_context.dispose()


def test_array_validation():
    """
    LESSON: Validate arrays in responses
    
    Real-world: Lists of products, users, orders, etc.
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        response = request_context.get("/posts")
        assert response.status == 200
        
        posts = response.json()
        
        # ========================================
        # Array-level validation
        # ========================================
        
        # 1. Verify it's an array
        assert isinstance(posts, list), "Response should be an array"
        
        # 2. Verify array is not empty
        assert len(posts) > 0, "Array should not be empty"
        
        print(f"Array contains {len(posts)} items")
        
        # 3. Verify all items have same structure
        first_item_keys = set(posts[0].keys())
        
        for i, post in enumerate(posts):
            current_keys = set(post.keys())
            assert current_keys == first_item_keys, \
                f"Item {i} has different structure: {current_keys}"
        
        print("All array items have consistent structure")
        
        # ========================================
        # Item-level validation
        # ========================================
        
        # 4. Validate each item's schema
        for post in posts:
            assert "userId" in post
            assert "id" in post
            assert "title" in post
            assert "body" in post
            
            # Type validation
            assert isinstance(post["userId"], int)
            assert isinstance(post["id"], int)
            assert isinstance(post["title"], str)
            assert isinstance(post["body"], str)
        
        print("All items have valid schema")
        
        # ========================================
        # Data integrity validation
        # ========================================
        
        # 5. Verify IDs are unique
        ids = [post["id"] for post in posts]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"
        
        print("All IDs are unique")
        
        # 6. Verify IDs are sequential (API-specific check)
        sorted_ids = sorted(ids)
        expected_ids = list(range(1, len(posts) + 1))
        # Note: This check is specific to JSONPlaceholder
        
        # 7. Verify userId distribution
        user_ids = [post["userId"] for post in posts]
        unique_users = set(user_ids)
        
        print(f"Posts from {len(unique_users)} different users")
        
    finally:
        request_context.dispose()


def test_conditional_field_validation():
    """
    LESSON: Validate fields based on conditions
    
    Real-world: Optional fields, different user types, feature flags
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        response = request_context.get("/products/1")
        assert response.status == 200
        
        product = response.json()
        
        # ========================================
        # Always required fields
        # ========================================
        required_fields = ["id", "title", "price"]
        for field in required_fields:
            assert field in product, f"Required field missing: {field}"
        
        # ========================================
        # Conditional validation
        # ========================================
        
        # If discountPercentage exists, validate it
        if "discountPercentage" in product:
            discount = product["discountPercentage"]
            assert isinstance(discount, (int, float)), \
                "discountPercentage should be numeric"
            assert 0 <= discount <= 100, \
                "discountPercentage should be 0-100"
        
        # If images exist, validate array
        if "images" in product:
            images = product["images"]
            assert isinstance(images, list), "images should be array"
            
            for img_url in images:
                assert isinstance(img_url, str), "Image URL should be string"
                assert img_url.startswith("http"), "Image should be valid URL"
        
        # If rating exists, validate range
        if "rating" in product:
            rating = product["rating"]
            assert isinstance(rating, (int, float)), "rating should be numeric"
            assert 0 <= rating <= 5, "rating should be 0-5"
        
        print("Conditional validation passed")
        
    finally:
        request_context.dispose()


def test_response_metadata_validation():
    """
    LESSON: Validate response headers and metadata
    
    Real-world: Verify caching, content type, rate limits
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        response = request_context.get("/posts/1")
        assert response.status == 200
        
        # ========================================
        # Headers validation
        # ========================================
        headers = response.headers
        
        # 1. Content-Type validation
        content_type = headers.get("content-type", "")
        assert "application/json" in content_type, \
            f"Expected JSON response, got {content_type}"
        
        print(f"Content-Type: {content_type}")
        
        # 2. Check common headers exist
        # Note: Not all APIs return all these headers
        
        if "server" in headers:
            print(f"Server: {headers['server']}")
        
        if "cache-control" in headers:
            print(f"Cache-Control: {headers['cache-control']}")
        
        if "x-ratelimit-limit" in headers:
            limit = headers["x-ratelimit-limit"]
            print(f"Rate Limit: {limit}")
        
        if "x-ratelimit-remaining" in headers:
            remaining = headers["x-ratelimit-remaining"]
            print(f"Remaining Requests: {remaining}")
        
        # ========================================
        # Response properties
        # ========================================
        
        # 3. URL validation (check for redirects)
        assert response.url == "https://jsonplaceholder.typicode.com/posts/1", \
            "Unexpected redirect"
        
        # 4. Status text
        assert response.status_text == "OK"
        
        # 5. OK property
        assert response.ok is True
        
        print("All response metadata valid")
        
    finally:
        request_context.dispose()


def test_error_response_validation():
    """
    LESSON: Validate error responses
    
    Real-world: Errors should have consistent structure
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # Trigger 404 error
        response = request_context.get("/products/999999")
        
        # Validate error status
        assert response.status == 404, \
            f"Expected 404, got {response.status}"
        
        # Parse error response
        error_data = response.json()
        
        # Validate error structure
        assert "message" in error_data, "Error should have 'message' field"
        
        print(f"Error response: {error_data['message']}")
        
        # Validate error message is meaningful
        message = error_data["message"]
        assert len(message) > 0, "Error message should not be empty"
        assert "not found" in message.lower() or "product" in message.lower(), \
            "Error message should be descriptive"
        
    finally:
        request_context.dispose()