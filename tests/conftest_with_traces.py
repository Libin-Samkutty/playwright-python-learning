"""
Alternative: Always save traces (useful for CI)
"""

import pytest
from playwright.sync_api import sync_playwright
import os
from datetime import datetime


@pytest.fixture(scope="function")
def traced_page(browser, request):
    """
    Page fixture that ALWAYS saves traces
    
    Useful for CI where you want traces for all tests
    """
    
    context = browser.new_context()
    
    # Create traces directory
    os.makedirs("traces", exist_ok=True)
    
    # Start tracing
    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True,
    )
    
    page = context.new_page()
    
    yield page
    
    # Always save trace
    test_name = request.node.name
    # Sanitize test name for filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
    trace_path = f"traces/{safe_name}.zip"
    
    context.tracing.stop(path=trace_path)
    print(f"\n Trace saved: {trace_path}")
    
    context.close()
