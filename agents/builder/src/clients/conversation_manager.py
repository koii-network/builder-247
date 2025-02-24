"""Database storage manager for LLM conversations."""

import sqlite3
import uuid
from pathlib import Path
from typing import Dict, Optional, List, TypedDict


class ConversationDetails(TypedDict):
    """Type definition for conversation details returned from database."""

    model: str
    system_prompt: Optional[str]


class ConversationManager:
    """Handles conversation and message storage."""

    def __init__(self, db_path: Path):
        self.db_path = db_path.expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with necessary tables."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    system_prompt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """
            )

    def create_conversation(
        self, model: str, system_prompt: Optional[str] = None
    ) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT INTO conversations (conversation_id, model, system_prompt) VALUES (?, ?, ?)",
                (conversation_id, model, system_prompt),
            )
        return conversation_id

    def get_conversation(self, conversation_id: str) -> ConversationDetails:
        """Get conversation details including system prompt."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT model, system_prompt FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            )
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Conversation {conversation_id} not found")
            return {"model": result[0], "system_prompt": result[1]}

    def get_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get all messages for a conversation in chronological order."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at",
                (conversation_id,),
            )
            return [
                {"role": role, "content": content}  # Return raw strings
                for role, content in cursor.fetchall()
            ]

    def save_message(self, conversation_id: str, role: str, content: str):
        """Save a message to the database.

        Args:
            conversation_id: The ID of the conversation
            role: The role of the message sender (e.g., "user", "assistant", "system")
            content: The message content as a string
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT INTO messages (message_id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), conversation_id, role, content),
            )
