from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config.settings import settings
from app.database.db import connect_to_mongo, close_mongo_connection
from app.routers import payments, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# Include routers
app.include_router(payments.router)
app.include_router(webhooks.router)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "message": "OK",
        "status": "healthy",
        "version": settings.api_version
    }

