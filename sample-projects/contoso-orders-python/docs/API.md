# Contoso Orders API Documentation

## Overview

The Contoso Orders API provides programmatic access to order management functionality.

**Base URL**: `https://api.orders.contoso.com/api/v1`

**Authentication**: All endpoints (except products) require session-based authentication.
Include your session ID in the `X-Session-ID` header.

## Quick Start

```bash
# List your orders
curl -H "X-Session-ID: your_session_id" \
  https://api.orders.contoso.com/api/v1/orders

# Create an order  
curl -X POST -H "X-Session-ID: your_session_id" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "cust_001", "items": [...]}' \
  https://api.orders.contoso.com/api/v1/orders
```

## Endpoints

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /orders | List orders |
| POST | /orders | Create order |
| GET | /orders/{id} | Get order |
| PATCH | /orders/{id} | Update order |
| POST | /orders/{id}/cancel | Cancel order |

### Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /customers | List customers |
| POST | /customers | Create customer |
| GET | /customers/{id} | Get customer |
| PATCH | /customers/{id} | Update customer |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /products | List products (public) |
| GET | /products/{id} | Get product (public) |

## Error Handling

All errors return a structured response:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### Common Error Codes

- `ORDER_NOT_FOUND` - Order does not exist
- `UNAUTHORIZED_CUSTOMER` - Cannot access this customer's data
- `ORDER_NOT_MODIFIABLE` - Order cannot be changed in current status
- `PAYMENT_AUTH_FAILED` - Payment authorization failed

## Rate Limiting

- 100 requests per minute per session
- Rate limit headers included in response

---

*Last updated: 2025-11-15*
