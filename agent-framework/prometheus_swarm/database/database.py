"""Database service module."""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from sqlmodel import SQLModel
from contextlib import contextmanager
from typing import Optional, Dict, Any
from .models import Conversation, Message, Log
import json

# Import engine from shared config
from .config import engine

# Create session factory
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


def get_conversation(session, conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get conversation details."""
    conversation = (
        session.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation:
        return None
    return {
        "model": conversation.model,
        "system_prompt": conversation.system_prompt,
    }


def save_log(
    session,
    level: str,
    message: str,
    module: str = None,
    function: str = None,
    path: str = None,
    line_no: int = None,
    exception: str = None,
    stack_trace: str = None,
    request_id: str = None,
    additional_data: str = None,
) -> bool:
    """Save a log entry to the database."""
    try:
        log = Log(
            level=level,
            message=message,
            module=module,
            function=function,
            path=path,
            line_no=line_no,
            exception=exception,
            stack_trace=stack_trace,
            request_id=request_id,
            additional_data=additional_data,
        )
        session.add(log)
        session.commit()
        return True
    except Exception as e:
        print(f"Failed to save log to database: {e}")  # Fallback logging
        return False


def get_messages(session, conversation_id: str):
    """Get all messages for a conversation."""
    conversation = (
        session.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation:
        return []
    return [
        {"role": msg.role, "content": json.loads(msg.content)}
        for msg in conversation.messages
    ]


def save_message(session, conversation_id: str, role: str, content: Any):
    """Save a message to the database."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=json.dumps(content),
    )
    session.add(message)
    session.commit()


def create_conversation(
    session, model: str, system_prompt: Optional[str] = None
) -> str:
    """Create a new conversation."""
    conversation = Conversation(
        model=model,
        system_prompt=system_prompt,
    )
    session.add(conversation)
    session.commit()
    return conversation.id


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
