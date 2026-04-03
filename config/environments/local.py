"""
config/environments/local.py
Local development environment configuration
"""

config = {
    "browser": {
        "headless": False,  # Show browser for local debugging
        "slow_mo": 100,     # Slow down for visibility
    },
    "environment": {
        "name": "local",
        "base_url": "https://www.saucedemo.com",
    },
    "reporting": {
        "screenshot_on_failure": True,
        "keep_passed_artifacts": True,  # Keep for debugging
    },
    "parallel": {
        "enabled": False,  # Sequential for debugging
    },
}
