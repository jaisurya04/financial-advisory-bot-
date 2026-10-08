"""
Run text extraction -> chunking -> embedding -> vector store indexing for
any documents not yet indexed. Usage: python scripts/index_documents.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database.connection import init_db, session_scope
from app.database.repositories import DocumentRepository
from app.rag.chunking import chunk_document
from app.rag.vector_store import get_vector_store

if __name__ == "__main__":
    init_db()
    with session_scope() as db:
        repo = DocumentRepository(db)
        docs = repo.get_unindexed(limit=1000)
        store = get_vector_store()

        total_chunks = 0
        for doc in docs:
            doc_dict = {
                "id": doc.id, "title": doc.title, "content": doc.content, "source": doc.source,
                "url": doc.url, "published_at": doc.published_at, "category": doc.category, "ticker": doc.ticker,
            }
            chunks = chunk_document(doc_dict)
            if chunks:
                store.upsert_chunks(chunks)
                total_chunks += len(chunks)
            repo.mark_indexed(doc.id)

        print(f"Indexed {len(docs)} documents into {total_chunks} chunks.")
