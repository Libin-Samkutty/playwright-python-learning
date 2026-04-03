"""
utils/logger.py
Centralized logging for test framework
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import os


class TestLogger:
    """
    Custom logger for test framework
    
    Features:
    - Console and file logging
    - Colored output
    - Test context tracking
    - Screenshot triggers
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m",     # Reset
    }
    
    def __init__(
        self,
        name: str = "playwright_tests",
        level: str = "INFO",
        log_file: Optional[str] = None,
        log_dir: str = "logs",
    ):
        """
        Initialize logger
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Log file path (auto-generated if None)
            log_dir: Directory for log files
        """
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers = []  # Clear existing handlers
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_colored_formatter())
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file or log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            if not log_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = f"{log_dir}/test_run_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(self._get_file_formatter())
            self.logger.addHandler(file_handler)
            
            self.log_file = log_file
    
    def _get_colored_formatter(self) -> logging.Formatter:
        """Get formatter with colors for console"""
        
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                color = TestLogger.COLORS.get(record.levelname, "")
                reset = TestLogger.COLORS["RESET"]
                
                # Format message
                timestamp = datetime.now().strftime("%H:%M:%S")
                message = f"{color}[{timestamp}] [{record.levelname:8}]{reset} {record.getMessage()}"
                
                return message
        
        return ColoredFormatter()
    
    def _get_file_formatter(self) -> logging.Formatter:
        """Get formatter for file"""
        
        return logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def step(self, step_number: int, description: str):
        """Log a test step"""
        self.info(f"Step {step_number}: {description}")
    
    def test_start(self, test_name: str):
        """Log test start"""
        self.info(f"{'='*60}")
        self.info(f"TEST START: {test_name}")
        self.info(f"{'='*60}")
    
    def test_end(self, test_name: str, passed: bool):
        """Log test end"""
        status = "[PASSED]" if passed else "[FAILED]"
        self.info(f"TEST END: {test_name} - {status}")
        self.info(f"{'='*60}")
    
    def exception(self, message: str, exc_info: bool = True):
        """Log exception with traceback"""
        self.logger.exception(message, exc_info=exc_info)


# Global logger instance
_logger: Optional[TestLogger] = None


def get_logger() -> TestLogger:
    """Get global logger instance"""
    
    global _logger
    
    if _logger is None:
        from config import get_settings
        settings = get_settings()
        
        _logger = TestLogger(
            level=settings.log_level,
            log_file=settings.log_file,
        )
    
    return _logger
