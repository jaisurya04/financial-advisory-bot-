# 💰 Financial Advisory Bot — RAG-Powered Chatbot

A production-style, end-to-end **financial advisory chatbot** built on a full **Retrieval-Augmented Generation (RAG)** pipeline — combining semantic search over a financial news knowledge base with LLM-based answer generation, conversational memory, and a clean REST API.

> Ask questions like *"What factors are affecting the banking sector?"* and get grounded, source-cited, context-aware answers — not hallucinated guesses.

---

## 🚀 Features

- 📰 **Automated news ingestion** — pulls financial news (or runs in demo mode with mock data, zero API keys required)
- ✂️ **Smart chunking** — recursive text splitting with configurable size/overlap
- 🧠 **Semantic embeddings** — local (sentence-transformers) or OpenAI-compatible, auto-dimension matching
- 🔍 **Vector search** — ChromaDB-powered retrieval with configurable Top-K and similarity threshold
- 💬 **Conversational memory** — persistent chat history with a windowed context for follow-up questions
- 🧩 **Prompt composition** — dedicated module merging system rules + retrieved context + chat history + query, with prompt-injection guardrails
- 🤖 **Pluggable LLM** — any OpenAI-compatible provider (OpenAI, Groq, etc.)
- ⚡ **FastAPI REST backend** — clean, documented, rate-limited, CORS-protected
- 🖥️ **Streamlit chat client** — source citations, session management, zero RAG logic on the frontend
- 🐳 **Docker-ready** — full `docker-compose` setup for one-command deployment

---

## 🏗️ Architecture

**Ingestion Pipeline**
```
Financial News API → Fetch → Clean/Normalize → Relational DB
   → Text Extraction → Chunking → Embeddings → Vector DB
```

**Query Pipeline**
```
User Question → REST API → Question Embedding → Vector Search
   → Top-K Chunks → Prompt Composition (+ Chat History) → LLM
   → Answer + Sources → Save to History → Response
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI, Pydantic |
| Database | SQLAlchemy (SQLite / PostgreSQL) |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers / OpenAI-compatible |
| LLM | OpenAI-compatible (OpenAI, Groq, etc.) |
| Chunking | LangChain Text Splitters |
| Frontend | Streamlit |
| Containerization | Docker, Docker Compose |

---

## 📂 Project Structure

```
financial-advisory-bot/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI entrypoint
│       ├── api/routes/          # chat, ingestion, health endpoints
│       ├── core/                # config, logging
│       ├── database/            # models, repositories, connection
│       ├── ingestion/           # news fetcher, cleaner, extractor, pipeline
│       ├── rag/                 # chunking, embeddings, vector store, retriever, prompt, chain
│       ├── chat/                # chat history service
│       └── schemas/             # Pydantic request/response models
├── frontend/                    # Streamlit chat client
├── scripts/                     # standalone ingest.py / index_documents.py
├── docker-compose.yml
└── README.md
```

---

## ⚡ Quick Start

### Option A — Local (no Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Runs out of the box with **mock news data + local embeddings — zero API keys required**. To enable full LLM-generated answers, add your API key to `.env`:

```
LLM_PROVIDER=openai
LLM_API_KEY=your_key_here
LLM_MODEL=your_model_name
LLM_BASE_URL=your_provider_base_url   # e.g. Groq, OpenAI, etc.
```

Seed the knowledge base:

```bash
curl -X POST http://localhost:8000/api/v1/ingest -H "Content-Type: application/json" -d "{}"
curl -X POST http://localhost:8000/api/v1/index -H "Content-Type: application/json" -d "{}"
```

Run the client:

```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Option B — Docker

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Backend → `http://localhost:8000` · Frontend → `http://localhost:8501`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service + vector store status |
| `POST` | `/api/v1/ingest` | Fetch financial news → store in DB |
| `POST` | `/api/v1/index` | Chunk → embed → store in vector DB |
| `POST` | `/api/v1/chat` | Ask a question, get a grounded answer + sources |
| `GET` | `/api/v1/chat/history/{session_id}` | Full conversation history |

Full interactive docs at `http://localhost:8000/docs` (Swagger UI).

---

## 🧠 Design Highlights

- **No hallucinated answers** — the system prompt instructs the LLM to explicitly say when retrieved context is insufficient, instead of inventing financial facts.
- **Not a licensed advisor** — responses are educational/general information with risk disclaimers on investment-related questions.
- **Prompt-injection guardrails** — retrieved context and chat history are clearly labeled as *data, not instructions* inside the composed prompt.
- **Follow-up question handling** — a lightweight query-rewrite step resolves pronouns ("it", "that") against the previous turn before retrieval.
- **Runs with zero API keys** out of the box, then upgrades piece by piece with real providers.

---

## 🧪 Tests

```bash
cd backend
pytest
```

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 👤 Author

**Jaisurya Marisamy**
IABAC Certified Data Scientist | Aspiring ML/Agentic AI Engineer

[LinkedIn](https://linkedin.com/in/jaisurya-m-698037316) · [GitHub](https://github.com/jaisurya04)
