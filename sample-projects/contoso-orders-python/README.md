# Contoso Orders API

Enterprise order management system for Contoso Corporation.

## Overview

This API handles order processing, customer management, and payment integration for the Contoso e-commerce platform.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn src.main:app --reload

# Run tests
pytest tests/
```

## Architecture

- **API Layer**: FastAPI endpoints in `src/api/`
- **Services**: Business logic in `src/services/`
- **Repositories**: Data access in `src/repositories/`
- **Models**: Domain models in `src/models/`

## Important Notes

⚠️ **Legacy Authentication**: The auth system in `src/legacy/` is managed by the Security team. Do NOT modify without approval.

## Team Contacts

- API Team: api-team@contoso.com
- Security Team: security@contoso.com
