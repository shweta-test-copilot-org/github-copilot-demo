"""
Contoso Orders API - Main Application Entry Point

This module initializes the FastAPI application and registers all routers.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import structlog

from src.api import orders, customers, products
from src.config import settings
from src.services.order_service import BusinessException

# NOTE: We use structlog for structured logging per Platform Team guidelines
logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    """
    Application factory pattern.
    
    Team Convention: Always use factory pattern for testability.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Enterprise Order Management API",
        docs_url="/docs" if settings.DEBUG else None,
    )
    
    # Register routers
    app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
    app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
    app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
    
    # Register exception handlers
    register_exception_handlers(app)
    
    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""
    
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        # Company Standard: All business exceptions return structured error response
        logger.warning(
            "business_exception",
            error_code=exc.error_code,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Log full exception for debugging but return sanitized response
        logger.exception("unhandled_exception", path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred",
                }
            },
        )


app = create_app()


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer."""
    return {"status": "healthy", "version": settings.VERSION}


@app.on_event("startup")
async def startup_event():
    logger.info("application_startup", version=settings.VERSION)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("application_shutdown")
