"""
API Trace Manager
-----------------
Manage tracing for API tests with Playwright

Tracing captures:
- All HTTP requests and responses
- Request/response headers
- Request/response bodies
- Timing information
- Network errors

Usage:
1. Enable tracing before test
2. Run API operations
3. Save trace on failure
4. Open in Playwright Trace Viewer
"""

import os
from datetime import datetime
from typing import Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import playwright_state as _pw_state


class APITraceManager:
    """
    Manages API request tracing for debugging
    
    Playwright's tracing works with browser contexts, not request contexts.
    For API testing, we use browser context's request property.
    
    Key Concept:
    - Browser Context can trace all network activity
    - Request Context alone CANNOT be traced
    - Solution: Use browser context for API calls when tracing needed
    """
    
    def __init__(self, trace_dir: str = "artifacts/traces"):
        """
        Initialize trace manager
        
        Args:
            trace_dir: Directory to save trace files
        """
        self.trace_dir = trace_dir
        self.browser_context = None
        self.is_tracing = False
        
        # Ensure trace directory exists
        os.makedirs(trace_dir, exist_ok=True)
    
    def start_tracing(self, name: str = None):
        """
        Start tracing API requests
        
        Args:
            name: Optional name for this trace session
        
        Returns:
            Request context for making API calls
        """
        browser = _pw_state.get_browser()
        
        # Create browser context (required for tracing)
        self.browser_context = browser.new_context()
        
        # Start tracing
        self.browser_context.tracing.start(
            screenshots=False,  # Not needed for API tests
            snapshots=True,     # Capture DOM snapshots (minimal for API)
            sources=False       # Source code not needed for API
        )
        
        self.is_tracing = True
        self.trace_name = name or f"api_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🔴 Tracing started: {self.trace_name}")
        
        # Return request context from browser context
        # This allows API calls to be traced
        return self.browser_context.request
    
    def stop_tracing(self, save: bool = True, test_passed: bool = True):
        """
        Stop tracing and optionally save trace file
        
        Args:
            save: Whether to save trace file
            test_passed: Whether test passed (affects filename)
        
        Returns:
            Path to trace file if saved, None otherwise
        """
        if not self.is_tracing or not self.browser_context:
            return None
        
        trace_path = None
        
        if save:
            # Add status to filename
            status = "PASSED" if test_passed else "FAILED"
            trace_filename = f"{self.trace_name}_{status}.zip"
            trace_path = os.path.join(self.trace_dir, trace_filename)
            
            # Stop and save trace
            self.browser_context.tracing.stop(path=trace_path)
            print(f"💾 Trace saved: {trace_path}")
        else:
            # Stop without saving
            self.browser_context.tracing.stop()
        
        # Cleanup
        self.browser_context.close()
        self.browser_context = None
        self.is_tracing = False
        
        return trace_path
    
    def save_trace_on_failure(self, test_name: str):
        """
        Save trace file for failed test
        
        Args:
            test_name: Name of the failed test
        
        Returns:
            Path to trace file
        """
        return self.stop_tracing(save=True, test_passed=False)
    
    def discard_trace(self):
        """
        Discard trace without saving (test passed)
        """
        self.stop_tracing(save=False)
    
    @staticmethod
    def open_trace(trace_path: str):
        """
        Instructions to open trace in viewer
        
        Args:
            trace_path: Path to trace file
        """
        print(f"\n📖 To view trace, run:")
        print(f"   playwright show-trace {trace_path}")
        print(f"\n   Or open https://trace.playwright.dev and upload the file")


class SimpleTracer:
    """
    Simplified tracer for quick debugging
    
    Usage:
        with SimpleTracer("my_test") as request_context:
            response = request_context.get("https://api.example.com/data")
    """
    
    def __init__(self, name: str, trace_dir: str = "artifacts/traces"):
        self.manager = APITraceManager(trace_dir)
        self.name = name
        self.request_context = None
        self._failed = False
    
    def __enter__(self):
        """Start tracing and return request context"""
        self.request_context = self.manager.start_tracing(self.name)
        return self.request_context
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop tracing, save on failure"""
        if exc_type is not None:
            # Test failed - save trace
            self._failed = True
            trace_path = self.manager.stop_tracing(save=True, test_passed=False)
            print(f"\n❌ Test failed! Trace saved for debugging.")
            APITraceManager.open_trace(trace_path)
        else:
            # Test passed - optionally save or discard
            # By default, save traces for all tests (useful for debugging)
            self.manager.stop_tracing(save=True, test_passed=True)
        
        return False  # Don't suppress exceptions
    
    def mark_failed(self):
        """Manually mark test as failed (for custom assertions)"""
        self._failed = True