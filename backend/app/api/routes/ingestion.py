from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.database.connection import get_db
from app.database.repositories import DocumentRepository
from app.ingestion.pipeline import run_ingestion
from app.rag.chunking import chunk_document
from app.rag.vector_store import get_vector_store
from app.schemas.documents import IngestRequest, IngestResponse, IndexRequest, IndexResponse

router = APIRouter()
logger = get_logger(__name__)


@router.post("/api/v1/ingest", response_model=IngestResponse)
def ingest_documents(payload: IngestRequest, db: Session = Depends(get_db)):
    """Fetch financial news/articles and store them in the relational database."""
    try:
        result = run_ingestion(db, query=payload.query)
        return IngestResponse(**result)
    except Exception as exc:
        logger.error(f"Ingestion failed: {exc}")
        raise HTTPException(status_code=502, detail="Failed to ingest financial news at this time.")


@router.post("/api/v1/index", response_model=IndexResponse)
def index_documents(payload: IndexRequest, db: Session = Depends(get_db)):
    """
    Text extraction -> chunking -> embedding -> vector store, for any
    documents not yet indexed.
    """
    repo = DocumentRepository(db)
    docs = repo.get_unindexed(limit=payload.limit)

    if not docs:
        return IndexResponse(documents_processed=0, chunks_indexed=0)

    store = get_vector_store()
    total_chunks = 0

    for doc in docs:
        doc_dict = {
            "id": doc.id, "title": doc.title, "content": doc.content, "source": doc.source,
            "url": doc.url, "published_at": doc.published_at, "category": doc.category, "ticker": doc.ticker,
        }
        try:
            chunks = chunk_document(doc_dict)
            if chunks:
                store.upsert_chunks(chunks)
                total_chunks += len(chunks)
            repo.mark_indexed(doc.id)
        except Exception as exc:
            logger.error(f"Failed to index document {doc.id}: {exc}")
            continue

    logger.info(f"Indexed {len(docs)} documents into {total_chunks} chunks.")
    return IndexResponse(documents_processed=len(docs), chunks_indexed=total_chunks)
