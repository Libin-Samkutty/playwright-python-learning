"""
Data Factories for API Testing
-------------------------------
Generate realistic test data using Faker library

Benefits:
- Consistent test data
- Realistic data (names, emails, addresses)
- Easy to customize
- Avoid hardcoded values
"""

from faker import Faker
import random

fake = Faker()


class PostFactory:
    """
    Factory for creating post data
    
    Usage:
        post_data = PostFactory.create()
        post_data = PostFactory.create(title="Custom Title")
    """
    
    @staticmethod
    def create(user_id=None, title=None, body=None):
        """
        Create post data
        
        Args:
            user_id: User ID (auto-generated if None)
            title: Post title (auto-generated if None)
            body: Post content (auto-generated if None)
        
        Returns:
            dict: Post data
        """
        return {
            "userId": user_id or random.randint(1, 10),
            "title": title or fake.sentence(nb_words=6),
            "body": body or fake.paragraph(nb_sentences=3)
        }
    
    @staticmethod
    def create_batch(count=5, **kwargs):
        """
        Create multiple posts
        
        Args:
            count: Number of posts to create
            **kwargs: Override fields for all posts
        
        Returns:
            list: List of post data dicts
        """
        return [PostFactory.create(**kwargs) for _ in range(count)]
    
    @staticmethod
    def create_with_id(post_id, **kwargs):
        """Create post with specific ID"""
        data = PostFactory.create(**kwargs)
        data["id"] = post_id
        return data


class UserFactory:
    """
    Factory for creating user data
    
    Generates realistic user profiles
    """
    
    @staticmethod
    def create(name=None, username=None, email=None):
        """
        Create user data
        
        Returns:
            dict: User data with realistic values
        """
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        return {
            "name": name or f"{first_name} {last_name}",
            "username": username or fake.user_name(),
            "email": email or fake.email(),
            "phone": fake.phone_number(),
            "website": fake.domain_name(),
            "address": {
                "street": fake.street_address(),
                "suite": f"Apt. {random.randint(1, 999)}",
                "city": fake.city(),
                "zipcode": fake.zipcode(),
                "geo": {
                    "lat": str(fake.latitude()),
                    "lng": str(fake.longitude())
                }
            },
            "company": {
                "name": fake.company(),
                "catchPhrase": fake.catch_phrase(),
                "bs": fake.bs()
            }
        }
    
    @staticmethod
    def create_simple(name=None, email=None):
        """
        Create user with minimal fields
        
        For APIs that don't need full profile
        """
        return {
            "name": name or fake.name(),
            "username": fake.user_name(),
            "email": email or fake.email()
        }
    
    @staticmethod
    def create_batch(count=5):
        """Create multiple users"""
        return [UserFactory.create() for _ in range(count)]


class ProductFactory:
    """
    Factory for product data (for e-commerce APIs)
    """
    
    CATEGORIES = [
        "smartphones", "laptops", "fragrances", "skincare", 
        "groceries", "home-decoration", "furniture"
    ]
    
    @staticmethod
    def create(title=None, price=None, category=None):
        """
        Create product data
        
        Returns:
            dict: Product data
        """
        return {
            "title": title or f"{fake.word().capitalize()} {fake.word().capitalize()}",
            "description": fake.text(max_nb_chars=200),
            "price": price or round(random.uniform(10, 1000), 2),
            "discountPercentage": round(random.uniform(0, 30), 2),
            "rating": round(random.uniform(3.5, 5.0), 2),
            "stock": random.randint(0, 100),
            "brand": fake.company(),
            "category": category or random.choice(ProductFactory.CATEGORIES),
            "thumbnail": fake.image_url(),
            "images": [fake.image_url() for _ in range(random.randint(1, 5))]
        }
    
    @staticmethod
    def create_batch(count=5, **kwargs):
        """Create multiple products"""
        return [ProductFactory.create(**kwargs) for _ in range(count)]
    
    @staticmethod
    def create_by_category(category):
        """Create product in specific category"""
        return ProductFactory.create(category=category)


class LoginFactory:
    """
    Factory for login credentials
    """
    
    # Known test users for DummyJSON
    DUMMYJSON_USERS = [
        {"username": "emilys", "password": "emilyspass"},
        {"username": "michaelw", "password": "michaelwpass"},
        {"username": "sophiab", "password": "sophiabpass"}
    ]
    
    @staticmethod
    def create_dummyjson_credentials(username=None):
        """
        Get DummyJSON test credentials
        
        Args:
            username: Specific username, or random if None
        
        Returns:
            dict: {username, password}
        """
        if username:
            user = next((u for u in LoginFactory.DUMMYJSON_USERS if u["username"] == username), None)
            if user:
                return user
        
        return random.choice(LoginFactory.DUMMYJSON_USERS)
    
    @staticmethod
    def create_custom(username=None, password=None):
        """Create custom login credentials"""
        return {
            "username": username or fake.user_name(),
            "password": password or fake.password(length=12)
        }


class QueryParamsFactory:
    """
    Factory for query parameters
    
    Useful for testing pagination, filtering, etc.
    """
    
    @staticmethod
    def create_pagination(page=None, limit=None):
        """Create pagination params"""
        return {
            "limit": limit or random.choice([10, 20, 50]),
            "skip": (page - 1) * limit if page and limit else 0
        }
    
    @staticmethod
    def create_search(query=None):
        """Create search params"""
        return {
            "q": query or fake.word()
        }
    
    @staticmethod
    def create_filter(user_id=None, category=None):
        """Create filter params"""
        params = {}
        if user_id:
            params["userId"] = user_id
        if category:
            params["category"] = category
        return params