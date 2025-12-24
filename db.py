from sqlmodel import SQLModel, create_engine, Session
import os

# Default to Postgres, but allow override
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fantasy_nba")

# Handle the case where the URL might start with "postgres://" which is deprecated in SQLAlchemy 1.4+
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
