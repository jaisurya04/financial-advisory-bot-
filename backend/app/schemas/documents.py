from typing import Optional

from pydantic import BaseModel


class IngestRequest(BaseModel):
    query: Optional[str] = "finance OR banking OR markets"


class IngestResponse(BaseModel):
    fetched: int
    inserted: int
    duplicates_skipped: int
    invalid_skipped: int


class IndexRequest(BaseModel):
    limit: Optional[int] = 200


class IndexResponse(BaseModel):
    documents_processed: int
    chunks_indexed: int
