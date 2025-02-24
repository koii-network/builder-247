"""Database storage manager for LLM conversations."""

import sqlite3
import uuid
import json
from pathlib import Path
from typing import Dict, Optional, List, TypedDict, Any


class ConversationDetails(TypedDict):
    """Type definition for conversation details returned from database."""

    model: str
    system_prompt: Optional[str]


def _safe_json_loads(s: str) -> Any:
    """Safely decode JSON, handling already decoded content."""
    if not isinstance(s, str):
        return s
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # If it's not valid JSON, treat it as a raw string
        return s


def _safe_json_dumps(obj: Any) -> str:
    """Safely encode to JSON, handling already encoded content."""
    if isinstance(obj, str):
        try:
            # Try to decode it - if it's already JSON, this will succeed
            json.loads(obj)
            # If we get here, it's already JSON encoded
            return obj
        except json.JSONDecodeError:
            # If it's not JSON, encode it
            return json.dumps(obj)
    # For non-strings, always encode
    return json.dumps(obj)


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

    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation in chronological order."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at",
                (conversation_id,),
            )
            return [
                {"role": role, "content": _safe_json_loads(content)}
                for role, content in cursor.fetchall()
            ]

    def save_message(self, conversation_id: str, role: str, content: Any):
        """Save a message to the database.

        Args:
            conversation_id: The ID of the conversation
            role: The role of the message sender (e.g., "user", "assistant", "system")
            content: The message content (string, dict, or list of content blocks)
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            content_str = _safe_json_dumps(content)
            conn.execute(
                "INSERT INTO messages (message_id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), conversation_id, role, content_str),
            )
