"""
tests/utils/error_handlers.py
Custom error handling utilities
"""

import functools
import traceback
from datetime import datetime
from typing import Callable, Any
import os


class TestErrorHandler:
    """
    Comprehensive error handler for Playwright tests
    """
    
    def __init__(
        self,
        screenshot_dir: str = "screenshots",
        html_dir: str = "html_dumps",
        enable_screenshots: bool = True,
        enable_html_dump: bool = True,
    ):
        self.screenshot_dir = screenshot_dir
        self.html_dir = html_dir
        self.enable_screenshots = enable_screenshots
        self.enable_html_dump = enable_html_dump
        
        # Create directories
        os.makedirs(screenshot_dir, exist_ok=True)
        os.makedirs(html_dir, exist_ok=True)
    
    def handle_error(
        self,
        page,
        error: Exception,
        test_name: str,
        step_name: str = "",
    ) -> dict:
        """
        Handle an error with full artifact capture
        
        Args:
            page: Playwright page
            error: The exception
            test_name: Name of the test
            step_name: Current step name
        
        Returns:
            Dictionary with artifact paths
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize_filename(test_name)
        
        artifacts = {
            "test_name": test_name,
            "step_name": step_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": timestamp,
        }
        
        # Capture screenshot
        if self.enable_screenshots:
            try:
                screenshot_path = f"{self.screenshot_dir}/{safe_name}_{timestamp}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                artifacts["screenshot"] = screenshot_path
            except Exception as e:
                artifacts["screenshot_error"] = str(e)
        
        # Capture HTML
        if self.enable_html_dump:
            try:
                html_path = f"{self.html_dir}/{safe_name}_{timestamp}.html"
                content = page.content()
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(content)
                artifacts["html"] = html_path
            except Exception as e:
                artifacts["html_error"] = str(e)
        
        # Capture additional info
        try:
            artifacts["url"] = page.url
            artifacts["title"] = page.title()
        except Exception:
            pass
        
        # Log the error
        self._log_error(artifacts, error)
        
        return artifacts
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use as filename"""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    
    def _log_error(self, artifacts: dict, error: Exception):
        """Log error details"""
        print("\n" + "=" * 60)
        print(" TEST FAILURE")
        print("=" * 60)
        print(f"Test: {artifacts.get('test_name', 'Unknown')}")
        print(f"Step: {artifacts.get('step_name', 'Unknown')}")
        print(f"Error: {artifacts.get('error_type', 'Unknown')}: {artifacts.get('error_message', '')}")
        print(f"URL: {artifacts.get('url', 'Unknown')}")
        
        if "screenshot" in artifacts:
            print(f" Screenshot: {artifacts['screenshot']}")
        if "html" in artifacts:
            print(f" HTML: {artifacts['html']}")
        
        print("=" * 60)
        print("Stack trace:")
        traceback.print_exc()
        print("=" * 60)


def with_error_handling(
    screenshot_on_error: bool = True,
    html_on_error: bool = True,
):
    """
    Decorator for test functions with error handling
    
    Usage:
        @with_error_handling()
        def test_something(page):
            ...
    """
    
    handler = TestErrorHandler(
        enable_screenshots=screenshot_on_error,
        enable_html_dump=html_on_error,
    )
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Find page argument
            page = kwargs.get("page") or (args[0] if args else None)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if page:
                    handler.handle_error(
                        page=page,
                        error=e,
                        test_name=func.__name__,
                    )
                raise
        
        return wrapper
    
    return decorator


class StepTracker:
    """
    Track test steps for better error context
    """
    
    def __init__(self, page, test_name: str):
        self.page = page
        self.test_name = test_name
        self.steps = []
        self.current_step = None
        self.error_handler = TestErrorHandler()
    
    def step(self, name: str):
        """
        Context manager for test steps
        
        Usage:
            with tracker.step("Fill login form"):
                page.fill("#username", "user")
        """
        
        class StepContext:
            def __init__(ctx_self, tracker, name):
                ctx_self.tracker = tracker
                ctx_self.name = name
            
            def __enter__(ctx_self):
                ctx_self.tracker.current_step = ctx_self.name
                ctx_self.tracker.steps.append(ctx_self.name)
                print(f"   Step: {ctx_self.name}")
                return ctx_self
            
            def __exit__(ctx_self, exc_type, exc_val, exc_tb):
                if exc_type:
                    ctx_self.tracker.error_handler.handle_error(
                        page=ctx_self.tracker.page,
                        error=exc_val,
                        test_name=ctx_self.tracker.test_name,
                        step_name=ctx_self.name,
                    )
                else:
                    print(f"   Step completed: {ctx_self.name}")
                return False  # Don't suppress exception
        
        return StepContext(self, name)
    
    def get_steps(self) -> list:
        """Get all completed steps"""
        return self.steps.copy()