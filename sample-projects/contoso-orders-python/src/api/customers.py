"""
Customer API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
import logging  # NOTE: This module uses stdlib logging (inconsistent with orders.py)

from src.models.customer import Customer, CustomerTier
from src.services.customer_service import CustomerService
from src.legacy.auth_provider import get_current_session, Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_customers(
    tier: Optional[str] = None,
    active_only: bool = True,
    limit: int = Query(50, le=200),
    session: Session = Depends(get_current_session),
):
    """List customers with filtering."""
    service = CustomerService()
    customers = service.get_customers(tier=tier, active_only=active_only, limit=limit)
    return {"customers": [c.to_dict() for c in customers], "count": len(customers)}


@router.get("/{customer_id}")
async def get_customer(
    customer_id: str,
    session: Session = Depends(get_current_session),
):
    service = CustomerService()
    customer = service.get_customer_by_id(customer_id)
    
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer.to_dict()


@router.post("/")
async def create_customer(
    name: str,
    email: str,
    company: Optional[str] = None,
    session: Session = Depends(get_current_session),
):
    """Create a new customer."""
    service = CustomerService()
    
    # Check for existing customer with same email
    existing = service.get_customer_by_email(email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    customer = service.create_customer(name=name, email=email, company=company)
    logger.info(f"Created customer {customer.id}")
    
    return customer.to_dict()


@router.patch("/{customer_id}")
async def update_customer(
    customer_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    tier: Optional[str] = None,
    session: Session = Depends(get_current_session),
):
    service = CustomerService()
    customer = service.update_customer(
        customer_id=customer_id,
        name=name,
        email=email,
        tier=CustomerTier(tier) if tier else None,
    )
    
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer.to_dict()


@router.get("/{customer_id}/orders")
async def get_customer_orders(
    customer_id: str,
    status: Optional[str] = None,
    session: Session = Depends(get_current_session),
):
    """Get all orders for a customer."""
    # TODO: Implement this endpoint - currently returns mock data
    return {
        "customer_id": customer_id,
        "orders": [],
        "message": "Not implemented yet"
    }
