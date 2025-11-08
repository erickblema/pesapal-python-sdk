import logging
from typing import Optional
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Settings
    mongodb_url: Optional[str] = None
    mongodb_db_name: str = "sdk_payments"
    
    # Pesapal Settings
    pesapal_consumer_key: Optional[str] = None
    pesapal_consumer_secret: Optional[str] = None
    pesapal_sandbox: bool = True
    pesapal_callback_url: Optional[str] = None
    pesapal_ipn_url: Optional[str] = None
    pesapal_ipn_id: Optional[str] = None  # IPN Notification ID (required for API 3.0)
    
    # API Settings
    api_title: str = "Pesapal Payment SDK API"
    api_version: str = "1.0.0"
    api_description: str = "Payment processing API using Pesapal SDK"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables not in this model


# Load settings
settings = Settings()


def log_configuration():
    """Log application configuration status."""
    env_path = Path(".env")
    env_exists = env_path.exists()
    
    # Check for placeholder password
    has_placeholder = False
    if settings.mongodb_url:
        has_placeholder = "<db_password>" in settings.mongodb_url or "YOUR_PASSWORD" in settings.mongodb_url
    
    # Log configuration
    if env_exists:
        logger.info("Configuration loaded from .env file")
    else:
        logger.info("Configuration loaded from environment variables")
    
    if settings.mongodb_url and not has_placeholder:
        logger.info(f"MongoDB configured: {settings.mongodb_db_name}")
    elif not settings.mongodb_url:
        logger.warning("MongoDB not configured")
    else:
        logger.warning("MongoDB URL contains placeholder password")
    
    # Check Pesapal configuration
    pesapal_configured = settings.pesapal_consumer_key and settings.pesapal_consumer_secret
    if pesapal_configured and settings.pesapal_ipn_id:
        logger.info("Pesapal configured and ready")
    elif pesapal_configured:
        logger.warning("PESAPAL_IPN_ID not set - required for API 3.0")
    else:
        logger.warning("Pesapal not configured")
    
    if has_placeholder:
        logger.warning("MONGODB_URL contains placeholder password - update in .env")


# Log configuration
log_configuration()

# Validate required settings
if not settings.mongodb_url:
    raise ValueError("MONGODB_URL environment variable is required")

# Check for placeholder password
if settings.mongodb_url and ("<db_password>" in settings.mongodb_url or "YOUR_PASSWORD" in settings.mongodb_url):
    raise ValueError("MONGODB_URL contains placeholder password. Please set your actual MongoDB password.")

