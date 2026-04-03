"""
config/__init__.py
Configuration management for test framework
"""

from config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
