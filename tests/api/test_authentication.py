"""
Module 3 - Part 1: Authentication & Authorization
--------------------------------------------------
Learn how to handle authentication in API tests:
- Token-based authentication
- Bearer tokens
- API keys
- Session management

Real-world APIs used:
- Restful Booker (token auth)
- DummyJSON (JWT tokens)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


def test_basic_auth_restful_booker():
    """
    LESSON: Token-based authentication flow
    
    Real-world scenario: User login to get authentication token
    
    Flow:
    1. POST credentials to /auth
    2. Receive token
    3. Use token in subsequent requests
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://restful-booker.herokuapp.com"
    )
    
    try:
        # ========================================
        # STEP 1: Authenticate and get token
        # ========================================
        print("\nStep 1: Authenticating...")
        
        auth_data = {
            "username": "admin",
            "password": "password123"
        }
        
        auth_response = request_context.post(
            "/auth",
            data=auth_data
        )
        
        # Verify authentication successful
        assert auth_response.status == 200, \
            f"Authentication failed with status {auth_response.status}"
        
        auth_result = auth_response.json()
        print(f"Auth response: {auth_result}")
        
        # Extract token
        assert "token" in auth_result, "Response missing 'token' field"
        token = auth_result["token"]
        
        print(f"Got token: {token[:20]}...")  # Print first 20 chars
        
        # ========================================
        # STEP 2: Use token to create a booking
        # ========================================
        print("\n📝 Step 2: Creating booking with token...")
        
        new_booking = {
            "firstname": "John",
            "lastname": "Doe",
            "totalprice": 111,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2024-01-01",
                "checkout": "2024-01-05"
            },
            "additionalneeds": "Breakfast"
        }
        
        # Create booking (this endpoint doesn't require auth for POST)
        create_response = request_context.post(
            "/booking",
            data=new_booking
        )
        
        assert create_response.status == 200
        booking_result = create_response.json()
        booking_id = booking_result["bookingid"]
        
        print(f" Created booking ID: {booking_id}")
        
        # ========================================
        # STEP 3: Update booking (requires auth)
        # ========================================
        print("\nStep 3: Updating booking with token...")
        
        updated_booking = {
            "firstname": "Jane",  # Changed from John
            "lastname": "Doe",
            "totalprice": 150,    # Changed from 111
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2024-01-01",
                "checkout": "2024-01-05"
            },
            "additionalneeds": "Breakfast and Dinner"  # Updated
        }
        
        # PUT request with authentication token
        # Note: Restful Booker uses Cookie authentication
        update_response = request_context.put(
            f"/booking/{booking_id}",
            data=updated_booking,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Cookie": f"token={token}"  # ← Token sent as cookie
            }
        )
        
        print(f"Update status: {update_response.status}")
        
        # Verify update successful
        assert update_response.status == 200, \
            f"Update failed with status {update_response.status}"
        
        updated_result = update_response.json()
        assert updated_result["firstname"] == "Jane"
        assert updated_result["totalprice"] == 150
        
        print(f" Booking updated: {updated_result['firstname']}")
        
        # ========================================
        # STEP 4: Delete booking (requires auth)
        # ========================================
        print("\nStep 4: Deleting booking with token...")
        
        delete_response = request_context.delete(
            f"/booking/{booking_id}",
            headers={
                "Cookie": f"token={token}"  # Auth required for delete
            }
        )
        
        # Delete returns 201 in this API (unusual, but that's the API design)
        assert delete_response.status == 201, \
            f"Delete failed with status {delete_response.status}"
        
        print(f" Booking deleted successfully")
        
    finally:
        request_context.dispose()


