"""
data/__init__.py
Test data management
"""

from data.factories.user_factory import UserFactory
from data.factories.product_factory import ProductFactory

__all__ = ["UserFactory", "ProductFactory"]