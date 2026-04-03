"""
data/factories/user_factory.py
User test data factory
"""

from dataclasses import dataclass, field
from typing import Optional, List
import random
import string
from datetime import datetime
import uuid


@dataclass
class User:
    """User data model"""
    
    username: str
    password: str
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    role: str = "customer"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class UserFactory:
    """
    Factory for creating test user data
    
    Usage:
        # Get predefined user
        user = UserFactory.standard_user()
        
        # Generate random user
        user = UserFactory.random_user()
        
        # Generate user with specific attributes
        user = UserFactory.create(role="admin", first_name="John")
    """
    
    # Predefined users for SauceDemo
    PREDEFINED_USERS = {
        "standard": User(
            username="standard_user",
            password="secret_sauce",
            email="standard@saucedemo.com",
            first_name="Standard",
            last_name="User",
            role="customer",
        ),
        "locked": User(
            username="locked_out_user",
            password="secret_sauce",
            email="locked@saucedemo.com",
            first_name="Locked",
            last_name="User",
            role="customer",
        ),
        "problem": User(
            username="problem_user",
            password="secret_sauce",
            email="problem@saucedemo.com",
            first_name="Problem",
            last_name="User",
            role="customer",
        ),
        "performance": User(
            username="performance_glitch_user",
            password="secret_sauce",
            email="performance@saucedemo.com",
            first_name="Performance",
            last_name="User",
            role="customer",
        ),
        "error": User(
            username="error_user",
            password="secret_sauce",
            email="error@saucedemo.com",
            first_name="Error",
            last_name="User",
            role="customer",
        ),
        "visual": User(
            username="visual_user",
            password="secret_sauce",
            email="visual@saucedemo.com",
            first_name="Visual",
            last_name="User",
            role="customer",
        ),
    }
    
    # Random data pools
    FIRST_NAMES = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
    
    @classmethod
    def standard_user(cls) -> User:
        """Get standard test user"""
        return cls.PREDEFINED_USERS["standard"]
    
    @classmethod
    def locked_user(cls) -> User:
        """Get locked out user"""
        return cls.PREDEFINED_USERS["locked"]
    
    @classmethod
    def problem_user(cls) -> User:
        """Get problem user"""
        return cls.PREDEFINED_USERS["problem"]
    
    @classmethod
    def performance_user(cls) -> User:
        """Get performance glitch user"""
        return cls.PREDEFINED_USERS["performance"]
    
    @classmethod
    def get_predefined(cls, user_type: str) -> User:
        """
        Get predefined user by type
        
        Args:
            user_type: standard, locked, problem, performance, error, visual
        """
        
        if user_type not in cls.PREDEFINED_USERS:
            raise ValueError(f"Unknown user type: {user_type}")
        
        return cls.PREDEFINED_USERS[user_type]
    
    @classmethod
    def all_valid_users(cls) -> List[User]:
        """Get all users that can successfully login"""
        
        return [
            cls.PREDEFINED_USERS["standard"],
            cls.PREDEFINED_USERS["problem"],
            cls.PREDEFINED_USERS["performance"],
            cls.PREDEFINED_USERS["error"],
            cls.PREDEFINED_USERS["visual"],
        ]
    
    @classmethod
    def random_user(cls, **overrides) -> User:
        """
        Generate random user data
        
        Args:
            **overrides: Override specific fields
        """
        
        username = cls._random_string(10)
        
        user = User(
            username=username,
            password=cls._random_string(12),
            email=f"{username}@test.com",
            first_name=random.choice(cls.FIRST_NAMES),
            last_name=random.choice(cls.LAST_NAMES),
            role="customer",
        )
        
        # Apply overrides
        for key, value in overrides.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        return user
    
    @classmethod
    def create(cls, **kwargs) -> User:
        """
        Create user with specific attributes
        
        Args:
            **kwargs: User attributes
        """
        
        return cls.random_user(**kwargs)
    
    @classmethod
    def invalid_user(cls) -> User:
        """Generate user with invalid credentials"""
        
        return User(
            username="invalid_user",
            password="invalid_password",
            email="invalid@test.com",
            first_name="Invalid",
            last_name="User",
        )
    
    @classmethod
    def batch(cls, count: int, **overrides) -> List[User]:
        """
        Generate multiple random users
        
        Args:
            count: Number of users to generate
            **overrides: Override fields for all users
        """
        
        return [cls.random_user(**overrides) for _ in range(count)]
    
    @staticmethod
    def _random_string(length: int) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))