from datetime import datetime
from typing import Any, Dict, Optional

from app.ingestion.cleaner import clean_text, validate_article
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def _parse_date(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None


def extract(article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Text extraction stage: raw article -> clean Document dict ready for DB storage.
    Returns None if the article fails validation.
    """
    cleaned_content = clean_text(article.get("content", ""))
    cleaned_description = clean_text(article.get("description", "")) if article.get("description") else None

    candidate = {
        "title": clean_text(article.get("title", "")),
        "description": cleaned_description,
        "content": cleaned_content,
        "source": article.get("source"),
        "author": article.get("author"),
        "category": article.get("category"),
        "ticker": article.get("ticker"),
        "url": article.get("url"),
        "published_at": _parse_date(article.get("published_at")),
    }

    if not validate_article(candidate):
        logger.warning(f"Rejected invalid/empty article: {candidate.get('title')!r}")
        return None

    return candidate
