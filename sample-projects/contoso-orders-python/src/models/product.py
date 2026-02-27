"""
Product Domain Model
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class ProductCategory(Enum):
    """Product categories."""
    ELECTRONICS = "electronics"
    FURNITURE = "furniture"
    OFFICE_SUPPLIES = "office_supplies"
    SOFTWARE = "software"


@dataclass
class Product:
    """
    Product domain entity.
    
    Represents a product in the catalog.
    """
    id: str
    sku: str
    name: str
    price: Decimal
    category: ProductCategory
    stock_quantity: int = 0
    description: Optional[str] = None
    is_active: bool = True
    
    @property
    def in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.stock_quantity > 0
    
    def has_sufficient_stock(self, quantity: int) -> bool:
        """Check if there's enough stock for requested quantity."""
        return self.stock_quantity >= quantity
    
    def reserve_stock(self, quantity: int) -> bool:
        """
        Reserve stock for an order.
        
        Returns True if reservation successful, False if insufficient stock.
        """
        if self.has_sufficient_stock(quantity):
            self.stock_quantity -= quantity
            return True
        return False
    
    def release_stock(self, quantity: int) -> None:
        """Release reserved stock (e.g., on order cancellation)."""
        self.stock_quantity += quantity
