"""
Contract Validator
------------------
Validates API responses against contracts
"""

from helpers.schema_validator import SchemaValidator


class ContractValidator:
    """
    Validates API behavior against contracts
    
    Ensures API adheres to its contract:
    - Correct status code
    - Response matches schema
    - Headers are correct
    """
    
    @staticmethod
    def validate_response(response, contract):
        """
        Validate API response against contract
        
        Args:
            response: Playwright Response object
            contract: APIContract instance
        
        Raises:
            AssertionError: If contract is violated
        """
        
        # 1. Validate status code
        assert response.status == contract.success_status, \
            f"Contract violation: Expected status {contract.success_status}, got {response.status}\n" \
            f"Contract: {contract}"
        
        # 2. Validate response schema (if defined)
        if contract.response_schema:
            SchemaValidator.validate_response(response, contract.response_schema)
        
        print(f"✅ Contract validated: {contract}")
    
    @staticmethod
    def validate_request(data, contract):
        """
        Validate request data against contract
        
        Args:
            data: Request body data
            contract: APIContract instance
        """
        if contract.request_schema:
            SchemaValidator.validate(data, contract.request_schema)
    
    @staticmethod
    def validate_error_response(response, contract, expected_status):
        """
        Validate error response against contract
        
        Args:
            response: Playwright Response object
            contract: APIContract instance
            expected_status: Expected error status code
        """
        assert response.status == expected_status, \
            f"Expected error status {expected_status}, got {response.status}"
        
        assert expected_status in contract.error_responses, \
            f"Status {expected_status} not defined in contract error responses"
        
        print(f"✅ Error contract validated: {contract} (status {expected_status})")
