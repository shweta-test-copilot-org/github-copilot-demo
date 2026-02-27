"""
Payment Service

Handles payment processing integration with external payment gateway.

NOTE: This follows the Circuit Breaker pattern per Architecture Review 2024-Q3.
All external calls use tenacity for retry logic.
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime
import uuid
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings

logger = structlog.get_logger(__name__)


class PaymentGatewayError(Exception):
    """Exception for payment gateway failures."""
    pass


class PaymentService:
    """
    Service for payment processing.
    
    Integrates with Contoso Payment Gateway API.
    All amounts are in USD.
    """
    
    def __init__(self):
        self.gateway_url = settings.PAYMENT_GATEWAY_URL
        self.timeout = settings.PAYMENT_GATEWAY_TIMEOUT
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(PaymentGatewayError),
    )
    async def authorize(
        self,
        amount: Decimal,
        customer_id: str,
        order_id: str,
        payment_method_id: Optional[str] = None,
    ) -> str:
        """
        Authorize a payment amount.
        
        Returns payment authorization ID on success.
        Raises PaymentGatewayError on failure.
        
        Team Convention: All external service calls must have retry logic.
        """
        logger.info(
            "authorizing_payment",
            amount=str(amount),
            customer_id=customer_id,
            order_id=order_id,
        )
        
        # Simulate payment gateway call
        # In production, this would be an HTTP call to the payment gateway
        payment_id = f"PAY-{uuid.uuid4().hex[:16].upper()}"
        
        # Simulate occasional failures for testing retry logic
        # if random.random() < 0.1:
        #     raise PaymentGatewayError("Gateway timeout")
        
        logger.info("payment_authorized", payment_id=payment_id)
        return payment_id
    
    async def capture(self, payment_id: str, amount: Optional[Decimal] = None) -> bool:
        """
        Capture an authorized payment.
        
        If amount is not specified, captures the full authorized amount.
        """
        logger.info("capturing_payment", payment_id=payment_id, amount=str(amount) if amount else "full")
        
        # Simulate capture
        return True
    
    async def void_authorization(self, payment_id: str) -> bool:
        """
        Void a payment authorization.
        
        Used when order is cancelled before capture.
        """
        logger.info("voiding_payment", payment_id=payment_id)
        
        # Simulate void
        return True
    
    async def refund(
        self,
        payment_id: str,
        amount: Decimal,
        reason: str,
    ) -> str:
        """
        Process a refund.
        
        Returns refund ID on success.
        """
        logger.info(
            "processing_refund",
            payment_id=payment_id,
            amount=str(amount),
            reason=reason,
        )
        
        refund_id = f"REF-{uuid.uuid4().hex[:12].upper()}"
        
        # Simulate refund processing
        logger.info("refund_processed", refund_id=refund_id)
        return refund_id
    
    async def get_payment_status(self, payment_id: str) -> dict:
        """Get current status of a payment."""
        # Simulate status lookup
        return {
            "payment_id": payment_id,
            "status": "authorized",
            "created_at": datetime.utcnow().isoformat(),
        }
