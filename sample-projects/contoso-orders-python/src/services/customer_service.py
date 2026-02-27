"""
Customer Service

Business logic for customer management.
"""

from typing import List, Optional
from datetime import datetime, timezone
import logging
import uuid

from src.models.customer import Customer, CustomerTier

# Using stdlib logging here (inconsistent with order_service which uses structlog)
logger = logging.getLogger(__name__)


# In-memory customer store (simulating database)
_CUSTOMERS: dict[str, Customer] = {
    "cust_001": Customer(
        id="cust_001",
        name="Acme Corporation",
        email="orders@acme.com",
        company="Acme Corp",
        tier=CustomerTier.ENTERPRISE,
        is_active=True,
    ),
    "cust_002": Customer(
        id="cust_002",
        name="Jane Smith",
        email="jane.smith@email.com",
        tier=CustomerTier.STANDARD,
        is_active=True,
    ),
    "cust_003": Customer(
        id="cust_003",
        name="Bob Johnson",
        email="bob.j@startup.io",
        company="StartupIO",
        tier=CustomerTier.PREMIUM,
        is_active=True,
    ),
}


class CustomerService:
    """Service for customer operations."""
    
    def get_customers(
        self,
        tier: Optional[str] = None,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Customer]:
        """Get list of customers with optional filtering."""
        customers = list(_CUSTOMERS.values())
        
        if active_only:
            customers = [c for c in customers if c.is_active]
        
        if tier:
            try:
                tier_enum = CustomerTier(tier.lower())
                customers = [c for c in customers if c.tier == tier_enum]
            except ValueError:
                logger.warning(f"Invalid tier filter: {tier}")
        
        return customers[:limit]
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """
        Get customer by ID.
        
        Team Convention: All repository methods return Optional[T]
        """
        return _CUSTOMERS.get(customer_id)
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Look up customer by email address."""
        email_lower = email.lower()
        for customer in _CUSTOMERS.values():
            if customer.email.lower() == email_lower:
                return customer
        return None
    
    def create_customer(
        self,
        name: str,
        email: str,
        company: Optional[str] = None,
    ) -> Customer:
        """Create a new customer."""
        customer_id = f"cust_{uuid.uuid4().hex[:8]}"
        
        customer = Customer(
            id=customer_id,
            name=name,
            email=email,
            company=company,
            tier=CustomerTier.STANDARD,  # All new customers start as standard
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        
        _CUSTOMERS[customer_id] = customer
        logger.info(f"Created new customer: {customer_id}")
        
        return customer
    
    def update_customer(
        self,
        customer_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        tier: Optional[CustomerTier] = None,
    ) -> Optional[Customer]:
        """Update customer details."""
        customer = self.get_customer_by_id(customer_id)
        
        if customer is None:
            return None
        
        if name:
            customer.name = name
        if email:
            customer.email = email
        if tier:
            customer.tier = tier
        
        customer.updated_at = datetime.now(timezone.utc)
        _CUSTOMERS[customer_id] = customer
        
        return customer
    
    def deactivate_customer(self, customer_id: str) -> bool:
        """
        Deactivate a customer account.
        
        Note: We soft-delete customers for audit trail purposes.
        """
        customer = self.get_customer_by_id(customer_id)
        if customer:
            customer.is_active = False
            customer.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def calculate_discount_rate(self, customer_id: str) -> float:
        """
        Calculate discount rate based on customer tier.
        
        TODO: Move discount rates to configuration
        """
        customer = self.get_customer_by_id(customer_id)
        if customer is None:
            return 0.0
        
        discount_rates = {
            CustomerTier.STANDARD: 0.0,
            CustomerTier.PREMIUM: 0.05,  # 5% discount
            CustomerTier.ENTERPRISE: 0.10,  # 10% discount
        }
        
        return discount_rates.get(customer.tier, 0.0)
