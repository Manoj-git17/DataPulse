"""
DataPulse - Database Connection and Session Management.
Supports both PostgreSQL and SQLite seamlessly via standard DATABASE_URL.
Cost: ₹0 (Embedded SQLite / Native PostgreSQL).
"""

import os
import threading
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

# Load environment configuration
load_dotenv()

DEFAULT_DB_PATH = Path("data/datapulse.db")


def normalize_database_url(url: str) -> str:
    """
    Normalize database URL schemes to explicitly use the psycopg2 driver
    (postgresql+psycopg2://) for PostgreSQL databases.
    Preserves sqlite:/// and already valid driver URLs.
    """
    if not url:
        return url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def get_database_url() -> str:
    """
    Construct the database connection string.
    - If DATABASE_URL is set in environment, use it (e.g. postgresql://user:pass@localhost:5432/datapulse_db).
    - If POSTGRES credentials are set, build the postgresql URI.
    - Otherwise, default to local SQLite database at data/datapulse.db.
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return normalize_database_url(env_url)

    # Check if discrete postgres credentials are provided
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")

    if db_user and db_pass and db_host and db_name and db_pass != "your_password_here":
        return f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    # Default zero-setup local SQLite path
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DEFAULT_DB_PATH.resolve()}"


_engines: dict[str, Engine] = {}
_session_factories: dict[int, sessionmaker] = {}
_engine_lock = threading.Lock()


def get_engine(database_url: str | None = None) -> Engine:
    """
    Get or create a cached SQLAlchemy Engine with optimal pooling settings.
    Reuses existing connection pools across requests to eliminate repeated
    TCP and TLS handshake overhead. Thread-safe for concurrent requests.
    """
    url = normalize_database_url(database_url or get_database_url())

    if url not in _engines:
        with _engine_lock:
            if url not in _engines:
                # SQLite-specific connection arguments (foreign keys enable)
                if url.startswith("sqlite"):
                    _engines[url] = create_engine(
                        url,
                        connect_args={"check_same_thread": False},
                    )
                else:
                    # PostgreSQL / Neon pooling settings:
                    # - pool_size: persistent connections in the pool
                    # - max_overflow: maximum overflow connections for peak traffic
                    # - pool_recycle: recycle before Neon's 300s idle timeout
                    # - pool_pre_ping: check connection health before checkout
                    _engines[url] = create_engine(
                        url,
                        pool_size=5,
                        max_overflow=10,
                        pool_recycle=280,
                        pool_pre_ping=True,
                    )

    return _engines[url]


def get_session_factory(engine: Engine | None = None) -> sessionmaker:
    """Return a sessionmaker bound to the given or default engine."""
    eng = engine or get_engine()
    eng_id = id(eng)
    if eng_id not in _session_factories:
        with _engine_lock:
            if eng_id not in _session_factories:
                _session_factories[eng_id] = sessionmaker(
                    autocommit=False, autoflush=False, bind=eng
                )
    return _session_factories[eng_id]


def get_session(engine: Engine | None = None) -> Session:
    """Return a new database session."""
    factory = get_session_factory(engine)
    return factory()


def reset_engine_cache() -> None:
    """Dispose and clear cached engines and factories. Used for test teardowns."""
    with _engine_lock:
        for engine in _engines.values():
            try:
                engine.dispose()
            except Exception:
                pass
        _engines.clear()
        _session_factories.clear()


def init_db(engine: Engine | None = None) -> None:
    """Create all tables defined in models.py."""
    from db.models import Base
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)
