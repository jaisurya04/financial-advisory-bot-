import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.repositories import ChatRepository

settings = get_settings()


def get_windowed_history(db: Session, session_id: str) -> List[Dict[str, str]]:
    """Returns the last N messages (configurable window) for prompt composition."""
    repo = ChatRepository(db)
    messages = repo.get_recent_messages(session_id, limit=settings.CHAT_HISTORY_WINDOW)
    return [{"role": m.role, "content": m.content} for m in messages]


def save_turn(db: Session, session_id: str, question: str, answer: str, sources: List[Dict[str, Any]]) -> None:
    repo = ChatRepository(db)
    repo.add_message(session_id=session_id, role="user", content=question)
    repo.add_message(session_id=session_id, role="assistant", content=answer, sources=sources)


def get_full_history(db: Session, session_id: str) -> List[Dict[str, Any]]:
    repo = ChatRepository(db)
    messages = repo.get_all_messages(session_id)
    return [
        {
            "role": m.role,
            "content": m.content,
            "sources": json.loads(m.sources) if m.sources else [],
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]
