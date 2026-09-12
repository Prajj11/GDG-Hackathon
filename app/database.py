"""Digital Guardrails — app.database compatibility facade.
Provides database engine and session management backed by SQLAlchemy 2.0.
"""
from backend.database import engine, DATABASE_URL, SessionLocal, Base

def init_db() -> None:
    """Initialize all database tables."""
    Base.metadata.create_all(engine)

def get_session():
    """FastAPI dependency yielding a database session."""
    with SessionLocal() as session:
        yield session

__all__ = ['engine', 'DATABASE_URL', 'SessionLocal', 'init_db', 'get_session']
