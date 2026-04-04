"""
Base API Client
---------------
Reusable API client with common functionality.

Benefits:
- DRY (Don't Repeat Yourself)
- Centralized error handling
- Consistent request/response handling
- Easy to mock in tests
"""

import sys
import os
import pytest
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import playwright_state as _pw_state


class BaseAPIClient:
    """
    Base class for API clients
    
    Provides common functionality for all API interactions:
    - Request context management
    - Common headers
    - Error handling
    - Response parsing
    """
    
    def __init__(self, base_url, headers=None):
        """
        Initialize API client
        
        Args:
            base_url: Base URL for API (e.g., "https://api.example.com")
            headers: Optional default headers dict
        """
        self.base_url = base_url
        self.default_headers = headers or {}
        self._context = None
    
    def _get_context(self):
        """Get or create request context (lazy initialization)"""
        if self._context is None:
            playwright = _pw_state.get_playwright()
            self._context = playwright.request.new_context(
                base_url=self.base_url,
                extra_http_headers=self.default_headers
            )
        return self._context
    
    def dispose(self):
        """Clean up request context"""
        if self._context:
            self._context.dispose()
            self._context = None
    
    def get(self, endpoint, params=None, headers=None):
        """
        Make GET request
        
        Args:
            endpoint: API endpoint (e.g., "/users/1")
            params: Optional query parameters dict
            headers: Optional request headers dict
        
        Returns:
            Response object
        """
        ctx = self._get_context()
        
        # Build URL with query params
        url = endpoint
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{endpoint}?{query_string}"
        
        # Merge headers
        request_headers = {**self.default_headers, **(headers or {})}
        
        return ctx.get(url, headers=request_headers if request_headers != self.default_headers else None)
    
    def post(self, endpoint, data=None, headers=None):
        """
        Make POST request
        
        Args:
            endpoint: API endpoint
            data: Request body (dict, will be converted to JSON)
            headers: Optional request headers dict
        
        Returns:
            Response object
        """
        ctx = self._get_context()
        request_headers = {**self.default_headers, **(headers or {})}
        
        return ctx.post(
            endpoint,
            data=data,
            headers=request_headers if request_headers != self.default_headers else None
        )
    
    def put(self, endpoint, data=None, headers=None):
        """Make PUT request"""
        ctx = self._get_context()
        request_headers = {**self.default_headers, **(headers or {})}
        
        return ctx.put(
            endpoint,
            data=data,
            headers=request_headers if request_headers != self.default_headers else None
        )
    
    def patch(self, endpoint, data=None, headers=None):
        """Make PATCH request"""
        ctx = self._get_context()
        request_headers = {**self.default_headers, **(headers or {})}
        
        return ctx.patch(
            endpoint,
            data=data,
            headers=request_headers if request_headers != self.default_headers else None
        )
    
    def delete(self, endpoint, headers=None):
        """Make DELETE request"""
        ctx = self._get_context()
        request_headers = {**self.default_headers, **(headers or {})}
        
        return ctx.delete(
            endpoint,
            headers=request_headers if request_headers != self.default_headers else None
        )
    
    def assert_success(self, response, expected_status=200):
        """
        Assert response is successful
        
        Args:
            response: Response object
            expected_status: Expected status code (default 200)
        
        Raises:
            AssertionError: If status doesn't match
        """
        assert response.status == expected_status, \
            f"Expected status {expected_status}, got {response.status}. Response: {response.text()}"
    
    def get_json(self, response):
        """
        Parse response as JSON with error handling
        
        Args:
            response: Response object
        
        Returns:
            Parsed JSON data
        
        Raises:
            ValueError: If response is not valid JSON
        """
        try:
            return response.json()
        except Exception as e:
            raise ValueError(f"Failed to parse JSON: {e}. Response: {response.text()}")


