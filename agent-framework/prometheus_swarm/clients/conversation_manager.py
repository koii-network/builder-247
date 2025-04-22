"""Database storage manager for LLM conversations."""

import uuid
import json
from typing import Dict, Optional, List, Any
from prometheus_swarm.database import (
    get_session,
    Conversation,
    Message,
    initialize_database,
)


class ConversationManager:
    """Handles conversation and message storage."""

    def __init__(self):
        """Initialize the conversation manager and database."""
        initialize_database()

    def create_conversation(
        self,
        model: str,
        system_prompt: Optional[str] = None,
        available_tools: Optional[List[str]] = None,
    ) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        with get_session() as session:
            conversation = Conversation(
                id=conversation_id,
                model=model,
                system_prompt=system_prompt,
                available_tools=(
                    json.dumps(available_tools) if available_tools else None
                ),
            )
            session.add(conversation)
            session.commit()
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation details."""
        with get_session() as session:
            conversation = session.get(Conversation, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            return {
                "model": conversation.model,
                "system_prompt": conversation.system_prompt,
                "available_tools": (
                    json.loads(conversation.available_tools)
                    if conversation.available_tools
                    else None
                ),
            }

    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation in chronological order."""
        with get_session() as session:
            conversation = session.get(Conversation, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            return [
                {"role": msg.role, "content": json.loads(msg.content)}
                for msg in conversation.messages
            ]

    def save_message(self, conversation_id: str, role: str, content: Any):
        """Save a message."""
        with get_session() as session:
            # First verify conversation exists
            conversation = session.get(Conversation, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Create and save message
            message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=role,
                content=json.dumps(content),
            )
            session.add(message)
            session.commit()

    def update_tools(
        self, conversation_id: str, available_tools: Optional[List[str]] = None
    ):
        """Update available tools for an existing conversation."""
        with get_session() as session:
            conversation = session.get(Conversation, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            conversation.available_tools = (
                json.dumps(available_tools) if available_tools else None
            )
            session.commit()
