"""
Advanced Pytest Fixtures for API Testing
-----------------------------------------
Demonstrates advanced fixture patterns:
- Fixture scopes (function, class, module, session)
- Fixture parametrization
- Fixture factories
- Fixture composition
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clients'))
from clients.base_client import JSONPlaceholderClient, DummyJSONClient


# ============================================
# FIXTURE SCOPES
# ============================================

@pytest.fixture(scope="function")  # Default: New instance per test
def api_client_function():
    """
    Function-scoped fixture (default)
    
    Creates NEW client for EACH test
    
    Use when:
    - Tests modify data
    - Tests need isolation
    - Most common scope
    """
    print("\n[FIXTURE] Creating function-scoped client")
    client = JSONPlaceholderClient()
    yield client
    print("[FIXTURE] Disposing function-scoped client")
    client.dispose()


@pytest.fixture(scope="module")  # Shared across all tests in file
def api_client_module():
    """
    Module-scoped fixture
    
    Creates ONE client for ALL tests in this module/file
    
    Use when:
    - Setup is expensive (e.g., authentication)
    - Tests only READ data (don't modify)
    - Want faster test execution
    
    ⚠️ WARNING: Tests share state!
    """
    print("\n[FIXTURE] Creating module-scoped client (shared)")
    client = JSONPlaceholderClient()
    yield client
    print("[FIXTURE] Disposing module-scoped client")
    client.dispose()


@pytest.fixture(scope="session")  # Shared across entire test session
def api_client_session():
    """
    Session-scoped fixture
    
    Creates ONE client for ENTIRE test run
    
    Use when:
    - Very expensive setup (database connection pool)
    - Read-only operations
    - Maximum performance
    
    ⚠️ WARNING: All tests share same instance!
    """
    print("\n[FIXTURE] Creating session-scoped client (global)")
    client = JSONPlaceholderClient()
    yield client
    print("[FIXTURE] Disposing session-scoped client")
    client.dispose()


# ============================================
# PARAMETRIZED FIXTURES
# ============================================

@pytest.fixture(params=[1, 2, 3])
def user_id(request):
    """
    Parametrized fixture
    
    Test runs MULTIPLE times, once for each parameter value
    
    Real-world: Test with different users, products, scenarios
    """
    return request.param


@pytest.fixture(params=[
    {"username": "emilys", "password": "emilyspass"},
    # Add more test users here
])
def user_credentials(request):
    """
    Parametrized fixture with complex data
    
    Each test runs with different credentials
    """
    return request.param


@pytest.fixture(params=[
    ("phone", 5),
    ("laptop", 10),
    ("watch", 3),
])
def search_params(request):
    """
    Parametrized fixture with tuples
    
    Returns: (search_query, expected_min_results)
    """
    return request.param


# ============================================
# FIXTURE FACTORIES
# ============================================

@pytest.fixture
def post_factory():
    """
    Factory fixture - returns a function that creates posts
    
    Use when:
    - Need to create multiple resources in one test
    - Need custom parameters per creation
    
    Example:
        def test_something(post_factory):
            post1 = post_factory("Title 1")
            post2 = post_factory("Title 2")
    """
    client = JSONPlaceholderClient()
    
    def _create_post(title, body=None, user_id=1):
        """Create a post with custom parameters"""
        return client.create_post(
            title=title,
            body=body or f"Body for {title}",
            user_id=user_id
        )
    
    yield _create_post
    
    client.dispose()


@pytest.fixture
def user_factory():
    """
    Factory for creating test users
    
    In real API with user creation endpoint
    """
    client = JSONPlaceholderClient()
    created_users = []
    
    def _create_user(name, email=None):
        """Create user (simulated)"""
        user = {
            "id": len(created_users) + 100,
            "name": name,
            "email": email or f"{name.lower().replace(' ', '')}@test.com"
        }
        created_users.append(user)
        return user
    
    yield _create_user
    
    # Cleanup: Delete created users (in real API)
    print(f"\n[CLEANUP] Would delete {len(created_users)} users")
    client.dispose()


# ============================================
# FIXTURE COMPOSITION
# ============================================

@pytest.fixture
def authenticated_client():
    """
    Composite fixture - combines client + authentication
    
    Automatically logs in before test runs
    """
    client = DummyJSONClient()
    
    # Perform authentication
    client.login("emilys", "emilyspass")
    print("\n[FIXTURE] Client authenticated")
    
    yield client
    
    client.dispose()


@pytest.fixture
def client_with_test_data(api_client_function, post_factory):
    """
    Composite fixture - combines multiple fixtures
    
    Sets up client with pre-created test data
    """
    # Create some test posts
    post1 = post_factory("Test Post 1")
    post2 = post_factory("Test Post 2")
    
    # Return client and created data
    return {
        "client": api_client_function,
        "posts": [post1, post2]
    }


# ============================================
# AUTOUSE FIXTURES
# ============================================

@pytest.fixture(autouse=True)
def print_test_name(request):
    """
    Autouse fixture - runs automatically for every test
    
    No need to explicitly request it
    
    Use for:
    - Logging
    - Setup that EVERY test needs
    - Monitoring
    """
    test_name = request.node.name
    print(f"\n{'='*60}")
    print(f"RUNNING TEST: {test_name}")
    print(f"{'='*60}")
    
    yield
    
    print(f"\n{'='*60}")
    print(f"FINISHED TEST: {test_name}")
    print(f"{'='*60}")


# ============================================
# CONDITIONAL FIXTURES
# ============================================

@pytest.fixture
def skip_in_ci(request):
    """
    Conditional fixture - skip test in CI environment
    
    Real-world: Skip slow tests in CI
    """
    import os
    if os.getenv("CI"):
        pytest.skip("Skipping in CI environment")


@pytest.fixture
def require_env_var(request):
    """
    Conditional fixture - require environment variable
    """
    import os
    required_var = "API_KEY"
    
    if not os.getenv(required_var):
        pytest.skip(f"Skipping: {required_var} not set")
    
    return os.getenv(required_var)