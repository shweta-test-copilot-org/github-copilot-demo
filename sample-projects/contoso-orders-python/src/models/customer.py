"""
Customer Domain Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class CustomerTier(Enum):
    """Customer tier levels for pricing and features."""
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class Customer:
    """
    Customer domain entity.
    
    Represents a customer account in the system.
    """
    id: str
    name: str
    email: str
    tier: CustomerTier = CustomerTier.STANDARD
    company: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "tier": self.tier.value,
            "company": self.company,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def display_name(self) -> str:
        """Get display name (company name if available, else customer name)."""
        return self.company or self.name
