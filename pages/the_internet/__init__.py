"""
pages/the_internet/__init__.py
Export The Internet page objects
"""

from pages.the_internet.login_page import TheInternetLoginPage
from pages.the_internet.secure_area_page import SecureAreaPage
from pages.the_internet.dynamic_loading_page import DynamicLoadingPage

__all__ = [
    "TheInternetLoginPage",
    "SecureAreaPage",
    "DynamicLoadingPage",
]