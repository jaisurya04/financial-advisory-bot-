"""
Run the ingestion pipeline standalone (outside the API), e.g. via cron.
Usage: python scripts/ingest.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database.connection import init_db, session_scope
from app.ingestion.pipeline import run_ingestion

if __name__ == "__main__":
    init_db()
    with session_scope() as db:
        result = run_ingestion(db)
        print(f"Ingestion result: {result}")
