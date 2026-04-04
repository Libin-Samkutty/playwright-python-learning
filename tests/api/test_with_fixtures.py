"""
Module 2 - Part 3: Using Fixtures in API Tests
-----------------------------------------------
Demonstrates how fixtures make tests cleaner and more maintainable
"""

def test_get_posts_with_fixture(api_context):
    """
    LESSON: Using the basic api_context fixture
    
    Notice how much cleaner this is compared to manual setup/teardown!
    """
    # No setup code needed - fixture handles it
    
    response = api_context.get("https://jsonplaceholder.typicode.com/posts")
    
    assert response.status == 200
    posts = response.json()
    assert len(posts) > 0
    
    # No cleanup code needed - fixture handles it automatically


def test_get_with_base_url(api_context_with_base_url):
    """
    LESSON: Using fixture with base URL
    
    Notice we use "/posts" instead of full URL
    """
    # Relative URL - base_url is automatically prepended
    response = api_context_with_base_url.get("/posts/1")
    
    assert response.status == 200
    post = response.json()
    assert post["id"] == 1


def test_create_with_base_url(api_context_with_base_url):
    """
    POST request with base URL fixture
    """
    new_post = {
        "title": "Test with Base URL",
        "body": "Using fixture with base URL",
        "userId": 1
    }
    
    # Relative URL
    response = api_context_with_base_url.post("/posts", data=new_post)
    
    assert response.status == 201
    created = response.json()
    assert created["title"] == new_post["title"]


def test_with_headers_fixture(api_context_with_headers):
    """
    LESSON: Using fixture with pre-configured headers
    
    Headers are automatically sent with every request
    """
    response = api_context_with_headers.get("/posts/1")
    
    assert response.status == 200
    # Custom headers were automatically included


def test_update_existing_post(created_post, api_context):
    """
    LESSON: Using data fixture
    
    The 'created_post' fixture creates a post before this test runs.
    This is useful for testing UPDATE/DELETE operations.
    """
    # 'created_post' is already created by the fixture
    # JSONPlaceholder simulates creation with ID 101 but doesn't persist it.
    # Use a known valid ID (1-100) for the actual PUT request.
    valid_id = created_post["id"] if created_post["id"] <= 100 else 1
    print(f"Testing with post ID: {valid_id}")

    # Update the post
    updated_data = {
        "id": valid_id,
        "title": "Updated by Test",
        "body": "This was updated in the test",
        "userId": created_post["userId"]
    }

    response = api_context.put(
        f"https://jsonplaceholder.typicode.com/posts/{valid_id}",
        data=updated_data
    )
    
    assert response.status == 200
    updated_post = response.json()
    assert updated_post["title"] == updated_data["title"]


def test_delete_existing_post(created_post, api_context):
    """
    LESSON: Testing deletion with data fixture
    """
    # Delete the post created by fixture
    response = api_context.delete(
        f"https://jsonplaceholder.typicode.com/posts/{created_post['id']}"
    )
    
    assert response.status in [200, 204]


def test_multiple_fixtures(created_post, created_user, api_context):
    """
    LESSON: Using multiple fixtures in one test
    
    Pytest automatically handles the dependency order
    """
    # Both fixtures have run - we have a post and a user
    print(f"Post ID: {created_post['id']}")
    print(f"User ID: {created_user['id']}")
    
    # Use both in your test logic
    assert created_post["userId"] > 0
    assert created_user["id"] > 0

def test_user_lifecycle(api_context):
    """Complete user management lifecycle"""
    
    # 1. Create user
    new_user = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com"
    }
    
    create_resp = api_context.post(
        "https://jsonplaceholder.typicode.com/users",
        data=new_user
    )
    assert create_resp.status == 201
    user = create_resp.json()
    # JSONPlaceholder doesn't persist POSTed data; verify creation from the response
    assert user["name"] == new_user["name"]
    assert user["email"] == new_user["email"]

    # 2. Verify an existing user (JSONPlaceholder only has users 1-10)
    existing_user_id = 1
    get_resp = api_context.get(
        f"https://jsonplaceholder.typicode.com/users/{existing_user_id}"
    )
    assert get_resp.status == 200
    assert get_resp.json()["id"] == existing_user_id

    # 3. Update user (using a known existing ID since POST data isn't persisted)
    updated_data = {
        "id": existing_user_id,
        "name": "John Doe Updated",
        "username": user["username"],
        "email": user["email"]
    }

    update_resp = api_context.put(
        f"https://jsonplaceholder.typicode.com/users/{existing_user_id}",
        data=updated_data
    )
    assert update_resp.status == 200
    assert update_resp.json()["name"] == "John Doe Updated"

    # 4. Delete user
    delete_resp = api_context.delete(
        f"https://jsonplaceholder.typicode.com/users/{existing_user_id}"
    )
    assert delete_resp.status in [200, 204]
    
    print("✅ User lifecycle test complete!")
