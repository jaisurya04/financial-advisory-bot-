"""
Vector database wrapper (ChromaDB) for storing/retrieving chunk embeddings
with metadata, and running semantic similarity search.
"""
from functools import lru_cache
from typing import Any, Dict, List

import chromadb

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.rag.embeddings import get_embedding_provider

settings = get_settings()
logger = get_logger(__name__)


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        self.collection = self.client.get_or_create_collection(name=settings.VECTOR_COLLECTION_NAME)
        self.embedder = get_embedding_provider()

    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed_texts(texts)
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        self.collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
        logger.info(f"Upserted {len(ids)} chunks into vector store '{settings.VECTOR_COLLECTION_NAME}'.")
        return len(ids)

    def similarity_search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        top_k = top_k or settings.TOP_K
        query_embedding = self.embedder.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        hits = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            similarity = 1 - dist  # cosine distance -> similarity approximation
            if similarity < settings.SIMILARITY_THRESHOLD:
                continue
            hits.append({"text": doc, "metadata": meta, "score": round(similarity, 4)})
        return hits

    def count(self) -> int:
        return self.collection.count()


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore()
