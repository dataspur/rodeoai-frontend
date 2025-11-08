"""Database configuration and session management for RodeoAI backend."""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL - can be configured via environment variable
# Default to SQLite for development if PostgreSQL URL not provided
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./rodeoai.db"  # Fallback to SQLite for easy development
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use with FastAPI's Depends() to inject DB sessions into routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)
