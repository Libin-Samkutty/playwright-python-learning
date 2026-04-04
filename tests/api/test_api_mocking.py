"""
Module 4 - Part 3: API Mocking with Playwright
-----------------------------------------------
Learn how to intercept and mock API responses

Real-world usage:
- Test error scenarios (500, 503)
- Test slow APIs (timeouts)
- Test without external dependencies
- Test edge cases (empty arrays, null values)

KEY CONCEPT: context.route() / page.route() only intercept requests made by
the browser rendering engine. Neither context.request nor page.request
(APIRequestContext) go through route handlers — they are direct HTTP clients.
To trigger route handlers, use page.evaluate() to run fetch() inside the
browser page itself.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _page_fetch(page, url, method="GET", body=None, headers=None):
    """Run fetch() inside the browser page so context.route() fires.

    Returns dict: { status: int, ok: bool, body: str }
    """
    return page.evaluate(
        """async ([url, method, body, headers]) => {
            const opts = { method, headers: headers || {} };
            if (body !== null && body !== undefined) opts.body = body;
            const resp = await fetch(url, opts);
            const text = await resp.text();
            return { status: resp.status, ok: resp.ok, body: text };
        }""",
        [url, method, body, headers or {}]
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_mock_basic():
    """
    LESSON: Basic API mocking

    Intercept API call and return custom response

    Real-world: Test UI behavior with specific API responses
    """

    browser = _pw_state.get_browser()
    context = browser.new_context()

    try:
        # ========================================
        # Setup mock
        # ========================================

        def handle_route(route):
            """
            Custom route handler

            This function intercepts the API call and returns mock data
            """
            print(f"\n[MOCK] Intercepted: {route.request.url}")

            # Create mock response
            mock_data = {
                "userId": 1,
                "id": 1,
                "title": "MOCKED POST TITLE",
                "body": "This is a mocked response, not real API data"
            }

            # Return mocked response
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_data)
            )

        # Intercept ALL requests to this URL pattern
        context.route(
            "**/posts/1",  # Pattern to match
            handle_route   # Handler function
        )

        # ========================================
        # Make API call via page.evaluate so the route fires
        # ========================================

        page = context.new_page()
        result = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/1")

        assert result["status"] == 200
        data = json.loads(result["body"])

        # Verify we got MOCKED data, not real data
        assert data["title"] == "MOCKED POST TITLE"
        assert "mocked response" in data["body"]

        print(f"\n[OK] Got mocked data: {data['title']}")

    finally:
        context.close()


def test_mock_error_response():
    """
    LESSON: Mock error responses (500, 404, etc.)

    Real-world: Test how your app handles server errors
    """

    browser = _pw_state.get_browser()
    context = browser.new_context()

    try:
        # ========================================
        # Mock 500 Internal Server Error
        # ========================================

        def handle_500_error(route):
            """Return 500 error"""
            print(f"\n[MOCK] Returning 500 error for: {route.request.url}")

            error_response = {
                "error": "Internal Server Error",
                "message": "Database connection failed"
            }

            route.fulfill(
                status=500,
                content_type="application/json",
                body=json.dumps(error_response)
            )

        context.route("**/posts/**", handle_500_error)

        # ========================================
        # Test error handling
        # ========================================

        page = context.new_page()
        result = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/1")

        # Verify error response
        assert result["status"] == 500
        assert result["ok"] is False

        error_data = json.loads(result["body"])
        assert "error" in error_data

        print(f"[OK] Successfully tested 500 error: {error_data['error']}")

    finally:
        context.close()


def test_mock_404_not_found():
    """
    LESSON: Mock 404 Not Found

    Real-world: Test UI when resource doesn't exist
    """

    browser = _pw_state.get_browser()
    context = browser.new_context()

    try:
        def handle_404(route):
            """Return 404"""
            route.fulfill(
                status=404,
                content_type="application/json",
                body=json.dumps({"error": "Post not found"})
            )

        context.route("**/posts/999", handle_404)

        page = context.new_page()
        result = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/999")

        assert result["status"] == 404
        print("[OK] Successfully tested 404 error")

    finally:
        context.close()


def test_mock_slow_response():
    """
    LESSON: Mock slow API responses

    Real-world: Test timeout handling, loading states
    """

    import time

    browser = _pw_state.get_browser()
    context = browser.new_context()

    try:
        def handle_slow_response(route):
            """Simulate slow API"""
            print("\n[MOCK] Simulating slow response...")

            # Simulate 2-second delay
            time.sleep(2)

            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"message": "This was delayed"})
            )

        context.route("**/posts/1", handle_slow_response)

        page = context.new_page()

        start_time = time.time()
        result = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/1")
        elapsed = time.time() - start_time

        assert result["status"] == 200
        assert elapsed >= 2, "Response should have been delayed"

        print(f"[OK] Response delayed by {elapsed:.2f} seconds")

    finally:
        context.close()


def test_mock_empty_array():
    """
    LESSON: Mock edge case - empty array

    Real-world: Test UI with no data
    """

    browser = _pw_state.get_browser()
    context = browser.new_context()

    try:
        def handle_empty_array(route):
            """Return empty array"""
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps([])  # Empty array
            )

        context.route("**/posts**", handle_empty_array)

        page = context.new_page()
        result = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts")

        assert result["status"] == 200
        data = json.loads(result["body"])

        assert isinstance(data, list)
        assert len(data) == 0

        print("[OK] Successfully tested empty array response")

    finally:
        context.close()


def test_mock_conditional_response():
    """
    LESSON: Conditional mocking based on request

    Real-world: Different responses for different requests
    """

    browser = _pw_state.get_browser()
    context = browser.new_context()

    try:
        def handle_conditional(route):
            """Different responses based on URL"""
            url = route.request.url

            if "/posts/1" in url:
                # Mock post 1
                route.fulfill(
                    status=200,
                    body=json.dumps({"id": 1, "title": "Mocked Post 1"})
                )
            elif "/posts/2" in url:
                # Mock post 2
                route.fulfill(
                    status=200,
                    body=json.dumps({"id": 2, "title": "Mocked Post 2"})
                )
            else:
                # Pass through to real API
                route.continue_()

        context.route("**/posts/**", handle_conditional)

        page = context.new_page()

        # Test post 1
        result1 = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/1")
        data1 = json.loads(result1["body"])
        assert data1["title"] == "Mocked Post 1"

        # Test post 2
        result2 = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/2")
        data2 = json.loads(result2["body"])
        assert data2["title"] == "Mocked Post 2"

        print("[OK] Conditional mocking works")

    finally:
        context.close()


def test_mock_post_request():
    """
    LESSON: Mock POST request

    Real-world: Test resource creation without hitting real API
    """

    browser = _pw_state.get_browser()
    context = browser.new_context()

    try:
        def handle_post_create(route):
            """Mock POST request"""
            request = route.request

            # Get request body (sent as JSON)
            post_data = request.post_data_json

            print(f"\n[MOCK] Received POST data: {post_data}")

            # Create mock response with generated ID
            created_post = {
                **post_data,
                "id": 999,  # Mocked ID
                "createdAt": "2024-01-01T00:00:00Z"
            }

            route.fulfill(
                status=201,
                body=json.dumps(created_post)
            )

        context.route("**/posts", handle_post_create)

        page = context.new_page()

        new_post = {
            "title": "Test Post",
            "body": "Test body",
            "userId": 1
        }

        # Send as JSON so post_data_json is populated in the handler
        result = _page_fetch(
            page,
            "https://jsonplaceholder.typicode.com/posts",
            method="POST",
            body=json.dumps(new_post),
            headers={"Content-Type": "application/json"}
        )

        assert result["status"] == 201
        created = json.loads(result["body"])

        assert created["id"] == 999
        assert created["title"] == "Test Post"

        print(f"[OK] Mocked POST successful: ID {created['id']}")

    finally:
        context.close()


def test_mock_with_fixture():
    """
    LESSON: Create reusable mock fixture

    This pattern is for demonstration; in practice you'd put this in conftest.py
    """

    browser = _pw_state.get_browser()
    context = browser.new_context()

    try:
        # Setup multiple mocks
        mocks = {
            "**/posts/1": {
                "status": 200,
                "body": {"id": 1, "title": "Mocked Title 1"}
            },
            "**/posts/2": {
                "status": 200,
                "body": {"id": 2, "title": "Mocked Title 2"}
            },
            "**/posts/404": {
                "status": 404,
                "body": {"error": "Not found"}
            }
        }

        # Apply all mocks — use a factory so the handler only takes `route`,
        # preventing Playwright from passing route.request into config.
        def make_handler(config):
            def handler(route):
                route.fulfill(
                    status=config["status"],
                    body=json.dumps(config["body"])
                )
            return handler

        for pattern, mock_config in mocks.items():
            context.route(pattern, make_handler(mock_config))

        page = context.new_page()

        # Test all mocks
        r1 = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/1")
        assert json.loads(r1["body"])["title"] == "Mocked Title 1"

        r2 = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/2")
        assert json.loads(r2["body"])["title"] == "Mocked Title 2"

        r404 = _page_fetch(page, "https://jsonplaceholder.typicode.com/posts/404")
        assert r404["status"] == 404

        print("[OK] All mocks working")

    finally:
        context.close()


def test_with_mock_error():
    """Mock a server error on a search endpoint."""

    browser = _pw_state.get_browser()
    ctx = browser.new_context()

    try:
        ctx.route("**/products/search**", lambda route: route.fulfill(
            status=500,
            body=json.dumps({"error": "Server error"})
        ))

        page = ctx.new_page()
        result = _page_fetch(page, "https://dummyjson.com/products/search?q=test")
        assert result["status"] == 500
        print("[OK] Error handling tested")
    finally:
        ctx.close()
