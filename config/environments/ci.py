"""
config/environments/ci.py
CI/CD environment configuration
"""

config = {
    "browser": {
        "headless": True,
        "slow_mo": 0,
        "args": [
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
        ],
    },
    "environment": {
        "name": "ci",
        "base_url": "https://www.saucedemo.com",
    },
    "reporting": {
        "html_report": True,
        "allure_report": True,
        "screenshot_on_failure": True,
        "keep_passed_artifacts": False,
    },
    "parallel": {
        "enabled": True,
        "workers": 4,
        "distribution": "loadfile",
    },
}
