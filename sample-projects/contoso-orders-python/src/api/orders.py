"""
Order API Endpoints

Handles all order-related HTTP operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path
from datetime import datetime
import structlog

from src.schemas.order_schemas import (
    OrderCreateRequest,
    OrderResponse,
    OrderListResponse,
    OrderUpdateRequest,
)
from src.services.order_service import OrderService, BusinessException
from src.legacy.auth_provider import get_current_session, Session

# NOTE: We use structlog for structured logging per Platform Team guidelines
logger = structlog.get_logger(__name__)

router = APIRouter()


def get_order_service() -> OrderService:
    """Dependency injection for OrderService."""
    return OrderService()


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    request: OrderCreateRequest,
    session: Session = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Create a new order.
    
    Requires authenticated session. The order will be associated with
    the customer from the session context.
    """
    logger.info(
        "create_order_request",
        customer_id=request.customer_id,
        item_count=len(request.items),
    )
    
    order = await order_service.create_order(
        customer_id=request.customer_id,
        items=request.items,
        shipping_address=request.shipping_address,
        session=session,
    )
    
    return OrderResponse.from_domain(order)


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    """
    List orders with optional filtering.
    
    Team Convention: All list endpoints must support pagination.
    """
    orders, total = await order_service.list_orders(
        status=status,
        customer_id=customer_id,
        page=page,
        page_size=page_size,
        session=session,
    )
    
    return OrderListResponse(
        items=[OrderResponse.from_domain(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str = Path(..., description="The order ID"),
    session: Session = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Get a single order by ID."""
    order = await order_service.get_order(order_id, session)
    
    if order is None:
        raise BusinessException(
            error_code="ORDER_NOT_FOUND",
            message=f"Order {order_id} not found",
            http_status=404,
        )
    
    return OrderResponse.from_domain(order)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    request: OrderUpdateRequest,
    session: Session = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Update an existing order.
    
    Only pending orders can be modified.
    """
    order = await order_service.update_order(order_id, request, session)
    return OrderResponse.from_domain(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    session: Session = Depends(get_current_session),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Cancel an order.
    
    Only pending or confirmed orders can be cancelled.
    Shipped orders require contacting support.
    """
    order = await order_service.cancel_order(order_id, session)
    return OrderResponse.from_domain(order)
