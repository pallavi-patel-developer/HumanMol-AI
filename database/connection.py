"""
HumanMol AI - Database Connection Manager
Provides SQLAlchemy engine and session factory with PostgreSQL support,
automatic SQLite fallback for fault tolerance, and comprehensive health status reporting.
"""

import os
import socket
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger("humanmol.database")

# Database URL configuration
POSTGRES_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres@localhost:5432/humanmol"
)
SQLITE_URL = "sqlite:///./database/humanmol.db"

Base = declarative_base()

_db_status_info = {
    "active_backend": "unknown",
    "is_fallback": False,
    "status": "initializing",
    "postgres_port_open": False,
    "postgres_auth_error": None,
    "database_name": "unknown"
}

def check_postgres_port(host="127.0.0.1", port=5432) -> bool:
    """Checks if PostgreSQL port is open and listening."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        res = s.connect_ex((host, port))
        s.close()
        return res == 0
    except Exception:
        return False

def get_engine():
    """
    Attempts to connect to PostgreSQL. Falls back to SQLite if PostgreSQL
    is unreachable or authentication fails, updating status metadata.
    """
    global _db_status_info
    port_open = check_postgres_port()
    _db_status_info["postgres_port_open"] = port_open

    # 1. Try PostgreSQL if configured
    if POSTGRES_URL.startswith("postgresql"):
        try:
            pg_engine = create_engine(POSTGRES_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
                logger.info("Successfully connected to PostgreSQL database.")
                _db_status_info.update({
                    "active_backend": "postgresql",
                    "is_fallback": False,
                    "status": "connected",
                    "database_name": POSTGRES_URL.split("/")[-1].split("?")[0],
                    "postgres_auth_error": None
                })
                return pg_engine
        except Exception as e:
            err_str = str(e)
            logger.warning(
                f"PostgreSQL connection to {POSTGRES_URL} failed: {err_str}. "
                f"Falling back to local SQLite database at {SQLITE_URL}."
            )
            _db_status_info["postgres_auth_error"] = (
                "FATAL: password authentication failed for user 'postgres'"
                if "password authentication failed" in err_str
                else err_str[:120]
            )

    # 2. Fallback to SQLite
    os.makedirs("./database", exist_ok=True)
    sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    with sqlite_engine.connect() as conn:
        conn.execute(text("SELECT 1;"))
    logger.info("Initialized SQLite database engine.")
    _db_status_info.update({
        "active_backend": "sqlite",
        "is_fallback": True,
        "status": "connected",
        "database_name": "humanmol.db"
    })
    return sqlite_engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency injection helper for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates all defined database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")

def get_db_status() -> dict:
    """Returns detailed database connectivity and configuration status."""
    global _db_status_info
    # Perform live ping
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
            live_status = "connected"
    except Exception as e:
        live_status = f"error: {str(e)[:100]}"

    return {
        "active_backend": _db_status_info.get("active_backend", engine.dialect.name),
        "is_fallback": _db_status_info.get("is_fallback", False),
        "status": live_status,
        "database_name": _db_status_info.get("database_name", "humanmol"),
        "postgres_port_open": _db_status_info.get("postgres_port_open", False),
        "postgres_auth_error": _db_status_info.get("postgres_auth_error"),
        "notice": (
            "PostgreSQL 18 is running on port 5432, but authentication failed for user 'postgres'. "
            "Local SQLite fallback (database/humanmol.db) is active with full persistence."
            if _db_status_info.get("is_fallback") and _db_status_info.get("postgres_port_open")
            else "Database connected."
        )
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database Status:", get_db_status())

