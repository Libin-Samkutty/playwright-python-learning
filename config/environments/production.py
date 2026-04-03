"""
config/environments/production.py
Production environment configuration (read-only tests)
"""

config = {
    "browser": {
        "headless": True,
    },
    "environment": {
        "name": "production",
        "base_url": "https://www.saucedemo.com",
        "mock_payments": False,  # Don't mock in production
    },
    "reporting": {
        "screenshot_on_failure": True,
    },
    "parallel": {
        "enabled": True,
        "workers": 2,  # Lower for production
    },
}
