"""
config/settings.py
Main configuration settings with environment support
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
import json


@dataclass
class BrowserConfig:
    """Browser configuration"""
    
    name: str = "chromium"
    headless: bool = True
    slow_mo: int = 0
    args: List[str] = field(default_factory=list)
    
    # Viewport
    viewport_width: int = 1280
    viewport_height: int = 720
    
    # Timeouts (ms)
    default_timeout: int = 30000
    navigation_timeout: int = 30000
    
    # Recording
    record_video: bool = False
    record_trace: bool = False
    screenshot_on_failure: bool = True


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration"""
    
    name: str = "local"
    base_url: str = "https://www.saucedemo.com"
    api_url: str = ""
    
    # Credentials
    default_username: str = "standard_user"
    default_password: str = "secret_sauce"
    
    # Feature flags
    enable_analytics: bool = False
    mock_payments: bool = True


@dataclass
class ReportingConfig:
    """Reporting configuration"""
    
    # Directories
    report_dir: str = "reports"
    screenshot_dir: str = "artifacts/screenshots"
    video_dir: str = "artifacts/videos"
    trace_dir: str = "artifacts/traces"
    
    # Report types
    html_report: bool = True
    allure_report: bool = True
    
    # Retention
    keep_passed_artifacts: bool = False
    artifact_retention_days: int = 7


@dataclass
class ParallelConfig:
    """Parallel execution configuration"""
    
    enabled: bool = True
    workers: int = 4  # 'auto' in pytest is handled separately
    distribution: str = "loadfile"  # loadfile, loadscope, load


@dataclass
class Settings:
    """
    Main settings class combining all configurations
    
    Usage:
        settings = Settings.load()
        print(settings.environment.base_url)
    """
    
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    parallel: ParallelConfig = field(default_factory=ParallelConfig)
    
    # Retry configuration
    retry_count: int = 0
    retry_delay: float = 1.0
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @classmethod
    def load(cls, env: str = None) -> "Settings":
        """
        Load settings for specified environment
        
        Args:
            env: Environment name (local, staging, production, ci)
                 If None, uses PLAYWRIGHT_ENV or defaults to 'local'
        
        Returns:
            Settings instance
        """
        
        # Determine environment
        env = env or os.environ.get("PLAYWRIGHT_ENV", "local")
        
        # Base settings
        settings = cls()
        
        # Load environment-specific overrides
        env_config = cls._load_env_config(env)
        
        # Apply environment settings
        if env_config:
            settings = cls._merge_config(settings, env_config)
        
        # Apply environment variable overrides
        settings = cls._apply_env_vars(settings)
        
        return settings
    
    @classmethod
    def _load_env_config(cls, env: str) -> Optional[Dict[str, Any]]:
        """Load environment configuration file"""
        
        config_path = Path(__file__).parent / "environments" / f"{env}.json"
        
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        
        # Try Python config
        try:
            if env == "local":
                from config.environments.local import config
                return config
            elif env == "staging":
                from config.environments.staging import config
                return config
            elif env == "production":
                from config.environments.production import config
                return config
            elif env == "ci":
                from config.environments.ci import config
                return config
        except ImportError:
            pass
        
        return None
    
    @classmethod
    def _merge_config(cls, settings: "Settings", config: Dict) -> "Settings":
        """Merge configuration dictionary into settings"""
        
        if "browser" in config:
            for key, value in config["browser"].items():
                if hasattr(settings.browser, key):
                    setattr(settings.browser, key, value)
        
        if "environment" in config:
            for key, value in config["environment"].items():
                if hasattr(settings.environment, key):
                    setattr(settings.environment, key, value)
        
        if "reporting" in config:
            for key, value in config["reporting"].items():
                if hasattr(settings.reporting, key):
                    setattr(settings.reporting, key, value)
        
        if "parallel" in config:
            for key, value in config["parallel"].items():
                if hasattr(settings.parallel, key):
                    setattr(settings.parallel, key, value)
        
        return settings
    
    @classmethod
    def _apply_env_vars(cls, settings: "Settings") -> "Settings":
        """Apply environment variable overrides"""
        
        # Browser
        if os.environ.get("BROWSER"):
            settings.browser.name = os.environ["BROWSER"]
        
        if os.environ.get("HEADLESS"):
            settings.browser.headless = os.environ["HEADLESS"].lower() == "true"
        
        if os.environ.get("SLOW_MO"):
            settings.browser.slow_mo = int(os.environ["SLOW_MO"])
        
        # Environment
        if os.environ.get("BASE_URL"):
            settings.environment.base_url = os.environ["BASE_URL"]
        
        if os.environ.get("TEST_USERNAME"):
            settings.environment.default_username = os.environ["TEST_USERNAME"]
        
        if os.environ.get("TEST_PASSWORD"):
            settings.environment.default_password = os.environ["TEST_PASSWORD"]
        
        # Parallel
        if os.environ.get("PARALLEL_WORKERS"):
            settings.parallel.workers = int(os.environ["PARALLEL_WORKERS"])
        
        return settings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        
        from dataclasses import asdict
        return asdict(self)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance (singleton pattern)
    
    Usage:
        from config import get_settings
        settings = get_settings()
    """
    
    global _settings
    
    if _settings is None:
        _settings = Settings.load()
    
    return _settings


def reload_settings(env: str = None) -> Settings:
    """Reload settings (useful for testing)"""
    
    global _settings
    _settings = Settings.load(env)
    return _settings
