from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config.settings import settings
from app.database.db import connect_to_mongo, close_mongo_connection
from app.routers import todos


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
app.include_router(todos.router)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "message": "OK",
        "status": "healthy",
        "version": settings.api_version
    }


@app.get("/debug/env")
async def debug_env():
    """
    Debug endpoint to check environment variables (passwords are masked).
    Useful for troubleshooting configuration issues.
    """
    import os
    from pathlib import Path
    
    env_path = Path(".env")
    env_exists = env_path.exists()
    
    # Mask MongoDB URL
    mongodb_url = settings.mongodb_url
    if mongodb_url and '@' in mongodb_url:
        parts = mongodb_url.split('@')
        if len(parts) == 2 and ':' in parts[0]:
            user, _ = parts[0].rsplit(':', 1)
            masked_url = f"{user}:***@{parts[1]}"
        else:
            masked_url = mongodb_url
    else:
        masked_url = mongodb_url
    
    return {
        "env_file_exists": env_exists,
        "env_file_path": str(env_path.absolute()) if env_exists else None,
        "settings": {
            "mongodb_url_set": bool(settings.mongodb_url),
            "mongodb_url_masked": masked_url,
            "mongodb_db_name": settings.mongodb_db_name,
            "api_title": settings.api_title,
            "api_version": settings.api_version
        },
        "environment_variables": {
            "MONGODB_URL": "***SET***" if os.getenv("MONGODB_URL") else "NOT SET",
            "MONGODB_DB_NAME": os.getenv("MONGODB_DB_NAME") or "NOT SET (using default)"
        }
    }
