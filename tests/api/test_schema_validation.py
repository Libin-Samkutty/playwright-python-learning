"""
Module 5 - Part 1: Schema Validation
-------------------------------------
Demonstrates comprehensive schema validation patterns
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state

# Import schemas
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))

from schemas.schemas import (
    POST_SCHEMA, USER_SCHEMA, POSTS_ARRAY_SCHEMA, USERS_ARRAY_SCHEMA,
    DUMMYJSON_LOGIN_SCHEMA, DUMMYJSON_PRODUCT_SCHEMA,
    DUMMYJSON_PRODUCTS_RESPONSE_SCHEMA, ERROR_SCHEMA, DUMMYJSON_USER_SCHEMA
)
from helpers.schema_validator import SchemaValidator


def test_validate_single_post():
    """
    LESSON: Basic schema validation
    
    Instead of manual assertions, validate entire structure at once
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        response = request_context.get("/posts/1")
        assert response.status == 200
        
        # ========================================
        # OLD WAY: Manual validation
        # ========================================
        # data = response.json()
        # assert "userId" in data
        # assert isinstance(data["userId"], int)
        # assert "id" in data
        # assert isinstance(data["id"], int)
        # ... 10+ more assertions
        
        # ========================================
        # NEW WAY: Schema validation
        # ========================================
        SchemaValidator.validate_response(response, POST_SCHEMA)
        
        print("✅ Post schema validation passed!")
        
        # You can still access data for additional checks
        data = response.json()
        print(f"   Post: {data['title'][:50]}...")
        
    finally:
        request_context.dispose()


def test_validate_posts_array():
    """
    LESSON: Validating arrays
    
    Ensures all items in array match schema
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        response = request_context.get("/posts?_limit=10")
        assert response.status == 200
        
        # Validate entire array and all items
        SchemaValidator.validate_response(response, POSTS_ARRAY_SCHEMA)
        
        data = response.json()
        print(f"✅ Validated {len(data)} posts against schema")
        
    finally:
        request_context.dispose()


def test_validate_nested_objects():
    """
    LESSON: Validating deeply nested structures
    
    Schema validation handles nested objects automatically
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        response = request_context.get("/users/1")
        assert response.status == 200
        
        # Validates:
        # - Top-level fields (id, name, username, etc.)
        # - Nested address object (street, city, zipcode, geo)
        # - Nested geo object (lat, lng)
        # - Nested company object (name, catchPhrase, bs)
        SchemaValidator.validate_response(response, USER_SCHEMA)
        
        data = response.json()
        print(f"✅ Validated user: {data['name']}")
        print(f"   Address: {data['address']['city']}")
        print(f"   Company: {data['company']['name']}")
        
    finally:
        request_context.dispose()


def test_validate_dummyjson_login():
    """
    LESSON: Validating authentication response
    
    NOTE: DummyJSON returns 'accessToken', not 'token'
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        login_data = {
            "username": "emilys",
            "password": "emilyspass"
        }
        
        response = request_context.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status == 200
        
        # Validate login response schema
        SchemaValidator.validate_response(response, DUMMYJSON_LOGIN_SCHEMA)
        
        data = response.json()
        
        # Note: accessToken, not token!
        access_token = data["accessToken"]
        refresh_token = data["refreshToken"]
        
        print(f"✅ Login validated: {data['username']}")
        print(f"   Access Token: {access_token[:30]}...")
        print(f"   Refresh Token: {refresh_token[:30]}...")
        
        # Verify token can be used
        me_response = request_context.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert me_response.status == 200
        SchemaValidator.validate_response(me_response, DUMMYJSON_USER_SCHEMA)
        
        print(f"✅ Token works: Authenticated as {data['username']}")
        
    finally:
        request_context.dispose()


def test_validate_products_with_pagination():
    """
    LESSON: Validating paginated responses
    
    Validates wrapper object + array of items
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        response = request_context.get("/products?limit=5&skip=0")
        assert response.status == 200
        
        # Validates:
        # - products array
        # - Each product in array
        # - total, skip, limit fields
        SchemaValidator.validate_response(response, DUMMYJSON_PRODUCTS_RESPONSE_SCHEMA)
        
        data = response.json()
        
        print(f"✅ Validated paginated response:")
        print(f"   Products: {len(data['products'])}")
        print(f"   Total: {data['total']}")
        print(f"   Skip: {data['skip']}")
        print(f"   Limit: {data['limit']}")
        
        # Verify pagination math
        assert len(data["products"]) == data["limit"]
        
    finally:
        request_context.dispose()