def test_bearer_token_auth_dummyjson():
    """
    LESSON: Bearer token authentication (most common in modern APIs)
    
    Real-world: JWT tokens, OAuth2 access tokens
    
    Format: Authorization: Bearer <token>
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # ========================================
        # STEP 1: Login to get JWT token
        # ========================================
        print("\nLogging in to get JWT token...")
        
        login_data = {
            "username": "emilys",  # DummyJSON test user
            "password": "emilyspass"
        }
        
        login_response = request_context.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert login_response.status == 200, \
            f"Login failed: {login_response.status}"
        
        login_result = login_response.json()
        print(f"Login response keys: {login_result.keys()}")
        
        # Extract JWT token
        assert "accessToken" in login_result, "No token in response"
        jwt_token = login_result["accessToken"]
        
        print(f" JWT Token received: {jwt_token[:30]}...")
        
        # Also get user info from response
        user_id = login_result.get("id")
        print(f"User ID: {user_id}")
        
        # ========================================
        # STEP 2: Access protected endpoint with Bearer token
        # ========================================
        print("\n🔒 Accessing protected endpoint...")
        
        # Get current user info (requires authentication)
        me_response = request_context.get(
            "/auth/me",
            headers={
                "Authorization": f"Bearer {jwt_token}"  # ← Bearer token format
            }
        )
        
        assert me_response.status == 200, \
            f"Protected endpoint failed: {me_response.status}"
        
        user_info = me_response.json()
        print(f" Got user info: {user_info.get('username')}")
        
        # Validate user info
        assert user_info["username"] == "emilys"
        assert "email" in user_info
        
        # ========================================
        # STEP 3: Refresh token (get new token)
        # ========================================
        print("\nRefreshing token...")
        
        refresh_response = request_context.post(
            "/auth/refresh",
            headers={
                "Authorization": f"Bearer {jwt_token}"
            }
        )
        
        if refresh_response.status == 200:
            refresh_result = refresh_response.json()
            new_token = refresh_result.get("accessToken")
            print(f" New token received: {new_token[:30]}...")
        else:
            print(f"Refresh returned: {refresh_response.status}")
        
    finally:
        request_context.dispose()


def test_auth_failure_scenarios():
    """
    LESSON: Negative testing - authentication failures
    
    Real-world: Verify your API properly rejects invalid auth attempts
    This is CRITICAL for security testing
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # ========================================
        # TEST 1: Invalid credentials
        # ========================================
        print("\nTest 1: Invalid credentials...")
        
        invalid_login = {
            "username": "wronguser",
            "password": "wrongpassword"
        }
        
        response = request_context.post(
            "/auth/login",
            data=invalid_login,
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 400 Bad Request or 401 Unauthorized
        print(f"Invalid login status: {response.status}")
        assert response.status in [400, 401], \
            "API should reject invalid credentials"
        
        error_data = response.json()
        print(f"Error message: {error_data}")
        
        # ========================================
        # TEST 2: Missing credentials
        # ========================================
        print("\nTest 2: Missing password...")
        
        incomplete_login = {
            "username": "emilys"
            # password missing
        }
        
        response = request_context.post(
            "/auth/login",
            data=incomplete_login,
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 400 Bad Request
        print(f"Missing password status: {response.status}")
        assert response.status == 400, \
            "API should reject incomplete credentials"
        
        # ========================================
        # TEST 3: Accessing protected endpoint without token
        # ========================================
        print("\nTest 3: No authentication token...")
        
        response = request_context.get("/auth/me")
        
        # Should return 401 Unauthorized or 403 Forbidden
        print(f"No token status: {response.status}")
        assert response.status in [401, 403], \
            "Protected endpoint should require authentication"
        
        # ========================================
        # TEST 4: Invalid/expired token
        # ========================================
        print("\nTest 4: Invalid token...")
        
        response = request_context.get(
            "/auth/me",
            headers={
                "Authorization": "Bearer invalid_fake_token_12345"
            }
        )
        
        print(f"Invalid token status: {response.status}")
        assert response.status in [401, 403], \
            "API should reject invalid tokens"
        
        print("\n All negative auth tests passed!")
        
    finally:
        request_context.dispose()


def test_api_key_authentication():
    """
    LESSON: API Key authentication
    
    Real-world: Many APIs use API keys (Stripe, SendGrid, AWS, etc.)
    
    Common formats:
    - Header: X-API-Key: your-key
    - Header: Authorization: ApiKey your-key
    - Query param: ?api_key=your-key
    """
    
    playwright = _pw_state.get_playwright()
    
    # Example: API key in headers
    request_context = playwright.request.new_context(
        base_url="https://api.example.com",
        extra_http_headers={
            "X-API-Key": "your-api-key-here",  # ← API key in header
            # OR
            # "Authorization": "ApiKey your-api-key-here"
        }
    )
    
    try:
        # All requests will include the API key automatically
        # response = request_context.get("/protected-endpoint")
        
        # Example with query parameter (alternative method)
        # Some APIs expect: GET /endpoint?api_key=xxx
        # response = request_context.get("/endpoint?api_key=your-key")
        
        print(" API Key authentication configured")
        
    finally:
        request_context.dispose()

def test_complete_authenticated_flow():
    playwright = _pw_state.get_playwright()
    ctx = playwright.request.new_context(base_url="https://dummyjson.com")
    
    try:
        # 1. Login
        login_resp = ctx.post("/auth/login", data={
            "username": "emilys",
            "password": "emilyspass"
        }, headers={"Content-Type": "application/json"})
        
        assert login_resp.status == 200
        token = login_resp.json()["accessToken"]
        print(f"Logged in, token: {token[:20]}...")
        
        # 2. Get user
        me_resp = ctx.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert me_resp.status == 200
        user = me_resp.json()
        print(f"User: {user['username']}")
        
        # 3. Search products
        search_resp = ctx.get("/products/search?q=phone")
        assert search_resp.status == 200
        
        results = search_resp.json()
        products = results["products"]
        print(f"Found {len(products)} products")
        
        # 4. Paginated products
        page_resp = ctx.get("/products?limit=5&skip=0")
        assert page_resp.status == 200
        
        page_data = page_resp.json()
        assert len(page_data["products"]) == 5
        print(f"Pagination working")
        
        print("\nComplete flow successful!")
        
    finally:
        ctx.dispose()
