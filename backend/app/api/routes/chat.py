from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.chat.history import get_windowed_history, save_turn, get_full_history
from app.core.logging_config import get_logger
from app.database.connection import get_db
from app.rag.chain import generate_answer, LLMError
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse

router = APIRouter()
logger = get_logger(__name__)


@router.post("/api/v1/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Full query-time RAG flow:
    question -> embedding -> vector search -> retrieved chunks ->
    prompt composition (+ chat history) -> LLM -> answer -> save to history -> response
    """
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    try:
        history = get_windowed_history(db, payload.session_id)
        result = generate_answer(question=question, chat_history=history)
        save_turn(db, payload.session_id, question, result["answer"], result["sources"])

        return ChatResponse(
            session_id=payload.session_id,
            question=question,
            answer=result["answer"],
            sources=result["sources"],
            retrieved_chunk_count=result["retrieved_chunk_count"],
        )
    except LLMError as exc:
        logger.error(f"LLM error for session {payload.session_id}: {exc}")
        raise HTTPException(status_code=502, detail="The assistant is temporarily unavailable. Please try again.")
    except Exception as exc:
        logger.error(f"Unexpected error in chat endpoint: {exc}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your question.")


@router.get("/api/v1/chat/history/{session_id}", response_model=ChatHistoryResponse)
def chat_history(session_id: str, db: Session = Depends(get_db)):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")
    messages = get_full_history(db, session_id)
    return ChatHistoryResponse(session_id=session_id, messages=messages)
