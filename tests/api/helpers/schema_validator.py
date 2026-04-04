"""
Schema Validation Helper
-------------------------
Wrapper around jsonschema for cleaner test code
"""

from jsonschema import validate, ValidationError, Draft7Validator
from jsonschema.exceptions import SchemaError
import json


class SchemaValidator:
    """
    Helper class for schema validation
    
    Provides:
    - Clear error messages
    - Validation helpers
    - Schema debugging
    """
    
    @staticmethod
    def validate(instance, schema, error_message_prefix="Schema validation failed"):
        """
        Validate instance against schema
        
        Args:
            instance: Data to validate (dict/list)
            schema: JSON Schema (dict)
            error_message_prefix: Custom error message prefix
        
        Raises:
            AssertionError: If validation fails (with detailed message)
        """
        try:
            validate(instance=instance, schema=schema)
        except ValidationError as e:
            # Create detailed error message
            error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
            
            detailed_error = f"""
{error_message_prefix}

Path: {error_path}
Error: {e.message}

Failed value:
{json.dumps(e.instance, indent=2)}

Schema requirement:
{json.dumps(e.schema, indent=2)}
"""
            raise AssertionError(detailed_error)
        except SchemaError as e:
            raise AssertionError(f"Invalid schema definition: {e.message}")
    
    @staticmethod
    def validate_response(response, schema):
        """
        Validate API response against schema
        
        Automatically parses JSON and validates
        
        Args:
            response: Playwright Response object
            schema: JSON Schema
        """
        try:
            data = response.json()
        except Exception as e:
            raise AssertionError(f"Failed to parse response as JSON: {e}")
        
        SchemaValidator.validate(
            instance=data,
            schema=schema,
            error_message_prefix=f"API response validation failed for {response.url}"
        )
    
    @staticmethod
    def is_valid(instance, schema):
        """
        Check if instance is valid (returns bool, doesn't raise)
        
        Args:
            instance: Data to validate
            schema: JSON Schema
        
        Returns:
            bool: True if valid, False otherwise
        """
        validator = Draft7Validator(schema)
        return validator.is_valid(instance)
    
    @staticmethod
    def get_errors(instance, schema):
        """
        Get all validation errors (doesn't raise)
        
        Args:
            instance: Data to validate
            schema: JSON Schema
        
        Returns:
            list: List of error messages
        """
        validator = Draft7Validator(schema)
        errors = []
        
        for error in validator.iter_errors(instance):
            error_path = " -> ".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{error_path}: {error.message}")
        
        return errors
    
    @staticmethod
    def validate_partial(instance, schema, check_required=False):
        """
        Validate partial data (e.g., PATCH request)
        
        Only validates fields that are present
        
        Args:
            instance: Partial data to validate
            schema: Full JSON Schema
            check_required: If True, enforce required fields
        """
        # Create modified schema without required constraint
        partial_schema = schema.copy()
        
        if not check_required and "required" in partial_schema:
            del partial_schema["required"]
        
        SchemaValidator.validate(instance, partial_schema)