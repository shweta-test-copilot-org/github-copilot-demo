"""
Customer API Tests
"""

import pytest
from fastapi.testclient import TestClient


class TestCustomerEndpoints:
    """Tests for customer API endpoints."""
    
    def test_list_customers(self, client: TestClient, auth_headers: dict):
        """Test listing customers."""
        response = client.get("/api/v1/customers/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert "count" in data
    
    def test_list_customers_filter_by_tier(self, client: TestClient, auth_headers: dict):
        """Test filtering customers by tier."""
        response = client.get(
            "/api/v1/customers/",
            params={"tier": "enterprise"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        for customer in data["customers"]:
            assert customer["tier"] == "enterprise"
    
    def test_get_customer_by_id(self, client: TestClient, auth_headers: dict):
        """Test getting a customer by ID."""
        response = client.get(
            "/api/v1/customers/cust_001",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "cust_001"
        assert "name" in data
        assert "email" in data
    
    def test_get_customer_not_found(self, client: TestClient, auth_headers: dict):
        response = client.get(
            "/api/v1/customers/nonexistent_customer",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
    
    def test_create_customer(self, client: TestClient, auth_headers: dict):
        """Test creating a new customer."""
        response = client.post(
            "/api/v1/customers/",
            params={
                "name": "New Test Customer",
                "email": "newcustomer@test.com",
                "company": "Test Company Inc",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Test Customer"
        assert data["email"] == "newcustomer@test.com"
        assert data["tier"] == "standard"  # Default tier
    
    def test_create_customer_duplicate_email(self, client: TestClient, auth_headers: dict):
        """Test that duplicate email is rejected."""
        # First create a customer
        client.post(
            "/api/v1/customers/",
            params={
                "name": "First Customer",
                "email": "duplicate@test.com",
            },
            headers=auth_headers,
        )
        
        # Try to create another with same email
        response = client.post(
            "/api/v1/customers/",
            params={
                "name": "Second Customer",
                "email": "duplicate@test.com",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_update_customer(self, client: TestClient, auth_headers: dict):
        """Test updating customer details."""
        response = client.patch(
            "/api/v1/customers/cust_001",
            params={"name": "Updated Name"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"


# TODO: Add more comprehensive tests
# - Test customer tier upgrade/downgrade
# - Test customer deactivation
# - Test customer order history endpoint