class JSONPlaceholderClient(BaseAPIClient):
    """
    Client for JSONPlaceholder API
    
    Real-world example: Specific client for a service
    """
    
    def __init__(self):
        super().__init__(
            base_url="https://jsonplaceholder.typicode.com",
            headers={"Content-Type": "application/json"}
        )
    
    def get_posts(self, user_id=None, limit=None):
        """
        Get posts, optionally filtered by user
        
        Args:
            user_id: Optional user ID to filter by
            limit: Optional limit for results
        
        Returns:
            List of posts
        """
        params = {}
        if user_id:
            params["userId"] = user_id
        if limit:
            params["_limit"] = limit
        
        response = self.get("/posts", params=params)
        self.assert_success(response)
        return self.get_json(response)
    
    def get_post(self, post_id):
        """Get single post by ID"""
        response = self.get(f"/posts/{post_id}")
        self.assert_success(response)
        return self.get_json(response)
    
    def create_post(self, title, body, user_id):
        """
        Create a new post
        
        Args:
            title: Post title
            body: Post content
            user_id: User ID
        
        Returns:
            Created post data
        """
        data = {
            "title": title,
            "body": body,
            "userId": user_id
        }
        
        response = self.post("/posts", data=data)
        self.assert_success(response, expected_status=201)
        return self.get_json(response)
    
    def update_post(self, post_id, title=None, body=None, user_id=None):
        """Update existing post"""
        # First get current post
        current = self.get_post(post_id)
        
        # Update fields
        updated = {
            "id": post_id,
            "title": title or current["title"],
            "body": body or current["body"],
            "userId": user_id or current["userId"]
        }
        
        response = self.put(f"/posts/{post_id}", data=updated)
        self.assert_success(response)
        return self.get_json(response)
    
    def delete_post(self, post_id):
        """Delete post"""
        response = self.delete(f"/posts/{post_id}")
        self.assert_success(response)
        return True
    
    def get_users(self):
        """Get all users"""
        response = self.get("/users")
        self.assert_success(response)
        return self.get_json(response)
    
    def get_user(self, user_id):
        """Get single user"""
        response = self.get(f"/users/{user_id}")
        self.assert_success(response)
        return self.get_json(response)


class DummyJSONClient(BaseAPIClient):
    """
    Client for DummyJSON API
    
    Includes authentication support
    """
    
    def __init__(self):
        super().__init__(
            base_url="https://dummyjson.com",
            headers={"Content-Type": "application/json"}
        )
        self._token = None
    
    def login(self, username, password):
        """
        Login and store token
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Login response data
        """
        data = {
            "username": username,
            "password": password
        }
        
        response = self.post("/auth/login", data=data)
        self.assert_success(response)
        
        result = self.get_json(response)
        self._token = result["accessToken"]
        
        # Update default headers with token
        self.default_headers["Authorization"] = f"Bearer {self._token}"
        
        return result
    
    def get_current_user(self):
        """Get current authenticated user"""
        if not self._token:
            raise ValueError("Not authenticated. Call login() first.")
        
        response = self.get("/auth/me")
        self.assert_success(response)
        return self.get_json(response)
    
    def get_products(self, limit=None, skip=None):
        """Get products with pagination"""
        params = {}
        if limit:
            params["limit"] = limit
        if skip:
            params["skip"] = skip
        
        response = self.get("/products", params=params)
        self.assert_success(response)
        return self.get_json(response)
    
    def search_products(self, query):
        """Search products"""
        params = {"q": query}
        response = self.get("/products/search", params=params)
        self.assert_success(response)
        return self.get_json(response)
    
    def get_product(self, product_id):
        """Get single product"""
        response = self.get(f"/products/{product_id}")
        self.assert_success(response)
        return self.get_json(response)
    
class MyDummyClient(BaseAPIClient):
    def __init__(self):
        super().__init__("https://dummyjson.com")
        self._token = None
    
    def login(self, username, password):
        resp = self.post("/auth/login", data={
            "username": username,
            "password": password
        })
        self.assert_success(resp)
        result = self.get_json(resp)
        self._token = result["accessToken"]
        self.default_headers["Authorization"] = f"Bearer {self._token}"
        return result
    
    def search(self, query):
        resp = self.get(f"/products/search?q={query}")
        self.assert_success(resp)
        return self.get_json(resp)

# 2. Fixture
@pytest.fixture
def auth_client():
    client = MyDummyClient()
    client.login("emilys", "emilyspass")
    yield client
    client.dispose()

# 3. Parametrized test
@pytest.mark.parametrize("query", ["phone", "laptop", "watch"])
def test_search_products(query, auth_client):
    results = auth_client.search(query)
    assert len(results["products"]) > 0
    print(f"Found {len(results['products'])} {query}s")