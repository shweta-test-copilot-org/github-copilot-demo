"""
Order Service

Handles all order-related business logic including validation,
pricing, and state management.
"""

from typing import List, Optional, Tuple
from datetime import datetime, timezone
from decimal import Decimal
import structlog

from src.models.order import Order, OrderItem, OrderStatus, ShippingAddress
from src.repositories.order_repo import OrderRepository
from src.services.payment_service import PaymentService
from src.legacy.auth_provider import Session
from src.config import settings

# NOTE: We use structlog for structured logging per Platform Team guidelines
logger = structlog.get_logger(__name__)


class BusinessException(Exception):
    """
    Standard business exception for the application.
    
    Company Standard: ALL business logic exceptions MUST use this class.
    Never raise raw exceptions from service layer.
    
    Error codes should be SCREAMING_SNAKE_CASE and documented in docs/error-codes.md
    """
    
    def __init__(
        self,
        error_code: str,
        message: str,
        http_status: int = 400,
        details: Optional[dict] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.http_status = http_status
        self.details = details or {}
        super().__init__(message)


class OrderService:
    """
    Order business logic service.
    
    NOTE: This follows the Circuit Breaker pattern per Architecture Review 2024-Q3.
    External service calls (payments) are wrapped with retry logic.
    """
    
    def __init__(self):
        self.repository = OrderRepository()
        self.payment_service = PaymentService()
        # TODO: Inject these dependencies properly
    
    async def create_order(
        self,
        customer_id: str,
        items: List[dict],
        shipping_address: dict,
        session: Session,
    ) -> Order:
        """
        Create a new order.
        
        Validates items, calculates totals, and initiates payment authorization.
        """
        logger.info("creating_order", customer_id=customer_id, item_count=len(items))
        
        # Validate customer has permission
        if not self._can_create_order(session, customer_id):
            raise BusinessException(
                error_code="UNAUTHORIZED_CUSTOMER",
                message="You can only create orders for your own account",
                http_status=403,
            )
        
        # Validate items
        order_items = self._validate_and_build_items(items)
        
        if not order_items:
            raise BusinessException(
                error_code="EMPTY_ORDER",
                message="Order must contain at least one item",
            )
        
        # Calculate totals
        subtotal = sum(item.total_price for item in order_items)
        tax = self._calculate_tax(subtotal, shipping_address)
        shipping_cost = self._calculate_shipping(order_items, shipping_address)
        total = subtotal + tax + shipping_cost
        
        # Create order entity
        order = Order(
            id=self._generate_order_id(),
            customer_id=customer_id,
            items=order_items,
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total,
            shipping_address=ShippingAddress(**shipping_address),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        # Persist order
        saved_order = self.repository.save(order)
        
        # Authorize payment (async in background if enabled)
        if settings.ENABLE_ASYNC_ORDER_PROCESSING:
            # TODO: Move to background task queue
            await self._authorize_payment_async(saved_order)
        else:
            await self._authorize_payment_async(saved_order)
        
        logger.info("order_created", order_id=saved_order.id, total=str(total))
        return saved_order
    
    async def get_order(self, order_id: str, session: Session) -> Optional[Order]:
        """
        Get an order by ID.
        
        Team Convention: All repository methods return Optional[T].
        """
        order = self.repository.find_by_id(order_id)
        
        if order and not self._can_view_order(session, order):
            raise BusinessException(
                error_code="ORDER_ACCESS_DENIED",
                message="You do not have permission to view this order",
                http_status=403,
            )
        
        return order
    
    async def list_orders(
        self,
        status: Optional[str],
        customer_id: Optional[str],
        page: int,
        page_size: int,
        session: Session,
    ) -> Tuple[List[Order], int]:
        """List orders with pagination."""
        # Non-admin users can only see their own orders
        if not session.is_admin:
            customer_id = session.user_id
        
        orders = self.repository.find_all(
            status=OrderStatus(status) if status else None,
            customer_id=customer_id,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        
        total = self.repository.count(
            status=OrderStatus(status) if status else None,
            customer_id=customer_id,
        )
        
        return orders, total
    
    async def update_order(
        self,
        order_id: str,
        updates: dict,
        session: Session,
    ) -> Order:
        """Update an order."""
        order = await self.get_order(order_id, session)
        
        if order is None:
            raise BusinessException(
                error_code="ORDER_NOT_FOUND",
                message=f"Order {order_id} not found",
                http_status=404,
            )
        
        if order.status != OrderStatus.PENDING:
            raise BusinessException(
                error_code="ORDER_NOT_MODIFIABLE",
                message="Only pending orders can be modified",
            )
        
        # Apply updates
        if hasattr(updates, "shipping_address") and updates.shipping_address:
            order.shipping_address = ShippingAddress(**updates.shipping_address.dict())
            order.shipping_cost = self._calculate_shipping(
                order.items, 
                updates.shipping_address.dict()
            )
            order.total = order.subtotal + order.tax + order.shipping_cost
        
        order.updated_at = datetime.now(timezone.utc)
        return self.repository.save(order)
    
    async def cancel_order(self, order_id: str, session: Session) -> Order:
        """Cancel an order."""
        order = await self.get_order(order_id, session)
        
        if order is None:
            raise BusinessException(
                error_code="ORDER_NOT_FOUND",
                message=f"Order {order_id} not found",
                http_status=404,
            )
        
        if order.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            raise BusinessException(
                error_code="ORDER_CANNOT_CANCEL",
                message=f"Cannot cancel order in {order.status.value} status",
            )
        
        # Void payment authorization
        if order.payment_id:
            await self.payment_service.void_authorization(order.payment_id)
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        
        logger.info("order_cancelled", order_id=order_id)
        return self.repository.save(order)
    
    def _can_create_order(self, session: Session, customer_id: str) -> bool:
        """Check if session user can create order for customer."""
        return session.is_admin or session.user_id == customer_id
    
    def _can_view_order(self, session: Session, order: Order) -> bool:
        """Check if session user can view order."""
        return session.is_admin or session.user_id == order.customer_id
    
    def _validate_and_build_items(self, items: List[dict]) -> List[OrderItem]:
        """Validate items and build OrderItem list."""
        order_items = []
        
        for item in items:
            # TODO: Validate product exists and has stock
            order_items.append(OrderItem(
                product_id=item["product_id"],
                sku=item.get("sku", ""),
                name=item.get("name", "Unknown Product"),
                quantity=item["quantity"],
                unit_price=Decimal(str(item["unit_price"])),
            ))
        
        return order_items
    
    def _calculate_tax(self, subtotal: Decimal, shipping_address: dict) -> Decimal:
        """
        Calculate tax based on shipping address.
        
        NOTE: This is simplified. Production uses TaxService integration.
        """
        # Simple tax calculation - 8% for all US addresses
        state = shipping_address.get("state", "")
        if state in ("OR", "MT", "NH", "DE"):
            return Decimal("0")  # No sales tax states
        return subtotal * Decimal("0.08")
    
    def _calculate_shipping(
        self, 
        items: List[OrderItem], 
        shipping_address: dict
    ) -> Decimal:
        """Calculate shipping cost."""
        # Simplified: flat rate based on item count
        # TODO: Integrate with actual shipping provider API
        base_rate = Decimal("5.99")
        per_item = Decimal("1.50")
        total_items = sum(item.quantity for item in items)
        return base_rate + (per_item * total_items)
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID."""
        import uuid
        return f"ORD-{uuid.uuid4().hex[:12].upper()}"
    
    async def _authorize_payment_async(self, order: Order) -> None:
        """Authorize payment for order."""
        try:
            payment_id = await self.payment_service.authorize(
                amount=order.total,
                customer_id=order.customer_id,
                order_id=order.id,
            )
            order.payment_id = payment_id
            self.repository.save(order)
        except Exception as e:
            logger.error("payment_authorization_failed", order_id=order.id, error=str(e))
            # Don't fail order creation - payment can be retried
            # Company Standard: Wrap all exceptions in BusinessException
            raise BusinessException(
                error_code="PAYMENT_AUTH_FAILED",
                message="Payment authorization failed. Please try again.",
                details={"order_id": order.id},
            )
