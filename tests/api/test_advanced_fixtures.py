"""
Module 4 - Part 2: Using Advanced Fixtures
-------------------------------------------
Practical examples of advanced fixture patterns
"""

import pytest
import sys
import os

# Import fixtures from advanced_fixtures.py
pytest_plugins = ["tests.api.fixtures.advanced_fixtures"]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clients'))
from clients.base_client import JSONPlaceholderClient


def test_with_function_scope(api_client_function):
    """
    LESSON: Function-scoped fixture
    
    New client instance for THIS test only
    """
    posts = api_client_function.get_posts(limit=3)
    assert len(posts) == 3
    print(f"✅ Got {len(posts)} posts with function-scoped client")


def test_with_module_scope(api_client_module):
    """
    LESSON: Module-scoped fixture
    
    Shares client with ALL tests in this file
    """
    posts = api_client_module.get_posts(limit=5)
    assert len(posts) == 5
    print(f"✅ Got {len(posts)} posts with module-scoped client")


def test_parametrized_user_id(user_id, api_client_function):
    """
    LESSON: Parametrized fixture
    
    This test runs 3 times (for user_id 1, 2, 3)
    
    Test output:
    - test_parametrized_user_id[1] PASSED
    - test_parametrized_user_id[2] PASSED
    - test_parametrized_user_id[3] PASSED
    """
    posts = api_client_function.get_posts(user_id=user_id)
    
    # Verify all posts belong to the user
    for post in posts:
        assert post["userId"] == user_id
    
    print(f"✅ User {user_id} has {len(posts)} posts")


def test_parametrized_search(search_params, api_client_function):
    """
    LESSON: Parametrized fixture with tuples
    
    Runs once for each (query, expected_min) tuple
    """
    # Note: We'll simulate this since JSONPlaceholder doesn't have search
    query, expected_min = search_params
    
    # In a real API with search:
    # results = api_client_function.search(query)
    # assert len(results) >= expected_min
    
    print(f"✅ Would search for '{query}' expecting >={expected_min} results")


def test_with_post_factory(post_factory):
    """
    LESSON: Factory fixture
    
    Create multiple resources with custom parameters
    """
    # Create multiple posts in one test
    post1 = post_factory("First Post")
    post2 = post_factory("Second Post", body="Custom body")
    post3 = post_factory("Third Post", user_id=2)
    
    # Verify each post
    assert post1["title"] == "First Post"
    assert post2["body"] == "Custom body"
    assert post3["userId"] == 2
    
    print(f"✅ Created 3 posts: {post1['id']}, {post2['id']}, {post3['id']}")


def test_with_user_factory(user_factory):
    """
    LESSON: Creating multiple users with factory
    """
    user1 = user_factory("John Doe")
    user2 = user_factory("Jane Smith", email="jane@custom.com")
    
    assert user1["name"] == "John Doe"
    assert user2["email"] == "jane@custom.com"
    
    print(f"✅ Created users: {user1['name']}, {user2['name']}")


def test_with_authenticated_client(authenticated_client):
    """
    LESSON: Composite fixture with pre-authentication
    
    Client is already logged in when test starts
    """
    # Client is already authenticated by the fixture
    user = authenticated_client.get_current_user()
    
    assert user["username"] == "emilys"
    print(f"✅ Authenticated as: {user['username']}")


def test_with_composite_fixture(client_with_test_data):
    """
    LESSON: Composite fixture with setup data
    
    Test starts with client AND pre-created data
    """
    client = client_with_test_data["client"]
    posts = client_with_test_data["posts"]
    
    # Test data already created
    assert len(posts) == 2
    print(f"✅ Test has {len(posts)} pre-created posts")


@pytest.mark.parametrize("title,user_id", [
    ("Post 1", 1),
    ("Post 2", 2),
    ("Post 3", 1),
])
def test_parametrized_test(title, user_id, post_factory):
    """
    LESSON: Combining @pytest.mark.parametrize with fixtures
    
    Runs 3 times with different (title, user_id) combinations
    """
    post = post_factory(title, user_id=user_id)
    
    assert post["title"] == title
    assert post["userId"] == user_id
    
    print(f"✅ Created '{title}' for user {user_id}")


def test_autouse_fixture_runs_automatically():
    """
    LESSON: Autouse fixtures
    
    The print_test_name fixture runs automatically
    You'll see test name printed before/after this test
    """
    print("Test body executing")
    assert True


# Example: Scope comparison test
def test_scope_comparison_1(api_client_function, api_client_module):
    """Compare function vs module scope"""
    print("\nTest 1:")
    print(f"  Function client ID: {id(api_client_function)}")
    print(f"  Module client ID: {id(api_client_module)}")


def test_scope_comparison_2(api_client_function, api_client_module):
    """
    Compare again
    
    - Function client: DIFFERENT ID (new instance)
    - Module client: SAME ID (shared instance)
    """
    print("\nTest 2:")
    print(f"  Function client ID: {id(api_client_function)}")
    print(f"  Module client ID: {id(api_client_module)}")