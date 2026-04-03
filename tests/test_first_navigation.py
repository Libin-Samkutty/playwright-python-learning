"""
CONCEPT: Basic Playwright test with pytest
GOAL: Navigate to a page and verify the title
REAL-WORLD USE: Every test starts with opening a page
"""

def test_navigate_to_example(browser):
    """
    Test: Open example.com and verify title
    Uses the fixture-provided browser (sync_playwright() can only be called
    once per session on Windows/Python 3.14, so the shared browser from
    conftest is used instead of creating a new one manually).
    """

    # Create a new context (isolated session)
    context = browser.new_context()

    # Create a new page
    page = context.new_page()

    # Action: Navigate to example.com
    page.goto("https://example.com")

    # Assertion: Verify the page title
    title = page.title()
    assert title == "Example Domain"  # This is the actual title

    # Cleanup
    context.close()