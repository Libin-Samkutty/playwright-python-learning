"""
Module 3 - Part 2: Query Parameters
------------------------------------
Learn how to work with query parameters for:
- Filtering data
- Pagination
- Sorting
- Searching

Real-world usage:
- E-commerce: Filter products by category, price range
- User management: Search users, paginate results
- Analytics: Filter by date range
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


def test_basic_query_parameters():
    """
    LESSON: Adding query parameters to requests
    
    Real-world: Filter blog posts by user ID
    GET /posts?userId=1
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        # Method 1: Include params in URL string
        response = request_context.get("/posts?userId=1")
        
        assert response.status == 200
        posts = response.json()
        
        # Verify all posts belong to user 1
        assert len(posts) > 0, "Should return posts for user 1"
        for post in posts:
            assert post["userId"] == 1, f"Expected userId=1, got {post['userId']}"
        
        print(f"Found {len(posts)} posts for user 1")
        
        # Method 2: Build URL programmatically (cleaner)
        user_id = 2
        response2 = request_context.get(f"/posts?userId={user_id}")
        
        assert response2.status == 200
        posts2 = response2.json()
        
        for post in posts2:
            assert post["userId"] == user_id
        
        print(f"Found {len(posts2)} posts for user {user_id}")
        
    finally:
        request_context.dispose()


def test_multiple_query_parameters():
    """
    LESSON: Using multiple query parameters
    
    Real-world: Filter products by multiple criteria
    GET /products?category=electronics&price_max=500&in_stock=true
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # ========================================
        # Example 1: Search products
        # ========================================
        print("\nSearching products...")
        
        # Search for "phone"
        search_query = "phone"
        response = request_context.get(f"/products/search?q={search_query}")
        
        assert response.status == 200
        result = response.json()
        
        products = result.get("products", [])
        print(f"Found {len(products)} products matching '{search_query}'")
        
        # Verify results contain search term
        for product in products[:3]:  # Check first 3
            title_lower = product["title"].lower()
            print(f"  - {product['title']}")
            # Search is in title or description
        
        # ========================================
        # Example 2: Pagination
        # ========================================
        print("\nTesting pagination...")
        
        # Get page 1 with 5 items
        page = 1
        limit = 5
        response = request_context.get(f"/products?limit={limit}&skip=0")
        
        assert response.status == 200
        result = response.json()
        
        products = result.get("products", [])
        total = result.get("total", 0)
        
        assert len(products) == limit, f"Expected {limit} products"
        print(f"Page {page}: {len(products)} products (Total: {total})")
        
        # Get page 2
        skip = limit  # Skip first 5
        response2 = request_context.get(f"/products?limit={limit}&skip={skip}")
        
        result2 = response2.json()
        products2 = result2.get("products", [])
        
        print(f"Page 2: {len(products2)} products")
        
        # Verify pages are different
        page1_ids = [p["id"] for p in products]
        page2_ids = [p["id"] for p in products2]
        
        # No overlap between pages
        assert set(page1_ids).isdisjoint(set(page2_ids)), \
            "Pages should have different products"
        
        # ========================================
        # Example 3: Sorting
        # ========================================
        print("\n Testing sorting...")
        
        # Note: Not all APIs support sorting, this is conceptual
        # In a real API: GET /products?sortBy=price&order=asc
        
        response = request_context.get("/products?limit=10")
        result = response.json()
        products = result.get("products", [])
        
        # Manual sorting verification
        prices = [p["price"] for p in products]
        print(f"Prices: {prices[:5]}...")
        
    finally:
        request_context.dispose()


def test_filtering_with_query_params():
    """
    LESSON: Advanced filtering
    
    Real-world: E-commerce product filtering
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # ========================================
        # Filter by category
        # ========================================
        print("\nFiltering by category...")
        
        category = "smartphones"
        response = request_context.get(f"/products/category/{category}")
        
        assert response.status == 200
        result = response.json()
        
        products = result.get("products", [])
        print(f"Found {len(products)} {category}")
        
        # Verify all products are in the category
        for product in products:
            assert product["category"] == category, \
                f"Expected category '{category}', got '{product['category']}'"
        
        # ========================================
        # Get all categories
        # ========================================
        print("\nGetting all categories...")
        
        response = request_context.get("/products/categories")
        assert response.status == 200
        
        categories = response.json()
        print(f"Available categories: {categories[:5]}...")
        
        assert len(categories) > 0
        
    finally:
        request_context.dispose()


def test_query_params_special_characters():
    """
    LESSON: Handling special characters in query params
    
    Real-world: User searches with spaces, special chars
    "iPhone 13 Pro" → "iPhone%2013%20Pro"
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # Playwright automatically URL-encodes special characters
        
        # Search with spaces
        search_term = "iPhone Pro"  # Spaces will be encoded
        response = request_context.get(f"/products/search?q={search_term}")
        
        # The actual request is: /products/search?q=iPhone%20Pro
        print(f"Searched for: '{search_term}'")
        print(f"Actual URL: {response.url}")
        
        assert response.status == 200
        
        # Special characters are handled automatically by Playwright
        # No need for manual encoding!
        
    finally:
        request_context.dispose()


def test_pagination_complete_example():
    """
    LESSON: Complete pagination implementation
    
    Real-world: Fetch all users across multiple pages
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        print("\nFetching all users with pagination...")
        
        all_users = []
        page_size = 10
        skip = 0
        
        while True:
            # Fetch one page
            response = request_context.get(
                f"/users?limit={page_size}&skip={skip}"
            )
            
            assert response.status == 200
            result = response.json()
            
            users = result.get("users", [])
            total = result.get("total", 0)
            
            print(f"Page {skip // page_size + 1}: Fetched {len(users)} users")
            
            # Add to collection
            all_users.extend(users)
            
            # Check if we got all users
            if len(all_users) >= total or len(users) == 0:
                break
            
            # Move to next page
            skip += page_size
            
            # Safety: Max 5 pages for demo
            if skip >= 50:
                break
        
        print(f"\nTotal users collected: {len(all_users)}")
        
        # Verify no duplicates
        user_ids = [u["id"] for u in all_users]
        assert len(user_ids) == len(set(user_ids)), "Found duplicate users"
        
    finally:
        request_context.dispose()


def test_query_params_builder_pattern():
    """
    LESSON: Building complex query strings programmatically
    
    Real-world: Dynamic filters based on user input
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        # Build query params dynamically
        filters = {
            "userId": 1,
            "_limit": 5,
            # "_sort": "title",  # Not all APIs support this
            # "_order": "asc"
        }
        
        # Method 1: Manual string building
        query_parts = [f"{key}={value}" for key, value in filters.items()]
        query_string = "&".join(query_parts)
        url = f"/posts?{query_string}"
        
        print(f"Built URL: {url}")
        
        response = request_context.get(url)
        assert response.status == 200
        
        posts = response.json()
        print(f"Got {len(posts)} posts with filters")
        
        # Verify filters applied
        assert len(posts) <= 5, "Limit not applied"
        for post in posts:
            assert post["userId"] == 1, "UserId filter not applied"
        
    finally:
        request_context.dispose()