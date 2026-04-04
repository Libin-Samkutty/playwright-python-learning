"""
API Response Schemas
--------------------
Define expected structure of API responses using JSON Schema.

JSON Schema Basics:
- type: Data type (string, number, object, array, boolean, null)
- properties: Object fields
- required: Mandatory fields
- items: Array item structure
- enum: Allowed values
- pattern: Regex pattern for strings
- minimum/maximum: Numeric constraints
"""

# ============================================
# BASIC SCHEMAS
# ============================================

POST_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {"type": "integer", "minimum": 1},
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1},
        "body": {"type": "string"}
    },
    "required": ["userId", "id", "title", "body"],
    "additionalProperties": False  # No extra fields allowed
}

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "username": {"type": "string", "minLength": 1},
        "email": {
            "type": "string",
            "format": "email",  # Built-in email validation
            "pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"
        },
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "suite": {"type": "string"},
                "city": {"type": "string"},
                "zipcode": {"type": "string"},
                "geo": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "string"},
                        "lng": {"type": "string"}
                    },
                    "required": ["lat", "lng"]
                }
            },
            "required": ["street", "city", "zipcode", "geo"]
        },
        "phone": {"type": "string"},
        "website": {"type": "string"},
        "company": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "catchPhrase": {"type": "string"},
                "bs": {"type": "string"}
            },
            "required": ["name"]
        }
    },
    "required": ["id", "name", "username", "email", "address", "phone", "website", "company"]
}

# ============================================
# ARRAY SCHEMAS
# ============================================

POSTS_ARRAY_SCHEMA = {
    "type": "array",
    "items": POST_SCHEMA,  # Each item must match POST_SCHEMA
    "minItems": 0  # Can be empty
}

USERS_ARRAY_SCHEMA = {
    "type": "array",
    "items": USER_SCHEMA,
    "minItems": 1  # Must have at least 1 user
}

# ============================================
# DUMMYJSON SCHEMAS
# ============================================

# Note: DummyJSON returns accessToken, not token
DUMMYJSON_LOGIN_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "gender": {"type": "string", "enum": ["male", "female"]},
        "image": {"type": "string"},
        "accessToken": {"type": "string", "minLength": 10},  # ← accessToken, not token
        "refreshToken": {"type": "string", "minLength": 10}
    },
    "required": ["id", "username", "email", "firstName", "lastName", "accessToken", "refreshToken"]
}

DUMMYJSON_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "email": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "gender": {"type": "string"},
        "image": {"type": "string"}
    },
    "required": ["id", "username", "email"]
}

DUMMYJSON_PRODUCT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "price": {"type": "number", "minimum": 0},
        "discountPercentage": {"type": "number", "minimum": 0, "maximum": 100},
        "rating": {"type": "number", "minimum": 0, "maximum": 5},
        "stock": {"type": "integer", "minimum": 0},
        "brand": {"type": "string"},
        "category": {"type": "string"},
        "thumbnail": {"type": "string"},
        "images": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["id", "title", "price", "category"]
}

DUMMYJSON_PRODUCTS_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "products": {
            "type": "array",
            "items": DUMMYJSON_PRODUCT_SCHEMA
        },
        "total": {"type": "integer", "minimum": 0},
        "skip": {"type": "integer", "minimum": 0},
        "limit": {"type": "integer", "minimum": 0}
    },
    "required": ["products", "total", "skip", "limit"]
}

# ============================================
# ERROR SCHEMAS
# ============================================

ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "error": {"type": "string"}
    },
    "required": ["message"]
}

# ============================================
# PARTIAL SCHEMAS (for PATCH operations)
# ============================================

PARTIAL_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"}
    },
    # Note: No required fields for PATCH
    "minProperties": 1  # At least one property must be present
}