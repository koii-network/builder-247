"""Database management module."""

import os
from pathlib import Path
from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine
from .models import Log, Conversation, Message, Submission


class Database:
    """Database manager."""

    def __init__(self, db_path: str | Path = None):
        """Initialize database connection."""
        if db_path is None:
            db_path = os.getenv("DATABASE_PATH", "database.db")

        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create SQLite URL
        self.url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(self.url)

        # Create all tables
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def session(self):
        """Create a new database session."""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save_log(self, **log_data):
        """Save a log entry."""
        with self.session() as session:
            log = Log(**log_data)
            session.add(log)
            return log

    def create_conversation(self, model: str, system_prompt: str = None) -> str:
        """Create a new conversation."""
        with self.session() as session:
            conversation = Conversation(model=model, system_prompt=system_prompt)
            session.add(conversation)
            session.commit()  # Need to commit to get the ID
            return conversation.id

    def get_conversation(self, conversation_id: str) -> dict:
        """Get conversation details."""
        with self.session() as session:
            conversation = session.get(Conversation, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            return {
                "model": conversation.model,
                "system_prompt": conversation.system_prompt,
            }

    def get_messages(self, conversation_id: str) -> list:
        """Get all messages for a conversation in chronological order."""
        with self.session() as session:
            messages = (
                session.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
                .all()
            )
            return [{"role": msg.role, "content": msg.content} for msg in messages]

    def save_message(self, conversation_id: str, role: str, content: str):
        """Save a message."""
        with self.session() as session:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
            )
            session.add(message)

    def save_submission(self, **submission_data):
        """Save a submission."""
        with self.session() as session:
            submission = Submission(**submission_data)
            session.add(submission)
            return submission

    def get_submission(self, round_number: int) -> Submission:
        """Get a submission by round number."""
        with self.session() as session:
            return session.get(Submission, round_number)

    def update_submission(self, round_number: int, **update_data):
        """Update a submission."""
        with self.session() as session:
            submission = session.get(Submission, round_number)
            if not submission:
                raise ValueError(f"Submission {round_number} not found")
            for key, value in update_data.items():
                setattr(submission, key, value)


# Global database instance
_db = None


def get_db() -> Database:
    """Get the global database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db
