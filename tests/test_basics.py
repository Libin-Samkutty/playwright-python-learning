"""
CONCEPT: Understanding pytest fundamentals
GOAL: Learn how pytest finds and runs tests
REAL-WORLD USE: Foundation for all test automation
"""

# A simple test function
def test_addition():
    """Test that 2 + 2 equals 4"""
    result = 2 + 2
    assert result == 4  # If this is False, test fails


def test_string_operations():
    """Test string methods"""
    text = "Playwright"
    assert text.startswith("Play")
    assert len(text) == 10


# This function will NOT run (doesn't start with 'test_')
def check_something():
    assert 1 == 1