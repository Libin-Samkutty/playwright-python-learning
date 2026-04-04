"""
Module 5 - Part 2: Using Data Factories
----------------------------------------
Demonstrates how factories improve test data management
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state

sys.path.insert(0, os.path.dirname(__file__))
from factories.base_factory import PostFactory, UserFactory, ProductFactory, LoginFactory
from schemas.schemas import POST_SCHEMA, DUMMYJSON_LOGIN_SCHEMA
from helpers.schema_validator import SchemaValidator


def test_create_post_with_factory():
    """
    LESSON: Using factory for test data
    
    Compare:
    WITHOUT FACTORY:
        data = {"userId": 1, "title": "Test", "body": "Content"}
    
    WITH FACTORY:
        data = PostFactory.create()
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        # Generate post data with factory
        post_data = PostFactory.create()
        
        print(f"\n📝 Generated post data:")
        print(f"   Title: {post_data['title']}")
        print(f"   Body: {post_data['body'][:50]}...")
        
        # Create post via API
        response = request_context.post("/posts", data=post_data)
        assert response.status == 201

        created = response.json()
        assert created["title"] == post_data["title"]

        # Validate API response matches schema (response includes id assigned by server)
        SchemaValidator.validate(created, POST_SCHEMA)
        
        print(f"✅ Created post with ID: {created['id']}")
        
    finally:
        request_context.dispose()


def test_create_multiple_posts_with_factory():
    """
    LESSON: Batch creation with factories
    
    Create multiple resources easily
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        # Generate 5 posts at once
        posts_data = PostFactory.create_batch(count=5, user_id=1)
        
        print(f"\n📚 Generated {len(posts_data)} posts:")
        
        created_posts = []
        for post_data in posts_data:
            response = request_context.post("/posts", data=post_data)
            assert response.status == 201
            
            created = response.json()
            created_posts.append(created)
            
            print(f"   - {created['title'][:40]}...")
        
        assert len(created_posts) == 5
        print(f"\n✅ Created {len(created_posts)} posts")
        
    finally:
        request_context.dispose()


def test_custom_factory_data():
    """
    LESSON: Customizing factory data
    
    Override specific fields while keeping others auto-generated
    """
    
    # Custom title, auto-generate rest
    post1 = PostFactory.create(title="My Custom Title")
    assert post1["title"] == "My Custom Title"
    assert "body" in post1  # Auto-generated
    
    # Custom user, auto-generate rest
    post2 = PostFactory.create(user_id=99)
    assert post2["userId"] == 99
    assert "title" in post2  # Auto-generated
    
    print("✅ Factory customization works")


def test_user_factory():
    """
    LESSON: Generating complex nested data
    
    Factory handles nested objects (address, company)
    """
    
    user_data = UserFactory.create()
    
    print(f"\n👤 Generated user:")
    print(f"   Name: {user_data['name']}")
    print(f"   Email: {user_data['email']}")
    print(f"   City: {user_data['address']['city']}")
    print(f"   Company: {user_data['company']['name']}")
    
    # Verify structure
    assert "name" in user_data
    assert "email" in user_data
    assert "address" in user_data
    assert "city" in user_data["address"]
    assert "geo" in user_data["address"]
    assert "company" in user_data
    
    print("✅ User factory generates complete nested structure")


def test_login_with_factory():
    """
    LESSON: Using factory for authentication
    
    Note: accessToken, not token!
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # Get test credentials from factory
        credentials = LoginFactory.create_dummyjson_credentials()
        
        print(f"\n🔐 Testing login with: {credentials['username']}")
        
        # Login
        response = request_context.post(
            "/auth/login",
            data=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status == 200
        
        # Validate response
        SchemaValidator.validate_response(response, DUMMYJSON_LOGIN_SCHEMA)
        
        login_data = response.json()
        
        # Extract accessToken (not token!)
        access_token = login_data["accessToken"]
        
        print(f"✅ Logged in as: {login_data['username']}")
        print(f"   Access Token: {access_token[:30]}...")
        
        # Use token
        me_response = request_context.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert me_response.status == 200
        print(f"✅ Token works!")
        
    finally:
        request_context.dispose()


@pytest.mark.parametrize("count", [3, 5, 10])
def test_factory_batch_sizes(count):
    """
    LESSON: Parametrized factory batch creation
    
    Test with different batch sizes
    """
    
    posts = PostFactory.create_batch(count=count)
    
    assert len(posts) == count
    
    # Verify all are unique
    titles = [p["title"] for p in posts]
    assert len(titles) == len(set(titles))  # All unique
    
    print(f"✅ Created {count} unique posts")


def test_product_factory_categories():
    """
    LESSON: Category-specific data generation
    """
    
    # Create products in different categories
    smartphone = ProductFactory.create_by_category("smartphones")
    laptop = ProductFactory.create_by_category("laptops")
    furniture = ProductFactory.create_by_category("furniture")
    
    assert smartphone["category"] == "smartphones"
    assert laptop["category"] == "laptops"
    assert furniture["category"] == "furniture"
    
    print(f"✅ Created products in different categories:")
    print(f"   - {smartphone['title']} ({smartphone['category']})")
    print(f"   - {laptop['title']} ({laptop['category']})")
    print(f"   - {furniture['title']} ({furniture['category']})")


def test_realistic_data_generation():
    """
    LESSON: Faker generates realistic data
    
    Useful for:
    - Demo environments
    - Load testing
    - Frontend development
    """
    
    # Generate 10 users
    users = UserFactory.create_batch(count=10)
    
    print("\n👥 Generated 10 realistic users:")
    for i, user in enumerate(users[:3], 1):  # Print first 3
        print(f"\n{i}. {user['name']}")
        print(f"   Email: {user['email']}")
        print(f"   Phone: {user['phone']}")
        print(f"   Company: {user['company']['name']}")
        print(f"   Location: {user['address']['city']}")
    
    print(f"\n✅ All {len(users)} users have realistic data")