"""
Order Domain Model

Represents an order in the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class OrderStatus(Enum):
    """Order lifecycle states."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class ShippingAddress:
    """Shipping address for an order."""
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "US"
    name: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class OrderItem:
    """Individual item in an order."""
    product_id: str
    sku: str
    name: str
    quantity: int
    unit_price: Decimal
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price for this line item."""
        return self.unit_price * self.quantity


@dataclass
class Order:
    """
    Order domain entity.
    
    Represents a customer order with items, payment, and shipping details.
    """
    id: str
    customer_id: str
    items: List[OrderItem]
    status: OrderStatus
    subtotal: Decimal
    tax: Decimal
    shipping_cost: Decimal
    total: Decimal
    shipping_address: ShippingAddress
    created_at: datetime
    updated_at: datetime
    payment_id: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    
    @property
    def item_count(self) -> int:
        """Total number of items in order."""
        return sum(item.quantity for item in self.items)
    
    @property  
    def is_cancellable(self) -> bool:
        """Check if order can be cancelled."""
        return self.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED)
    
    @property
    def is_modifiable(self) -> bool:
        """Check if order can be modified."""
        return self.status == OrderStatus.PENDING
    
    def can_transition_to(self, new_status: OrderStatus) -> bool:
        """
        Check if order can transition to a new status.
        
        Valid transitions:
        - PENDING -> CONFIRMED, CANCELLED
        - CONFIRMED -> PROCESSING, CANCELLED
        - PROCESSING -> SHIPPED, CANCELLED
        - SHIPPED -> DELIVERED
        - DELIVERED -> REFUNDED
        """
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [OrderStatus.REFUNDED],
            OrderStatus.CANCELLED: [],
            OrderStatus.REFUNDED: [],
        }
        return new_status in valid_transitions.get(self.status, [])
