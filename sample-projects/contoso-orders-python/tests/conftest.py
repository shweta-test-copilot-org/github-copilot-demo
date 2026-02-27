"""
Pytest Configuration and Fixtures

This file contains shared fixtures used across all test modules.

Team Convention: All new tests should use these fixtures.
Do not create duplicate fixtures in individual test files.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app
from src.models.order import Order, OrderItem, OrderStatus, ShippingAddress
from src.models.customer import Customer, CustomerTier
from src.legacy.auth_provider import Session, _SESSION_STORE

# NOTE: Use datetime.utcnow() to match legacy auth_provider pattern (naive datetime)
# Do NOT use timezone-aware datetimes here - it causes comparison issues


# =============================================================================
# CLIENT FIXTURES
# =============================================================================

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Synchronous test client for FastAPI.
    
    Use this for simple endpoint tests that don't require async.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client() -> AsyncClient:
    """
    Async test client for FastAPI.
    
    Use this when testing async endpoints or when you need
    to make multiple concurrent requests.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================

@pytest.fixture
def test_session() -> Session:
    """
    Create a test session for authenticated requests.
    
    Usage:
        def test_protected_endpoint(client, test_session):
            response = client.get(
                "/api/v1/orders",
                headers={"X-Session-ID": test_session.session_id}
            )
    """
    session = Session(
        session_id="test_session_12345",
        user_id="test_user_001",
        user_email="test@contoso.com",
        is_admin=False,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    _SESSION_STORE[session.session_id] = session
    yield session
    # Cleanup
    _SESSION_STORE.pop(session.session_id, None)


@pytest.fixture
def admin_session() -> Session:
    """
    Create an admin session for testing admin-only endpoints.
    """
    session = Session(
        session_id="admin_test_session_12345",
        user_id="admin_test_001",
        user_email="admin.test@contoso.com",
        is_admin=True,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    _SESSION_STORE[session.session_id] = session
    yield session
    # Cleanup
    _SESSION_STORE.pop(session.session_id, None)


@pytest.fixture
def auth_headers(test_session: Session) -> dict:
    """
    Convenience fixture for authentication headers.
    
    Usage:
        def test_endpoint(client, auth_headers):
            response = client.get("/api/v1/orders", headers=auth_headers)
    """
    return {"X-Session-ID": test_session.session_id}


@pytest.fixture
def admin_headers(admin_session: Session) -> dict:
    """Authentication headers for admin requests."""
    return {"X-Session-ID": admin_session.session_id}


# =============================================================================
# DOMAIN OBJECT FIXTURES
# =============================================================================

@pytest.fixture
def sample_customer() -> Customer:
    """Create a sample customer for testing."""
    return Customer(
        id="cust_test_001",
        name="Test Customer",
        email="customer@test.com",
        company="Test Corp",
        tier=CustomerTier.PREMIUM,
        is_active=True,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_order_item() -> OrderItem:
    """Create a sample order item."""
    return OrderItem(
        product_id="prod_test_001",
        sku="TEST-SKU-001",
        name="Test Product",
        quantity=2,
        unit_price=Decimal("99.99"),
    )


@pytest.fixture
def sample_shipping_address() -> ShippingAddress:
    """Create a sample shipping address."""
    return ShippingAddress(
        street="123 Test Street",
        city="Test City",
        state="WA",
        postal_code="98101",
        country="US",
        name="Test Recipient",
        phone="555-0100",
    )


@pytest.fixture
def sample_order(
    sample_order_item: OrderItem,
    sample_shipping_address: ShippingAddress,
) -> Order:
    """
    Create a sample order for testing.
    
    This fixture depends on sample_order_item and sample_shipping_address.
    """
    return Order(
        id="ORD-TEST12345678",
        customer_id="cust_test_001",
        items=[sample_order_item],
        status=OrderStatus.PENDING,
        subtotal=Decimal("199.98"),
        tax=Decimal("16.00"),
        shipping_cost=Decimal("8.99"),
        total=Decimal("224.97"),
        shipping_address=sample_shipping_address,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


# =============================================================================
# REQUEST PAYLOAD FIXTURES
# =============================================================================

@pytest.fixture
def create_order_payload() -> dict:
    """
    Sample payload for creating an order.
    
    Use this as a base and modify as needed for specific tests.
    """
    return {
        "customer_id": "cust_test_001",
        "items": [
            {
                "product_id": "prod_001",
                "sku": "LAPTOP-PRO-15",
                "name": "ProBook Laptop 15\"",
                "quantity": 1,
                "unit_price": "1299.99",
            }
        ],
        "shipping_address": {
            "street": "123 Test Street",
            "city": "Seattle",
            "state": "WA",
            "postal_code": "98101",
            "country": "US",
        },
    }


# =============================================================================
# CLEANUP FIXTURES  
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_orders():
    """
    Automatically clean up orders after each test.
    
    This ensures tests don't interfere with each other.
    """
    from src.repositories.order_repo import _ORDERS
    
    # Store existing orders
    existing_orders = dict(_ORDERS)
    
    yield
    
    # Restore original state after test
    _ORDERS.clear()
    _ORDERS.update(existing_orders)
