from sqlmodel import SQLModel, create_engine, Session
import os
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # For development/testing, use SQLite as fallback with a warning
    logger.warning(
        "DATABASE_URL environment variable not set. "
        "Using SQLite for development. Set DATABASE_URL for production use."
    )
    DATABASE_URL = "sqlite:///./fantasy_nba.db"

# Handle the case where the URL might start with "postgres://" which is deprecated in SQLAlchemy 1.4+
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure engine based on database type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
