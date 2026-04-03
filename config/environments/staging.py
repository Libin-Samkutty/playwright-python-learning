"""
config/environments/staging.py
Staging environment configuration
"""

config = {
    "browser": {
        "headless": True,
    },
    "environment": {
        "name": "staging",
        "base_url": "https://staging.saucedemo.com",  # Example
    },
    "reporting": {
        "screenshot_on_failure": True,
        "keep_passed_artifacts": False,
    },
    "parallel": {
        "enabled": True,
        "workers": 4,
    },
}
