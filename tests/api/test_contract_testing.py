"""
Module 5 - Part 3A: Contract Testing
-------------------------------------
Demonstrates how to test APIs against defined contracts
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import playwright_state as _pw_state

sys.path.insert(0, os.path.dirname(__file__))
from contracts.api_contracts import ContractRegistry
from helpers.contract_validator import ContractValidator
from factories.base_factory import PostFactory, LoginFactory


def test_get_post_contract():
    """
    LESSON: Testing GET endpoint against contract
    
    Validates:
    - Status code matches contract
    - Response schema matches contract
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        # Get the contract
        contract = ContractRegistry.get_contract("get_post")
        
        print(f"\n📋 Testing contract: {contract}")
        
        # Make API request
        response = request_context.get("/posts/1")
        
        # Validate response against contract
        ContractValidator.validate_response(response, contract)
        
    finally:
        request_context.dispose()


def test_get_posts_contract():
    """
    LESSON: Testing array endpoint with query params
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        contract = ContractRegistry.get_contract("get_posts")
        
        print(f"\n📋 Testing contract: {contract}")
        
        # Test without params
        response = request_context.get("/posts")
        ContractValidator.validate_response(response, contract)
        
        # Test with query params (defined in contract)
        response = request_context.get("/posts?userId=1&_limit=5")
        ContractValidator.validate_response(response, contract)
        
        data = response.json()
        assert len(data) <= 5  # Limit applied
        
        print(f"✅ Contract valid with query params")
        
    finally:
        request_context.dispose()


def test_create_post_contract():
    """
    LESSON: Testing POST endpoint
    
    Validates both request and response against contract
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        contract = ContractRegistry.get_contract("create_post")
        
        print(f"\n📋 Testing contract: {contract}")
        
        # Generate request data
        post_data = PostFactory.create()
        
        # Validate request data against contract
        ContractValidator.validate_request(post_data, contract)
        print("✅ Request data matches contract")
        
        # Make API request
        response = request_context.post("/posts", data=post_data)
        
        # Validate response against contract
        ContractValidator.validate_response(response, contract)
        
    finally:
        request_context.dispose()


def test_update_post_contract():
    """
    LESSON: Testing PUT endpoint
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        contract = ContractRegistry.get_contract("update_post")
        
        print(f"\n📋 Testing contract: {contract}")
        
        # Prepare update data
        update_data = {
            "id": 1,
            "userId": 1,
            "title": "Updated Title",
            "body": "Updated body content"
        }
        
        # Validate request
        ContractValidator.validate_request(update_data, contract)
        
        # Make request
        response = request_context.put("/posts/1", data=update_data)
        
        # Validate response
        ContractValidator.validate_response(response, contract)
        
    finally:
        request_context.dispose()


def test_delete_post_contract():
    """
    LESSON: Testing DELETE endpoint
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        contract = ContractRegistry.get_contract("delete_post")
        
        print(f"\n📋 Testing contract: {contract}")
        
        response = request_context.delete("/posts/1")
        
        ContractValidator.validate_response(response, contract)
        
    finally:
        request_context.dispose()


def test_login_contract():
    """
    LESSON: Testing authentication contract
    
    Note: Validates accessToken (not token) is returned
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        contract = ContractRegistry.get_contract("login")
        
        print(f"\n📋 Testing contract: {contract}")
        
        # Get test credentials
        credentials = LoginFactory.create_dummyjson_credentials()
        
        # Validate request
        ContractValidator.validate_request(credentials, contract)
        print("✅ Login request matches contract")
        
        # Make request
        response = request_context.post(
            "/auth/login",
            data=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        # Validate response
        ContractValidator.validate_response(response, contract)
        
        # Verify accessToken is present (contract requirement)
        data = response.json()
        assert "accessToken" in data, "Contract requires accessToken field"
        assert "refreshToken" in data, "Contract requires refreshToken field"
        
        print(f"✅ Login contract validated, got accessToken")
        
    finally:
        request_context.dispose()


def test_authenticated_endpoint_contract():
    """
    LESSON: Testing protected endpoint contract
    
    Validates authorization header requirement
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        # First login to get token
        login_contract = ContractRegistry.get_contract("login")
        credentials = LoginFactory.create_dummyjson_credentials()
        
        login_response = request_context.post(
            "/auth/login",
            data=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        ContractValidator.validate_response(login_response, login_contract)
        
        access_token = login_response.json()["accessToken"]
        
        # Now test protected endpoint
        user_contract = ContractRegistry.get_contract("get_current_user")
        
        print(f"\n📋 Testing contract: {user_contract}")
        
        response = request_context.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        ContractValidator.validate_response(response, user_contract)
        
    finally:
        request_context.dispose()


def test_products_contract():
    """
    LESSON: Testing pagination contract
    """
    
    playwright = _pw_state.get_playwright()
    request_context = playwright.request.new_context(
        base_url="https://dummyjson.com"
    )
    
    try:
        contract = ContractRegistry.get_contract("get_products")
        
        print(f"\n📋 Testing contract: {contract}")
        
        # Test with pagination params
        response = request_context.get("/products?limit=10&skip=0")
        
        ContractValidator.validate_response(response, contract)
        
        data = response.json()
        
        # Verify pagination fields (required by contract)
        assert "products" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        
        print(f"✅ Pagination contract validated")
        
    finally:
        request_context.dispose()


def test_contract_detects_breaking_changes():
    """
    LESSON: Contracts detect breaking API changes
    
    Simulates what happens when API changes break the contract
    """
    
    from jsonschema import ValidationError
    
    contract = ContractRegistry.get_contract("get_post")
    
    # Simulate API response with breaking change
    # (missing required field 'body')
    broken_response = {
        "userId": 1,
        "id": 1,
        "title": "Test Post"
        # Missing 'body' field - contract violation!
    }
    
    from helpers.schema_validator import SchemaValidator
    
    try:
        SchemaValidator.validate(broken_response, contract.response_schema)
        pytest.fail("Should have detected contract violation")
    except AssertionError as e:
        print(f"\n✅ Contract caught breaking change:")
        print(f"   {str(e)[:100]}...")


@pytest.mark.parametrize("contract_name", [
    "get_post",
    "get_posts",
    "create_post",
    "update_post",
    "delete_post"
])
def test_all_jsonplaceholder_contracts(contract_name):
    """
    LESSON: Parametrized contract testing
    
    Test all contracts in one go
    """
    
    contract = ContractRegistry.get_contract(contract_name)
    print(f"\n📋 Testing: {contract}")
    
    # Each contract is validated
    # (Actual API calls would go here, simplified for demo)
    
    assert contract is not None
    assert contract.success_status in [200, 201]


def test_list_all_contracts():
    """
    LESSON: Contract documentation
    
    Contracts serve as living API documentation
    """
    
    print("\n📚 Available API Contracts:\n")
    
    for name in ContractRegistry.list_contracts():
        contract = ContractRegistry.get_contract(name)
        print(f"{name:20} - {contract.method:6} {contract.endpoint:20} - {contract.description}")
    
    print(f"\n✅ {len(ContractRegistry.list_contracts())} contracts defined")
