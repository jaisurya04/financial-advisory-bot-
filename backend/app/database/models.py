import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class FinancialDocument(Base):
    """Raw/processed financial news & articles fetched during ingestion."""
    __tablename__ = "financial_documents"

    id = Column(String, primary_key=True, default=_uuid)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True, index=True)
    url = Column(String, nullable=True)
    author = Column(String, nullable=True)
    category = Column(String, nullable=True, index=True)
    ticker = Column(String, nullable=True, index=True)
    published_at = Column(DateTime, nullable=True)
    is_indexed = Column(String, default="false")  # "true" once chunked+embedded
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_financial_documents_source_category", "source", "category"),
    )


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"), index=True, nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON-encoded list of source dicts
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    session = relationship("ChatSession", back_populates="messages")
