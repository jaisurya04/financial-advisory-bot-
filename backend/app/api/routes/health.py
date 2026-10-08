from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.rag.vector_store import get_vector_store

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    vector_count = None
    try:
        vector_count = get_vector_store().count()
    except Exception:
        vector_count = -1  # vector store not reachable

    return {
        "status": "ok",
        "database": "connected",
        "vector_store_document_count": vector_count,
    }
