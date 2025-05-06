"""Database models."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, UniqueConstraint
from sqlalchemy import CheckConstraint
from pydantic import field_validator, constr, ConfigDict

class Conversation(SQLModel, table=True):
    """Conversation model."""

    id: str = Field(primary_key=True)
    model: str
    system_prompt: Optional[str] = None
    available_tools: Optional[str] = None  # JSON list of tool names
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message model."""

    id: str = Field(primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id")
    role: str
    content: str  # JSON-encoded content
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation: Conversation = Relationship(back_populates="messages")


class Log(SQLModel, table=True):
    """Log entry model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    path: Optional[str] = None
    line_no: Optional[int] = None
    exception: Optional[str] = None
    stack_trace: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Optional[str] = None


class Evidence(SQLModel, table=True):
    """Evidence model to ensure uniqueness."""

    __tablename__ = 'evidence'
    
    model_config = ConfigDict(
        validate_assignment=True,
        from_attributes=True
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(min_length=1, max_length=10000)
    type: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('content', 'type', name='uix_evidence_content_type'),
    )
    
    @field_validator('content')
    @classmethod
    def validate_non_empty(cls, v):
        """Validate content is not just whitespace"""
        if not isinstance(v, str):
            raise ValueError("Content must be a string")
        v = v.strip()
        if not v:
            raise ValueError("Content cannot be empty or just whitespace")
        return v