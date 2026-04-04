"""
Module 4 - Part 1: Using API Clients in Tests
----------------------------------------------
Demonstrates how API clients make tests cleaner and more maintainable
"""

import pytest
import sys
import os

# Add clients directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clients'))
from clients.base_client import JSONPlaceholderClient, DummyJSONClient


def test_with_jsonplaceholder_client():
    """
    LESSON: Using API client for cleaner tests
    
    Compare:
    WITHOUT CLIENT:
        ctx = playwright.request.new_context(...)
        response = ctx.get("https://jsonplaceholder.typicode.com/posts/1")
        assert response.status == 200
        data = response.json()
    
    WITH CLIENT:
        client = JSONPlaceholderClient()
        post = client.get_post(1)  # ✅ Clean and simple!
    """
    
    client = JSONPlaceholderClient()
    
    try:
        # ========================================
        # Test 1: Get single post
        # ========================================
        print("\n📝 Getting post...")
        
        post = client.get_post(1)
        
        # Client already handled status check and JSON parsing
        assert post["id"] == 1
        assert "title" in post
        assert "body" in post
        
        print(f"✅ Got post: {post['title'][:50]}...")
        
        # ========================================
        # Test 2: Get posts by user
        # ========================================
        print("\n📚 Getting posts by user...")
        
        user_posts = client.get_posts(user_id=1)
        
        assert len(user_posts) > 0
        for post in user_posts:
            assert post["userId"] == 1
        
        print(f"✅ Found {len(user_posts)} posts for user 1")
        
        # ========================================
        # Test 3: Create post
        # ========================================
        print("\n✏️ Creating post...")
        
        new_post = client.create_post(
            title="Test Post via Client",
            body="This is much cleaner!",
            user_id=1
        )
        
        assert new_post["title"] == "Test Post via Client"
        assert "id" in new_post
        
        print(f"✅ Created post ID: {new_post['id']}")
        
        # ========================================
        # Test 4: Update post
        # ========================================
        print("\n📝 Updating post...")
        
        updated = client.update_post(
            post_id=1,
            title="Updated Title"
        )
        
        assert updated["title"] == "Updated Title"
        assert updated["id"] == 1
        
        print(f"✅ Updated post: {updated['title']}")
        
        # ========================================
        # Test 5: Delete post
        # ========================================
        print("\n🗑️ Deleting post...")
        
        result = client.delete_post(1)
        assert result is True
        
        print("✅ Post deleted")
        
    finally:
        client.dispose()


def test_with_dummyjson_client():
    """
    LESSON: Using authenticated client
    
    Client handles token management automatically
    """
    
    client = DummyJSONClient()
    
    try:
        # ========================================
        # Test 1: Login
        # ========================================
        print("\n🔐 Logging in...")
        
        login_result = client.login("emilys", "emilyspass")
        
        assert "accessToken" in login_result
        assert "id" in login_result
        
        print(f"✅ Logged in as: {login_result['username']}")
        
        # ========================================
        # Test 2: Get current user
        # ========================================
        print("\n👤 Getting current user...")
        
        user = client.get_current_user()
        
        assert user["username"] == "emilys"
        assert "email" in user
        
        print(f"✅ Current user: {user['firstName']} {user['lastName']}")
        
        # ========================================
        # Test 3: Search products
        # ========================================
        print("\n🔍 Searching products...")
        
        results = client.search_products("phone")
        
        assert "products" in results
        products = results["products"]
        
        print(f"✅ Found {len(products)} products")
        
        # ========================================
        # Test 4: Get paginated products
        # ========================================
        print("\n📄 Getting paginated products...")
        
        page1 = client.get_products(limit=5, skip=0)
        page2 = client.get_products(limit=5, skip=5)
        
        assert len(page1["products"]) == 5
        assert len(page2["products"]) == 5
        
        # Different products on each page
        page1_ids = [p["id"] for p in page1["products"]]
        page2_ids = [p["id"] for p in page2["products"]]
        
        assert set(page1_ids).isdisjoint(set(page2_ids))
        
        print("✅ Pagination working correctly")
        
    finally:
        client.dispose()


def test_client_error_handling():
    """
    LESSON: Client error handling
    
    Clients provide better error messages
    """
    
    client = JSONPlaceholderClient()
    
    try:
        # Try to get non-existent post
        try:
            post = client.get_post(999999)
            pytest.fail("Should have raised assertion error")
        except AssertionError as e:
            # Client provides helpful error message
            assert "404" in str(e)
            print(f"✅ Error handling works: {e}")
        
    finally:
        client.dispose()


def test_multiple_clients():
    """
    LESSON: Using multiple clients in one test
    
    Real-world: Testing integrations between services
    """
    
    jp_client = JSONPlaceholderClient()
    dj_client = DummyJSONClient()
    
    try:
        # Get data from JSONPlaceholder
        posts = jp_client.get_posts(limit=5)
        print(f"\n✅ Got {len(posts)} posts from JSONPlaceholder")
        
        # Login to DummyJSON
        dj_client.login("emilys", "emilyspass")
        products = dj_client.get_products(limit=5)
        print(f"✅ Got {products['total']} products from DummyJSON")
        
        # Both clients work independently
        assert len(posts) == 5
        assert len(products["products"]) == 5
        
    finally:
        jp_client.dispose()
        dj_client.dispose()
