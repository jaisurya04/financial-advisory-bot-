import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import FinancialDocument, ChatSession, ChatMessage


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> FinancialDocument:
        doc = FinancialDocument(**kwargs)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def bulk_create(self, documents: List[dict]) -> List[FinancialDocument]:
        objs = [FinancialDocument(**d) for d in documents]
        self.db.add_all(objs)
        self.db.commit()
        for o in objs:
            self.db.refresh(o)
        return objs

    def get_unindexed(self, limit: int = 200) -> List[FinancialDocument]:
        stmt = select(FinancialDocument).where(FinancialDocument.is_indexed == "false").limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def mark_indexed(self, document_id: str) -> None:
        doc = self.db.get(FinancialDocument, document_id)
        if doc:
            doc.is_indexed = "true"
            doc.updated_at = datetime.utcnow()
            self.db.commit()

    def exists_by_url(self, url: str) -> bool:
        if not url:
            return False
        stmt = select(FinancialDocument.id).where(FinancialDocument.url == url)
        return self.db.execute(stmt).first() is not None

    def count(self) -> int:
        return self.db.query(FinancialDocument).count()


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_session(self, session_id: str) -> ChatSession:
        stmt = select(ChatSession).where(ChatSession.session_id == session_id)
        session = self.db.execute(stmt).scalar_one_or_none()
        if session is None:
            session = ChatSession(session_id=session_id)
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        return session

    def add_message(self, session_id: str, role: str, content: str, sources: Optional[list] = None) -> ChatMessage:
        self.get_or_create_session(session_id)
        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=json.dumps(sources or []),
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_recent_messages(self, session_id: str, limit: int) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(self.db.execute(stmt).scalars().all())
        return list(reversed(messages))  # chronological order

    def get_all_messages(self, session_id: str) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(self.db.execute(stmt).scalars().all())
