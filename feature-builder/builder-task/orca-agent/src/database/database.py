"""Database service module."""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from sqlmodel import SQLModel
from contextlib import contextmanager
from typing import Optional, Dict, Any
from .models import Submission

# Import engine from agent framework's shared config
from prometheus_swarm.database.config import engine

# Create session factory using shared engine
Session = sessionmaker(bind=engine)


def get_db():
    """Get database session.

    Returns a Flask-managed session if in app context, otherwise a thread-local session.
    The session is automatically managed:
    - In Flask context: Session is stored in g and cleaned up when the request ends
    - Outside Flask context: Use get_session() context manager for automatic cleanup
    """
    try:
        from flask import g, has_app_context

        if has_app_context():
            if "db" not in g:
                g.db = Session()
            return g.db
    except ImportError:
        pass
    return Session()


def initialize_database():
    """Initialize database tables if they don't exist."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Get all model classes from SQLModel metadata
    model_tables = SQLModel.metadata.tables

    # Only create tables that don't exist
    tables_to_create = []
    for table_name, table in model_tables.items():
        if table_name not in existing_tables:
            tables_to_create.append(table)

    if tables_to_create:
        SQLModel.metadata.create_all(engine, tables=tables_to_create)


def get_submission(
    session, task_id: str, round_number: int
) -> Optional[Dict[str, Any]]:
    """Get submission details."""
    submission = (
        session.query(Submission)
        .filter(Submission.task_id == task_id, Submission.round_number == round_number)
        .first()
    )
    if not submission:
        return None
    return {
        "task_id": submission.task_id,
        "round_number": submission.round_number,
        "status": submission.status,
        "pr_url": submission.pr_url,
        "username": submission.username,
        "repo_owner": submission.repo_owner,
        "repo_name": submission.repo_name,
        "uuid": submission.uuid,
        "node_type": submission.node_type,
    }


def save_submission(
    session,
    task_id: str,
    round_number: int,
    status: str = "pending",
    pr_url: Optional[str] = None,
    username: Optional[str] = None,
    repo_owner: str = None,
    repo_name: str = None,
    uuid: Optional[str] = None,
    node_type: str = "worker",
) -> bool:
    """Save a submission to the database."""
    try:
        submission = Submission(
            task_id=task_id,
            round_number=round_number,
            status=status,
            pr_url=pr_url,
            username=username,
            repo_owner=repo_owner,
            repo_name=repo_name,
            uuid=uuid,
            node_type=node_type,
        )
        session.add(submission)
        session.commit()
        return True
    except Exception as e:
        print(f"Failed to save submission to database: {e}")  # Fallback logging
        return False


@contextmanager
def get_session():
    """Context manager for database sessions.

    Prefer using get_db() for Flask applications.
    Use this when you need explicit session management:

    with get_session() as session:
        # do stuff with session
        session.commit()
    """
    session = get_db()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        # Only close if not in Flask context (Flask handles closing)
        try:
            from flask import has_app_context

            if not has_app_context():
                session.close()
        except ImportError:
            session.close()
