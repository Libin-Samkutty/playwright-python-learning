"""
tests/utils/trace_manager.py
Advanced trace recording and management
"""

from playwright.sync_api import BrowserContext, Page
from pathlib import Path
from datetime import datetime
import os
import zipfile
import json


class TraceManager:
    """
    Comprehensive trace management
    
    Features:
    - Configurable trace options
    - Conditional trace saving
    - Trace analysis
    - Trace metadata
    """
    
    def __init__(
        self,
        base_dir: str = "artifacts/traces",
        screenshots: bool = True,
        snapshots: bool = True,
        sources: bool = True,
    ):
        """
        Initialize TraceManager
        
        Args:
            base_dir: Base directory for traces
            screenshots: Include screenshots in trace
            snapshots: Include DOM snapshots
            sources: Include source code
        """
        
        self.base_dir = Path(base_dir)
        self.screenshots = screenshots
        self.snapshots = snapshots
        self.sources = sources
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def start_tracing(self, context: BrowserContext, name: str = ""):
        """
        Start tracing for a context
        
        Args:
            context: Browser context
            name: Trace name (for metadata)
        """
        
        context.tracing.start(
            screenshots=self.screenshots,
            snapshots=self.snapshots,
            sources=self.sources,
            name=name,
        )
        
        # Store metadata
        context._trace_name = name
        context._trace_start = datetime.now()
    
    def stop_and_save(
        self,
        context: BrowserContext,
        test_name: str,
        save: bool = True,
    ) -> str:
        """
        Stop tracing and optionally save
        
        Args:
            context: Browser context
            test_name: Test name for filename
            save: Whether to save the trace
        
        Returns:
            Path to trace file (or empty if not saved)
        """
        
        if not save:
            context.tracing.stop()
            return ""
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize(test_name)
        trace_path = self.base_dir / f"{safe_name}_{timestamp}.zip"
        
        context.tracing.stop(path=str(trace_path))
        
        print(f" Trace saved: {trace_path}")
        print(f"   View with: playwright show-trace {trace_path}")
        
        return str(trace_path)
    
    def _sanitize(self, name: str) -> str:
        """Sanitize string for filename"""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    
    def analyze_trace(self, trace_path: str) -> dict:
        """
        Analyze a trace file and extract information
        
        Args:
            trace_path: Path to trace zip file
        
        Returns:
            Dictionary with trace analysis
        """
        
        analysis = {
            "path": trace_path,
            "size_mb": os.path.getsize(trace_path) / (1024 * 1024),
            "actions": [],
            "screenshots_count": 0,
            "network_requests": 0,
        }
        
        try:
            with zipfile.ZipFile(trace_path, "r") as zf:
                # List contents
                file_list = zf.namelist()
                
                # Count screenshots
                analysis["screenshots_count"] = len(
                    [f for f in file_list if f.endswith(".png")]
                )
                
                # Try to read trace data
                if "trace.trace" in file_list:
                    # Trace format is internal, limited analysis
                    pass
                
                analysis["files"] = file_list
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def cleanup_old_traces(self, days: int = 7):
        """
        Clean up traces older than specified days
        
        Args:
            days: Delete traces older than this many days
        """
        
        import time
        
        cutoff = time.time() - (days * 24 * 60 * 60)
        
        for trace_file in self.base_dir.glob("*.zip"):
            if trace_file.stat().st_mtime < cutoff:
                trace_file.unlink()
                print(f" Deleted old trace: {trace_file}")
