# SDK Payments API

A FastAPI-based payment processing SDK API with Alembic migrations and Neon Postgres database.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Neon Postgres connection string:

```env
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**For Neon Postgres:**
- Get your connection string from the Neon dashboard
- Format: `postgresql://username:password@host/database?sslmode=require`
- Neon automatically provides SSL, so include `?sslmode=require`

### 3. Initialize Alembic (First Time)

Alembic is already configured. To create your first migration:

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Running the Application

```bash
uvicorn main:app --reload
```

Or using FastAPI CLI:

```bash
fastapi dev main.py
```

Access the API:
- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Database Migrations with Alembic

### Create a New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

### View Current Revision

```bash
alembic current
```

## Project Structure

```
sdk-payments/
├── alembic/              # Alembic migration files
│   ├── versions/         # Migration versions
│   ├── env.py           # Alembic environment config
│   └── script.py.mako   # Migration template
├── app/                  # Application code
│   ├── __init__.py
│   ├── database.py      # Database connection and session
│   └── main.py          # (if you move routes here)
├── main.py              # FastAPI application entry point
├── alembic.ini           # Alembic configuration
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not in git)
```

## Database Connection

The database connection is configured in `app/database.py`:
- Uses async SQLAlchemy with asyncpg
- Connection string from `DATABASE_URL` environment variable
- Session management with dependency injection

## Using Database in Routes

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@app.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    # Use db session here
    return {"items": []}
```

## Testing

```bash
pytest
```

## Notes

- The database connection uses async SQLAlchemy for better performance
- Alembic automatically converts `postgresql://` to `postgresql+asyncpg://` for async support
- Always use migrations in production, never `Base.metadata.create_all()`

