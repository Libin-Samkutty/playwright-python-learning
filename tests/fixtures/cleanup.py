"""
tests/fixtures/cleanup.py
Fixture cleanup patterns
"""

import pytest
import os
import tempfile
import shutil


@pytest.fixture
def temp_directory():
    """
    CLEANUP PATTERN: Using yield for guaranteed cleanup
    
    The code after yield ALWAYS runs, even if test fails
    """
    
    # SETUP: Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="playwright_test_")
    print(f"\nCreated temp directory: {temp_dir}")
    
    yield temp_dir
    
    # TEARDOWN: Clean up (always runs)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temp directory: {temp_dir}")


@pytest.fixture
def screenshot_on_failure(page, request, temp_directory):
    """
    CLEANUP PATTERN: Capture screenshot on test failure
    
    Uses request.node to access test information
    """
    
    yield page
    
    # Check if test failed
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        # Take screenshot
        test_name = request.node.name
        screenshot_path = os.path.join(
            temp_directory, 
            f"{test_name}_failure.png"
        )
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")


@pytest.fixture
def database_transaction(db_connection):
    """
    CLEANUP PATTERN: Database transaction rollback
    
    REAL-WORLD USE:
    - Test data cleanup
    - Isolated database tests
    """
    
    # Start transaction
    transaction = db_connection.begin()
    
    yield db_connection
    
    # Rollback transaction (cleanup)
    transaction.rollback()


@pytest.fixture
def api_test_user(api_client):
    """
    CLEANUP PATTERN: Create and delete test data
    
    REAL-WORLD USE:
    - API testing
    - Creating test fixtures in external systems
    """
    
    # SETUP: Create user via API
    response = api_client.post("/users", json={
        "username": "test_user_123",
        "email": "test@example.com",
    })
    user_id = response.json()["id"]
    
    yield {"id": user_id, "username": "test_user_123"}
    
    # TEARDOWN: Delete user
    api_client.delete(f"/users/{user_id}")

@pytest.fixture
def multiple_resources(request, browser_instance):
    """
    CLEANUP PATTERN: Multiple cleanup actions with addfinalizer
    
    WHY USE addfinalizer:
    - Register multiple cleanup functions
    - Cleanup functions run in reverse order (LIFO)
    - Each cleanup runs even if previous cleanup fails
    """
    
    resources = {}
    
    # Create context 1
    context1 = browser_instance.new_context()
    resources["context1"] = context1
    
    # Register cleanup for context1
    request.addfinalizer(lambda: context1.close())
    
    # Create context 2
    context2 = browser_instance.new_context()
    resources["context2"] = context2
    
    # Register cleanup for context2
    request.addfinalizer(lambda: context2.close())
    
    # Create pages
    resources["page1"] = context1.new_page()
    resources["page2"] = context2.new_page()
    
    return resources


@pytest.fixture
def tracked_downloads(page, request, tmp_path):
    """
    CLEANUP PATTERN: Track and cleanup downloaded files
    """
    
    downloaded_files = []
    
    def track_download(download):
        path = tmp_path / download.suggested_filename
        download.save_as(path)
        downloaded_files.append(path)
    
    page.on("download", track_download)
    
    yield page
    
    # Cleanup all downloaded files
    for file_path in downloaded_files:
        if file_path.exists():
            file_path.unlink()
            print(f"Cleaned up: {file_path}")