"""Database service module."""

from flask import g
import os
from sqlmodel import Session, create_engine
from src.database.models import Log, Conversation, Message, Submission

# Create engine using the same database path
engine = create_engine(
    f"sqlite:///{os.getenv('DATABASE_PATH', 'database.db')}",
    connect_args={"check_same_thread": False},
)


def get_db() -> Session:
    """Get database session."""
    if "db" not in g:
        g.db = Session(engine)
    return g.db


def close_db(e=None):
    """Close database session."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialize_database():
    """Initialize database tables."""
    # Create all tables from models
    Log.metadata.create_all(engine)
    Conversation.metadata.create_all(engine)
    Message.metadata.create_all(engine)
    Submission.metadata.create_all(engine)


# Initialize database on module load
initialize_database()
