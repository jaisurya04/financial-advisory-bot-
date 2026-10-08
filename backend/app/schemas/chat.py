from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128, description="Client-generated session identifier")
    question: str = Field(..., min_length=1, max_length=2000)


class SourceItem(BaseModel):
    title: str = ""
    source: str = ""
    url: Optional[str] = None
    published_at: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    sources: List[SourceItem] = []
    retrieved_chunk_count: int = 0


class ChatHistoryMessage(BaseModel):
    role: str
    content: str
    sources: List[SourceItem] = []
    created_at: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatHistoryMessage]
