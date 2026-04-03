"""
tests/utils/allure_helpers.py
Allure reporting helper utilities
"""

import allure
from playwright.sync_api import Page
from functools import wraps
from typing import Callable


def allure_step(step_name: str):
    """
    Decorator to wrap function as Allure step with screenshot
    
    Usage:
        @allure_step("Login to application")
        def login(page, user, password):
            ...
    """
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with allure.step(step_name):
                result = func(*args, **kwargs)
                
                # Try to capture screenshot if page available
                for arg in args:
                    if isinstance(arg, Page):
                        try:
                            allure.attach(
                                arg.screenshot(),
                                name=f"{step_name} - Screenshot",
                                attachment_type=allure.attachment_type.PNG,
                            )
                        except Exception:
                            pass
                        break
                
                return result
        
        return wrapper
    
    return decorator


def attach_screenshot(page: Page, name: str = "Screenshot"):
    """
    Attach screenshot to Allure report
    
    Usage:
        attach_screenshot(page, "After Login")
    """
    
    allure.attach(
        page.screenshot(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def attach_page_source(page: Page, name: str = "Page Source"):
    """
    Attach page HTML to Allure report
    """
    
    allure.attach(
        page.content(),
        name=name,
        attachment_type=allure.attachment_type.HTML,
    )


def attach_console_logs(page: Page, logs: list, name: str = "Console Logs"):
    """
    Attach console logs to Allure report
    """
    
    log_text = "\n".join(str(log) for log in logs)
    
    allure.attach(
        log_text,
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )


def attach_video(video_path: str, name: str = "Test Video"):
    """
    Attach video to Allure report
    """
    
    with open(video_path, "rb") as f:
        allure.attach(
            f.read(),
            name=name,
            attachment_type=allure.attachment_type.WEBM,
        )


def attach_trace_link(trace_path: str):
    """
    Attach trace file link to Allure report
    """
    
    allure.attach(
        f"View trace: playwright show-trace {trace_path}",
        name="Trace File",
        attachment_type=allure.attachment_type.TEXT,
    )


class AllureLogger:
    """
    Logger that integrates with Allure
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.logs = []
    
    def log_step(self, message: str, screenshot: bool = True):
        """
        Log a step with optional screenshot
        """
        
        self.logs.append(message)
        
        with allure.step(message):
            if screenshot:
                attach_screenshot(self.page, message)
    
    def log_info(self, message: str):
        """Log info message"""
        self.logs.append(f"INFO: {message}")
        allure.attach(message, name="Info", attachment_type=allure.attachment_type.TEXT)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.logs.append(f"WARNING: {message}")
        allure.attach(message, name="Warning", attachment_type=allure.attachment_type.TEXT)
    
    def log_error(self, message: str, screenshot: bool = True):
        """Log error with screenshot"""
        self.logs.append(f"ERROR: {message}")
        
        with allure.step(f"ERROR: {message}"):
            if screenshot:
                attach_screenshot(self.page, "Error State")
            attach_page_source(self.page, "Error Page Source")