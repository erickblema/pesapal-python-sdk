import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config.settings import settings
from app.database.db import connect_to_mongo, close_mongo_connection
from app.routers import payments, webhooks, ipn
from app.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting application...")
    await connect_to_mongo()
    logger.info("Application started successfully")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await close_mongo_connection()
    logger.info("Application shut down")


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# Include routers
app.include_router(payments.router)
app.include_router(webhooks.router)
app.include_router(ipn.router)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "message": "OK",
        "status": "healthy",
        "version": settings.api_version
    }

