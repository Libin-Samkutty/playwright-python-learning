"""
tests/fixtures/lazy.py
Lazy initialization patterns
"""

import pytest


class LazyResource:
    """
    LAZY PATTERN: Resource created only when first accessed
    
    USE CASE:
    - Expensive resources that might not be used
    - Conditional resource creation
    """
    
    def __init__(self, creator_func):
        self._creator_func = creator_func
        self._value = None
        self._created = False
    
    @property
    def value(self):
        if not self._created:
            self._value = self._creator_func()
            self._created = True
        return self._value
    
    @property
    def was_created(self):
        return self._created


@pytest.fixture
def lazy_browser(playwright_instance):
    """
    LAZY FIXTURE: Browser only created if actually used
    
    Useful when test might not need browser
    """
    
    def create_browser():
        print("Creating browser (lazy)...")
        return playwright_instance.chromium.launch(headless=True)
    
    lazy = LazyResource(create_browser)
    
    yield lazy
    
    # Only close if it was created
    if lazy.was_created:
        lazy.value.close()
        print("Closed lazy browser")


@pytest.fixture
def expensive_api_data():
    """
    LAZY FIXTURE: Expensive data fetched only if needed
    """
    
    def fetch_data():
        print("Fetching expensive API data...")
        # Simulate expensive API call
        import time
        time.sleep(0.5)
        return {"data": "expensive"}
    
    return LazyResource(fetch_data)
