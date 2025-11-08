from typing import Optional
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


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
    print("📋 Configuration:")
    print(f"   Environment: {'✅ .env file loaded' if env_exists else '⚠️  Using environment variables'}")
    print(f"   MongoDB: {'✅ Configured' if settings.mongodb_url and not has_placeholder else '❌ Not configured'}")
    if settings.mongodb_url:
        print(f"   Database: {settings.mongodb_db_name}")
    
    # Check Pesapal configuration
    pesapal_configured = settings.pesapal_consumer_key and settings.pesapal_consumer_secret
    print(f"   Pesapal: {'✅ Configured' if pesapal_configured and settings.pesapal_ipn_id else '❌ Not configured'}")
    if pesapal_configured and not settings.pesapal_ipn_id:
        print("   ⚠️  Warning: PESAPAL_IPN_ID not set - required for API 3.0")
        print("      Register an IPN URL in Pesapal dashboard to get an IPN ID")
    
    if has_placeholder:
        print("  ⚠️  Warning: Placeholder password detected - update MONGODB_URL in .env")


# Log configuration
log_configuration()

# Validate required settings
if not settings.mongodb_url:
    raise ValueError("MONGODB_URL environment variable is required")

# Check for placeholder password
if settings.mongodb_url and ("<db_password>" in settings.mongodb_url or "YOUR_PASSWORD" in settings.mongodb_url):
    raise ValueError("MONGODB_URL contains placeholder password. Please set your actual MongoDB password.")

