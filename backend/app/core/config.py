"""
Centralized application configuration.
All tunables (chunk size, top_k, model names, etc.) live here and are
sourced from environment variables / .env — never hardcoded elsewhere.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # --- LLM ---
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_BASE_URL: str = ""
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 800

    # --- Embeddings ---
    EMBEDDING_PROVIDER: str = "local"  # "local" (sentence-transformers) or "openai"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_API_KEY: str = ""

    # --- News ingestion ---
    NEWS_API_KEY: str = ""
    NEWS_API_URL: str = "https://newsapi.org/v2/everything"

    # --- Vector store ---
    VECTOR_DB_PATH: str = "./vector_store"
    VECTOR_COLLECTION_NAME: str = "financial_documents"
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.0

    # --- Chunking ---
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120

    # --- Chat history ---
    CHAT_HISTORY_WINDOW: int = 6

    # --- API / security ---
    CORS_ALLOW_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    RATE_LIMIT_PER_MINUTE: int = 30

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ALLOW_ORIGINS.split(",") if o.strip()]

    @property
    def news_mock_mode(self) -> bool:
        return not bool(self.NEWS_API_KEY)


@lru_cache
def get_settings() -> Settings:
    return Settings()
