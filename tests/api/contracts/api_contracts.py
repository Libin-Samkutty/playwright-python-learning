"""
API Contracts
-------------
Define expected API behavior as contracts

A contract specifies:
- Request format
- Response format
- Status codes
- Headers
- Error responses

Benefits:
- Detect breaking changes
- Self-documenting API
- Frontend/Backend alignment
- Version management
"""

from schemas.schemas import (
    POST_SCHEMA, USER_SCHEMA, POSTS_ARRAY_SCHEMA,
    DUMMYJSON_LOGIN_SCHEMA, DUMMYJSON_PRODUCTS_RESPONSE_SCHEMA,
    ERROR_SCHEMA
)


class APIContract:
    """
    Base class for API contracts
    
    A contract defines the expected behavior of an API endpoint
    """
    
    def __init__(self, endpoint, method, description):
        self.endpoint = endpoint
        self.method = method
        self.description = description
        self.request_schema = None
        self.response_schema = None
        self.success_status = 200
        self.error_responses = {}
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.description}"


# ============================================
# JSONPlaceholder Contracts
# ============================================

class GetPostContract(APIContract):
    """
    Contract: Get single post
    
    Endpoint: GET /posts/{id}
    Success: 200 OK
    Response: Single post object
    """
    
    def __init__(self):
        super().__init__(
            endpoint="/posts/{id}",
            method="GET",
            description="Get a single post by ID"
        )
        self.response_schema = POST_SCHEMA
        self.success_status = 200
        self.error_responses = {
            404: "Post not found"
        }


class GetPostsContract(APIContract):
    """
    Contract: Get all posts
    
    Endpoint: GET /posts
    Query Params: userId (optional), _limit (optional)
    Success: 200 OK
    Response: Array of posts
    """
    
    def __init__(self):
        super().__init__(
            endpoint="/posts",
            method="GET",
            description="Get all posts, optionally filtered by userId"
        )
        self.response_schema = POSTS_ARRAY_SCHEMA
        self.success_status = 200
        self.query_params = {
            "userId": {"type": "integer", "required": False},
            "_limit": {"type": "integer", "required": False}
        }


class CreatePostContract(APIContract):
    """
    Contract: Create new post
    
    Endpoint: POST /posts
    Request Body: {title, body, userId}
    Success: 201 Created
    Response: Created post with ID
    """
    
    def __init__(self):
        super().__init__(
            endpoint="/posts",
            method="POST",
            description="Create a new post"
        )
        self.request_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "body": {"type": "string"},
                "userId": {"type": "integer", "minimum": 1}
            },
            "required": ["title", "body", "userId"]
        }
        self.response_schema = POST_SCHEMA
        self.success_status = 201
        self.error_responses = {
            400: "Invalid request body"
        }


class UpdatePostContract(APIContract):
    """
    Contract: Update existing post
    
    Endpoint: PUT /posts/{id}
    Request Body: Complete post object
    Success: 200 OK
    Response: Updated post
    """
    
    def __init__(self):
        super().__init__(
            endpoint="/posts/{id}",
            method="PUT",
            description="Update an existing post"
        )
        self.request_schema = POST_SCHEMA
        self.response_schema = POST_SCHEMA
        self.success_status = 200
        self.error_responses = {
            404: "Post not found"
        }


class DeletePostContract(APIContract):
    """
    Contract: Delete post
    
    Endpoint: DELETE /posts/{id}
    Success: 200 OK
    Response: Empty object or deleted post
    """
    
    def __init__(self):
        super().__init__(
            endpoint="/posts/{id}",
            method="DELETE",
            description="Delete a post"
        )
        self.success_status = 200
        self.error_responses = {
            404: "Post not found"
        }


# ============================================
# DummyJSON Contracts
# ============================================

class LoginContract(APIContract):
    """
    Contract: User login
    
    Endpoint: POST /auth/login
    Request Body: {username, password}
    Success: 200 OK
    Response: User data + accessToken + refreshToken
    """
    
    def __init__(self):
        super().__init__(
            endpoint="/auth/login",
            method="POST",
            description="User login to get access token"
        )
        self.request_schema = {
            "type": "object",
            "properties": {
                "username": {"type": "string", "minLength": 1},
                "password": {"type": "string", "minLength": 1}
            },
            "required": ["username", "password"]
        }
        self.response_schema = DUMMYJSON_LOGIN_SCHEMA
        self.success_status = 200
        self.error_responses = {
            400: "Invalid credentials",
            401: "Unauthorized"
        }


class GetCurrentUserContract(APIContract):
    """
    Contract: Get current authenticated user
    
    Endpoint: GET /auth/me
    Headers: Authorization: Bearer {accessToken}
    Success: 200 OK
    Response: User data
    """
    
    def __init__(self):
        super().__init__(
            endpoint="/auth/me",
            method="GET",
            description="Get current user information"
        )
        self.required_headers = {
            "Authorization": "Bearer token required"
        }
        self.success_status = 200
        self.error_responses = {
            401: "Not authenticated",
            403: "Invalid token"
        }


class GetProductsContract(APIContract):
    """
    Contract: Get products with pagination
    
    Endpoint: GET /products
    Query Params: limit, skip
    Success: 200 OK
    Response: {products, total, skip, limit}
    """
    
    def __init__(self):
        super().__init__(
            endpoint="/products",
            method="GET",
            description="Get paginated products"
        )
        self.response_schema = DUMMYJSON_PRODUCTS_RESPONSE_SCHEMA
        self.success_status = 200
        self.query_params = {
            "limit": {"type": "integer", "default": 30},
            "skip": {"type": "integer", "default": 0}
        }


# ============================================
# Contract Registry
# ============================================

class ContractRegistry:
    """
    Central registry of all API contracts
    
    Usage:
        contract = ContractRegistry.get_contract("get_post")
        ContractRegistry.validate_all(api_client)
    """
    
    contracts = {
        # JSONPlaceholder
        "get_post": GetPostContract(),
        "get_posts": GetPostsContract(),
        "create_post": CreatePostContract(),
        "update_post": UpdatePostContract(),
        "delete_post": DeletePostContract(),
        
        # DummyJSON
        "login": LoginContract(),
        "get_current_user": GetCurrentUserContract(),
        "get_products": GetProductsContract(),
    }
    
    @classmethod
    def get_contract(cls, name):
        """Get contract by name"""
        if name not in cls.contracts:
            raise ValueError(f"Unknown contract: {name}")
        return cls.contracts[name]
    
    @classmethod
    def list_contracts(cls):
        """List all available contracts"""
        return list(cls.contracts.keys())
    
    @classmethod
    def get_contracts_by_endpoint(cls, endpoint):
        """Get all contracts for an endpoint"""
        return [
            contract for contract in cls.contracts.values()
            if contract.endpoint == endpoint
        ]