"""
Embedding generation for both document chunks and user questions.
Provider is configurable via EMBEDDING_PROVIDER:
  - "local": sentence-transformers, runs fully offline, no API key needed.
  - "openai": OpenAI-compatible embeddings API.
The embedding dimension automatically matches whichever model is selected.
"""
from functools import lru_cache
from typing import List

from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class EmbeddingProvider:
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]

    @property
    def dimension(self) -> int:
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading local embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self._dim = self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        vectors = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return vectors.tolist()

    @property
    def dimension(self) -> int:
        return self._dim


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str, api_key: str, base_url: str = ""):
        from openai import OpenAI
        if not api_key:
            raise ValueError("EMBEDDING_API_KEY is required when EMBEDDING_PROVIDER=openai")
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model_name = model_name
        self._dim = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(model=self.model_name, input=texts)
        vectors = [item.embedding for item in response.data]
        if self._dim is None and vectors:
            self._dim = len(vectors[0])
        return vectors

    @property
    def dimension(self) -> int:
        if self._dim is None:
            # Trigger a single embedding call to discover dimension.
            self._dim = len(self.embed_texts(["dimension probe"])[0])
        return self._dim


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbeddingProvider(
            model_name=settings.EMBEDDING_MODEL,
            api_key=settings.EMBEDDING_API_KEY,
        )
    return LocalEmbeddingProvider(model_name=settings.EMBEDDING_MODEL)
