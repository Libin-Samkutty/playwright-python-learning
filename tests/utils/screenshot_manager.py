"""
tests/utils/screenshot_manager.py
Advanced screenshot management
"""

from playwright.sync_api import Page, Locator
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
import json
import base64


class ScreenshotManager:
    """
    Comprehensive screenshot management for tests
    
    Features:
    - Automatic directory management
    - Multiple screenshot types
    - Screenshot comparison
    - Screenshot metadata
    - Base64 encoding for reports
    """
    
    def __init__(
        self,
        base_dir: str = "artifacts/screenshots",
        test_name: str = "",
        create_subdirs: bool = True,
    ):
        """
        Initialize ScreenshotManager
        
        Args:
            base_dir: Base directory for screenshots
            test_name: Current test name (for organizing)
            create_subdirs: Create timestamped subdirectories
        """
        
        self.base_dir = Path(base_dir)
        self.test_name = test_name
        self.screenshot_count = 0
        self.screenshots: List[Dict[str, Any]] = []
        
        # Create directory structure
        if create_subdirs and test_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.test_dir = self.base_dir / f"{self._sanitize(test_name)}_{timestamp}"
        else:
            self.test_dir = self.base_dir
        
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def _sanitize(self, name: str) -> str:
        """Sanitize string for filename"""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    
    def _generate_filename(self, name: str, extension: str = "png") -> Path:
        """Generate unique filename"""
        self.screenshot_count += 1
        timestamp = datetime.now().strftime("%H%M%S_%f")
        filename = f"{self.screenshot_count:03d}_{self._sanitize(name)}_{timestamp}.{extension}"
        return self.test_dir / filename
    
    def capture(
        self,
        page: Page,
        name: str,
        description: str = "",
        full_page: bool = False,
        **kwargs,
    ) -> str:
        """
        Capture screenshot of entire page
        
        Args:
            page: Playwright page
            name: Screenshot name
            description: Description for metadata
            full_page: Capture full scrollable page
            **kwargs: Additional screenshot options
        
        Returns:
            Path to screenshot
        """
        
        filepath = self._generate_filename(name)
        
        page.screenshot(
            path=str(filepath),
            full_page=full_page,
            **kwargs,
        )
        
        # Store metadata
        metadata = {
            "name": name,
            "description": description,
            "filepath": str(filepath),
            "timestamp": datetime.now().isoformat(),
            "url": page.url,
            "title": page.title(),
            "full_page": full_page,
            "viewport": page.viewport_size,
        }
        self.screenshots.append(metadata)
        
        print(f" Screenshot: {name} -> {filepath}")
        
        return str(filepath)
    
    def capture_element(
        self,
        locator: Locator,
        name: str,
        description: str = "",
        **kwargs,
    ) -> str:
        """
        Capture screenshot of specific element
        
        Args:
            locator: Element locator
            name: Screenshot name
            description: Description for metadata
            **kwargs: Additional screenshot options
        
        Returns:
            Path to screenshot
        """
        
        filepath = self._generate_filename(name)
        
        locator.screenshot(path=str(filepath), **kwargs)
        
        metadata = {
            "name": name,
            "description": description,
            "filepath": str(filepath),
            "timestamp": datetime.now().isoformat(),
            "type": "element",
        }
        self.screenshots.append(metadata)
        
        print(f" Element screenshot: {name} -> {filepath}")
        
        return str(filepath)
    
    def capture_region(
        self,
        page: Page,
        name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        description: str = "",
    ) -> str:
        """
        Capture screenshot of specific region
        
        Args:
            page: Playwright page
            name: Screenshot name
            x, y: Top-left coordinates
            width, height: Region dimensions
            description: Description for metadata
        
        Returns:
            Path to screenshot
        """
        
        filepath = self._generate_filename(name)
        
        page.screenshot(
            path=str(filepath),
            clip={"x": x, "y": y, "width": width, "height": height},
        )
        
        metadata = {
            "name": name,
            "description": description,
            "filepath": str(filepath),
            "timestamp": datetime.now().isoformat(),
            "type": "region",
            "clip": {"x": x, "y": y, "width": width, "height": height},
        }
        self.screenshots.append(metadata)
        
        print(f" Region screenshot: {name} -> {filepath}")
        
        return str(filepath)
    
    def capture_with_highlight(
        self,
        page: Page,
        locator: Locator,
        name: str,
        description: str = "",
        highlight_style: str = "3px solid red",
    ) -> str:
        """
        Capture screenshot with element highlighted
        
        Args:
            page: Playwright page
            locator: Element to highlight
            name: Screenshot name
            description: Description
            highlight_style: CSS border style for highlight
        
        Returns:
            Path to screenshot
        """
        
        # Add highlight
        original_style = locator.evaluate(
            f"""element => {{
                const original = element.style.outline;
                element.style.outline = '{highlight_style}';
                return original;
            }}"""
        )
        
        try:
            filepath = self.capture(page, name, description)
        finally:
            # Remove highlight
            locator.evaluate(
                f"element => element.style.outline = '{original_style or ''}'"
            )
        
        return filepath
    
    def capture_comparison(
        self,
        page: Page,
        name: str,
        before_action: callable,
        after_action: callable,
        description: str = "",
    ) -> tuple:
        """
        Capture before/after screenshots for comparison
        
        Args:
            page: Playwright page
            name: Base name for screenshots
            before_action: Action to perform before "before" screenshot
            after_action: Action to perform before "after" screenshot
            description: Description
        
        Returns:
            Tuple of (before_path, after_path)
        """
        
        before_action()
        before_path = self.capture(page, f"{name}_before", f"{description} - Before")
        
        after_action()
        after_path = self.capture(page, f"{name}_after", f"{description} - After")
        
        return before_path, after_path
    
    def to_base64(self, filepath: str) -> str:
        """
        Convert screenshot to base64 for embedding in reports
        
        Args:
            filepath: Path to screenshot
        
        Returns:
            Base64 encoded string
        """
        
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def save_metadata(self) -> str:
        """
        Save screenshot metadata to JSON file
        
        Returns:
            Path to metadata file
        """
        
        metadata_path = self.test_dir / "screenshots_metadata.json"
        
        with open(metadata_path, "w") as f:
            json.dump({
                "test_name": self.test_name,
                "total_screenshots": len(self.screenshots),
                "directory": str(self.test_dir),
                "screenshots": self.screenshots,
            }, f, indent=2)
        
        return str(metadata_path)
    
    def get_all_screenshots(self) -> List[Dict[str, Any]]:
        """Get all captured screenshots metadata"""
        return self.screenshots.copy()
    
    def cleanup(self, keep_on_failure: bool = True, test_passed: bool = True):
        """
        Clean up screenshots
        
        Args:
            keep_on_failure: Keep screenshots if test failed
            test_passed: Whether the test passed
        """
        
        if test_passed and not keep_on_failure:
            import shutil
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
                print(f" Cleaned up screenshots: {self.test_dir}")