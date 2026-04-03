"""
tests/utils/video_manager.py
Video recording management
"""

from playwright.sync_api import BrowserContext, Page
from pathlib import Path
from datetime import datetime
import os
import shutil


class VideoManager:
    """
    Manage video recording for tests
    
    Features:
    - Automatic video recording
    - Conditional saving (only on failure)
    - Video organization
    - Video metadata
    """
    
    def __init__(
        self,
        base_dir: str = "artifacts/videos",
        video_size: dict = None,
    ):
        """
        Initialize VideoManager
        
        Args:
            base_dir: Base directory for videos
            video_size: Video dimensions {"width": 1280, "height": 720}
        """
        
        self.base_dir = Path(base_dir)
        self.video_size = video_size or {"width": 1280, "height": 720}
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_recording_context(
        self,
        browser,
        test_name: str,
        **context_options,
    ) -> BrowserContext:
        """
        Create browser context with video recording
        
        Args:
            browser: Playwright browser
            test_name: Name of the test (for organizing)
            **context_options: Additional context options
        
        Returns:
            Browser context with video recording
        """
        
        # Create test-specific directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize(test_name)
        video_dir = self.base_dir / f"{safe_name}_{timestamp}"
        video_dir.mkdir(parents=True, exist_ok=True)
        
        context = browser.new_context(
            record_video_dir=str(video_dir),
            record_video_size=self.video_size,
            **context_options,
        )
        
        # Store metadata on context
        context._video_dir = video_dir
        context._test_name = test_name
        
        return context
    
    def _sanitize(self, name: str) -> str:
        """Sanitize string for filename"""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    
    def save_video(
        self,
        page: Page,
        final_name: str = None,
        keep: bool = True,
    ) -> str:
        """
        Save video with custom name
        
        Args:
            page: Playwright page
            final_name: Custom filename for video
            keep: Whether to keep the video
        
        Returns:
            Path to saved video (or empty if not kept)
        """
        
        if not page.video:
            return ""
        
        # Get original video path
        video_path = page.video.path()
        
        if not keep:
            # Delete video
            if os.path.exists(video_path):
                os.remove(video_path)
            return ""
        
        if final_name:
            # Rename video
            video_dir = Path(video_path).parent
            new_path = video_dir / f"{self._sanitize(final_name)}.webm"
            
            # Close video first (context must be closed)
            if os.path.exists(video_path):
                shutil.move(video_path, new_path)
                return str(new_path)
        
        return video_path
    
    def cleanup_on_success(self, context: BrowserContext):
        """
        Delete videos if test passed (save disk space)
        
        Args:
            context: Browser context with video recording
        """
        
        if hasattr(context, "_video_dir"):
            video_dir = context._video_dir
            if video_dir.exists():
                shutil.rmtree(video_dir)
                print(f" Cleaned up video: {video_dir}")
