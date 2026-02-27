"""
Product API Endpoints

Provides product catalog access for order creation.
"""

from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from decimal import Decimal

from src.models.product import Product, ProductCategory


router = APIRouter()


# Inline schemas (different pattern than orders - shows inconsistency)
class ProductResponse(BaseModel):
    id: str
    sku: str
    name: str
    description: Optional[str]
    price: Decimal
    category: str
    in_stock: bool
    stock_quantity: int


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int


# In-memory product catalog (simulating database)
# NOTE: In production, this comes from ProductService
PRODUCT_CATALOG = [
    Product(
        id="prod_001",
        sku="LAPTOP-PRO-15",
        name="ProBook Laptop 15\"",
        description="Professional laptop with 16GB RAM",
        price=Decimal("1299.99"),
        category=ProductCategory.ELECTRONICS,
        stock_quantity=50,
    ),
    Product(
        id="prod_002",
        sku="MOUSE-WL-001",
        name="Wireless Mouse",
        description="Ergonomic wireless mouse",
        price=Decimal("49.99"),
        category=ProductCategory.ELECTRONICS,
        stock_quantity=200,
    ),
    Product(
        id="prod_003",
        sku="DESK-STD-001",
        name="Standing Desk",
        description="Adjustable height standing desk",
        price=Decimal("599.99"),
        category=ProductCategory.FURNITURE,
        stock_quantity=25,
    ),
    Product(
        id="prod_004",
        sku="CHAIR-ERG-001",
        name="Ergonomic Office Chair",
        description="Lumbar support office chair",
        price=Decimal("399.99"),
        category=ProductCategory.FURNITURE,
        stock_quantity=40,
    ),
    Product(
        id="prod_005",
        sku="MONITOR-27-4K",
        name="27\" 4K Monitor",
        description="Ultra HD professional display",
        price=Decimal("549.99"),
        category=ProductCategory.ELECTRONICS,
        stock_quantity=75,
    ),
]


@router.get("/", response_model=ProductListResponse)
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    in_stock_only: bool = Query(False, description="Show only in-stock items"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
):
    """
    List available products.
    
    NOTE: This endpoint is public (no auth required) as product
    catalog is not sensitive data.
    """
    results = PRODUCT_CATALOG.copy()
    
    if category:
        try:
            cat = ProductCategory(category.lower())
            results = [p for p in results if p.category == cat]
        except ValueError:
            raise HTTPException(400, f"Invalid category: {category}")
    
    if in_stock_only:
        results = [p for p in results if p.in_stock]
    
    if search:
        search_lower = search.lower()
        results = [
            p for p in results 
            if search_lower in p.name.lower() or 
               (p.description and search_lower in p.description.lower())
        ]
    
    if min_price is not None:
        results = [p for p in results if p.price >= min_price]
    
    if max_price is not None:
        results = [p for p in results if p.price <= max_price]
    
    return ProductListResponse(
        products=[_to_response(p) for p in results],
        total=len(results),
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    """Get a single product by ID."""
    for product in PRODUCT_CATALOG:
        if product.id == product_id:
            return _to_response(product)
    
    raise HTTPException(status_code=404, detail="Product not found")


@router.get("/sku/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str):
    """Get a product by SKU."""
    for product in PRODUCT_CATALOG:
        if product.sku == sku:
            return _to_response(product)
    
    raise HTTPException(status_code=404, detail="Product not found")


def _to_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category.value,
        in_stock=product.in_stock,
        stock_quantity=product.stock_quantity,
    )
