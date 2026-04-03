"""
tests/fixtures/caching.py
Fixture caching patterns
"""

import pytest
from functools import lru_cache


@lru_cache(maxsize=10)
def get_cached_test_data(data_file: str) -> dict:
    """
    CACHED FUNCTION: Load test data with caching
    
    Called by fixture but cached across calls
    """
    
    print(f"Loading test data from {data_file}...")
    
    # Simulate loading from file
    return {
        "loaded_from": data_file,
        "data": {"key": "value"},
    }


@pytest.fixture
def cached_data(request):
    """
    CACHED FIXTURE: Uses LRU cache for expensive operations
    
    Multiple tests requesting same data get cached version
    """
    
    # Get data file from marker or default
    marker = request.node.get_closest_marker("data_file")
    data_file = marker.args[0] if marker else "default.json"
    
    return get_cached_test_data(data_file)
