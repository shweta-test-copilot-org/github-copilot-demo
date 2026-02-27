"""
Order API Schemas

Pydantic models for order-related API requests and responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from src.models.order import Order, OrderStatus


class OrderItemRequest(BaseModel):
    """Item in an order creation request."""
    product_id: str = Field(..., description="Product ID")
    sku: str = Field("", description="Product SKU")
    name: str = Field("", description="Product name")
    quantity: int = Field(..., ge=1, le=100, description="Quantity to order")
    unit_price: Decimal = Field(..., ge=0, description="Price per unit")


class ShippingAddressRequest(BaseModel):
    """Shipping address for order."""
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., min_length=5, max_length=20)
    country: str = Field(default="US", max_length=2)
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class OrderCreateRequest(BaseModel):
    """Request to create a new order."""
    customer_id: str = Field(..., description="Customer ID for the order")
    items: List[OrderItemRequest] = Field(..., min_length=1, max_length=50)
    shipping_address: dict = Field(..., description="Shipping address")
    notes: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_id": "cust_001",
                "items": [
                    {
                        "product_id": "prod_001",
                        "sku": "LAPTOP-PRO-15",
                        "name": "ProBook Laptop",
                        "quantity": 1,
                        "unit_price": "1299.99"
                    }
                ],
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "Seattle",
                    "state": "WA",
                    "postal_code": "98101",
                    "country": "US"
                }
            }
        }
    )


class OrderUpdateRequest(BaseModel):
    """Request to update an existing order."""
    shipping_address: Optional[ShippingAddressRequest] = None
    notes: Optional[str] = Field(None, max_length=500)


class OrderItemResponse(BaseModel):
    """Order item in response."""
    product_id: str
    sku: str
    name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class ShippingAddressResponse(BaseModel):
    """Shipping address in response."""
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    name: Optional[str] = None
    phone: Optional[str] = None


class OrderResponse(BaseModel):
    """Order response model."""
    id: str
    customer_id: str
    status: str
    items: List[OrderItemResponse]
    subtotal: Decimal
    tax: Decimal
    shipping_cost: Decimal
    total: Decimal
    shipping_address: ShippingAddressResponse
    payment_id: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_domain(cls, order: Order) -> "OrderResponse":
        """Convert domain Order to response model."""
        return cls(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    sku=item.sku,
                    name=item.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                )
                for item in order.items
            ],
            subtotal=order.subtotal,
            tax=order.tax,
            shipping_cost=order.shipping_cost,
            total=order.total,
            shipping_address=ShippingAddressResponse(
                street=order.shipping_address.street,
                city=order.shipping_address.city,
                state=order.shipping_address.state,
                postal_code=order.shipping_address.postal_code,
                country=order.shipping_address.country,
                name=order.shipping_address.name,
                phone=order.shipping_address.phone,
            ),
            payment_id=order.payment_id,
            tracking_number=order.tracking_number,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
    
    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """Paginated list of orders."""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    
    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return (self.page * self.page_size) < self.total
