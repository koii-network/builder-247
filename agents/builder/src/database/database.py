"""Database service module."""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlmodel import SQLModel
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any
from .models import Conversation, Message, Log
import json

# Create engine
engine = create_engine(os.getenv("DATABASE_PATH", "sqlite:///database.db"))

# Create session factory
Session = sessionmaker(bind=engine)


def get_db():
    """Get database session.

    Returns a Flask-managed session if in app context, otherwise a thread-local session.
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


def close_db(e=None):
    """Close database session.

    Can be used as Flask teardown function or called directly.
    """
    try:
        from flask import g, has_app_context

        if has_app_context():
            db = g.pop("db", None)
            if db is not None:
                db.close()
    except ImportError:
        pass


def initialize_database():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


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
