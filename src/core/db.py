from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy import event
import os
import logging

logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """Get database URL from environment with validation."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Example: postgresql://user:pass@localhost:5432/fantasy_nba"
        )
    # Handle Heroku-style postgres:// URLs (deprecated in SQLAlchemy 1.4+)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

# Connection pool configuration for production use
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # 30 minutes

def create_engine_with_retry(url: str, max_retries: int = 3):
    """Create database engine with connection pool configuration."""
    engine = create_engine(
        url,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        poolclass=QueuePool,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT,
        pool_recycle=POOL_RECYCLE,
        pool_pre_ping=True,  # Verify connections before use
    )
    
    # Log connection events for debugging
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_conn, connection_record):
        logger.debug("Database connection established")
    
    @event.listens_for(engine, "checkout")
    def on_checkout(dbapi_conn, connection_record, connection_proxy):
        logger.debug("Connection checked out from pool")
    
    return engine

# Lazy initialization to allow testing with different engines
_engine = None

def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        _engine = create_engine_with_retry(get_database_url())
    return _engine

# For backward compatibility - but prefer get_engine() for new code
@property
def engine():
    return get_engine()

# Module-level engine for compatibility with existing code
try:
    engine = create_engine_with_retry(get_database_url())
except ValueError:
    # Allow module to load even without DATABASE_URL (for testing)
    engine = None
    logger.warning("DATABASE_URL not set - database operations will fail")

def create_db_and_tables():
    """Create all tables defined in SQLModel metadata."""
    if engine is None:
        raise RuntimeError("Database engine not initialized. Set DATABASE_URL.")
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency injection for FastAPI - yields a database session."""
    if engine is None:
        raise RuntimeError("Database engine not initialized. Set DATABASE_URL.")
    with Session(engine) as session:
        yield session
