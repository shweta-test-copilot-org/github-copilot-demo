"""
Application Configuration

Uses pydantic-settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Team Convention: All configuration must go through this class.
    Never use os.environ directly in application code.
    """
    
    # Application
    APP_NAME: str = "Contoso Orders API"
    VERSION: str = "2.4.1"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./contoso_orders.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Legacy Auth Service (managed by Security Team)
    # NOTE: Do not change these without Security Team approval
    AUTH_SERVICE_URL: str = "http://auth.internal.contoso.com"
    SESSION_TIMEOUT_MINUTES: int = 30
    
    # External Services
    PAYMENT_GATEWAY_URL: str = "https://payments.contoso.com/api"
    PAYMENT_GATEWAY_TIMEOUT: int = 30
    
    # Feature Flags
    ENABLE_NEW_PRICING_ENGINE: bool = False  # TODO: Enable after Q2 rollout
    ENABLE_ASYNC_ORDER_PROCESSING: bool = True
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    
    Using lru_cache ensures we only parse environment once.
    """
    return Settings()


# Convenience accessor
settings = get_settings()
