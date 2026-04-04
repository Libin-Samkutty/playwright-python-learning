"""
Module 2 - Part 2: Complete CRUD Operations
--------------------------------------------
CRUD = Create, Read, Update, Delete

This demonstrates a complete lifecycle:
1. Create a resource (POST)
2. Read it back (GET)
3. Update it (PUT)
4. Delete it (DELETE)
5. Verify deletion (GET again)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state


def test_complete_crud_lifecycle():
    """
    LESSON: Full CRUD lifecycle in one test
    
    Real-world: Testing a complete user journey:
    - User registers (CREATE)
    - Views profile (READ)
    - Updates profile (UPDATE)
    - Deletes account (DELETE)
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        # ========================================
        # 1️⃣ CREATE (POST)
        # ========================================
        print("\n1️⃣ CREATE: Creating a new post...")
        
        new_post = {
            "title": "CRUD Test Post",
            "body": "Testing full CRUD lifecycle",
            "userId": 1
        }
        
        create_response = request_context.post(
            "https://jsonplaceholder.typicode.com/posts",
            data=new_post
        )
        
        assert create_response.status == 201
        created_post = create_response.json()
        post_id = created_post["id"]

        print(f"   ✅ Created post with ID: {post_id}")

        # JSONPlaceholder simulates creation but doesn't persist new resources.
        # IDs above 100 don't exist on the server, so use a known valid ID
        # for subsequent READ/UPDATE/DELETE operations.
        read_post_id = post_id if post_id <= 100 else 1

        # ========================================
        # 2️⃣ READ (GET)
        # ========================================
        print(f"\n2️⃣ READ: Fetching post {read_post_id}...")
        
        read_response = request_context.get(
            f"https://jsonplaceholder.typicode.com/posts/{read_post_id}"
        )

        assert read_response.status == 200
        fetched_post = read_response.json()

        # Verify we got a valid post back
        assert fetched_post["id"] == read_post_id

        print(f"   ✅ Successfully retrieved post: '{fetched_post['title']}'")

        # ========================================
        # 3️⃣ UPDATE (PUT)
        # ========================================
        print(f"\n3️⃣ UPDATE: Updating post {read_post_id}...")

        updated_data = {
            "id": read_post_id,  # PUT usually requires ID in body
            "title": "UPDATED: CRUD Test Post",
            "body": "This post has been updated",
            "userId": 1
        }
        
        update_response = request_context.put(
            f"https://jsonplaceholder.typicode.com/posts/{read_post_id}",
            data=updated_data
        )
        
        # PUT typically returns 200 OK
        assert update_response.status == 200
        updated_post = update_response.json()
        
        # Verify update was applied
        assert updated_post["title"] == updated_data["title"]
        assert updated_post["body"] == updated_data["body"]
        
        print(f"   ✅ Post updated: '{updated_post['title']}'")
        
        # ========================================
        # 4️⃣ DELETE (DELETE)
        # ========================================
        print(f"\n4️⃣ DELETE: Deleting post {read_post_id}...")

        delete_response = request_context.delete(
            f"https://jsonplaceholder.typicode.com/posts/{read_post_id}"
        )
        
        # DELETE typically returns:
        # 200 OK or 204 No Content
        assert delete_response.status in [200, 204], \
            f"Expected 200/204, got {delete_response.status}"
        
        print(f"   ✅ Post deleted successfully")
        
        # ========================================
        # 5️⃣ VERIFY DELETION (GET again)
        # ========================================
        print(f"\n5️⃣ VERIFY: Confirming post {read_post_id} is deleted...")

        # Note: JSONPlaceholder doesn't actually delete (it's fake)
        # In a real API, this would return 404
        verify_response = request_context.get(
            f"https://jsonplaceholder.typicode.com/posts/{read_post_id}"
        )
        
        # In real API: assert verify_response.status == 404
        # JSONPlaceholder still returns 200, but in production you'd check 404
        
        print(f"   ✅ Verification complete (status: {verify_response.status})")
        print("\n🎉 Complete CRUD lifecycle tested successfully!\n")
        
    finally:
        request_context.dispose()


def test_update_with_put():
    """
    LESSON: PUT request - Complete replacement
    
    Real-world: User updates their entire profile
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        # PUT replaces the ENTIRE resource
        post_id = 1
        
        updated_post = {
            "id": post_id,
            "title": "Completely Updated Title",
            "body": "Completely updated body content",
            "userId": 1
        }
        
        response = request_context.put(
            f"https://jsonplaceholder.typicode.com/posts/{post_id}",
            data=updated_post
        )
        
        assert response.status == 200
        
        result = response.json()
        assert result["title"] == updated_post["title"]
        assert result["body"] == updated_post["body"]
        
        print(f"✅ PUT successful: {result['title']}")
        
    finally:
        request_context.dispose()


def test_update_with_patch():
    """
    LESSON: PATCH request - Partial update
    
    Difference between PUT and PATCH:
    - PUT: Replaces entire resource (all fields required)
    - PATCH: Updates only specified fields (partial update)
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        post_id = 1
        
        # PATCH: Only updating title, leaving other fields unchanged
        partial_update = {
            "title": "Only Title Updated"
            # body and userId remain unchanged
        }
        
        response = request_context.patch(
            f"https://jsonplaceholder.typicode.com/posts/{post_id}",
            data=partial_update
        )
        
        assert response.status == 200
        
        result = response.json()
        assert result["title"] == partial_update["title"]
        
        print(f"✅ PATCH successful: {result['title']}")
        
    finally:
        request_context.dispose()


def test_delete_resource():
    """
    LESSON: DELETE request
    
    Real-world: User deletes their account, removes post, cancels order
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context()
    
    try:
        post_id = 1
        
        response = request_context.delete(
            f"https://jsonplaceholder.typicode.com/posts/{post_id}"
        )
        
        # Common DELETE status codes:
        # 200 OK - Deleted, returns deleted resource
        # 204 No Content - Deleted, no body returned
        # 404 Not Found - Resource doesn't exist
        
        assert response.status in [200, 204]
        
        print(f"✅ Deleted post {post_id}")
        
    finally:
        request_context.dispose()
