"""
Order API Tests

Tests for order-related endpoints.

Team Convention: Follow the Arrange-Act-Assert pattern in all tests.
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from src.models.order import OrderStatus


class TestOrderEndpoints:
    """Tests for /api/v1/orders endpoints."""
    
    @pytest.mark.skip(reason="TODO: Fix order creation service async issue - good exercise for participants!")
    def test_create_order_success(self, client: TestClient, auth_headers: dict, create_order_payload: dict):
        """
        Test successful order creation.
        
        Arrange: Set up authenticated client and valid payload
        Act: POST to /api/v1/orders
        Assert: Returns 201 with order details
        """
        # Update payload to use the test user's customer ID
        create_order_payload["customer_id"] = "test_user_001"
        
        response = client.post(
            "/api/v1/orders/",
            json=create_order_payload,
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("ORD-")
        assert data["status"] == "pending"
        assert data["customer_id"] == "test_user_001"
        assert len(data["items"]) == 1
    
    def test_create_order_unauthorized(self, client: TestClient, create_order_payload: dict):
        """Test order creation without authentication."""
        response = client.post("/api/v1/orders/", json=create_order_payload)
        
        assert response.status_code == 401
    
    def test_create_order_empty_items(self, client: TestClient, auth_headers: dict):
        """Test order creation with no items fails."""
        payload = {
            "customer_id": "test_user_001",
            "items": [],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Seattle",
                "state": "WA",
                "postal_code": "98101",
            },
        }
        
        response = client.post("/api/v1/orders/", json=payload, headers=auth_headers)
        
        # Should fail validation (empty items)
        assert response.status_code == 422  # Validation error
    
    def test_list_orders_authenticated(self, client: TestClient, auth_headers: dict):
        """Test listing orders for authenticated user."""
        response = client.get("/api/v1/orders/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
    
    def test_list_orders_with_status_filter(self, client: TestClient, auth_headers: dict):
        """Test listing orders filtered by status."""
        response = client.get(
            "/api/v1/orders/",
            params={"status": "pending"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        # All returned orders should be pending
        for order in data["items"]:
            assert order["status"] == "pending"
    
    def test_get_order_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent order."""
        response = client.get(
            "/api/v1/orders/ORD-DOESNOTEXIST",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "ORDER_NOT_FOUND"


class TestOrderValidation:
    """Tests for order validation rules."""
    
    def test_order_item_quantity_validation(self, client: TestClient, auth_headers: dict):
        """Test that order item quantity must be positive."""
        payload = {
            "customer_id": "test_user_001",
            "items": [
                {
                    "product_id": "prod_001",
                    "quantity": 0,  # Invalid
                    "unit_price": "10.00",
                }
            ],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Seattle",
                "state": "WA",
                "postal_code": "98101",
            },
        }
        
        response = client.post("/api/v1/orders/", json=payload, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_order_different_customer_forbidden(self, client: TestClient, auth_headers: dict):
        """Test that non-admin cannot create order for different customer."""
        payload = {
            "customer_id": "different_customer_999",  # Not the authenticated user
            "items": [
                {
                    "product_id": "prod_001",
                    "sku": "TEST",
                    "name": "Test",
                    "quantity": 1,
                    "unit_price": "10.00",
                }
            ],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Seattle",
                "state": "WA",
                "postal_code": "98101",
            },
        }
        
        response = client.post("/api/v1/orders/", json=payload, headers=auth_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED_CUSTOMER"


class TestOrderCancellation:
    """Tests for order cancellation."""
    
    # TODO: Add tests for order cancellation
    # - Test cancellation of pending order succeeds
    # - Test cancellation of shipped order fails
    # - Test cancellation voids payment authorization
    
    def test_cancel_nonexistent_order(self, client: TestClient, auth_headers: dict):
        """Test cancelling non-existent order fails."""
        response = client.post(
            "/api/v1/orders/ORD-DOESNOTEXIST/cancel",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
