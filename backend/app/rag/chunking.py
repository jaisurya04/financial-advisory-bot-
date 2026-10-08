from typing import Any, Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings

settings = get_settings()


def chunk_document(document: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Splits a single document's content into overlapping chunks, preserving
    parent metadata on every chunk (document_id, source, title, url, etc.).

    Document -> Chunk 1, Chunk 2, ..., Chunk N
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    text = document.get("content", "")
    if not text:
        return []

    raw_chunks = splitter.split_text(text)

    chunks = []
    for idx, chunk_text in enumerate(raw_chunks):
        chunks.append({
            "chunk_id": f"{document['id']}_chunk_{idx}",
            "text": chunk_text,
            "metadata": {
                "document_id": document["id"],
                "source": document.get("source") or "unknown",
                "title": document.get("title") or "",
                "url": document.get("url") or "",
                "published_at": str(document.get("published_at") or ""),
                "category": document.get("category") or "",
                "ticker": document.get("ticker") or "",
                "chunk_index": idx,
            },
        })
    return chunks
