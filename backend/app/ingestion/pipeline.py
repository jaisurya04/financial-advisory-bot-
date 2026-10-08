from typing import Dict

from sqlalchemy.orm import Session

from app.database.repositories import DocumentRepository
from app.ingestion.news_fetcher import NewsFetcher
from app.ingestion import text_extractor
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def run_ingestion(db: Session, query: str = "finance OR banking OR markets") -> Dict[str, int]:
    """
    INGESTION FLOW:
    Financial News API -> Fetch -> Clean/normalize -> Store in relational DB

    Returns counts for observability.
    """
    logger.info("Ingestion started.")
    fetcher = NewsFetcher()
    raw_articles = fetcher.fetch(query=query)
    logger.info(f"Documents fetched: {len(raw_articles)}")

    repo = DocumentRepository(db)
    to_insert = []
    skipped_duplicates = 0
    skipped_invalid = 0

    for raw in raw_articles:
        if repo.exists_by_url(raw.get("url")):
            skipped_duplicates += 1
            continue
        extracted = text_extractor.extract(raw)
        if extracted is None:
            skipped_invalid += 1
            continue
        to_insert.append(extracted)

    created = repo.bulk_create(to_insert) if to_insert else []
    logger.info(
        f"Ingestion complete. inserted={len(created)} "
        f"duplicates_skipped={skipped_duplicates} invalid_skipped={skipped_invalid}"
    )

    return {
        "fetched": len(raw_articles),
        "inserted": len(created),
        "duplicates_skipped": skipped_duplicates,
        "invalid_skipped": skipped_invalid,
    }
