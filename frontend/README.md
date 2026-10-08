# Financial Advisory Bot — Client

A minimal Streamlit chat client that talks to the backend purely over REST
(`/api/v1/chat`, `/api/v1/ingest`, `/api/v1/index`). No RAG logic lives here.

## Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

By default it points at `http://localhost:8000`. To change it, create
`.streamlit/secrets.toml` with:

```toml
API_BASE_URL = "http://localhost:8000"
```

## Prefer React instead?

The backend is a plain REST API, so any frontend works. A React/Vite client
would call the same three endpoints:

- `POST /api/v1/chat` — send a question, get back `{answer, sources}`
- `POST /api/v1/ingest` — trigger news ingestion
- `POST /api/v1/index` — trigger chunk + embed + vector store indexing
- `GET /api/v1/chat/history/{session_id}` — load past messages
