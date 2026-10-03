"""
SQLAlchemy Engine and Session manager for DriverGuard.

Provides database connection lifecycle management using SQLAlchemy 2.0.
Configures SQLite foreign keys and WAL mode via event listeners.
"""

import os
from flask import g, current_app
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from driverguard.app.models import Base

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "driverguard.db"
)


def get_db_path() -> str:
    if current_app:
        return current_app.config.get("DATABASE_PATH", DEFAULT_DB_PATH)
    return DEFAULT_DB_PATH


def get_engine():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_url = f"sqlite:///{db_path}"
    
    eng = create_engine(db_url, echo=False)

    @event.listens_for(eng, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()

    return eng


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """
    Return per-request SQLAlchemy Session.
    Reuses session on Flask 'g' context object.
    """
    if "db_session" not in g:
        g.db_session = SessionLocal()
    return g.db_session


def close_db_session(e=None):
    """Close active SQLAlchemy session at end of HTTP request."""
    session = g.pop("db_session", None)
    if session is not None:
        session.close()


def init_db(app=None):
    """Initialize database tables using SQLAlchemy Base.metadata.create_all."""
    eng = get_engine()
    Base.metadata.create_all(bind=eng)


def init_app(app):
    """Register teardown context and create tables on app startup."""
    app.teardown_appcontext(close_db_session)
    init_db(app)
