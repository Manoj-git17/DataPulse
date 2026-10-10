"""
DataPulse - Database Connection and Session Management.
Supports both PostgreSQL and SQLite seamlessly via standard DATABASE_URL.
Cost: ₹0 (Embedded SQLite / Native PostgreSQL).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

# Load environment configuration
load_dotenv()

DEFAULT_DB_PATH = Path("data/datapulse.db")


def get_database_url() -> str:
    """
    Construct the database connection string.
    - If DATABASE_URL is set in environment, use it (e.g. postgresql://user:pass@localhost:5432/datapulse_db).
    - If POSTGRES credentials are set, build the postgresql URI.
    - Otherwise, default to local SQLite database at data/datapulse.db.
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Check if discrete postgres credentials are provided
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")

    if db_user and db_pass and db_host and db_name and db_pass != "your_password_here":
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    # Default zero-setup local SQLite path
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DEFAULT_DB_PATH.resolve()}"


def get_engine(database_url: str | None = None) -> Engine:
    """
    Create a SQLAlchemy Engine with optimal pooling settings.
    """
    url = database_url or get_database_url()

    # SQLite-specific connection arguments (foreign keys enable)
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})

    # PostgreSQL / Standard RDBMS
    return create_engine(url, pool_pre_ping=True)


def get_session_factory(engine: Engine | None = None) -> sessionmaker:
    """Return a sessionmaker bound to the given or default engine."""
    eng = engine or get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=eng)


def get_session(engine: Engine | None = None) -> Session:
    """Return a new database session."""
    factory = get_session_factory(engine)
    return factory()


def init_db(engine: Engine | None = None) -> None:
    """Create all tables defined in models.py."""
    from db.models import Base
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)
