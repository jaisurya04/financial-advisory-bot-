"""
Ties together retrieval, prompt composition, and LLM generation into a
single callable RAG chain used by the chat API route.
"""
from typing import Any, Dict, List

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.rag.retriever import retrieve_context
from app.rag import prompt as prompt_module

settings = get_settings()
logger = get_logger(__name__)


class LLMError(Exception):
    pass


def _call_llm(messages: List[Dict[str, str]]) -> str:
    """Calls the configured OpenAI-compatible LLM. Provider is swappable via config."""
    if not settings.LLM_API_KEY:
        # Deterministic offline fallback so the project remains runnable/demoable
        # without any API key configured.
        logger.warning("LLM_API_KEY not set — returning a template response (demo mode).")
        return (
            "I don't have an LLM API key configured right now, so I can't generate a full answer. "
            "Based on the retrieved context above, please review the listed sources directly. "
            "To enable full answer generation, set LLM_API_KEY in your .env file."
        )

    try:
        from openai import OpenAI
        kwargs = {"api_key": settings.LLM_API_KEY}
        if settings.LLM_BASE_URL:
            kwargs["base_url"] = settings.LLM_BASE_URL
        client = OpenAI(**kwargs)

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )
        return response.choices[0].message.content
    except Exception as exc:
        logger.error(f"LLM request failed: {exc}")
        raise LLMError(f"LLM generation failed: {exc}") from exc


def generate_answer(question: str, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Full query-time flow:
      question -> retrieve context -> compose prompt (+ history) -> LLM -> answer + sources
    """
    retrieved_chunks = retrieve_context(question=question, recent_messages=chat_history)
    messages = prompt_module.compose_prompt(
        question=question, chat_history=chat_history, retrieved_chunks=retrieved_chunks
    )

    answer_text = _call_llm(messages)

    sources = []
    seen_urls = set()
    for chunk in retrieved_chunks:
        meta = chunk["metadata"]
        url = meta.get("url")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        sources.append({
            "title": meta.get("title", ""),
            "source": meta.get("source", ""),
            "url": url,
            "published_at": meta.get("published_at", ""),
        })

    return {"answer": answer_text, "sources": sources, "retrieved_chunk_count": len(retrieved_chunks)}
