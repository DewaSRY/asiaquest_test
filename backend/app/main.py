import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.routes import api_router
from app.database import engine


def validate_env_variables() -> bool:
    """Validate that all required environment variables are loaded."""
    try:
        settings = get_settings()
        required_vars = [
            ("DATABASE_URL", settings.DATABASE_URL),
            ("JWT_SECRET_KEY", settings.JWT_SECRET_KEY),
            ("JWT_ALGORITHM", settings.JWT_ALGORITHM),
            ("APP_NAME", settings.APP_NAME),
            ("APP_VERSION", settings.APP_VERSION),
        ]
        
        missing_vars = [name for name, value in required_vars if not value]
        
        if missing_vars:
            print(f" Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        print("All required environment variables are loaded")
        return True
    except Exception as e:
        print(f"Failed to load environment variables: {e}")
        return False


async def test_database_connection() -> bool:
    """Test the database connection."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection established successfully")
        return True
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Validate env and database connection
    print("Starting application...")
    
    if not validate_env_variables():
        print(" Terminating: Environment variables not configured properly")
        sys.exit(1)
    
    if not await test_database_connection():
        print(" Terminating: Database connection failed")
        sys.exit(1)
    
    print("Application startup complete")
    yield
    
    # Shutdown
    print("Shutting down application...")
    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API with JWT Authentication",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Welcome to the API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
