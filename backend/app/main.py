from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routes import chat, ingestion, health
from app.core.config import get_settings
from app.core.logging_config import configure_logging, get_logger
from app.database.connection import init_db

settings = get_settings()
configure_logging()
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

app = FastAPI(
    title="Financial Advisory Bot API",
    description="RAG-powered financial advisory chatbot backend.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    logger.info("Starting Financial Advisory Bot API...")
    init_db()
    logger.info("Database initialized.")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak internal stack traces / secrets to the client.
    logger.error(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(health.router, tags=["health"])
app.include_router(chat.router, tags=["chat"])
app.include_router(ingestion.router, tags=["ingestion"])


@app.get("/")
def root():
    return {"message": "Financial Advisory Bot API is running. See /docs for API documentation."}
