from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from app.config.settings import settings


class MongoDB:
    """MongoDB database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


db = MongoDB()


async def connect_to_mongo():
    """Create database connection."""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.mongodb_db_name]
        await db.client.admin.command('ping')
        print(f"✅ MongoDB connected: {settings.mongodb_db_name}")
    except Exception as e:
        error_msg = str(e).lower()
        
        if "authentication failed" in error_msg or "bad auth" in error_msg:
            print("❌ MongoDB authentication failed")
            print("   → Check password in MONGODB_URL or verify Atlas user credentials")
        elif "timeout" in error_msg or "connection" in error_msg:
            print("❌ MongoDB connection timeout")
            print("   → Check network access or Atlas cluster status")
        else:
            print(f"❌ MongoDB connection failed: {str(e)[:100]}")
        
        raise


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
        print("🔌 MongoDB disconnected")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if db.database is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return db.database

