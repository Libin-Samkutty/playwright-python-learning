"""
data/factories/product_factory.py
Product test data factory
"""

from dataclasses import dataclass, field
from typing import List, Optional
from decimal import Decimal
import uuid


@dataclass
class Product:
    """Product data model"""
    
    id: str
    name: str
    description: str
    price: Decimal
    image_url: str = ""
    inventory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def price_display(self) -> str:
        """Formatted price string"""
        return f"${self.price:.2f}"
    
    @property
    def add_to_cart_id(self) -> str:
        """Generate add-to-cart button ID"""
        return f"add-to-cart-{self.id}"
    
    @property
    def remove_id(self) -> str:
        """Generate remove button ID"""
        return f"remove-{self.id}"


class ProductFactory:
    """
    Factory for creating test product data
    
    Usage:
        # Get specific product
        product = ProductFactory.backpack()
        
        # Get all products
        products = ProductFactory.all_products()
        
        # Get products by criteria
        cheap = ProductFactory.get_cheapest()
    """
    
    # SauceDemo products
    PRODUCTS = {
        "backpack": Product(
            id="sauce-labs-backpack",
            name="Sauce Labs Backpack",
            description="carry.allTheThings() with the sleek, streamlined Sly Pack...",
            price=Decimal("29.99"),
        ),
        "bike_light": Product(
            id="sauce-labs-bike-light",
            name="Sauce Labs Bike Light",
            description="A red light isn't the dubious caused by a alarm...",
            price=Decimal("9.99"),
        ),
        "bolt_tshirt": Product(
            id="sauce-labs-bolt-t-shirt",
            name="Sauce Labs Bolt T-Shirt",
            description="Get your testing superhero on with the Sauce Labs bolt T-shirt...",
            price=Decimal("15.99"),
        ),
        "fleece_jacket": Product(
            id="sauce-labs-fleece-jacket",
            name="Sauce Labs Fleece Jacket",
            description="It's not every day that you come across a midweight quarter-zip fleece jacket...",
            price=Decimal("49.99"),
        ),
        "onesie": Product(
            id="sauce-labs-onesie",
            name="Sauce Labs Onesie",
            description="Rib snap infant onesie for the junior automation engineer...",
            price=Decimal("7.99"),
        ),
        "red_tshirt": Product(
            id="test.allthethings()-t-shirt-(red)",
            name="Test.allTheThings() T-Shirt (Red)",
            description="This classic Sauce Labs t-shirt is perfect to wear when cozying up...",
            price=Decimal("15.99"),
        ),
    }
    
    @classmethod
    def backpack(cls) -> Product:
        """Get backpack product"""
        return cls.PRODUCTS["backpack"]
    
    @classmethod
    def bike_light(cls) -> Product:
        """Get bike light product"""
        return cls.PRODUCTS["bike_light"]
    
    @classmethod
    def bolt_tshirt(cls) -> Product:
        """Get bolt t-shirt product"""
        return cls.PRODUCTS["bolt_tshirt"]
    
    @classmethod
    def fleece_jacket(cls) -> Product:
        """Get fleece jacket product"""
        return cls.PRODUCTS["fleece_jacket"]
    
    @classmethod
    def onesie(cls) -> Product:
        """Get onesie product"""
        return cls.PRODUCTS["onesie"]
    
    @classmethod
    def red_tshirt(cls) -> Product:
        """Get red t-shirt product"""
        return cls.PRODUCTS["red_tshirt"]
    
    @classmethod
    def get_by_id(cls, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        
        for product in cls.PRODUCTS.values():
            if product.id == product_id:
                return product
        return None
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional[Product]:
        """Get product by name (partial match)"""
        
        name_lower = name.lower()
        for product in cls.PRODUCTS.values():
            if name_lower in product.name.lower():
                return product
        return None
    
    @classmethod
    def all_products(cls) -> List[Product]:
        """Get all products"""
        return list(cls.PRODUCTS.values())
    
    @classmethod
    def get_cheapest(cls) -> Product:
        """Get cheapest product"""
        return min(cls.all_products(), key=lambda p: p.price)
    
    @classmethod
    def get_most_expensive(cls) -> Product:
        """Get most expensive product"""
        return max(cls.all_products(), key=lambda p: p.price)
    
    @classmethod
    def sorted_by_price_asc(cls) -> List[Product]:
        """Get products sorted by price ascending"""
        return sorted(cls.all_products(), key=lambda p: p.price)
    
    @classmethod
    def sorted_by_price_desc(cls) -> List[Product]:
        """Get products sorted by price descending"""
        return sorted(cls.all_products(), key=lambda p: p.price, reverse=True)
    
    @classmethod
    def sorted_by_name_asc(cls) -> List[Product]:
        """Get products sorted by name A-Z"""
        return sorted(cls.all_products(), key=lambda p: p.name)
    
    @classmethod
    def sorted_by_name_desc(cls) -> List[Product]:
        """Get products sorted by name Z-A"""
        return sorted(cls.all_products(), key=lambda p: p.name, reverse=True)
    
    @classmethod
    def random_product(cls) -> Product:
        """Get random product"""
        import random
        return random.choice(cls.all_products())
    
    @classmethod
    def random_products(cls, count: int) -> List[Product]:
        """Get random products (unique)"""
        import random
        all_products = cls.all_products()
        count = min(count, len(all_products))
        return random.sample(all_products, count)
    
    @classmethod
    def total_price(cls, products: List[Product]) -> Decimal:
        """Calculate total price of products"""
        return sum(p.price for p in products)