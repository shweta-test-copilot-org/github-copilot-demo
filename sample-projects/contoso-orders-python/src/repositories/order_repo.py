"""
Order Repository

Data access for Order entities.
"""

from typing import Optional, List
from datetime import datetime

from src.repositories.base import BaseRepository
from src.models.order import Order, OrderStatus


# In-memory store (simulating database)
_ORDERS: dict[str, Order] = {}


class OrderRepository(BaseRepository[Order]):
    """
    Repository for Order entity persistence.
    
    Currently uses in-memory storage for demonstration.
    In production, this would use SQLAlchemy or similar ORM.
    
    Team Convention: All repository methods return Optional[T] for single-item lookups.
    """
    
    def find_by_id(self, entity_id: str) -> Optional[Order]:
        """Find order by ID."""
        return _ORDERS.get(entity_id)
    
    def find_all(
        self,
        offset: int = 0,
        limit: int = 100,
        status: Optional[OrderStatus] = None,
        customer_id: Optional[str] = None,
        **filters,
    ) -> List[Order]:
        """
        Find orders with optional filtering.
        
        Supports filtering by status and customer_id.
        """
        orders = list(_ORDERS.values())
        
        # Apply filters
        if status:
            orders = [o for o in orders if o.status == status]
        
        if customer_id:
            orders = [o for o in orders if o.customer_id == customer_id]
        
        # Sort by created_at descending (newest first)
        orders.sort(key=lambda o: o.created_at, reverse=True)
        
        # Apply pagination
        return orders[offset:offset + limit]
    
    def find_by_customer(self, customer_id: str) -> List[Order]:
        """Get all orders for a customer."""
        return [o for o in _ORDERS.values() if o.customer_id == customer_id]
    
    def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Get all orders with a specific status."""
        return [o for o in _ORDERS.values() if o.status == status]
    
    def save(self, entity: Order) -> Order:
        """Save or update an order."""
        entity.updated_at = datetime.utcnow()
        _ORDERS[entity.id] = entity
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete an order by ID."""
        if entity_id in _ORDERS:
            del _ORDERS[entity_id]
            return True
        return False
    
    def count(
        self,
        status: Optional[OrderStatus] = None,
        customer_id: Optional[str] = None,
        **filters,
    ) -> int:
        """Count orders matching filters."""
        orders = list(_ORDERS.values())
        
        if status:
            orders = [o for o in orders if o.status == status]
        
        if customer_id:
            orders = [o for o in orders if o.customer_id == customer_id]
        
        return len(orders)
    
    def find_recent(self, hours: int = 24) -> List[Order]:
        """
        Find orders created in the last N hours.
        
        Used for monitoring and reporting dashboards.
        """
        from datetime import timedelta, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [
            o for o in _ORDERS.values() 
            if o.created_at and o.created_at >= cutoff
        ]