def test_schema_validation_detects_errors():
    """
    LESSON: Schema validation catches errors
    
    Demonstrates how schema validation fails when data is wrong
    """
    
    # ========================================
    # Test 1: Missing required field
    # ========================================
    print("\n❌ Test 1: Missing required field...")
    
    invalid_post = {
        "userId": 1,
        "id": 1,
        "title": "Test"
        # Missing 'body' (required field)
    }
    
    errors = SchemaValidator.get_errors(invalid_post, POST_SCHEMA)
    assert len(errors) > 0
    print(f"   Caught error: {errors[0]}")
    
    # ========================================
    # Test 2: Wrong data type
    # ========================================
    print("\n❌ Test 2: Wrong data type...")
    
    invalid_post = {
        "userId": "not-a-number",  # Should be integer
        "id": 1,
        "title": "Test",
        "body": "Content"
    }
    
    assert SchemaValidator.is_valid(invalid_post, POST_SCHEMA) is False
    print("   Caught type error")
    
    # ========================================
    # Test 3: Extra fields (when not allowed)
    # ========================================
    print("\n❌ Test 3: Extra fields...")
    
    invalid_post = {
        "userId": 1,
        "id": 1,
        "title": "Test",
        "body": "Content",
        "extraField": "not-allowed"  # additionalProperties: false
    }
    
    assert SchemaValidator.is_valid(invalid_post, POST_SCHEMA) is False
    print("   Caught extra field")
    
    print("\n✅ Schema validation catches all errors!")


def test_validate_error_response():
    """
    LESSON: Validating error responses
    
    Error responses should also have consistent schema
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # Trigger 404 error
        response = request_context.get("/products/999999")
        
        assert response.status == 404
        
        # Validate error response structure
        SchemaValidator.validate_response(response, ERROR_SCHEMA)
        
        error = response.json()
        print(f"✅ Error response validated: {error['message']}")
        
    finally:
        request_context.dispose()


def test_partial_validation():
    """
    LESSON: Validating partial updates (PATCH)
    
    PATCH requests only include changed fields
    """
    
    # Full object (PUT)
    full_post = {
        "userId": 1,
        "id": 1,
        "title": "Full Post",
        "body": "Complete content"
    }
    
    # Validate full object
    SchemaValidator.validate(full_post, POST_SCHEMA)
    print("✅ Full object validated")
    
    # Partial object (PATCH)
    partial_post = {
        "title": "Updated Title"
        # Only updating title, other fields omitted
    }
    
    # This would fail with regular schema (missing required fields)
    # assert SchemaValidator.is_valid(partial_post, POST_SCHEMA) is False
    
    # Use partial validation
    SchemaValidator.validate_partial(partial_post, POST_SCHEMA)
    print("✅ Partial object validated")


@pytest.mark.parametrize("user_id", [1, 2, 3])
def test_validate_multiple_users(user_id):
    """
    LESSON: Combining parametrization with schema validation
    
    Validate schema for multiple resources
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        response = request_context.get(f"/users/{user_id}")
        assert response.status == 200
        
        # Validate each user against schema
        SchemaValidator.validate_response(response, USER_SCHEMA)
        
        data = response.json()
        print(f"✅ User {user_id} validated: {data['name']}")
        
    finally:
        request_context.dispose()