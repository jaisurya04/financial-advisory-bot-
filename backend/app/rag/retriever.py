"""
RAG retrieval pipeline: question -> embedding -> vector search -> top-K chunks.
Also handles follow-up query rewriting so pronouns like "it"/"that" resolve
against recent chat history before retrieval.
"""
from typing import Any, Dict, List

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.rag.vector_store import get_vector_store

settings = get_settings()
logger = get_logger(__name__)


def rewrite_query_with_history(question: str, recent_messages: List[Dict[str, str]]) -> str:
    """
    Lightweight, dependency-free follow-up handling: prefix the current
    question with the last user/assistant turn so the embedding captures
    the conversational topic (e.g. "it" -> resolves near "inflation").

    This is a heuristic (not full coreference resolution) but is enough to
    meaningfully improve retrieval for short follow-up questions.
    """
    if not recent_messages:
        return question

    is_short_followup = len(question.split()) <= 6 or any(
        pronoun in question.lower() for pronoun in ["it", "that", "this", "those", "they"]
    )
    if not is_short_followup:
        return question

    last_user_turns = [m["content"] for m in recent_messages if m["role"] == "user"]
    if not last_user_turns:
        return question

    context_hint = last_user_turns[-1]
    rewritten = f"{context_hint} — follow-up: {question}"
    logger.info(f"Rewrote follow-up query for retrieval: {rewritten!r}")
    return rewritten


def retrieve_context(question: str, recent_messages: List[Dict[str, str]] = None, top_k: int = None) -> List[Dict[str, Any]]:
    """
    STEP: Receive question -> generate embedding -> search vector DB ->
    retrieve + rank top-K relevant chunks. Returns list of {text, metadata, score}.
    """
    recent_messages = recent_messages or []
    search_query = rewrite_query_with_history(question, recent_messages)

    store = get_vector_store()
    hits = store.similarity_search(query=search_query, top_k=top_k or settings.TOP_K)

    # Deduplicate by document_id + chunk_index in case of overlapping upserts.
    seen = set()
    deduped = []
    for h in hits:
        key = (h["metadata"].get("document_id"), h["metadata"].get("chunk_index"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(h)

    logger.info(f"Retrieved {len(deduped)} relevant chunks for query.")
    return deduped
